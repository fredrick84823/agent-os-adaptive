# aoa-eval：分類準確度驗證

`aoa-classify` 把每個檔案分成 core／business／leaf。`aoa-eval` 拿幾個釘住 commit 的開源 repo，和人工（目前是 agent）標註比對，回答三個問題：

1. **準不準**：Cohen's kappa、線性加權 kappa、per-class precision／recall、confusion matrix、非對稱成本。
2. **穩不穩**：同一 commit 跑兩次輸出要位元相同；相鄰 commit 之間，沒被改到的檔案不該換類別。
3. **有沒有預測力**（選用）：在一年前的 commit 分類，之後的 bug-fix commit 改到的檔案是不是偏向 core。

> ⚠️ **標註是 agent（Grok Bot）的初始標註，尚未經人工複核。** 只有一位標註者、沒有 inter-rater 一致度；在有人複核之前，這些數字只能拿來比較規則變體的相對好壞，不能當成「分類器有多準」的結論，也不該拿來調權重。

最新結果：[`results/report.md`](results/report.md)（`report.json` 是完整資料，含每個錯判檔案的規則、百分位、blast radius 與標註理由）。

## 跑法

```bash
uv sync
uv run aoa-eval run                       # 第一次會把 repos.toml 的 repo 完整 clone 到 ~/.cache/aoa-eval/repos（django 約 300 MB）
uv run aoa-eval run --replay              # 加跑歷史回放
uv run aoa-eval run --repos flask,zod --variants current --no-stability
uv run aoa-eval run --cache-dir /path/to/clones --no-fetch   # 用現成的完整 clone、不連網
```

- 輸出：`--out`（預設 `eval/results`）底下的 `report.json`、`report.md`；不含時間戳與絕對路徑，同樣輸入位元相同。
- exit code：`0` 通過；`1` gate 失敗——gate 變體（`current`）有任何 **core → leaf**、同一 commit 兩次輸出不同、或指定了 `--min-kappa` 而 kappa 不到；`2` 設定或環境錯誤（repo 不存在、標註路徑不在圖上…）。
- 分析在暫存 git worktree 裡跑，不會改快取 clone 的工作目錄；分類不讀被測 repo 的 `.aoa.toml`（評估的是預設規則本身）。

## 檔案

| 路徑 | 內容 |
|---|---|
| `repos.toml` | 受測 repo：名稱、URL、完整 40 字元 commit SHA、穩定性／回放參數 |
| `ground_truth/<repo>.jsonl` | 一行一個標註：`{"path", "label", "rationale"}`；`#` 開頭是註解 |
| `aoa_eval/variants.py` | 並排比較的規則變體（格式同 `.aoa.toml` 的 `[classify]`） |
| `aoa_eval/scoring.py` | kappa、per-class、成本矩陣 |
| `results/` | 進版控的基準報告，改規則的 PR 要一起更新 |

## 標註定義

問題是：**AI 改這個檔案時要多小心？**（不是「這個檔案多重要」）

| 類別 | 定義 | 例子 |
|---|---|---|
| core | 改錯會讓大多數使用者或大部分功能壞掉、或碰到安全／資料完整性；需要人工審查與完整測試 | flask `app.py`、`sessions.py`；httpx `_transports/default.py`；zod `v4/core/core.ts`；django `db/models/base.py` |
| business | 一般功能程式碼：改錯會壞一個功能，但影響範圍有限、有測試可以抓 | flask `cli.py`；zod `locales/en.ts`（預設錯誤訊息）；django `contrib/admin/filters.py` |
| leaf | 改錯幾乎不影響使用者：測試、範例、腳本、benchmark、單一翻譯檔、沒有人依賴的工具 | zod 非英文 `locales/*.ts`；django `contrib/sitemaps/views.py`；各 repo 的 tests |

每筆標註都寫了 `rationale`。標註時**先不看分類器的預測**，只看檔案的角色（讀程式與 import 它的地方）。

## 抽樣方式

| repo | commit | 標註數 | 方法 |
|---|---|---|---|
| flask | `49943b5a` | 34 | 24 個 ranked 檔案全標 + 10 個測試／範例 |
| httpx | `b5addb64` | 31 | 23 個 ranked 全標 + 8 個測試 |
| zod | `2554b70c` | 63 | `aoa-eval sample zod --per-class 15 --non-ranked 6` 的 51 個 + 12 個刻意挑的關鍵模組 |
| django | `308b6d6a` | 75 | `aoa-eval sample` 的 53 個 + 22 個刻意挑的（含 181 檔 runtime 循環的成員） |

`aoa-eval sample` 依**預測類別**分層、以 `sha256(seed:path)` 排序取前 N 個，只印路徑不印預測。抽樣時用的是 rules 2026.11-1。

## 指標

