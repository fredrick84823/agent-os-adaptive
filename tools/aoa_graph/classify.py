"""aoa-classify：讀 aoa-graph 的輸出，用確定性規則把每個檔案分成 core／business／leaf。

順序：
  1. 母體：測試檔與範例程式碼直接判 leaf，不參與排名
  2. 硬規則（命中即 core）：config core_paths、敏感類別（路徑 token／glob／import 的套件／套件入口）、runtime 循環（另標 high_risk）
  3. 風險分數 risk = impact × cost_of_failure ÷ detectability，在母體內取 midrank 百分位切分
  4. overrides.jsonl：比計算結果嚴格的自動生效；比較寬鬆的要有 approved_by（人工）才生效

同樣的輸入（graph／metrics／unresolved／設定檔／覆蓋率檔／overrides）→ nodes.json 位元相同。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from . import SCHEMA_VERSION, VERSION
from . import coverage_input, rules
from .metrics import tarjan_scc

NAME = "aoa-classify"
DEFAULT_DIR = "agent-os-adaptive/architecture-analysis"
OVERRIDES_NAME = "overrides.jsonl"
CLASSES = ("leaf", "business", "core")
STRICTNESS = {c: i for i, c in enumerate(CLASSES)}
# cfg 沒有 [structure] 時（例如舊的呼叫端自己組 cfg）用 2026.11-1 的行為。
STRUCTURE_DEFAULTS = {"runtime_cycle_core": "all", "cycle_hub_all_max_size": 3, "cycle_hub_min_share": 0.1,
                      "barrel_passthrough": "off", "barrel_min_entries": 3,
                      "barrel_catalog_max_internal_share": 0.1}


class InputError(ValueError):
    pass


# ---------------------------------------------------------------------------
# 圖：排除測試／範例後的遞移依賴者，以及可達的測試檔數
# ---------------------------------------------------------------------------

def reverse_reach(node_ids: list[str], edges: list[tuple[str, str]], prod: set[str], tests: set[str]):
    """回傳 {node: (prod_blast_radius, test_reach, prod_fan_in)}。

    prod_blast_radius：反向可達的「母體內」檔案數（不含自己；同一個 SCC 的成員互相計入，與 metrics.json 一致）。
    test_reach：反向可達的測試檔數（直接或遞移 import 它的測試）。
    """
    adj = {n: [] for n in node_ids}
    radj = {n: [] for n in node_ids}
    for s, t in edges:
        adj[s].append(t)
        radj[t].append(s)
    for n in node_ids:
        adj[n].sort()
        radj[n].sort()
    sccs = tarjan_scc(node_ids, adj)
    comp_of = {n: ci for ci, comp in enumerate(sccs) for n in comp}
    bit = {n: 1 << i for i, n in enumerate(node_ids)}
    prod_mask = sum(bit[n] for n in prod)
    test_mask = sum(bit[n] for n in tests)
    comp_mask = [sum(bit[n] for n in comp) for comp in sccs]
    reach = [0] * len(sccs)
    for ci in range(len(sccs) - 1, -1, -1):
        acc = 0
        for n in sccs[ci]:
            for d in radj[n]:
                dc = comp_of[d]
                if dc != ci:
                    acc |= comp_mask[dc] | reach[dc]
        reach[ci] = acc
    out = {}
    for n in node_ids:
        r = (reach[comp_of[n]] | comp_mask[comp_of[n]]) & ~bit[n]
        out[n] = (
            (r & prod_mask).bit_count(),
            (r & test_mask).bit_count(),
            sum(1 for d in radj[n] if d in prod),
        )
    return out


def barrel_cuts(nodes: dict[str, dict], edges: list[dict], mode: str, min_entries: float,
                max_internal_share: float = 0.1):
    """找出 TS/JS barrel 檔，回傳 (不往下傳 blast radius 的 re-export 邊, {barrel: {"kind", "entries"}})。

    barrel：所有 runtime 內部 import（kinds 不只 type）都是 re-export，且至少 min_entries 個。
    catalog barrel：barrel 的 re-export 目標彼此幾乎沒有 runtime import（目標之間的邊 ≤ max_internal_share × 目標數；
    並列的 locale、icon…，容許少數棄用別名，例如 zod 的 ua.ts → uk.ts）。
    mode="catalog" 只切 catalog barrel；"all" 切所有 barrel；"off" 不切。
    """
    if mode == "off":
        return set(), {}
    out_rt: dict[str, list[tuple[str, list[str]]]] = {}
    runtime_pairs = set()
    for e in edges:
        if e["kinds"] != ["type"]:
            out_rt.setdefault(e["source"], []).append((e["target"], e["kinds"]))
            runtime_pairs.add((e["source"], e["target"]))
    cuts, barrels = set(), {}
    for src in sorted(out_rt):
        if nodes.get(src, {}).get("language") not in ("typescript", "javascript"):
            continue
        outs = out_rt[src]
        if len(outs) < min_entries or not all("reexport" in k and set(k) <= {"reexport", "type"} for _, k in outs):
            continue
        targets = sorted(t for t, _ in outs)
        tset = set(targets)
        internal = sum(1 for a in targets for b in tset if a != b and (a, b) in runtime_pairs)
        catalog = internal <= max_internal_share * len(targets)
        kind = "catalog" if catalog else "barrel"
        barrels[src] = {"kind": kind, "entries": len(targets)}
        if mode == "all" or catalog:
            cuts.update((src, t) for t in targets)
    return cuts, barrels


def cycle_hubs(node_ids: list[str], edges: list[dict], m: dict, st: dict) -> dict[str, dict]:
    """runtime 循環成員 → {"hub", "fan_in"（循環內被幾個成員 runtime import）, "min_fan_in", "size"}。"""
    members: dict[object, list[str]] = {}
    for n in node_ids:
        if m[n].get("in_runtime_cycle"):
            members.setdefault(m[n].get("runtime_scc_id"), []).append(n)
    comp = {n: c for c, ns in members.items() for n in ns}
    fan_in = {n: set() for n in comp}
    for e in edges:
        s, t = e["source"], e["target"]
        if e["kinds"] != ["type"] and s in comp and t in comp and comp[s] == comp[t] and s != t:
            fan_in[t].add(s)
    out = {}
    for c, ns in members.items():
        size = len(ns)
        need = 0 if size <= st["cycle_hub_all_max_size"] else max(2, math.ceil(st["cycle_hub_min_share"] * size - 1e-9))
        for n in ns:
            k = len(fan_in[n])
            out[n] = {"hub": k >= need, "fan_in": k, "min_fan_in": need, "size": size}
    return out


def midrank_percentiles(scores: dict[str, float]) -> dict[str, float]:
    """百分位 = 100 × (分數比它低的數量 + 0.5 × 同分數量) ÷ N；同分同百分位。"""
    vals = sorted(scores.values())
    n = len(vals)
    out = {}
    import bisect
    for k, v in scores.items():
        lo = bisect.bisect_left(vals, v)
        hi = bisect.bisect_right(vals, v)
        out[k] = round(100.0 * (lo + 0.5 * (hi - lo)) / n, 2)
    return out


def _log2p(x) -> float:
    return math.log2(1 + (x or 0))


# ---------------------------------------------------------------------------
# 規則
# ---------------------------------------------------------------------------

def is_package_entrypoint(node: dict, root: Path | None) -> bool:
    nid = node["id"]
    name = nid.rsplit("/", 1)[-1]
    parent = nid.rsplit("/", 1)[0] if "/" in nid else ""
    if node.get("language") == "python":
        return name == "__init__.py" and bool(node.get("module")) and "." not in node["module"]
    stem = name.split(".", 1)[0]
    if stem != "index":
        return False
    if parent in ("", "src"):
        return True
    if root is None:
        return False
    if (root / parent / "package.json").is_file():
        return True
    if parent.endswith("/src") and (root / parent[: -len("/src")] / "package.json").is_file():
        return True
    return False


def sensitive_hits(node: dict, packages: list[str], cfg: dict, root: Path | None) -> list[tuple[str, str]]:
    """回傳 [(rule_id, reason)]，每個類別最多一筆（取第一個證據）。"""
    nid = node["id"]
    toks = rules.path_tokens(nid)
    hits = []
    for cat in cfg["sensitive"]:
        rid = f"sensitive:{cat['id']}"
        reason = None
        g = rules.first_glob(cat.get("paths", []), nid)
        if g:
            reason = f"path matches '{g}'"
        if reason is None:
            for kw in cat.get("keywords", []):
                t = rules.keyword_hit(kw, toks)
                if t:
                    reason = f"path token '{t}' matches keyword '{kw}'"
                    break
        if reason is None:
            for pkg in cat.get("packages", []):
                if pkg in packages:
                    reason = f"imports package '{pkg}'"
                    break
        if reason is None and cat.get("entrypoints") and is_package_entrypoint(node, root):
            reason = "package entrypoint (public import surface)"
        if reason:
            hits.append((rid, f"{rid}: {reason} ({cat.get('description', '')})".replace(" ()", "")))
    return hits


# ---------------------------------------------------------------------------
# overrides
# ---------------------------------------------------------------------------

def load_overrides(path: Path | None) -> list[dict]:
    if path is None or not path.is_file():
        return []
    entries = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            e = json.loads(s)
        except json.JSONDecodeError as ex:
            raise InputError(f"{path.name}:{n}: 不是合法的 JSON（{ex.msg}）") from ex
        if not isinstance(e, dict) or not isinstance(e.get("node"), str) or e.get("to") not in CLASSES:
            raise InputError(f"{path.name}:{n}: 需要 \"node\"（檔案路徑）與 \"to\"（{'/'.join(CLASSES)}）")
        if not str(e.get("reason", "")).strip():
            raise InputError(f"{path.name}:{n}: 需要 \"reason\"")
        entries.append({**e, "line": n})
    return entries


def apply_overrides(computed: dict[str, str], entries: list[dict]):
    """回傳 (final_class, {node: [applied entries]}, applied, pending, ignored)。"""
    final = dict(computed)
    per_node: dict[str, list[dict]] = {}
    applied, pending, ignored = [], [], []
    base = dict(computed)
    for e in entries:  # 先處理人工核准的放寬（檔案順序，後者為準）
        n = e["node"]
        if n not in computed:
            continue
        if STRICTNESS[e["to"]] < STRICTNESS[computed[n]] and str(e.get("approved_by", "")).strip():
            base[n] = e["to"]
    for e in entries:
        n = e["node"]
        rec = {k: e[k] for k in sorted(e) if k in ("node", "to", "by", "reason", "evidence", "approved_by", "line")}
        if n not in computed:
            ignored.append({**rec, "why": "node not in graph"})
            continue
        rec["from"] = computed[n]
        diff = STRICTNESS[e["to"]] - STRICTNESS[computed[n]]
        if diff > 0:
            rec["kind"] = "stricter"
            applied.append(rec)
            per_node.setdefault(n, []).append(rec)
        elif diff == 0:
            ignored.append({**rec, "why": "same as computed class"})
        elif str(e.get("approved_by", "")).strip():
            rec["kind"] = "looser_approved"
            applied.append(rec)
            per_node.setdefault(n, []).append(rec)
        else:
            rec["kind"] = "looser_needs_approval"
            pending.append(rec)
    for n, recs in per_node.items():
        cls = base[n]
        for r in recs:
            if r["kind"] == "stricter" and STRICTNESS[r["to"]] > STRICTNESS[cls]:
                cls = r["to"]
        final[n] = cls
    return final, per_node, applied, pending, ignored


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def classify(graph: dict, metrics: dict, unresolved: dict | None, cfg: dict,
             root: Path | None = None, coverage: dict[str, float] | None = None,
             overrides: list[dict] | None = None) -> dict:
    if graph.get("source") != metrics.get("source"):
        raise InputError("graph.json 與 metrics.json 的 source（commit／dirty）不一致，請重跑 aoa-graph")
    coverage = coverage or {}
    th, w = cfg["thresholds"], cfg["weights"]
    st = {**STRUCTURE_DEFAULTS, **cfg.get("structure", {})}
    nodes = {n["id"]: n for n in graph["nodes"]}
    node_ids = sorted(nodes)
    m = metrics["nodes"]
    missing = [n for n in node_ids if n not in m]
    if missing:
        raise InputError(f"metrics.json 缺少節點：{missing[:3]}…")
    edges = sorted((e["source"], e["target"]) for e in graph["edges"])
    pkgs: dict[str, list[str]] = {}
    for e in graph.get("external", []):
        pkgs.setdefault(e["source"], []).append(e["package"])
    parse_errors = set((unresolved or {}).get("parse_errors", []))

    tests = {n for n in node_ids if nodes[n].get("is_test") or rules.first_glob(cfg["test_paths"], n)}
    examples = {n for n in node_ids if n not in tests and rules.first_glob(cfg["example_paths"], n)}
    prod = [n for n in node_ids if n not in tests and n not in examples]
    cuts, barrels = barrel_cuts(nodes, graph["edges"], st["barrel_passthrough"], st["barrel_min_entries"],
                                 st["barrel_catalog_max_internal_share"])
    entry_of: dict[str, list[str]] = {}
    for b, t in sorted(cuts):
        entry_of.setdefault(t, []).append(b)
    reach = reverse_reach(node_ids, [e for e in edges if e not in cuts], set(prod), tests)
    hubs = cycle_hubs(node_ids, graph["edges"], m, st)

    factors, scores = {}, {}
    for n in node_ids:
        mm = m[n]
        prod_blast, test_reach, prod_fan_in = reach[n]
        churn, bugfix = mm.get("churn"), mm.get("bugfix_count")
        cov = coverage.get(n)
        impact = math.log2(2 + prod_blast) * (1 + w["churn"] * _log2p(churn))
        cost = 1 + w["bugfix"] * _log2p(bugfix)
        detect = (1 + w["direct_tests"] * _log2p(mm.get("test_fan_in"))
                  + w["transitive_tests"] * _log2p(test_reach) + w["coverage"] * (cov or 0.0))
        factors[n] = {
            "impact": round(impact, 4),
            "cost_of_failure": round(cost, 4),
            "detectability": round(detect, 4),
            "prod_blast_radius": prod_blast,
            "prod_fan_in": prod_fan_in,
            "test_fan_in": mm.get("test_fan_in"),
            "test_reach": test_reach,
            "churn": churn,
            "bugfix_count": bugfix,
            "coverage": cov,
            "runtime_cycle_fan_in": hubs[n]["fan_in"] if n in hubs else None,
        }
        if n in prod:
            scores[n] = round(impact * cost / detect, 6)
    pct = midrank_percentiles(scores) if scores else {}

    core_cut = 100 - th["core_top_percent"]
    core_boundary = core_cut - th["boundary_margin_percent"]
    leaf_cut = th["leaf_bottom_percent"] - th["boundary_margin_percent"]

    computed, out_nodes = {}, {}
    for n in node_ids:
        node, mm, f = nodes[n], m[n], factors[n]
        rule_ids, reasons, high_risk = [], [], False
        p = pct.get(n)
        g = rules.first_glob(cfg["core_paths"], n)
        if g:
            rule_ids.append("config_core_path")
            reasons.append(f"config_core_path: path matches '{g}' in core_paths")
        if n in tests or n in examples:
            if not rule_ids:
                rid = "test_file" if n in tests else "example_code"
                rule_ids.append(rid)
                reasons.append(f"{rid}: not ranked (" + ("test code" if n in tests else "example/docs code, not shipped") + ")")
            cls = "core" if "config_core_path" in rule_ids else "leaf"
        else:
            if not rules.first_glob(cfg["not_sensitive"], n):
                for rid, why in sensitive_hits(node, sorted(set(pkgs.get(n, []))), cfg, root):
                    rule_ids.append(rid)
                    reasons.append(why)
            if mm.get("in_runtime_cycle"):
                h = hubs[n]
                where = (f"runtime cycle {mm.get('runtime_scc_id')} ({h['size']} files; imported by {h['fan_in']} "
                         f"other members at runtime")
                if st["runtime_cycle_core"] == "all" or h["hub"]:
                    high_risk = True
                    rule_ids.append("runtime_cycle")
                    hub_txt = "" if st["runtime_cycle_core"] == "all" else f", hub: ≥ {h['min_fan_in']} needed"
                    reasons.append(f"runtime_cycle: member of {where}{hub_txt}) — changes ripple both ways")
                else:
                    reasons.append(f"note: member of {where}, below the hub cut of {h['min_fan_in']}) "
                                   "— not a hub, ranked by score")
            elif mm.get("in_cycle"):
                reasons.append(f"note: in type-only cycle {mm.get('scc_id')} (not a runtime cycle; no rule applied)")
            for b in entry_of.get(n, []):
                reasons.append(f"note: re-exported by {barrels[b]['kind']} barrel {b} ({barrels[b]['entries']} entries); "
                               f"its dependents are not counted in this file's blast radius (barrel_passthrough = {st['barrel_passthrough']})")
            score_txt = (f"risk {scores[n]:.3f} at p{p:g} (impact {f['impact']} × cost {f['cost_of_failure']} "
                         f"÷ detectability {f['detectability']}; prod blast {f['prod_blast_radius']}, "
                         f"churn {f['churn']}, bug-fix {f['bugfix_count']}, tests direct {f['test_fan_in']} / reach {f['test_reach']})")
            if rule_ids:
                cls = "core"
                reasons.append(f"score: {score_txt}")
            elif p >= core_cut:
                cls = "core"
                rule_ids.append("score_top")
                reasons.append(f"score_top: top {th['core_top_percent']:g}% — {score_txt}")
            elif p >= core_boundary:
                cls = "core"
                rule_ids.append("score_boundary")
                reasons.append(f"score_boundary: within {th['boundary_margin_percent']:g} points of the core cut (p{core_cut:g}), leaning stricter — {score_txt}")
            elif p < leaf_cut and f["prod_blast_radius"] <= th["leaf_max_prod_blast_radius"]:
                cls = "leaf"
                rule_ids.append("score_low")
                reasons.append(f"score_low: below p{leaf_cut:g} and prod blast radius {f['prod_blast_radius']} ≤ {th['leaf_max_prod_blast_radius']:g} — {score_txt}")
            elif p < leaf_cut:
                cls = "business"
                rule_ids.append("leaf_blast_guard")
                reasons.append(f"leaf_blast_guard: low score but {f['prod_blast_radius']} non-test files depend on it (> {th['leaf_max_prod_blast_radius']:g}) — {score_txt}")
            elif p < th["leaf_bottom_percent"]:
                cls = "business"
                rule_ids.append("leaf_boundary")
                reasons.append(f"leaf_boundary: within {th['boundary_margin_percent']:g} points of the leaf cut (p{th['leaf_bottom_percent']:g}), leaning stricter — {score_txt}")
            else:
                cls = "business"
                rule_ids.append("score_mid")
                reasons.append(f"score_mid: {score_txt}")
            if cls == "leaf" and n in parse_errors:
                cls = "business"
                rule_ids.append("parse_error_uncertain")
                reasons.append("parse_error_uncertain: tree-sitter reported a parse error, edges may be incomplete → not leaf")
        computed[n] = cls
        out_nodes[n] = {
            "computed_class": cls,
            "rules": rule_ids,
            "reasons": reasons,
            "high_risk": high_risk,
            "risk_score": scores.get(n),
            "percentile": p,
            "population": "test" if n in tests else "example" if n in examples else "ranked",
            "factors": f,
        }

    final, per_node, applied, pending, ignored = apply_overrides(computed, overrides or [])
    for n in node_ids:
        o = out_nodes[n]
        o["class"] = final[n]
        o["overrides"] = per_node.get(n, [])
        p = o["percentile"]
        if o["high_risk"] or (p is not None and p >= core_cut and final[n] == "core"):
            o["risk_level"] = "HIGH"
        elif final[n] == "leaf":
            o["risk_level"] = "LOW"
        else:
            o["risk_level"] = "MEDIUM"

    counts = {c: sum(1 for n in node_ids if final[n] == c) for c in CLASSES}
    rule_counts: dict[str, int] = {}
    for n in node_ids:
        for r in out_nodes[n]["rules"]:
            rule_counts[r] = rule_counts.get(r, 0) + 1
    ranked = len(prod)
    return {
        "schema_version": SCHEMA_VERSION,
        "generator": {"name": NAME, "version": VERSION},
        "source": metrics.get("source"),
        "rules_version": {"default": cfg.get("default_version"), "repo": cfg.get("repo_version")},
        "params": {
            "thresholds": th,
            "weights": w,
            "structure": st,
            "formula": "risk = log2(2 + prod_blast_radius) × (1 + w.churn·log2(1+churn)) × (1 + w.bugfix·log2(1+bugfix_count)) "
                       "÷ (1 + w.direct_tests·log2(1+test_fan_in) + w.transitive_tests·log2(1+test_reach) + w.coverage·coverage)",
            "percentile": "midrank over ranked (non-test, non-example) files",
            "sensitive_categories": [s["id"] for s in cfg["sensitive"]],
            "core_paths": cfg["core_paths"],
            "not_sensitive": cfg["not_sensitive"],
            "example_paths": cfg["example_paths"],
            "test_paths": cfg["test_paths"],
            "history_available": any(m[n].get("churn") is not None for n in node_ids),
        },
        "summary": {
            "nodes": len(node_ids),
            "ranked": ranked,
            "tests": len(tests),
            "examples": len(examples),
            **counts,
            "computed": {c: sum(1 for n in node_ids if computed[n] == c) for c in CLASSES},
            "ranked_by_class": {c: sum(1 for n in prod if final[n] == c) for c in CLASSES},
            "high_risk": sum(1 for n in node_ids if out_nodes[n]["high_risk"]),
            "runtime_cycle_members": len(hubs),
            "runtime_cycle_hubs": sum(1 for h in hubs.values() if h["hub"]) if st["runtime_cycle_core"] == "hubs" else len(hubs),
            "barrels": {k: sum(1 for b in barrels.values() if b["kind"] == k) for k in ("barrel", "catalog")},
            "barrel_edges_cut": len(cuts),
            "rules": dict(sorted(rule_counts.items())),
            "overrides_applied": len(applied),
            "overrides_pending": len(pending),
            "overrides_ignored": len(ignored),
        },
        "overrides": {"applied": applied, "pending": pending, "ignored": ignored},
        "nodes": out_nodes,
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: argparse.Namespace) -> tuple[dict, Path]:
    root = Path(args.repo).resolve()
    in_dir = Path(args.in_dir).resolve() if args.in_dir else root / DEFAULT_DIR
    docs = {}
    for name in ("graph", "metrics", "unresolved"):
        p = in_dir / f"{name}.json"
        if not p.is_file():
            if name == "unresolved":
                docs[name] = None
                continue
            raise InputError(f"找不到 {p}；請先跑 `aoa-graph {args.repo}`")
        docs[name] = json.loads(p.read_text(encoding="utf-8"))

    cfg_default = rules.load_default()
    cfg_path = None
    if not args.no_config:
        cfg_path = Path(args.config).resolve() if args.config else root / rules.REPO_CONFIG_NAME
        if args.config and not cfg_path.is_file():
            raise InputError(f"找不到設定檔 {cfg_path}")
        if not cfg_path.is_file():
            cfg_path = None
    cfg = rules.merge(cfg_default, rules.load_repo_config(cfg_path) if cfg_path else {})

    node_ids = sorted(n["id"] for n in docs["graph"]["nodes"])
    cov_path = None
    if not args.no_coverage:
        if args.coverage:
            cov_path = Path(args.coverage).resolve()
            if not cov_path.is_file():
                raise InputError(f"找不到覆蓋率檔 {cov_path}")
        elif cfg.get("coverage"):
            cov_path = (root / cfg["coverage"]).resolve()
            if not cov_path.is_file():
                raise InputError(f"設定檔指定的覆蓋率檔不存在：{cfg['coverage']}")
        else:
            cov_path = next((root / c for c in coverage_input.AUTO_CANDIDATES if (root / c).is_file()), None)
    cov, cov_info = ({}, None)
    if cov_path:
        cov, cov_info = coverage_input.load(cov_path, root, node_ids)
        cov_info = {"path": _rel(cov_path, root), **cov_info}

    ov_path = Path(args.overrides).resolve() if args.overrides else in_dir / OVERRIDES_NAME
    overrides = load_overrides(ov_path)

    doc = classify(docs["graph"], docs["metrics"], docs["unresolved"], cfg, root, cov, overrides)
    doc["inputs"] = {
        "config": {"path": _rel(cfg_path, root), "sha256": _sha(cfg_path)} if cfg_path else None,
        "coverage": cov_info,
        "overrides": {"path": _rel(ov_path, root), "sha256": _sha(ov_path), "entries": len(overrides)}
        if ov_path.is_file() else None,
        "unresolved_json": docs["unresolved"] is not None,
    }
    out = Path(args.out).resolve() if args.out else in_dir
    return doc, out


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="aoa-classify",
        description="讀 aoa-graph 的 graph.json／metrics.json，用確定性規則輸出 nodes.json（core／business／leaf）。",
    )
    p.add_argument("repo", nargs="?", default=".", help="repo 路徑（預設：目前目錄）；用來找 .aoa.toml、覆蓋率檔與 package.json")
    p.add_argument("--in", dest="in_dir", help=f"aoa-graph 輸出目錄（預設：<repo>/{DEFAULT_DIR}）")
    p.add_argument("--out", help="nodes.json 輸出目錄（預設：同 --in）")
    p.add_argument("--config", help=f"設定檔（預設：<repo>/{rules.REPO_CONFIG_NAME}，不存在就只用預設規則）")
    p.add_argument("--no-config", action="store_true", help="忽略 repo 設定檔，只用預設規則")
    p.add_argument("--coverage", help="覆蓋率檔（coverage.py JSON 或 lcov）；預設看設定檔，再找 " + "、".join(coverage_input.AUTO_CANDIDATES))
    p.add_argument("--no-coverage", action="store_true", help="不讀覆蓋率檔")
    p.add_argument("--overrides", help=f"覆寫紀錄（預設：<in>/{OVERRIDES_NAME}）")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        doc, out = run(args)
    except (InputError, rules.ConfigError, ValueError) as e:
        print(f"aoa-classify: {e}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    (out / "nodes.json").write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    s = doc["summary"]
    print(
        f"aoa-classify: {s['nodes']} nodes ({s['ranked']} ranked, {s['tests']} tests, {s['examples']} examples) → "
        f"core {s['core']}, business {s['business']}, leaf {s['leaf']}; high_risk {s['high_risk']}; "
        f"overrides applied {s['overrides_applied']}, pending {s['overrides_pending']} → {out / 'nodes.json'}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
