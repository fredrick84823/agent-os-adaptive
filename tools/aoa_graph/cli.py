"""aoa-graph CLI：python3 tools/aoa_graph <repo> [options]"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import NAME, SCHEMA_VERSION, VERSION
from .discover import LANG_GROUPS, is_test, language_of, list_repo_files, source_files
from .extract import extract
from .git_history import DEFAULT_BUGFIX_PATTERN, head_info, history_metrics
from .metrics import compute
from .resolve_py import PyResolver
from .resolve_ts import TsResolver

DEFAULT_OUT = "agent-os-adaptive/architecture-analysis"


def build(root: Path, args: argparse.Namespace) -> dict:
    """分析 root，回傳 {"graph": ..., "metrics": ..., "unresolved": ...}（尚未寫檔）。"""
    langs = set()
    for g in args.lang.split(","):
        langs |= LANG_GROUPS[g.strip()] if g.strip() != "all" else set().union(*LANG_GROUPS.values())
    use_git = not args.no_git
    all_files = list_repo_files(root, use_git=use_git, excludes=tuple(args.exclude))
    files, too_big = source_files(root, all_files, langs)

    ts_resolver = TsResolver(root, all_files)
    py_resolver = PyResolver([f for f in files if f.endswith(".py")], tuple(args.py_root))

    edges: dict[tuple[str, str], dict] = {}
    external: dict[tuple[str, str], set[str]] = {}
    unresolved: list[dict] = []
    parse_errors: list[str] = []
    nodes = []
    for f in files:
        lang = language_of(f)
        data = (root / f).read_bytes()
        raws, has_error = extract(lang, data)
        if has_error:
            parse_errors.append(f)
        node = {
            "id": f,
            "language": "python" if lang == "python" else ("typescript" if lang in ("typescript", "tsx") else "javascript"),
            "is_test": is_test(f),
            "loc": data.count(b"\n") + (0 if not data or data.endswith(b"\n") else 1),
        }
        if lang == "python":
            node["module"] = py_resolver.module_of(f)
        nodes.append(node)
        for raw in raws:
            if raw.spec is None:
                unresolved.append({
                    "source": f, "line": raw.line, "kind": raw.kind,
                    "specifier": None, "expression": raw.expr, "reason": "dynamic_expression",
                })
                continue
            if lang == "python":
                results = py_resolver.resolve(f, raw)
            else:
                results = [ts_resolver.resolve(f, raw.spec)]
            for status, value in results:
                if status == "internal":
                    if value == f:
                        continue
                    e = edges.setdefault((f, value), {"kinds": set(), "count": 0})
                    e["kinds"].add(raw.kind)
                    e["count"] += 1
                elif status == "external":
                    external.setdefault((f, value), set()).add(raw.kind)
                elif status == "unresolved":
                    unresolved.append({
                        "source": f, "line": raw.line, "kind": raw.kind,
                        "specifier": raw.spec, "expression": None, "reason": value,
                    })

    node_ids = [n["id"] for n in nodes]
    edge_list = sorted(edges)
    runtime_edges = [k for k in edge_list if edges[k]["kinds"] != {"type"}]
    graph_metrics, cycles, runtime_cycles = compute(
        node_ids, edge_list, {n["id"]: n["is_test"] for n in nodes}, runtime_edges
    )

    head = head_info(root) if use_git else None
    source = {
        "commit": head["commit"] if head else None,
        "dirty": head["dirty"] if head else None,
    }
    git_params = {"git_available": head is not None}
    if head and not args.no_history:
        hist, hp = history_metrics(
            root, node_ids, head["commit_time"], args.since_days, args.bugfix_pattern,
            args.co_change_top, args.max_commit_files,
        )
        git_params.update(hp, shallow=head["shallow"])
        for n in node_ids:
            graph_metrics[n].update(hist[n])
    else:
        for n in node_ids:
            graph_metrics[n].update(churn=None, churn_lines=None, bugfix_count=None, co_change=[])

    generator = {"name": NAME, "version": VERSION}
    graph = {
        "schema_version": SCHEMA_VERSION,
        "generator": generator,
        "source": source,
        "granularity": "file",
        "nodes": nodes,
        "edges": [
            {"source": s, "target": t, "kinds": sorted(edges[(s, t)]["kinds"]), "count": edges[(s, t)]["count"]}
            for s, t in edge_list
        ],
        "external": [
            {"source": s, "package": p, "kinds": sorted(external[(s, p)])} for s, p in sorted(external)
        ],
    }
    unresolved.sort(key=lambda u: (u["source"], u["line"], u["kind"], u["specifier"] or "", u["expression"] or ""))
    unresolved_doc = {
        "schema_version": SCHEMA_VERSION,
        "generator": generator,
        "source": source,
        "items": unresolved,
        "parse_errors": sorted(parse_errors),
        "skipped_large_files": sorted(too_big),
    }
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "generator": generator,
        "source": source,
        "params": {"edge_kinds_counted": "all", **git_params},
        "summary": {
            "nodes": len(nodes),
            "edges": len(edge_list),
            "cycles": len(cycles),
            "nodes_in_cycles": sum(c["size"] for c in cycles),
            "runtime_cycles": len(runtime_cycles),
            "nodes_in_runtime_cycles": sum(c["size"] for c in runtime_cycles),
            "unresolved": len(unresolved),
            "parse_errors": len(parse_errors),
        },
        "cycles": cycles,
        "runtime_cycles": runtime_cycles,
        "nodes": graph_metrics,
    }
    return {"graph": graph, "metrics": metrics, "unresolved": unresolved_doc}


def dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="aoa-graph",
        description="用 tree-sitter 產生 TS/JS 與 Python repo 的確定性檔案級依賴圖與指標。",
    )
    p.add_argument("repo", nargs="?", default=".", help="要分析的 repo 路徑（預設：目前目錄）")
    p.add_argument("--out", help=f"輸出目錄（預設：<repo>/{DEFAULT_OUT}）")
    p.add_argument("--lang", default="all", help="all | ts | py，可用逗號組合（ts 含 JS）")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                   help="額外排除的路徑 glob（可重複），例如 'docs/**'")
    p.add_argument("--py-root", action="append", default=[], metavar="DIR",
                   help="額外的 Python 匯入根目錄（可重複）；repo 根目錄與 src/ 會自動加入")
    p.add_argument("--since-days", type=int, default=180, help="churn／bug-fix 的時間視窗（以 HEAD 時間往回算，預設 180）")
    p.add_argument("--bugfix-pattern", default=DEFAULT_BUGFIX_PATTERN, help="判定 bug-fix commit 的 regex（比對 commit subject，不分大小寫）")
    p.add_argument("--co-change-top", type=int, default=3, help="每個節點列出幾個共同變更夥伴（0 = 不算）")
    p.add_argument("--max-commit-files", type=int, default=50, help="超過這麼多檔案的 commit 不計入 co-change（大量格式化等）")
    p.add_argument("--no-git", action="store_true", help="不使用 git（改用檔案系統列舉，且不算歷史指標）")
    p.add_argument("--no-history", action="store_true", help="用 git 列檔，但不算 churn／bug-fix／co-change")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    root = Path(args.repo).resolve()
    if not root.is_dir():
        print(f"aoa-graph: {root} 不是目錄", file=sys.stderr)
        return 2
    start = time.monotonic()
    result = build(root, args)
    out = Path(args.out).resolve() if args.out else root / DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    for name in ("graph", "metrics", "unresolved"):
        (out / f"{name}.json").write_text(dump(result[name]), encoding="utf-8")
    s = result["metrics"]["summary"]
    print(
        f"aoa-graph: {s['nodes']} nodes, {s['edges']} edges, {s['cycles']} cycles "
        f"({s['nodes_in_cycles']} nodes; runtime-only: {s['runtime_cycles']} cycles), {s['unresolved']} unresolved, "
        f"{len(result['graph']['external'])} external refs, {s['parse_errors']} parse errors "
        f"in {time.monotonic() - start:.2f}s → {out}",
        file=sys.stderr,
    )
    return 0
