"""辨識 Django migration 檔，擷取 aoa-classify 分組需要的事實（不 import、不執行）。

Django migration：`<app>/migrations/NNNN_<name>.py`（四位數字開頭）且檔內有 `class Migration`。
擷取：
  - number：檔名開頭的編號
  - data_ops：檔內出現的 `RunPython`／`RunSQL`（資料遷移、手寫 SQL；對既有資料不可逆）
  - replaces：squashed migration 的 `replaces = [("app", "0001_x"), …]` 列出的 migration 名稱
"""
from __future__ import annotations

import re

_PATH = re.compile(r"(?:^|/)migrations/(\d{4})_[A-Za-z0-9_]*\.py$")
_CLASS = re.compile(rb"^class\s+Migration\b", re.MULTILINE)
_DATA_OPS = re.compile(rb"\b(RunPython|RunSQL)\b")
_REPLACES = re.compile(rb"^\s*replaces\s*=\s*[\[(]", re.MULTILINE)
_PAIR = re.compile(rb"""\(\s*['"][^'"]+['"]\s*,\s*['"]([^'"]+)['"]\s*\)""")


def _bracket_body(data: bytes, start: int) -> bytes:
    """從 start（左括號的下一個位元組）取到對應的右括號為止。"""
    depth, i = 1, start
    while i < len(data) and depth:
        c = data[i:i + 1]
        if c in (b"[", b"("):
            depth += 1
        elif c in (b"]", b")"):
            depth -= 1
        i += 1
    return data[start:i]


def inspect(path: str, data: bytes) -> dict | None:
    m = _PATH.search(path)
    if not m or not _CLASS.search(data):
        return None
    replaces: list[str] = []
    r = _REPLACES.search(data)
    if r:
        body = _bracket_body(data, r.end())
        replaces = sorted({p.decode("utf-8", "replace") for p in _PAIR.findall(body)})
    return {
        "number": int(m.group(1)),
        "data_ops": sorted({op.decode() for op in _DATA_OPS.findall(data)}),
        "replaces": replaces,
    }
