"""從 git log 計算 churn、bug-fix 次數與共同變更（co-change）。

時間視窗錨定在 HEAD commit 的 committer 時間（不是「現在」），
所以同一個 commit 不論哪天重跑，結果都一樣。
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
from itertools import combinations
from pathlib import Path

DEFAULT_BUGFIX_PATTERN = r"\b(fix(es|ed)?|bug(fix)?s?|hotfix(es)?|revert(s|ed)?)\b"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "core.quotepath=off", *args],
        check=True, capture_output=True,
    ).stdout.decode("utf-8", "replace")


def head_info(root: Path) -> dict | None:
    try:
        sha = _git(root, "rev-parse", "HEAD").strip()
        ct = int(_git(root, "show", "-s", "--format=%ct", "HEAD").strip())
        shallow = _git(root, "rev-parse", "--is-shallow-repository").strip() == "true"
        dirty = bool(_git(root, "status", "--porcelain", "--untracked-files=no").strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
    return {"commit": sha, "commit_time": ct, "shallow": shallow, "dirty": dirty}


def _iso(ts: int) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def history_metrics(
    root: Path,
    nodes: list[str],
    head_time: int,
    since_days: int,
    bugfix_pattern: str,
    co_change_top: int,
    max_commit_files: int,
) -> tuple[dict, dict]:
    """回傳 (每個節點的 git 指標, 參數紀錄)。"""
    since = head_time - since_days * 86400
    raw = _git(
        root, "log", "HEAD", "--no-merges", "--no-renames", "--relative", "--numstat",
        f"--since={_iso(since)}", "--format=%x1e%H%x1f%ct%x1f%s",
    )
    bug_re = re.compile(bugfix_pattern, re.IGNORECASE)
    node_set = set(nodes)
    stats = {n: {"churn": 0, "churn_lines": 0, "bugfix_count": 0} for n in nodes}
    pair_counts: dict[tuple[str, str], int] = {}
    commits_seen = 0
    for block in raw.split("\x1e"):
        if not block.strip():
            continue
        header, _, body = block.partition("\n")
        parts = header.split("\x1f")
        if len(parts) < 3:
            continue
        ct = int(parts[1])
        if ct < since or ct > head_time:
            continue
        commits_seen += 1
        is_fix = bool(bug_re.search(parts[2]))
        touched_all = []
        touched_nodes = []
        for line in body.splitlines():
            cols = line.split("\t")
            if len(cols) != 3:
                continue
            add, dele, path = cols
            touched_all.append(path)
            if path not in node_set:
                continue
            touched_nodes.append(path)
            s = stats[path]
            s["churn"] += 1
            s["churn_lines"] += (int(add) if add.isdigit() else 0) + (int(dele) if dele.isdigit() else 0)
            if is_fix:
                s["bugfix_count"] += 1
        if co_change_top and len(touched_all) <= max_commit_files:
            for a, b in combinations(sorted(set(touched_nodes)), 2):
                pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

    partners: dict[str, list[tuple[str, int]]] = {n: [] for n in nodes}
    for (a, b), c in pair_counts.items():
        if c >= 2:
            partners[a].append((b, c))
            partners[b].append((a, c))
    for n in nodes:
        top = sorted(partners[n], key=lambda x: (-x[1], x[0]))[:co_change_top]
        churn = stats[n]["churn"]
        stats[n]["co_change"] = [
            {"node": p, "count": c, "ratio": round(c / churn, 4) if churn else 0.0} for p, c in top
        ]
    params = {
        "since_days": since_days,
        "window_start": _iso(since),
        "window_end": _iso(head_time),
        "bugfix_pattern": bugfix_pattern,
        "co_change_top": co_change_top,
        "co_change_min_count": 2,
        "max_commit_files": max_commit_files,
        "commits_in_window": commits_seen,
    }
    return stats, params
