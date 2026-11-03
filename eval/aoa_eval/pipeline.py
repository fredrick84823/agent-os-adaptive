"""在一個 checkout 上跑 aoa-graph → aoa-classify（in-process，不寫進 repo）。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from aoa_graph import classify as C
from aoa_graph import cli, rules


def dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def config(extra: dict | None = None) -> dict:
    """預設規則 + extra（與 .aoa.toml 的 [classify] 同格式，例如評估用的規則變體）。"""
    extra = extra or {}
    rules._validate(extra, "variant")
    return rules.merge(rules.load_default(), extra)


def analyze(root: Path, variants: dict[str, dict]) -> dict:
    """回傳 {"graph_sha256", "nodes": {variant: nodes_doc}, "nodes_sha256": {variant: sha}}。

    圖只建一次，各規則變體共用；分類不讀 repo 的 .aoa.toml（評估要比的是預設規則本身）。
    """
    args = cli.parse_args([str(root)])
    built = cli.build(root, args)
    gsha = hashlib.sha256("".join(cli.dump(built[k]) for k in ("graph", "metrics", "unresolved")).encode()).hexdigest()
    out = {"graph_sha256": gsha, "summary": built["metrics"]["summary"], "nodes": {}, "nodes_sha256": {}}
    for name, extra in variants.items():
        doc = C.classify(built["graph"], built["metrics"], built["unresolved"], config(extra), root, {}, [])
        out["nodes"][name] = doc
        out["nodes_sha256"][name] = hashlib.sha256(dump(doc).encode()).hexdigest()
    return out


def classes(doc: dict) -> dict[str, str]:
    return {n: v["class"] for n, v in doc["nodes"].items()}
