"""把評估結果寫成 report.json 與 report.md（不含時間戳與絕對路徑，同輸入位元相同）。"""
from __future__ import annotations

from .scoring import CLASSES


def _f(x, nd=3):
    if x is None:
        return "–"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def gates(results: list[dict], gate_variant: str, min_kappa: float | None) -> list[str]:
    fails = []
    for r in results:
        v = r["variants"].get(gate_variant, {})
        acc = v.get("accuracy")
        if acc and acc["all"]["core_to_leaf"] > 0:
            fails.append(f"{r['repo']}: core→leaf = {acc['all']['core_to_leaf']}（{', '.join(acc['core_to_leaf_paths'])}）")
        if r.get("determinism") and not r["determinism"]["ok"]:
            fails.append(f"{r['repo']}: 同一 commit 兩次輸出不同")
        if min_kappa is not None and acc and (acc["all"]["kappa"] is None or acc["all"]["kappa"] < min_kappa):
            fails.append(f"{r['repo']}: kappa {_f(acc['all']['kappa'])} < {min_kappa}")
    return fails


def markdown(results: list[dict], variants: list[str], gate_variant: str, fails: list[str]) -> str:
    L = ["# aoa-eval report", ""]
    L.append(f"Gate variant: `{gate_variant}` — " + ("**PASS**" if not fails else "**FAIL**"))
    for f in fails:
        L.append(f"- {f}")
    L.append("")
    L.append("> 標註是 agent 的初始標註，尚未經人工複核（見 eval/README.md）。")
    L.append("")
    L.append("## Accuracy")
    L.append("")
    L.append("| repo | variant | n (ranked) | kappa | weighted κ | kappa ranked | core→leaf | under | over | mean cost |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        for v in variants:
            acc = r["variants"][v].get("accuracy")
            if not acc:
                continue
            a, rk = acc["all"], acc["ranked_only"]
            L.append(f"| {r['repo']} | {v} | {a['n']} ({rk['n']}) | {_f(a['kappa'])} | {_f(a['weighted_kappa'])} | "
                     f"{_f(rk['kappa'])} | {a['core_to_leaf']} | {a['under_classified']} | {a['over_classified']} | {_f(a['cost_mean'])} |")
    L.append("")
    L.append("## Class counts")
    L.append("")
    L.append("| repo | variant | rules | nodes | core | business | leaf | ranked core／business／leaf | high_risk |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        for v in variants:
            s = r["variants"][v]["summary"]
            rb = s["ranked_by_class"]
            L.append(f"| {r['repo']} | {v} | {r['variants'][v]['rules_version']['default']} | {s['nodes']} | {s['core']} | "
                     f"{s['business']} | {s['leaf']} | {rb['core']}／{rb['business']}／{rb['leaf']} | {s['high_risk']} |")
    L.append("")
    if any(r.get("determinism") for r in results):
        L.append("## Determinism")
        L.append("")
        L.append("| repo | graph identical | nodes identical |")
        L.append("|---|---|---|")
        for r in results:
            d = r.get("determinism")
            if d:
                L.append(f"| {r['repo']} | {d['graph_identical']} | {all(d['nodes_identical'].values())} |")
        L.append("")
    if any("stability" in r["variants"][v] for r in results for v in variants):
        L.append("## Stability (adjacent first-parent commits)")
        L.append("")
        L.append("| repo | variant | commits | class churn | churn on untouched files | labelled files that flipped |")
        L.append("|---|---|---|---|---|---|")
        for r in results:
            for v in variants:
                st = r["variants"][v].get("stability")
                if st:
                    flipped = sorted({p for pr in st["pairs"] for p in pr["labelled_changes"]})
                    L.append(f"| {r['repo']} | {v} | {st['commits']} | {_f(st['churn_rate'], 4)} | "
                             f"{_f(st['untouched_churn_rate'], 4)} | {len(flipped)} |")
        L.append("")
    if any("replay" in r["variants"][v] for r in results for v in variants):
        L.append("## Historical replay")
        L.append("")
        L.append("在較舊的 commit 分類，數之後的 bug-fix commit 改到哪些檔案。lift = 該類被改到的比例 ÷ 全體比例。")
        L.append("")
        L.append("| repo | variant | replay commit | bug-fix commits | touched／ranked | core lift | business lift | leaf lift |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in results:
            for v in variants:
                rp = r["variants"][v].get("replay")
                if rp:
                    pc = rp["per_class"]
                    L.append(f"| {r['repo']} | {v} | `{rp['commit'][:10]}` | {rp['bugfix_commits']} | "
                             f"{rp['touched_by_bugfix']}／{rp['ranked_files']} | {_f(pc['core']['lift'])} | "
                             f"{_f(pc['business']['lift'])} | {_f(pc['leaf']['lift'])} |")
        L.append("")
    L.append("## Per repo")
    for r in results:
        L.append("")
        L.append(f"### {r['repo']} @ `{r['commit'][:10]}`")
        for v in variants:
            acc = r["variants"][v].get("accuracy")
            if not acc:
                continue
            a = acc["all"]
            L.append("")
            L.append(f"**{v}** — confusion（列 = 標註，欄 = 預測）")
            L.append("")
            L.append("| label \\ pred | " + " | ".join(CLASSES) + " | recall |")
            L.append("|---|" + "---|" * (len(CLASSES) + 1))
            for t in CLASSES:
                L.append(f"| {t} | " + " | ".join(str(a["confusion"][t][p]) for p in CLASSES)
                         + f" | {_f(a['per_class'][t]['recall'])} |")
            L.append("| precision | " + " | ".join(_f(a["per_class"][p]["precision"]) for p in CLASSES) + " | |")
            if acc["errors"]:
                L.append("")
                L.append("<details><summary>Disagreements (" + str(len(acc["errors"])) + ")</summary>")
                L.append("")
                L.append("| path | label | pred | rules | pct | prod blast |")
                L.append("|---|---|---|---|---|---|")
                for e in acc["errors"]:
                    L.append(f"| `{e['path']}` | {e['label']} | {e['predicted']} | {', '.join(e['rules'])} | "
                             f"{_f(e['percentile'], 1)} | {e['prod_blast_radius']} |")
                L.append("")
                L.append("</details>")
    return "\n".join(L) + "\n"
