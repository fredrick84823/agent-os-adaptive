"""aoa-eval CLI。

  aoa-eval run      對 repos.toml 的 pinned repo 跑分類並和標註比對；core→leaf > 0 或輸出不確定 → exit 1
  aoa-eval sample   列出分層抽樣的檔案路徑（只印路徑，不印預測），給人標註用
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import labels as L
from . import pipeline
from .evaluate import evaluate_repo
from .report import gates, markdown
from .repos import (
    DEFAULT_LABELS,
    DEFAULT_REPOS,
    EvalError,
    default_cache_dir,
    ensure_repo,
    load_repos,
    worktree,
)
from .variants import GATE_VARIANT, VARIANTS


def _select(specs, names: str | None):
    if not names:
        return specs
    want = [n.strip() for n in names.split(",") if n.strip()]
    by = {s.name: s for s in specs}
    unknown = [n for n in want if n not in by]
    if unknown:
        raise EvalError(f"repos.toml 沒有 {unknown}（有：{sorted(by)}）")
    return [by[n] for n in want]


def cmd_run(args) -> int:
    specs = _select(load_repos(Path(args.repos_file)), args.repos)
    cache = Path(args.cache_dir) if args.cache_dir else default_cache_dir()
    variants = {v: VARIANTS[v] for v in (args.variants.split(",") if args.variants else VARIANTS)}
    if GATE_VARIANT not in variants:
        raise EvalError(f"--variants 必須包含 gate 變體 {GATE_VARIANT}")
    label_dir = Path(args.labels_dir)
    results = []
    for spec in specs:
        lp = label_dir / f"{spec.name}.jsonl"
        lab = L.load(lp) if lp.is_file() else None
        if lab is None:
            print(f"aoa-eval: {spec.name} 沒有標註檔 {lp}，只跑確定性／穩定性", file=sys.stderr)
        repo = ensure_repo(spec, cache, fetch=not args.no_fetch)
        if args.stability_commits is not None:
            spec = type(spec)(**{**spec.__dict__, "stability_commits": args.stability_commits})
        results.append(evaluate_repo(
            spec, repo, lab, variants,
            do_stability=not args.no_stability, do_replay=args.replay, determinism=not args.no_determinism,
            log=lambda m: print(f"aoa-eval: {m}", file=sys.stderr),
        ))
    fails = gates(results, GATE_VARIANT, args.min_kappa)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = {"gate_variant": GATE_VARIANT, "gate_failures": fails, "results": results}
    (out / "report.json").write_text(pipeline.dump(doc), encoding="utf-8")
    md = markdown(results, list(variants), GATE_VARIANT, fails)
    (out / "report.md").write_text(md, encoding="utf-8")
    sha = hashlib.sha256((out / "report.json").read_bytes()).hexdigest()[:16]
    print(f"aoa-eval: wrote {out / 'report.md'} (report.json sha256 {sha})", file=sys.stderr)
    for f in fails:
        print(f"aoa-eval: GATE FAIL {f}", file=sys.stderr)
    return 1 if fails else 0


def cmd_sample(args) -> int:
    """以 sha256(path) 排序做確定性抽樣：ranked 檔案依預測類別分層，另加少量測試／範例檔。只印路徑。"""
    spec = _select(load_repos(Path(args.repos_file)), args.repo)[0]
    cache = Path(args.cache_dir) if args.cache_dir else default_cache_dir()
    repo = ensure_repo(spec, cache, fetch=not args.no_fetch)
    with worktree(repo, spec.commit) as wt:
        a = pipeline.analyze(wt, {args.variant: VARIANTS[args.variant]})
    doc = a["nodes"][args.variant]
    lp = Path(args.labels_dir) / f"{spec.name}.jsonl"
    done = {e["path"] for e in L.load(lp)} if lp.is_file() else set()
    key = lambda p: hashlib.sha256(f"{args.seed}:{p}".encode()).hexdigest()
    picked = []
    for c in ("core", "business", "leaf"):
        pool = sorted((n for n, v in doc["nodes"].items() if v["population"] == "ranked" and v["class"] == c and n not in done), key=key)
        picked += pool[: args.per_class]
    other = sorted((n for n, v in doc["nodes"].items() if v["population"] != "ranked" and n not in done), key=key)
    picked += other[: args.non_ranked]
    for p in sorted(picked):
        print(json.dumps({"path": p}))
    return 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="aoa-eval", description="用人工標註驗證 aoa-classify 的分類準確度。")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--repos-file", default=str(DEFAULT_REPOS), help="pinned repo 清單（預設 eval/repos.toml）")
        sp.add_argument("--labels-dir", default=str(DEFAULT_LABELS), help="標註目錄（預設 eval/ground_truth）")
        sp.add_argument("--cache-dir", help="repo clone 的快取目錄（預設 $AOA_EVAL_CACHE 或 ~/.cache/aoa-eval/repos）")
        sp.add_argument("--no-fetch", action="store_true", help="不 clone／fetch，快取沒有就報錯")

    r = sub.add_parser("run", help="評估並寫出 report.json／report.md")
    common(r)
    r.add_argument("--repos", help="只跑這些 repo（逗號分隔）")
    r.add_argument("--out", default="eval/results", help="報告輸出目錄（預設 eval/results）")
    r.add_argument("--variants", help=f"規則變體（逗號分隔；可用：{', '.join(VARIANTS)}）")
    r.add_argument("--no-stability", action="store_true", help="不跑相鄰 commit 穩定性")
    r.add_argument("--stability-commits", type=int, help="覆寫 repos.toml 的 stability_commits")
    r.add_argument("--no-determinism", action="store_true", help="不重跑第二次比對輸出")
    r.add_argument("--replay", action="store_true", help="加跑歷史回放（之後的 bug-fix 是否偏向 core）")
    r.add_argument("--min-kappa", type=float, help="kappa 低於此值也算失敗（預設不檢查）")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("sample", help="列出分層抽樣的路徑給人標註（不顯示預測）")
    common(s)
    s.add_argument("repo")
    s.add_argument("--per-class", type=int, default=15, help="每個預測類別抽幾個 ranked 檔案")
    s.add_argument("--non-ranked", type=int, default=5, help="另抽幾個測試／範例檔")
    s.add_argument("--variant", default=GATE_VARIANT, choices=list(VARIANTS))
    s.add_argument("--seed", default="aoa-eval-1")
    s.set_defaults(func=cmd_sample)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        return args.func(args)
    except EvalError as e:
        print(f"aoa-eval: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
