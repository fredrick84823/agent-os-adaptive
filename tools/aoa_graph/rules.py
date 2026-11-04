"""aoa-classify 的規則設定：載入預設規則、合併 repo 的 .aoa.toml、path glob 與路徑 token 比對。"""
from __future__ import annotations

import copy
import re
import sys
from functools import cache
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - 3.10 only
    import tomli as tomllib

DEFAULT_RULES_PATH = Path(__file__).with_name("default_rules.toml")
REPO_CONFIG_NAME = ".aoa.toml"

LIST_KEYS = ("test_paths", "example_paths", "core_paths", "not_sensitive", "disable")
TOP_KEYS = {"version", "coverage", "thresholds", "weights", "structure", "sensitive", "keyword_scope", "migrations",
            *LIST_KEYS}
# keyword_scope：敏感 keyword 比對路徑的哪一段（2026.11-4 起）
KEYWORD_SCOPES = ("package", "repo")
# [migrations]：Django migration 分組規則（2026.11-4 起）
MIGRATION_KEYS = {"mode": ("grouped", "off"), "history_class": ("business", "leaf"),
                  "superseded_class": ("leaf", "business"), "latest_core": int, "data_ops_core": bool}
THRESHOLD_KEYS = {"core_top_percent", "leaf_bottom_percent", "boundary_margin_percent", "leaf_max_prod_blast_radius"}
WEIGHT_KEYS = {"churn", "bugfix", "direct_tests", "transitive_tests", "coverage"}
# [structure]：圖結構規則（runtime 循環的 hub、barrel 檔）。值的型別各自不同，見 _validate_structure。
STRUCTURE_ENUMS = {"runtime_cycle_core": ("hubs", "all"), "barrel_passthrough": ("catalog", "all", "off")}
STRUCTURE_NUMBERS = {"cycle_hub_all_max_size", "cycle_hub_min_share", "barrel_min_entries", "barrel_catalog_max_internal_share"}
SENSITIVE_KEYS = {"id", "description", "keywords", "paths", "packages", "entrypoints", "replace"}


class ConfigError(ValueError):
    pass


def _check_list(where: str, value) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"{where} 必須是字串陣列")
    return value


def _validate(cfg: dict, where: str) -> None:
    unknown = set(cfg) - TOP_KEYS
    if unknown:
        raise ConfigError(f"{where}: 不認得的欄位 {sorted(unknown)}")
    for k in LIST_KEYS:
        if k in cfg:
            _check_list(f"{where}.{k}", cfg[k])
    if "version" in cfg and not isinstance(cfg["version"], (str, int)):
        raise ConfigError(f"{where}.version 必須是字串或整數")
    if "coverage" in cfg and not isinstance(cfg["coverage"], str):
        raise ConfigError(f"{where}.coverage 必須是字串（路徑）")
    for table, keys in (("thresholds", THRESHOLD_KEYS), ("weights", WEIGHT_KEYS)):
        t = cfg.get(table, {})
        if not isinstance(t, dict):
            raise ConfigError(f"{where}.{table} 必須是 table")
        bad = set(t) - keys
        if bad:
            raise ConfigError(f"{where}.{table}: 不認得的欄位 {sorted(bad)}")
        for k, v in t.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                raise ConfigError(f"{where}.{table}.{k} 必須是 ≥ 0 的數字")
    _validate_structure(cfg.get("structure", {}), f"{where}.structure")
    if "keyword_scope" in cfg and cfg["keyword_scope"] not in KEYWORD_SCOPES:
        raise ConfigError(f"{where}.keyword_scope 必須是 {' | '.join(KEYWORD_SCOPES)}")
    _validate_migrations(cfg.get("migrations", {}), f"{where}.migrations")
    for i, s in enumerate(cfg.get("sensitive", [])):
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not s["id"]:
            raise ConfigError(f"{where}.sensitive[{i}] 需要字串 id")
        bad = set(s) - SENSITIVE_KEYS
        if bad:
            raise ConfigError(f"{where}.sensitive[{s['id']}]: 不認得的欄位 {sorted(bad)}")
        for k in ("keywords", "paths", "packages"):
            if k in s:
                _check_list(f"{where}.sensitive[{s['id']}].{k}", s[k])


def _validate_structure(t, where: str) -> None:
    if not isinstance(t, dict):
        raise ConfigError(f"{where} 必須是 table")
    bad = set(t) - set(STRUCTURE_ENUMS) - STRUCTURE_NUMBERS
    if bad:
        raise ConfigError(f"{where}: 不認得的欄位 {sorted(bad)}")
    for k, v in t.items():
        if k in STRUCTURE_ENUMS:
            if v not in STRUCTURE_ENUMS[k]:
                raise ConfigError(f"{where}.{k} 必須是 {' | '.join(STRUCTURE_ENUMS[k])}")
        elif isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            raise ConfigError(f"{where}.{k} 必須是 ≥ 0 的數字")


def _validate_migrations(t, where: str) -> None:
    if not isinstance(t, dict):
        raise ConfigError(f"{where} 必須是 table")
    bad = set(t) - set(MIGRATION_KEYS)
    if bad:
        raise ConfigError(f"{where}: 不認得的欄位 {sorted(bad)}")
    for k, v in t.items():
        spec = MIGRATION_KEYS[k]
        if spec is bool:
            if not isinstance(v, bool):
                raise ConfigError(f"{where}.{k} 必須是 true／false")
        elif spec is int:
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                raise ConfigError(f"{where}.{k} 必須是 ≥ 0 的整數")
        elif v not in spec:
            raise ConfigError(f"{where}.{k} 必須是 {' | '.join(spec)}")


