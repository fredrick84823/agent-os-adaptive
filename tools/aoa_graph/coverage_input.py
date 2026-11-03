"""讀覆蓋率檔，回傳 {node_id: 行覆蓋率 0–1}。支援 coverage.py JSON（`coverage json`）與 lcov（`lcov.info`）。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUTO_CANDIDATES = ("coverage.json", "coverage/lcov.info", "lcov.info")


def _parse_coverage_py(text: str) -> dict[str, tuple[int, int]]:
    doc = json.loads(text)
    files = doc.get("files")
    if not isinstance(files, dict):
        raise ValueError("coverage.py JSON 缺少 files")
    out = {}
    for path, info in files.items():
        s = info.get("summary", {})
        out[path] = (int(s.get("covered_lines", 0)), int(s.get("num_statements", 0)))
    return out


def _parse_lcov(text: str) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    cur, lh, lf = None, 0, 0
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("SF:"):
            cur, lh, lf = line[3:], 0, 0
        elif line.startswith("LH:"):
            lh = int(line[3:])
        elif line.startswith("LF:"):
            lf = int(line[3:])
        elif line == "end_of_record" and cur is not None:
            h0, f0 = out.get(cur, (0, 0))
            out[cur] = (h0 + lh, f0 + lf)
            cur = None
    return out


def _normalize(path: str, root: Path) -> str:
    p = path.replace("\\", "/")
    if Path(p).is_absolute():
        try:
            p = Path(p).resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return p.lstrip("/")
    while p.startswith("./"):
        p = p[2:]
    return p


def load(path: Path, root: Path, node_ids: list[str]) -> tuple[dict[str, float], dict]:
    """回傳 ({node: 覆蓋率}, 描述資訊)。路徑先照 repo 相對路徑比對，比不到再找唯一的後綴相符節點。"""
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if text.lstrip().startswith("{"):
        fmt, data = "coverage.py-json", _parse_coverage_py(text)
    elif "SF:" in text:
        fmt, data = "lcov", _parse_lcov(text)
    else:
        raise ValueError(f"{path.name}: 認不出覆蓋率格式（支援 coverage.py JSON 與 lcov）")
    ids = set(node_ids)
    totals: dict[str, list[int]] = {}
    unmatched = 0
    for p, (hit, total) in sorted(data.items()):
        rel = _normalize(p, root)
        node = rel if rel in ids else None
        if node is None:
            cands = [n for n in node_ids if n.endswith("/" + rel) or rel.endswith("/" + n)]
            node = cands[0] if len(cands) == 1 else None
        if node is None:
            unmatched += 1
            continue
        t = totals.setdefault(node, [0, 0])
        t[0] += hit
        t[1] += total
    cov = {n: round(h / t, 4) for n, (h, t) in sorted(totals.items()) if t > 0}
    info = {
        "format": fmt,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "files_in_report": len(data),
        "files_matched": len(cov),
        "files_unmatched": unmatched,
    }
    return cov, info
