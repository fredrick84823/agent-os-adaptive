"""把 TS/JS import specifier 解析成 repo 內的檔案。

支援：相對路徑、副檔名補全、index 檔、`./x.js` → `x.ts`（TS ESM 慣例）、
tsconfig/jsconfig `baseUrl` 與 `paths`（含 `extends` 相對路徑，best-effort）、
monorepo workspace 套件（以 package.json `name` 對應）。
"""
from __future__ import annotations

import json
import posixpath
import re

CODE_EXTS = (".ts", ".tsx", ".d.ts", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs")
_JS_TO_TS = {".js": (".ts", ".tsx", ".d.ts"), ".jsx": (".tsx",), ".mjs": (".mts", ".d.mts"), ".cjs": (".cts", ".d.cts")}
# 非程式碼資源（css、圖片、json…）不算依賴邊，也不算 unresolved
ASSET_EXTS = frozenset({
    ".css", ".scss", ".sass", ".less", ".styl", ".pcss", ".svg", ".png", ".jpg", ".jpeg", ".gif",
    ".webp", ".avif", ".ico", ".bmp", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".json", ".json5",
    ".html", ".md", ".mdx", ".txt", ".yaml", ".yml", ".wasm", ".graphql", ".gql", ".vue", ".svelte",
    ".astro", ".mp3", ".mp4", ".webm", ".wav", ".glsl", ".frag", ".vert", ".csv", ".xml", ".toml",
})


_BUILD_DIR_RE = re.compile(r"^\.?/?(dist|distribution|lib|build|out|esm|cjs|types|dts)/(.+)$")
_CODE_EXT_RE = re.compile(r"(\.d)?\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$")


def strip_jsonc(text: str) -> str:
    """移除 JSONC 的註解與尾逗號（tsconfig 允許這兩種寫法）。"""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def package_name(spec: str) -> str:
    if spec.startswith("node:"):
        return spec
    parts = spec.split("/")
    return "/".join(parts[:2]) if spec.startswith("@") and len(parts) > 1 else parts[0]


class TsResolver:
    def __init__(self, root, all_files: list[str]):
        self.root = root
        self.files = set(all_files)
        self._config_cache: dict[str, dict | None] = {}
        self._nearest_cache: dict[str, str | None] = {}
        self.config_files = {
            p for p in all_files if posixpath.basename(p) in ("tsconfig.json", "jsconfig.json")
        }
        self.workspace = self._workspace_packages(all_files)
        self.package_jsons = {posixpath.dirname(p) for p in all_files if posixpath.basename(p) == "package.json"}

    # ---------- file probing ----------
    def try_file(self, base: str) -> str | None:
        base = posixpath.normpath(base)
        if base.startswith("../") or base == "..":
            return None
        if base in self.files and base.endswith(CODE_EXTS):
            return base
        stem, ext = posixpath.splitext(base)
        for alt in _JS_TO_TS.get(ext, ()):
            if stem + alt in self.files:
                return stem + alt
        for ext in CODE_EXTS:
            if base + ext in self.files:
                return base + ext
        for ext in CODE_EXTS:
            cand = posixpath.join(base, "index" + ext) if base != "." else "index" + ext
            if cand in self.files:
                return cand
        return None

    # ---------- tsconfig ----------
    def _read_json(self, path: str) -> dict | None:
        try:
            return json.loads(strip_jsonc((self.root / path).read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return None

    def _load_config(self, path: str, depth: int = 0) -> dict | None:
        """回傳 {"baseUrl": 絕對於 repo 的路徑或 None, "paths": {...}, "paths_base": 路徑}。"""
        if path in self._config_cache:
            return self._config_cache[path]
        data = self._read_json(path) if path in self.files else None
        if not isinstance(data, dict):
            self._config_cache[path] = None
            return None
        cfg = {"baseUrl": None, "paths": None, "paths_base": None}
        ext = data.get("extends")
        for e in ([ext] if isinstance(ext, str) else ext if isinstance(ext, list) else []):
            if isinstance(e, str) and e.startswith(".") and depth < 8:
                parent_path = posixpath.normpath(posixpath.join(posixpath.dirname(path), e))
                if not parent_path.endswith(".json"):
                    parent_path += ".json"
                parent = self._load_config(parent_path, depth + 1)
                if parent:
                    for k, v in parent.items():
                        if v is not None:
                            cfg[k] = v
        here = posixpath.dirname(path)
        opts = data.get("compilerOptions") if isinstance(data.get("compilerOptions"), dict) else {}
        if isinstance(opts.get("baseUrl"), str):
            cfg["baseUrl"] = posixpath.normpath(posixpath.join(here, opts["baseUrl"]))
        if isinstance(opts.get("paths"), dict):
            cfg["paths"] = opts["paths"]
            cfg["paths_base"] = None  # 由 baseUrl 或本檔目錄決定
            cfg["_paths_dir"] = here
        base = cfg.get("baseUrl")
        if cfg["paths"] is not None:
            cfg["paths_base"] = base if base is not None else cfg.get("_paths_dir", here)
        self._config_cache[path] = cfg
        return cfg

    def _nearest_config(self, importer: str) -> dict | None:
        d = posixpath.dirname(importer)
        if d in self._nearest_cache:
            path = self._nearest_cache[d]
        else:
            path, cur = None, d
            while True:
                for name in ("tsconfig.json", "jsconfig.json"):
                    cand = posixpath.join(cur, name) if cur else name
                    if cand in self.config_files:
                        path = cand
                        break
                if path or not cur:
                    break
                cur = posixpath.dirname(cur)
            self._nearest_cache[d] = path
        return self._load_config(path) if path else None

    # ---------- workspace packages ----------
    def _workspace_packages(self, all_files: list[str]) -> dict[str, str]:
        pkgs: dict[str, str] = {}
        for p in all_files:
            if posixpath.basename(p) != "package.json":
                continue
            data = self._read_json(p)
            if isinstance(data, dict) and isinstance(data.get("name"), str):
                pkgs.setdefault(data["name"], posixpath.dirname(p))
        return pkgs

    def _package_entry(self, pkg_dir: str) -> str | None:
        data = self._read_json(posixpath.join(pkg_dir, "package.json") if pkg_dir else "package.json") or {}
        cands: list[str] = []

        def collect(v):
            if isinstance(v, str):
                cands.append(v)
            elif isinstance(v, dict):
                for k in sorted(v):
                    if k == "." or not k.startswith("."):
                        collect(v[k])
            elif isinstance(v, list):
                for x in v:
                    collect(x)

        for key in ("source", "types", "typings", "exports", "module", "main"):
            collect(data.get(key))
        cands += ["src/index", "source/index", "index"]
        for c in cands:
            hit = self.try_file(posixpath.join(pkg_dir, c))
            if hit:
                return hit
            # dist/index.js 常不在版控；試著對應回 src/ 或 source/
            m = _BUILD_DIR_RE.match(c)
            if m:
                rest = _CODE_EXT_RE.sub("", m.group(2))
                for src_dir in ("src", "source"):
                    hit = self.try_file(posixpath.join(pkg_dir, src_dir, rest))
                    if hit:
                        return hit
        return None

    # ---------- main entry ----------
    def resolve(self, importer: str, spec: str) -> tuple[str, str]:
        """回傳 (status, value)：
        ("internal", 檔案路徑) | ("external", 套件名) | ("asset", spec) | ("unresolved", 原因)
        """
        spec = spec.split("?", 1)[0].split("#", 1)[0] if not spec.startswith("#") else spec
        if not spec:
            return "unresolved", "empty_specifier"
        ext = posixpath.splitext(spec)[1].lower()
        if ext in ASSET_EXTS:
            return "asset", spec
        if spec.startswith(("./", "../")) or spec in (".", ".."):
            target = posixpath.normpath(posixpath.join(posixpath.dirname(importer), spec))
            if target.startswith(".."):
                return "unresolved", "outside_repo"
            hit = self.try_file(target)
            return ("internal", hit) if hit else ("unresolved", "not_found")
        if spec.startswith("/"):
            return "unresolved", "absolute_path"
        if spec.startswith("#"):
            return self._resolve_subpath_import(importer, spec)

        cfg = self._nearest_config(importer)
        if cfg and cfg.get("paths"):
            matched, hit = self._match_paths(cfg, spec)
            if hit:
                return "internal", hit
            if matched:
                return "unresolved", "tsconfig_paths_target_not_found"
        if cfg and cfg.get("baseUrl") is not None:
            hit = self.try_file(posixpath.join(cfg["baseUrl"], spec))
            if hit:
                return "internal", hit

        name = package_name(spec)
        if name in self.workspace:
            pkg_dir = self.workspace[name]
            sub = spec[len(name):].lstrip("/")
            if not sub:
                hit = self._package_entry(pkg_dir)
            else:
                hit = next(
                    (h for d in ("", "src", "source") if (h := self.try_file(posixpath.join(pkg_dir, d, sub)))),
                    None,
                )
            if hit:
                return "internal", hit
            return "unresolved", "workspace_package_entry_not_found"
        return "external", name

    def _resolve_subpath_import(self, importer: str, spec: str) -> tuple[str, str]:
        """package.json `imports` 欄位（`#types/*` 這類 subpath import），取最近的 package.json。"""
        d = posixpath.dirname(importer)
        while True:
            if d in self.package_jsons:
                break
            if not d:
                return "unresolved", "package_imports_field_missing"
            d = posixpath.dirname(d)
        data = self._read_json(posixpath.join(d, "package.json") if d else "package.json") or {}
        imports = data.get("imports")
        if not isinstance(imports, dict):
            return "unresolved", "package_imports_field_missing"
        matched, hit = self._match_patterns(imports, spec, d, collect_all=True)
        if hit:
            return "internal", hit
        return "unresolved", "package_imports_target_not_found" if matched else "package_imports_no_match"

    def _match_patterns(self, table: dict, spec: str, base: str, collect_all: bool = False):
        best = None  # (prefix_len, pattern)
        for pattern in table:
            if "*" in pattern:
                pre, _, suf = pattern.partition("*")
                matches = spec.startswith(pre) and spec.endswith(suf) and len(spec) >= len(pre) + len(suf)
                if matches and (best is None or len(pre) > best[0]):
                    best = (len(pre), pattern)
            elif pattern == spec:
                best = (10**9, pattern)
                break
        if best is None:
            return False, None
        pattern = best[1]
        star = None
        if "*" in pattern:
            pre, _, suf = pattern.partition("*")
            star = spec[len(pre): len(spec) - len(suf)]
        targets: list[str] = []

        def collect(v):
            if isinstance(v, str):
                targets.append(v)
            elif isinstance(v, list):
                for x in v:
                    collect(x)
            elif isinstance(v, dict) and collect_all:
                for k in sorted(v):
                    collect(v[k])

        collect(table[pattern])
        for sub in targets:
            target = sub.replace("*", star) if star is not None else sub
            full = posixpath.join(base, target)
            hit = self.try_file(full)
            if not hit:
                m = _BUILD_DIR_RE.match(target)
                if m:
                    rest = _CODE_EXT_RE.sub("", m.group(2))
                    hit = next((h for sd in ("src", "source") if (h := self.try_file(posixpath.join(base, sd, rest)))), None)
            if hit:
                return True, hit
        return True, None

    def _match_paths(self, cfg: dict, spec: str) -> tuple[bool, str | None]:
        return self._match_patterns(cfg["paths"], spec, cfg["paths_base"])
