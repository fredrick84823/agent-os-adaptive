"""ground_truth/<repo>.jsonl：每行 {"path", "label", "rationale"}，# 開頭為註解。"""
from __future__ import annotations

import json
from pathlib import Path

from .repos import EvalError
from .scoring import CLASSES


def load(path: Path) -> list[dict]:
    out, seen = [], set()
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            e = json.loads(s)
        except json.JSONDecodeError as ex:
            raise EvalError(f"{path.name}:{i}: 不是合法的 JSON（{ex.msg}）") from ex
        if not isinstance(e, dict) or not isinstance(e.get("path"), str) or e.get("label") not in CLASSES:
            raise EvalError(f"{path.name}:{i}: 需要 \"path\" 與 \"label\"（{'/'.join(CLASSES)}）")
        if not str(e.get("rationale", "")).strip():
            raise EvalError(f"{path.name}:{i}: 需要 \"rationale\"（為什麼是這個類別）")
        if e["path"] in seen:
            raise EvalError(f"{path.name}:{i}: {e['path']} 重複標註")
        seen.add(e["path"])
        out.append({**e, "line": i})
    if not out:
        raise EvalError(f"{path.name}: 沒有任何標註")
    return out