def load_default() -> dict:
    cfg = tomllib.loads(DEFAULT_RULES_PATH.read_text(encoding="utf-8"))
    _validate(cfg, "default_rules.toml")
    return cfg


def load_repo_config(path: Path) -> dict:
    """讀 .aoa.toml 的 [classify] table（沒有就回傳空 dict）。"""
    try:
        doc = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path.name}: TOML 格式錯誤：{e}") from e
    cfg = doc.get("classify", {})
    if not isinstance(cfg, dict):
        raise ConfigError(f"{path.name}: [classify] 必須是 table")
    _validate(cfg, f"{path.name} [classify]")
    return cfg


def merge(default: dict, repo: dict) -> dict:
    """repo 設定覆蓋預設：

    - 清單欄位（core_paths、example_paths…）與 coverage：整個取代
    - keyword_scope：取代
    - thresholds／weights／structure／migrations：逐欄覆蓋
    - sensitive：同 id 時把 keywords／paths／packages 併入預設（replace = true 則整筆取代），新 id 附加在後
    - disable：移除指定 id 的敏感類別
    """
    out = copy.deepcopy(default)
    out["default_version"] = str(default.get("version", ""))
    out["repo_version"] = str(repo["version"]) if "version" in repo else None
    out.pop("version", None)
    for k in (*LIST_KEYS, "coverage", "keyword_scope"):
        if k in repo:
            out[k] = list(repo[k]) if k in LIST_KEYS else repo[k]
    for table in ("thresholds", "weights", "structure", "migrations"):
        out[table] = {**out.get(table, {}), **repo.get(table, {})}
    by_id = {s["id"]: s for s in out.get("sensitive", [])}
    order = [s["id"] for s in out.get("sensitive", [])]
    for s in repo.get("sensitive", []):
        if s["id"] in by_id and not s.get("replace"):
            base = by_id[s["id"]]
            for k in ("keywords", "paths", "packages"):
                base[k] = base.get(k, []) + [v for v in s.get(k, []) if v not in base.get(k, [])]
            for k in ("description", "entrypoints"):
                if k in s:
                    base[k] = s[k]
        else:
            if s["id"] not in by_id:
                order.append(s["id"])
            by_id[s["id"]] = {k: v for k, v in s.items() if k != "replace"}
    disabled = set(out.get("disable", []))
    unknown = disabled - set(by_id)
    if unknown:
        raise ConfigError(f"disable 指定了不存在的敏感類別 {sorted(unknown)}（可用：{order}）")
    out["sensitive"] = [by_id[i] for i in order if i not in disabled]
    return out


# ---------------------------------------------------------------------------
# 比對
# ---------------------------------------------------------------------------

@cache
def _glob_regex(pattern: str) -> re.Pattern:
    """CODEOWNERS／gitignore 式 glob（簡化版）。

    - `*` 不跨 `/`，`**` 跨任意層，`?` 單一字元
    - 開頭是 `/` 或中間含 `/` → 從 repo 根目錄錨定；否則任何深度都可命中（`*.py`、`auth`）
    - 命中目錄就涵蓋底下所有檔案（`docs` 與 `docs/` 都涵蓋 `docs/a.py`）
    """
    p = pattern.strip()
    anchored = p.startswith("/") or "/" in p.strip("/")
    p = p.strip("/")
    out = []
    segs = p.split("/")
    for i, seg in enumerate(segs):
        last = i == len(segs) - 1
        if seg == "**":
            out.append(".*" if last else "(?:[^/]+/)*")
            continue
        part = ""
        for ch in seg:
            part += "[^/]*" if ch == "*" else "[^/]" if ch == "?" else re.escape(ch)
        out.append(part if last else part + "/")
    body = "".join(out)
    prefix = "" if anchored else "(?:.*/)?"
    return re.compile(f"{prefix}{body}(?:/.*)?")


def glob_match(pattern: str, path: str) -> bool:
    return _glob_regex(pattern).fullmatch(path) is not None


def first_glob(patterns: list[str], path: str) -> str | None:
    for p in patterns:
        if glob_match(p, path):
            return p
    return None


_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+\d*|[A-Z]+\d*|\d+")


def path_tokens(path: str) -> list[str]:
    """`src/AuthProvider/user_sessions.py` → ['src', 'auth', 'provider', 'user', 'sessions', 'py']"""
    toks = []
    for part in re.split(r"[/_\-.\s]+", path):
        toks.extend(t.lower() for t in _CAMEL.findall(part))
    return toks


def _tok_eq(tok: str, kw: str) -> bool:
    """完全相同、複數（s／es），或去掉結尾數字後相同（oauth2 → oauth2 與 auth2 → auth 都算）。"""
    for t in (tok, tok.rstrip("0123456789")):
        if t and (t == kw or t == kw + "s" or t == kw + "es"):
            return True
    return False


def keyword_hit(keyword: str, tokens: list[str]) -> str | None:
    """回傳命中的 token（多 token keyword 回傳以 - 連接的片段），沒命中回傳 None。"""
    parts = [p for p in re.split(r"[-_\s]+", keyword.lower()) if p]
    n = len(parts)
    for i in range(len(tokens) - n + 1):
        window = tokens[i:i + n]
        if all(_tok_eq(t, k) for t, k in zip(window, parts)):
            return "-".join(window)
    return None
