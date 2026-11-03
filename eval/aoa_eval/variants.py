"""評估時比較的規則變體（格式同 .aoa.toml 的 [classify]）。

"current" 是目前的預設規則；其他變體重現舊版行為或單獨開關一項修正，讓 report 能並排看修正前後（ablation）。
gate（core→leaf 必須是 0）只看 GATE_VARIANT。
"""
from __future__ import annotations

BEFORE = {"runtime_cycle_core": "all", "barrel_passthrough": "off"}

VARIANTS: dict[str, dict] = {
    # 2026.11-1 的行為：每個 runtime 循環成員都是 core、barrel 不特別處理
    "before": {"structure": dict(BEFORE)},
    # 只開「循環只取 hub」
    "hubs-only": {"structure": {**BEFORE, "runtime_cycle_core": "hubs"}},
    # 只開「catalog barrel 不往下傳」
    "catalog-only": {"structure": {**BEFORE, "barrel_passthrough": "catalog"}},
    # 實驗：所有 barrel 都不往下傳（沒有採用，留著對照）
    "all-barrels": {"structure": {"runtime_cycle_core": "hubs", "barrel_passthrough": "all"}},
    # 目前的預設規則（2026.11-2：hubs + catalog）
    "current": {},
}
GATE_VARIANT = "current"
