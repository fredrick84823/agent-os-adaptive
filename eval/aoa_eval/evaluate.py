"""單一 repo 的評估：準確度（對標註）、確定性、相鄰 commit 穩定性、歷史回放。"""
from __future__ import annotations

import re
from pathlib import Path

from aoa_graph.git_history import DEFAULT_BUGFIX_PATTERN

from . import pipeline, scoring
from .repos import (
    EvalError,
    RepoSpec,
    commit_before,
    commit_time,
    first_parent_chain,
    git,
    worktree,
)

CLASSES = scoring.CLASSES


def _summary(doc: dict) -> dict:
    s = doc["summary"]
    return {
        "nodes": s["nodes"], "ranked": s["ranked"], "tests": s["tests"], "examples": s["examples"],
        "core": s["core"], "business": s["business"], "leaf": s["leaf"],
        "ranked_by_class": s["ranked_by_class"], "high_risk": s["high_risk"],
        "rules": s["rules"],
    }


def accuracy(doc: dict, labels: list[dict]) -> dict:
    nodes = doc["nodes"]
    missing = [e["path"] for e in labels if e["path"] not in nodes]
    if missing:
        raise EvalError(f"標註的路徑不在圖上（commit 換了？路徑打錯？）：{missing[:5]}")
    pairs_all, pairs_ranked, errors = [], [], []
    for e in sorted(labels, key=lambda x: x["path"]):
        n = nodes[e["path"]]
        pair = (e["label"], n["class"])
        pairs_all.append(pair)
        if n["population"] == "ranked":
            pairs_ranked.append(pair)
        if pair[0] != pair[1]:
            errors.append({
                "path": e["path"], "label": e["label"], "predicted": n["class"],
                "severity": scoring.COST[pair[0]][pair[1]],
                "rules": n["rules"], "percentile": n["percentile"],
                "prod_blast_radius": n["factors"]["prod_blast_radius"],
                "rationale": e["rationale"],
            })
    errors.sort(key=lambda x: (-x["severity"], x["path"]))
    return {
        "all": scoring.score(pairs_all),
        "ranked_only": scoring.score(pairs_ranked),
        "errors": errors,
        "core_to_leaf_paths": [x["path"] for x in errors if x["label"] == "core" and x["predicted"] == "leaf"],
    }


def stability(repo: Path, chain: list[str], per_commit: dict[str, dict[str, str]], labelled: set[str]) -> dict:
    """chain：[pinned, parent, …]；per_commit：commit → {file: class}。比較每對相鄰 commit。"""
    pairs = []
    tot_common = tot_changed = tot_untouched_changed = tot_untouched = 0
    for newer, older in zip(chain, chain[1:]):
        a, b = per_commit[older], per_commit[newer]
        common = sorted(set(a) & set(b))
        touched = set(git(repo, "diff", "--no-renames", "--name-only", older, newer).split("\n")) - {""}
        changed = [n for n in common if a[n] != b[n]]
        untouched = [n for n in common if n not in touched]
        unt_changed = [n for n in changed if n not in touched]
        tot_common += len(common)
        tot_changed += len(changed)
        tot_untouched += len(untouched)
        tot_untouched_changed += len(unt_changed)
        pairs.append({
            "from": older, "to": newer, "files_common": len(common), "files_touched": len(touched & set(common)),
            "class_changes": len(changed), "class_changes_untouched": len(unt_changed),
            "labelled_changes": sorted(n for n in changed if n in labelled),
            "examples": [{"path": n, "from": a[n], "to": b[n], "touched": n in touched} for n in changed[:10]],
        })
    return {
        "commits": len(chain),
        "pairs": pairs,
        "churn_rate": round(tot_changed / tot_common, 6) if tot_common else None,
        "untouched_churn_rate": round(tot_untouched_changed / tot_untouched, 6) if tot_untouched else None,
    }


def bugfix_touches(repo: Path, since: str, until: str, pattern: str = DEFAULT_BUGFIX_PATTERN) -> tuple[dict[str, int], int]:
    raw = git(repo, "log", "--no-merges", "--no-renames", "--name-only", "--format=%x1e%s", f"{since}..{until}")
    bug = re.compile(pattern, re.IGNORECASE)
    counts: dict[str, int] = {}
    commits = 0
    for block in raw.split("\x1e"):
        lines = [x for x in block.split("\n") if x.strip()]
        if not lines or not bug.search(lines[0]):
            continue
        commits += 1
        for f in set(lines[1:]):
            counts[f] = counts.get(f, 0) + 1
    return counts, commits


