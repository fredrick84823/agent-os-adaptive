"""評估時比較的規則變體（格式同 .aoa.toml 的 [classify]）。

"current" 是目前的預設規則；其他變體重現舊版行為或單獨開關一項修正，讓 report 能並排看修正前後（ablation）。
gate（core→leaf 必須是 0）只看 GATE_VARIANT。
"""
from __future__ import annotations

BEFORE = {"runtime_cycle_core": "all", "barrel_passthrough": "off"}
# 2026.11-4 之前的 keyword 比對範圍與 migration 規則（完整路徑、每個 migration 都靠 db_schema glob 進 core）
PRE_MONOREPO = {"keyword_scope": "repo", "migrations": {"mode": "off"}}

VARIANTS: dict[str, dict] = {
    # 2026.11-1 的行為：每個 runtime 循環成員都是 core、barrel 不特別處理
    "before": {"structure": dict(BEFORE), **PRE_MONOREPO},
    # 只開「循環只取 hub」
    "hubs-only": {"structure": {**BEFORE, "runtime_cycle_core": "hubs"}, **PRE_MONOREPO},
    # 只開「catalog barrel 不往下傳」
    "catalog-only": {"structure": {**BEFORE, "barrel_passthrough": "catalog"}, **PRE_MONOREPO},
    # 實驗：所有 barrel 都不往下傳（沒有採用，留著對照）
    "all-barrels": {"structure": {"runtime_cycle_core": "hubs", "barrel_passthrough": "all"}},
    # 2026.11-3 的預設規則（keyword 比對完整路徑、migration 不分組）
    "2026.11-3": dict(PRE_MONOREPO),
    # 目前的預設規則（2026.11-4：hubs + catalog；business 為預設類別；keyword 只比對套件根目錄以下；Django migration 分組）
    "current": {},
}
GATE_VARIANT = "current"