- **kappa**：扣掉「碰巧一致」後的一致度（1 完全一致、0 等於亂猜）。另報只算 ranked 檔案（排除測試與範例）的 kappa，因為測試檔幾乎都判對，會把整體數字墊高。
- **線性加權 kappa**：類別有序，差一級（core↔business）的錯比差兩級（core↔leaf）輕。
- **成本矩陣**（`scoring.COST[標註][預測]`）：低估風險比高估貴。

  | 標註 \ 預測 | core | business | leaf |
  |---|---|---|---|
  | core | 0 | 4 | **10（gate：必須為 0 個）** |
  | business | 1 | 0 | 2 |
  | leaf | 1.5 | 0.5 | 0 |

  理由：判 leaf 的檔案 AI 會比較放手改，core 被當 leaf 是唯一會直接出事的錯；高估只是多花審查時間。數字是主觀設定，只用來排序錯誤嚴重度與比較變體。
- **穩定性**：pinned commit 往前 4 個 first-parent commit，每對相鄰 commit 算「類別變了的檔案比例」，並分開算**沒被該 commit 改到的檔案**（理想上是 0；百分位是相對值，別的檔案變了也可能把它擠過門檻）。
- **歷史回放**（`--replay`）：在 pinned commit 前 365 天的 commit 分類，數之後的 bug-fix commit（subject 符合 aoa-graph 的 bug-fix pattern）改到哪些 ranked 檔案；`lift` = 該類別被改到的比例 ÷ 全體被改到的比例。core lift > 1 表示 core 確實比較常出 bug。

## Phase 3 的發現與修正（rules 2026.11-1 → 2026.11-2）

| repo | 變體 | kappa | 加權 κ | core→leaf | 低估／高估 | 平均成本 | core／business／leaf（全部檔案） | high_risk |
|---|---|---|---|---|---|---|---|---|
| flask | before | 0.379 | 0.522 | 0 | 5／9 | 0.765 | 12／10／61 | 11 |
| flask | current | 0.469 | 0.574 | 0 | 5／7 | 0.706 | 10／12／61 | 7 |
| httpx | before = current | 0.571 | 0.667 | 0 | 2／7 | 0.403 | 9／14／37 | 2 |
| zod | before | 0.405 | 0.455 | 0 | 4／21 | 0.532 | 26／105／391 | 2 |
| zod | current | 0.387 | 0.483 | 0 | 2／24 | 0.413 | 32／99／391 | 2 |
| django | before | 0.459 | 0.556 | 0 | 5／23 | 0.493 | 374／205／2405 | 244 |
| django | current | 0.486 | 0.577 | 0 | 7／19 | 0.533 | 277／302／2405 | 56 |

1. **大型 runtime 循環讓 core 膨脹**（django、flask）。django 有一個 181 檔的循環，2026.11-1 把每個成員都判 core。改成只有 **hub**（循環內被 ≥ max(2, ⌈10% × 大小⌉) 個成員 import）才是 core，其他成員照分數分類。django core 374 → 277、high_risk 244 → 56；flask `testing.py`、`sansio/blueprints.py` 回到 business（`debughelpers.py`、`templating.py` 仍是 hub、仍判 core）。代價：django `core/cache/backends/base.py`、`db/backends/utils.py`（標 core）掉成 business，低估 5 → 7。
2. **barrel re-export 灌大 blast radius**（zod）。`v4/locales/index.ts` re-export 63 個 locale，每個 locale 繼承 `v4/core` 的 134 個 dependents，被排到 p90 以上變 core。新規則：條目彼此獨立的 **catalog barrel** 不把 dependents 往下傳。locale 的 blast radius 降到 0–2，樣本裡被判 core 的 locale 從 5 個剩 2 個，加權 κ 與平均成本變好，但未加權 kappa 0.405 → 0.387：locale 仍因 churn／bugfix 落在 business（不是 leaf），而 locale 讓出的百分位被其他檔案補上（core 26 → 32）。`"all"`（所有 barrel 都切）在報告裡當對照：會切掉 `v4/core/index.ts` 這類真的依賴，不採用。

## 已知限制

- 標註未經人工複核、只有一位標註者；`rationale` 是判斷依據，歡迎直接改 JSONL 並在 PR 說明。
- 依預測類別分層抽樣 + 刻意挑選的檔案 → 樣本分布不等於 repo 分布，kappa 不能外推成整個 repo 的準確度。
- 抽樣用的是舊規則的預測；新規則下的分層可能不同。
- 只有 4 個 repo、3 個 Python + 1 個 TS；沒有 Go／Rust／monorepo 應用程式。
- 百分位是 repo 內相對值：修正一群檔案的分數，會把別的檔案擠過門檻（見 zod）。
- churn／bugfix 會被大量檔案一起改的 commit 灌水（翻譯、格式化）。
- django `django/test/client.py` 這類「給使用者用的測試工具」被 `test_paths` 當測試檔，一律 leaf；標註是 business。
- Python `__init__.py` 的 re-export 沒有 barrel 處理；barrel 規則只看 TS/JS。