def replay(doc: dict, touches: dict[str, int], bugfix_commits: int) -> dict:
    """在舊 commit 的分類（只看 ranked 檔案），之後 bug-fix commit 改到的檔案是否偏向 core。"""
    ranked = {n: v["class"] for n, v in doc["nodes"].items() if v["population"] == "ranked"}
    total = len(ranked)
    hit_total = sum(1 for n in ranked if touches.get(n))
    base = hit_total / total if total else 0.0
    per = {}
    for c in CLASSES:
        files = [n for n in ranked if ranked[n] == c]
        hit = [n for n in files if touches.get(n)]
        rate = len(hit) / len(files) if files else None
        per[c] = {
            "files": len(files), "touched_by_bugfix": len(hit),
            "rate": None if rate is None else round(rate, 4),
            "lift": None if rate is None or base == 0 else round(rate / base, 3),
            "bugfix_touches": sum(touches.get(n, 0) for n in files),
        }
    return {
        "bugfix_commits": bugfix_commits,
        "ranked_files": total,
        "touched_by_bugfix": hit_total,
        "base_rate": round(base, 4),
        "per_class": per,
        "share_of_touched_files_in_core": round(per["core"]["touched_by_bugfix"] / hit_total, 4) if hit_total else None,
        "core_share_of_files": round(per["core"]["files"] / total, 4) if total else None,
    }


def evaluate_repo(spec: RepoSpec, repo: Path, labels: list[dict] | None, variants: dict[str, dict],
                  do_stability: bool = True, do_replay: bool = False, determinism: bool = True,
                  log=lambda msg: None) -> dict:
    result: dict = {"repo": spec.name, "url": spec.url, "commit": spec.commit, "variants": {}}
    log(f"{spec.name}: analyze {spec.commit[:10]}")
    with worktree(repo, spec.commit) as wt:
        first = pipeline.analyze(wt, variants)
    det = None
    if determinism:
        log(f"{spec.name}: determinism re-run (fresh worktree)")
        with worktree(repo, spec.commit) as wt:
            second = pipeline.analyze(wt, variants)
        det = {
            "graph_identical": first["graph_sha256"] == second["graph_sha256"],
            "nodes_identical": {v: first["nodes_sha256"][v] == second["nodes_sha256"][v] for v in variants},
            "nodes_sha256": first["nodes_sha256"],
        }
        det["ok"] = det["graph_identical"] and all(det["nodes_identical"].values())
    result["determinism"] = det
    result["graph"] = {k: first["summary"][k] for k in ("nodes", "edges", "runtime_cycles", "nodes_in_runtime_cycles")}

    chain_classes: dict[str, dict[str, dict[str, str]]] = {v: {spec.commit: pipeline.classes(first["nodes"][v])} for v in variants}
    chain = []
    if do_stability and spec.stability_commits > 0:
        chain = first_parent_chain(repo, spec.commit, spec.stability_commits)
        for c in chain[1:]:
            log(f"{spec.name}: stability {c[:10]}")
            with worktree(repo, c) as wt:
                a = pipeline.analyze(wt, variants)
            for v in variants:
                chain_classes[v][c] = pipeline.classes(a["nodes"][v])

    rep = None
    if do_replay:
        ts = commit_time(repo, spec.commit) - spec.replay_days * 86400
        rc = commit_before(repo, spec.commit, ts)
        if rc:
            log(f"{spec.name}: replay at {rc[:10]} ({spec.replay_days} days earlier)")
            with worktree(repo, rc) as wt:
                rep = {"commit": rc, "days": spec.replay_days, "analysis": pipeline.analyze(wt, variants)}
            rep["touches"], rep["bugfix_commits"] = bugfix_touches(repo, rc, spec.commit)

    labelled = {e["path"] for e in labels or []}
    for v in variants:
        doc = first["nodes"][v]
        vr: dict = {"rules_version": doc["rules_version"], "summary": _summary(doc)}
        if labels:
            vr["accuracy"] = accuracy(doc, labels)
        if chain:
            vr["stability"] = stability(repo, chain, chain_classes[v], labelled)
        if rep:
            vr["replay"] = {"commit": rep["commit"], "days": rep["days"],
                            **replay(rep["analysis"]["nodes"][v], rep["touches"], rep["bugfix_commits"])}
        result["variants"][v] = vr
    return result
