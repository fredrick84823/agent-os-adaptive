"""aoa-classify --check-diff：讀 nodes.json 與 git diff，回報這次改動碰到的最嚴格類別。

給 AI coding 流程用的升級檢查（escalation check）：
  - 每個改到的檔案（含刪除、未追蹤的新檔）對到 nodes.json 的 class
  - 不在 nodes.json 的新原始碼檔：用路徑規則推估（core_paths／敏感類別的路徑規則 → core；測試／範例 → leaf；其餘 → business，預設類別）
  - 依賴清單（package.json、pyproject.toml、requirements*.txt）新增的套件數 > --max-new-deps → 升級到 core 流程
  - 碰到 core（或 --fail-on 指定的類別）或需要升級 → exit 3；沒有 → exit 0；輸入錯誤 → exit 2

比較基準是 `git merge-base <base> HEAD` 到工作目錄（含已 stage、未 stage 與未追蹤的檔案），
也就是「這個分支相對 base 改了什麼」，base 之後自己前進的檔案不算。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from . import discover, rules

CLASSES = ("leaf", "business", "core")
STRICTNESS = {c: i for i, c in enumerate(CLASSES)}
WORKFLOW = {
    "leaf": "instructions/leaf-workflow.md",
    "business": "instructions/business-workflow.md",
    "core": "instructions/core-workflow.md",
}
EXIT_OK, EXIT_ERROR, EXIT_FLAG = 0, 2, 3
MANIFESTS = ("package.json", "pyproject.toml")
REQ_RE = re.compile(r"^requirements[\w.-]*\.(?:txt|in)$")
_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


class CheckError(ValueError):
    pass


def _git(root: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if check and p.returncode != 0:
        raise CheckError(f"git {' '.join(args)} 失敗：{p.stderr.strip() or p.stdout.strip()}")
    return p.stdout if p.returncode == 0 else ""


# ---------------------------------------------------------------------------
# 依賴清單
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _pep508_names(specs) -> set[str]:
    out = set()
    for s in specs or []:
        if isinstance(s, str):
            m = _REQ_NAME.match(s)
            if m:
                out.add(_norm(m.group(1)))
    return out


def manifest_deps(name: str, text: str | None) -> set[str]:
    """回傳依賴清單裡宣告的套件名（正規化）。解析失敗 → 空集合（不因格式錯誤擋住檢查）。"""
    if not text:
        return set()
    base = name.rsplit("/", 1)[-1]
    try:
        if base == "package.json":
            doc = json.loads(text)
            return {f"npm:{k}" for sec in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
                    for k in (doc.get(sec) or {})}
        if base == "pyproject.toml":
            doc = rules.tomllib.loads(text)
            proj = doc.get("project", {})
            names = _pep508_names(proj.get("dependencies"))
            for group in (proj.get("optional-dependencies") or {}).values():
                names |= _pep508_names(group)
            for group in (doc.get("dependency-groups") or {}).values():
                names |= _pep508_names(g for g in group if isinstance(g, str))
            poetry = doc.get("tool", {}).get("poetry", {})
            names |= {_norm(k) for k in (poetry.get("dependencies") or {}) if k != "python"}
            for g in (poetry.get("group") or {}).values():
                names |= {_norm(k) for k in (g.get("dependencies") or {})}
            return {f"py:{n}" for n in names}
        if REQ_RE.match(base):
            lines = [ln.split("#", 1)[0] for ln in text.splitlines()]
            return {f"py:{n}" for n in _pep508_names(ln for ln in lines if ln.strip() and not ln.strip().startswith("-"))}
    except (ValueError, AttributeError, rules.tomllib.TOMLDecodeError):
        return set()
    return set()


def is_manifest(path: str) -> bool:
    base = path.rsplit("/", 1)[-1]
    return base in MANIFESTS or bool(REQ_RE.match(base))


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def changed_files(root: Path, base: str) -> tuple[str, list[tuple[str, str]]]:
    """回傳 (merge-base commit, [(status, path)])；路徑相對 root（--relative），status 是 A/M/D/T/?（未追蹤）。"""
    _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    mb = _git(root, "merge-base", base, "HEAD").strip()
    if not mb:
        raise CheckError(f"{base} 與 HEAD 沒有共同祖先")
    out = []
    for line in _git(root, "diff", "--name-status", "--no-renames", "--relative", mb, "--").splitlines():
        if line.strip():
            st, path = line.split("\t", 1)
            out.append((st[0], path))
    seen = {p for _, p in out}
    for path in _git(root, "ls-files", "--others", "--exclude-standard").splitlines():
        if path.strip() and path not in seen:
            out.append(("?", path))
    return mb, sorted(out, key=lambda x: x[1])


def infer_new_file(path: str, cfg: dict, root: Path) -> tuple[str, list[str], str]:
    """不在 nodes.json 的原始碼檔：只用路徑能判的規則推估（看不到 import，所以不跑風險分數）。"""
    g = rules.first_glob(cfg["core_paths"], path)
    if g:
        return "core", ["config_core_path"], f"config_core_path: path matches '{g}' in core_paths"
    if discover.is_test(path) or rules.first_glob(cfg["test_paths"], path):
        return "leaf", ["test_file"], "test_file: new test file"
    if rules.first_glob(cfg["example_paths"], path):
        return "leaf", ["example_code"], "example_code: new example/docs file"
    if not rules.first_glob(cfg["not_sensitive"], path):
        from .classify import sensitive_hits  # 避免循環 import
        node = {"id": path, "language": discover.language_of(path), "module": None}
        hits = sensitive_hits(node, [], cfg, root)
        if hits:
            return "core", [r for r, _ in hits], "; ".join(w for _, w in hits)
    return "business", ["default"], ("default: new file not in nodes.json, not core, not leaf by path rules "
                                     "(re-run aoa-graph + aoa-classify after the change to score it)")


def check(root: Path, nodes_doc: dict, base: str, cfg: dict, max_new_deps: int = 0,
          ignore_prefixes: tuple[str, ...] = ()) -> dict:
    nodes = nodes_doc.get("nodes", {})
    mb, changes = changed_files(root, base)
    changes = [(st, p) for st, p in changes if not any(p.startswith(x) for x in ignore_prefixes)]
    files, new_deps = [], []
    for st, path in changes:
        rec = {"path": path, "status": st}
        if path in nodes:
            n = nodes[path]
            rec.update({"class": n["class"], "rules": n.get("rules", []), "source": "nodes.json"})
        elif st != "D" and discover.language_of(path) and not any(p in discover.IGNORE_DIRS for p in path.split("/")[:-1]):
            cls, rids, why = infer_new_file(path, cfg, root)
            rec.update({"class": cls, "rules": rids, "source": "inferred", "reason": why})
        else:
            rec.update({"class": None, "rules": [], "source": "not classified"})
        if is_manifest(path):
            before = manifest_deps(path, _git(root, "show", f"{mb}:./{path}", check=False) if st not in ("A", "?") else None)
            after = manifest_deps(path, (root / path).read_text(encoding="utf-8", errors="replace") if (root / path).is_file() else None)
            added = sorted(after - before)
            rec["new_dependencies"] = added
            new_deps += [f"{d} ({path})" for d in added]
        files.append(rec)

    classified = [f for f in files if f["class"]]
    strictest = max((f["class"] for f in classified), key=STRICTNESS.get, default=None)
    escalations = []
    if strictest == "core":
        escalations.append("diff touches core nodes: " + ", ".join(f["path"] for f in classified if f["class"] == "core"))
    if len(new_deps) > max_new_deps:
        escalations.append(f"diff adds {len(new_deps)} new dependencies (> --max-new-deps {max_new_deps}): " + ", ".join(new_deps))
    workflow_class = "core" if escalations else strictest
    src = nodes_doc.get("source") or {}
    warnings = []
    if src.get("commit"):
        anc = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", src["commit"], "HEAD"],
                             capture_output=True, check=False)
        if anc.returncode != 0:
            warnings.append(f"nodes.json was built at {src['commit'][:10]}, which is not an ancestor of HEAD "
                            "— re-run aoa-graph + aoa-classify")
    if src.get("dirty"):
        warnings.append("nodes.json was built from a dirty worktree")
    return {
        "base": base,
        "merge_base": mb,
        "nodes_source": src,
        "rules_version": nodes_doc.get("rules_version"),
        "strictest": strictest,
        "workflow_class": workflow_class,
        "workflow": WORKFLOW.get(workflow_class) if workflow_class else None,
        "escalate": bool(escalations),
        "escalations": escalations,
        "new_dependencies": new_deps,
        "warnings": warnings,
        "counts": {c: sum(1 for f in classified if f["class"] == c) for c in CLASSES} | {"unclassified": len(files) - len(classified)},
        "files": files,
    }


def render(res: dict) -> str:
    L = []
    src = res["nodes_source"] or {}
    rv = (res.get("rules_version") or {}).get("default")
    L.append(f"aoa-classify --check-diff: base {res['base']} (merge-base {res['merge_base'][:10]}); "
             f"nodes.json @ {str(src.get('commit') or '?')[:10]} (rules {rv})")
    if not res["files"]:
        L.append("no changed files")
    for f in sorted(res["files"], key=lambda x: (-STRICTNESS.get(x["class"], -1), x["path"])):
        cls = f["class"] or "-"
        mark = "*" if f["source"] == "inferred" else " "
        extra = f" [{', '.join(f['rules'])}]" if f["rules"] else ""
        if f["source"] == "inferred":
            extra += " (new file, inferred from path)"
        elif f["source"] == "not classified":
            extra += " (not a classified source file)"
        if f.get("new_dependencies"):
            extra += f" (+{len(f['new_dependencies'])} deps: {', '.join(f['new_dependencies'])})"
        L.append(f"  {cls:<8}{mark} {f['status']} {f['path']}{extra}")
    c = res["counts"]
    L.append(f"touched: core {c['core']}, business {c['business']}, leaf {c['leaf']}, unclassified {c['unclassified']}")
    for w in res["warnings"]:
        L.append(f"WARNING: {w}")
    for e in res["escalations"]:
        L.append(f"ESCALATE: {e}")
    if res["workflow_class"]:
        L.append(f"strictest class: {res['strictest']} → workflow: {res['workflow_class']} ({res['workflow']})")
    else:
        L.append("strictest class: none (no classified source files touched)")
    return "\n".join(L)


def main_check(args, cfg: dict, nodes_path: Path) -> int:
    root = Path(args.repo).resolve()
    if not nodes_path.is_file():
        print(f"aoa-classify: 找不到 {nodes_path}；請先跑 `aoa-graph` 與 `aoa-classify`", file=sys.stderr)
        return EXIT_ERROR
    try:
        doc = json.loads(nodes_path.read_text(encoding="utf-8"))
        try:  # aoa-graph／aoa-classify 自己的輸出目錄不算改動
            ignore = (nodes_path.parent.resolve().relative_to(root).as_posix() + "/",)
        except ValueError:
            ignore = ()
        res = check(root, doc, args.check_diff, cfg, args.max_new_deps, ignore)
    except (CheckError, json.JSONDecodeError) as e:
        print(f"aoa-classify: {e}", file=sys.stderr)
        return EXIT_ERROR
    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render(res))
    flagged = res["escalate"]
    if args.fail_on == "business" and res["strictest"] in ("business", "core"):
        flagged = True
    if args.fail_on == "never":
        flagged = False
    return EXIT_FLAG if flagged else EXIT_OK
