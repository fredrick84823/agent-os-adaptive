"""分類準確度指標。

主要指標是兩個二元決策（AI coding 流程真正要做的判斷）：
  - is core？ 看 core recall——真的 core 有多少被判成 core（漏判 = 敏感檔案走了比較鬆的流程）
  - is leaf？ 看 leaf precision——判成 leaf 的有多少真的是 leaf（誤判 = AI 在不該放手的檔案上直接改）
另有硬性門檻 core → leaf 必須是 0。

次要指標：confusion matrix、Cohen's kappa（未加權／線性加權）、per-class precision／recall、非對稱成本。
類別有序：leaf < business < core。成本矩陣刻意不對稱——把風險低估（往 leaf 判）比高估貴得多。
"""
from __future__ import annotations

CLASSES = ("leaf", "business", "core")
_IDX = {c: i for i, c in enumerate(CLASSES)}

# COST[true][pred]：每個標註檔案的錯判成本。
# - 低估（pred 比 true 寬鬆）：AI 會在比實際更危險的檔案上用比較少的審查與測試 → 貴
# - 高估（pred 比 true 嚴格）：多花審查時間，但不會出事 → 便宜
# - core → leaf 另外當硬性門檻（必須是 0），這裡的 10 只影響平均成本
COST = {
    "core": {"core": 0.0, "business": 4.0, "leaf": 10.0},
    "business": {"core": 1.0, "business": 0.0, "leaf": 2.0},
    "leaf": {"core": 1.5, "business": 0.5, "leaf": 0.0},
}


def confusion(pairs: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    """pairs：[(true, pred)] → {true: {pred: count}}，三個類別都會出現（0 也列）。"""
    m = {t: {p: 0 for p in CLASSES} for t in CLASSES}
    for t, p in pairs:
        m[t][p] += 1
    return m


def _kappa(m: dict[str, dict[str, int]], weights) -> float | None:
    n = sum(sum(r.values()) for r in m.values())
    if n == 0:
        return None
    row = {t: sum(m[t].values()) for t in CLASSES}
    col = {p: sum(m[t][p] for t in CLASSES) for p in CLASSES}
    obs = sum(weights(t, p) * m[t][p] for t in CLASSES for p in CLASSES) / n
    exp = sum(weights(t, p) * row[t] * col[p] for t in CLASSES for p in CLASSES) / (n * n)
    if exp == 0:
        return 1.0 if obs == 0 else None
    return 1.0 - obs / exp


def cohen_kappa(m: dict[str, dict[str, int]]) -> float | None:
    """未加權 Cohen's kappa（以「不一致」權重表示：對角線 0，其餘 1）。全部同一類時回傳 None。"""
    return _kappa(m, lambda t, p: 0.0 if t == p else 1.0)


def linear_weighted_kappa(m: dict[str, dict[str, int]]) -> float | None:
    """線性加權 kappa：類別有序，差一級的錯比差兩級輕（core↔leaf 權重 1，相鄰 0.5）。"""
    span = len(CLASSES) - 1
    return _kappa(m, lambda t, p: abs(_IDX[t] - _IDX[p]) / span)


def per_class(m: dict[str, dict[str, int]]) -> dict[str, dict]:
    out = {}
    for c in CLASSES:
        tp = m[c][c]
        support = sum(m[c].values())
        predicted = sum(m[t][c] for t in CLASSES)
        prec = tp / predicted if predicted else None
        rec = tp / support if support else None
        f1 = 2 * prec * rec / (prec + rec) if prec and rec else (0.0 if prec is not None and rec is not None else None)
        out[c] = {"support": support, "predicted": predicted, "precision": _r(prec), "recall": _r(rec), "f1": _r(f1)}
    return out


def binary(pairs: list[tuple[str, str]], cls: str) -> dict:
    """把三類問題收斂成「是不是 cls」的二元決策：tp／fp／fn／tn、precision、recall。"""
    tp = sum(1 for t, p in pairs if t == cls and p == cls)
    fp = sum(1 for t, p in pairs if t != cls and p == cls)
    fn = sum(1 for t, p in pairs if t == cls and p != cls)
    tn = len(pairs) - tp - fp - fn
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "support": tp + fn, "predicted": tp + fp,
        "precision": _r(tp / (tp + fp)) if tp + fp else None,
        "recall": _r(tp / (tp + fn)) if tp + fn else None,
    }


def _r(x: float | None) -> float | None:
    return None if x is None else round(x, 4)


def score(pairs: list[tuple[str, str]]) -> dict:
    m = confusion(pairs)
    n = len(pairs)
    agree = sum(m[c][c] for c in CLASSES)
    total_cost = sum(COST[t][p] for t, p in pairs)
    under = sum(1 for t, p in pairs if _IDX[p] < _IDX[t])
    over = sum(1 for t, p in pairs if _IDX[p] > _IDX[t])
    return {
        "n": n,
        "is_core": binary(pairs, "core"),   # 主要：recall
        "is_leaf": binary(pairs, "leaf"),   # 主要：precision
        "accuracy": _r(agree / n) if n else None,
        "kappa": _r(cohen_kappa(m)),
        "weighted_kappa": _r(linear_weighted_kappa(m)),
        "confusion": m,
        "per_class": per_class(m),
        "core_to_leaf": m["core"]["leaf"],
        "under_classified": under,
        "over_classified": over,
        "cost_total": round(total_cost, 4),
        "cost_mean": _r(total_cost / n) if n else None,
    }
