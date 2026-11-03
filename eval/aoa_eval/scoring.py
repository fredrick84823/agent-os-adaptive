"""分類準確度指標：confusion matrix、Cohen's kappa、per-class precision／recall、非對稱成本。

類別有序：leaf < business < core。成本矩陣刻意不對稱——把風險低估（往 leaf 判）比高估貴得多，
core → leaf 是唯一的硬性失敗條件。
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
