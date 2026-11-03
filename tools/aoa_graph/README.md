# aoa-graph

用 tree-sitter 為 **TypeScript / JavaScript 與 Python** repo 產生確定性的檔案級依賴圖與指標。
`instructions/analyze-node-classes.md` 第一步就是跑這支工具；模型只解讀輸出，不再自己估度數。

```bash
uv sync                                   # 在本 repo 根目錄；依 uv.lock 建立 .venv（安裝 uv：https://docs.astral.sh/uv/getting-started/installation/）
uv run python tools/aoa_graph <repo> [--out DIR] [options]
uv run aoa-graph <repo> [options]         # 同上，pyproject.toml 的 [project.scripts] 入口
uv run --project ~/agent-os-adaptive aoa-graph .   # 從別的專案根目錄執行
uv run aoa-classify <repo>                # 讀上面的輸出，寫 nodes.json（同 `aoa-graph classify <repo>`）
uv run pytest                             # 測試
```

預設輸出到 `<repo>/agent-os-adaptive/architecture-analysis/`。`uv run aoa-graph --help`、`uv run aoa-classify --help` 列出所有選項。分類器見下方 [aoa-classify](#aoa-classify)。

## 決定性

同一個 commit 重跑，三個 JSON 位元完全相同：

- 檔案清單來自 `git ls-files`（只看追蹤中的檔案）；非 git 目錄才退回檔案系統列舉。
- 所有清單排序固定，JSON 以 `sort_keys` 輸出；不含時間戳、主機名稱、絕對路徑。
- churn／bug-fix 的時間視窗以 **HEAD commit 的 committer 時間**往回算，不是「現在」。
- tree-sitter 與 grammar 版本在 `pyproject.toml` 固定，並由 `uv.lock` 鎖定完整相依樹。

工作目錄有未 commit 的修改時，`source.dirty` 會是 `true`，此時輸出只代表當下的工作目錄。

## 節點與邊

- **節點**＝一個原始碼檔（`.ts .tsx .mts .cts .js .jsx .mjs .cjs .py`）。不混用函式／類別粒度。
- **邊**＝`importer → imported`，只連 repo 內的檔案。`kinds` 記錄這條邊來自哪種 import：

| kind | TS / JS | Python |
|---|---|---|
| `static` | `import … from`、`import "x"` | `import x`、`from x import y` |
| `type` | `import type`、`export type … from` | `if TYPE_CHECKING:` 區塊內的 import |
| `reexport` | `export * from`、`export { a } from` | — |
| `require` | `require("x")`、`import x = require("x")` | — |
| `dynamic` | `import("x")`（字面字串） | `importlib.import_module("x")`、`__import__("x")`（字面字串） |

參數不是字面字串的動態 import（`import(name)`、`import_module(f"…")`）不會變成邊，而是列進 `unresolved.json`。

### TS / JS 解析順序

1. 相對路徑：原樣 → `./x.js` 對應 `x.ts`／`x.tsx`（TS ESM 慣例）→ 補副檔名 → `index.*`。
2. 最近的 `tsconfig.json`／`jsconfig.json` 的 `paths`（支援 `*`、最長前綴優先、相對路徑的 `extends`）→ `baseUrl`。
3. package.json `imports`（`#internal/*` subpath imports，取最近的 package.json）。
4. monorepo workspace 套件：bare specifier 對到 repo 內某個 package.json 的 `name`，入口依 `source`／`types`／`exports`／`module`／`main`；指向未追蹤的 `dist/`、`distribution/`、`lib/` 時改試 `src/`、`source/`。
5. 都不是 → `external`（套件名：`react`、`@scope/name`、`node:fs`）。
6. 樣式、圖片、JSON 等資源（`.css`、`.svg`、`.json`…）不算邊也不算 unresolved。

### Python 解析

- 模組名稱：從檔案往上找最上層「含 `__init__.py` 的目錄」，其父目錄就是 root（`src/pkg/a.py` → `pkg.a`；中間沒有 `__init__.py` 的 namespace 子目錄會被跨過）。repo 根目錄、`src/` 與 `--py-root` 另以完整路徑再登記一次。
- `import a.b.c` 連到最長的存在前綴；`from pkg import name` 若 `pkg.name` 是模組就連到它，否則連到 `pkg` 本身。
- 相對 import 依 importer 所在 package 解析（包含檔名不是合法識別字的 Django migration）。
- 沒有 `__init__.py` 的腳本目錄（`scripts/`、`tests/`）只對同目錄的檔案可見，避免 `import utils` 誤連到不相干的同名檔。
- 不加隱含的「父 package `__init__.py`」邊（`import a.b` 雖然會執行 `a/__init__.py`，但不算一條邊）。

### 忽略的目錄

`node_modules`、`.venv`／`venv`／任何含 `pyvenv.cfg` 的目錄（僅非 git 模式）、`site-packages`、`__pycache__`、`dist`、`build`、`.next`、`coverage`、`vendor` 等（完整清單見 `discover.py` 的 `IGNORE_DIRS`）。超過 1 MB 的檔案與 `*.min.js` 略過。`--exclude GLOB` 可再排除。

## 輸出格式

### graph.json

```json
{
  "schema_version": 1,
  "generator": {"name": "aoa-graph", "version": "0.1.0"},
  "source": {"commit": "<sha>", "dirty": false},
  "granularity": "file",
  "nodes": [{"id": "src/app/core.py", "language": "python", "module": "app.core", "is_test": false, "loc": 120}],
  "edges": [{"source": "src/app/core.py", "target": "src/app/db.py", "kinds": ["static"], "count": 1}],
  "external": [{"source": "src/app/db.py", "package": "sqlalchemy", "kinds": ["static"]}]
}
```

### metrics.json

三個檔案都帶 `schema_version`、`generator`、`source`。`metrics.json` 的 `nodes` 以檔案路徑為 key：

| 欄位 | 定義 |
|---|---|
| `fan_in` / `fan_out` | 直接依賴它／它直接依賴的 repo 內檔案數（不含自己） |
| `test_fan_in` | `fan_in` 中有幾個是測試檔（`is_test` 規則見 `discover.py`） |
| `blast_radius` | 反向圖上能走到它的檔案數＝改它可能波及的檔案數（含測試；同一個循環內的成員互相計入） |
| `in_cycle` / `scc_id` | 是否位在大小 > 1 的強連通分量（Tarjan）；`scc_id` 對應頂層 `cycles[].id` |
| `in_runtime_cycle` / `runtime_scc_id` | 同上，但忽略只有 `type` 的邊（TS `import type`、Python `TYPE_CHECKING`）；對應 `runtime_cycles[]` |
| `churn` / `churn_lines` | 視窗內觸及此檔的 commit 數／增刪行數（不含 merge commit） |
| `bugfix_count` | 視窗內 subject 符合 `--bugfix-pattern` 的 commit 數 |
| `co_change` | 最常一起被改的檔案（至少 2 次），`ratio`＝共同次數 ÷ 本檔 churn；超過 `--max-commit-files` 個檔案的 commit 不計 |

沒有 git 或用了 `--no-history` 時，歷史欄位為 `null`。頂層 `params` 記錄視窗起訖、regex 與門檻，`summary` 是總數。

### unresolved.json

```json
{
  "items": [{"source": "src/x.ts", "line": 12, "kind": "dynamic", "specifier": null,
             "expression": "import(`./plugins/${name}`)", "reason": "dynamic_expression"}],
  "parse_errors": ["src/uses-new-syntax.ts"],
  "skipped_large_files": []
}
```

`reason`：`dynamic_expression`、`not_found`、`outside_repo`、`absolute_path`、`tsconfig_paths_target_not_found`、`package_imports_no_match`、`package_imports_target_not_found`、`package_imports_field_missing`、`workspace_package_entry_not_found`、`relative_beyond_top_level`、`importer_not_a_module`。

`parse_errors` 是 tree-sitter 回報語法錯誤的檔案。錯誤通常只影響局部（例如 grammar 尚未支援 TS 4.7 的 `in`/`out` variance 標註），import 仍會被擷取，但這些檔案的邊值得抽查。

## 已知限制

- 靜態分析看不到：DI 容器、外掛註冊、設定檔驅動的路由、`sys.path` 操作、字串拼接的動態 import。這些交給模型依 `unresolved.json` 判讀。
- package.json `exports` 的 subpath pattern（`"./v4/*"`）只做 best-effort；tsconfig `extends` 只追相對路徑，不追 npm 套件（`@tsconfig/node20`）。
- 檔案改名前的歷史不會接到新檔名上（`git log --no-renames`）。
- shallow clone 的歷史不完整，`params.shallow` 會是 `true`。

---

# aoa-classify

讀 `graph.json`／`metrics.json`（`unresolved.json` 可選），用**確定性規則**把每個檔案分成 core／business／leaf，寫出 `nodes.json`。模型不做分類，只解釋，並可在 `overrides.jsonl` 提出覆寫。

```bash
uv run aoa-classify <repo>                          # 讀 <repo>/agent-os-adaptive/architecture-analysis/*.json
uv run aoa-classify <repo> --coverage coverage.json # 指定覆蓋率檔
uv run --project ~/agent-os-adaptive aoa-classify . # 從別的專案根目錄執行
```

| 選項 | 預設 |
|---|---|
| `--in DIR` | `<repo>/agent-os-adaptive/architecture-analysis` |
| `--out DIR` | 同 `--in` |
| `--config FILE`／`--no-config` | `<repo>/.aoa.toml`（不存在就只用預設規則） |
| `--coverage FILE`／`--no-coverage` | 設定檔的 `coverage`，否則依序找 `coverage.json`、`coverage/lcov.info`、`lcov.info` |
| `--overrides FILE` | `<in>/overrides.jsonl` |

## 分類流程

```
所有檔案
 ├─ 測試檔（graph is_test 或 test_paths）→ leaf［test_file］，不參與排名
 ├─ 範例／文件站／benchmark（example_paths）→ leaf［example_code］，不參與排名
 └─ 其餘（ranked）
     1. 硬規則，命中任一 → core
        config_core_path   .aoa.toml 的 core_paths（CODEOWNERS 式 glob；也適用測試檔）
        sensitive:<id>     路徑 token／glob／import 的套件／套件入口（not_sensitive 可豁免）
        runtime_cycle      位於 runtime 循環（SCC > 1，不含只有 type 的邊）→ 另標 high_risk
     2. 風險分數 → midrank 百分位 p（只在 ranked 檔案之間比）
        p ≥ 90                         → core［score_top］
        85 ≤ p < 90                    → core［score_boundary］（邊界往嚴格靠）
        p < 35 且 prod_blast_radius ≤ 2 → leaf［score_low］
        p < 35 但 prod_blast_radius > 2 → business［leaf_blast_guard］
        35 ≤ p < 40                    → business［leaf_boundary］（邊界往嚴格靠）
        其餘                           → business［score_mid］
     3. 判成 leaf 但 tree-sitter 有 parse error → business［parse_error_uncertain］
 最後套用 overrides.jsonl
```

數字（90、85、35、40、2）都來自 `default_rules.toml` 的 `[thresholds]`，可在 `.aoa.toml` 改。

### 風險分數

```
risk = impact × cost_of_failure ÷ detectability

impact          = log2(2 + prod_blast_radius) × (1 + 0.25·log2(1 + churn))
cost_of_failure = 1 + 0.5·log2(1 + bugfix_count)
detectability   = 1 + 0.5·log2(1 + test_fan_in) + 0.25·log2(1 + test_reach) + 1.0·coverage
```

| 因子 | 來源 | 為什麼這樣算 |
|---|---|---|
| `prod_blast_radius` | 從 `graph.json` 重算：反向可達的 ranked 檔案數 | **排除測試檔與範例**。測試 import 一個模組不會讓它壞掉時傷到更多使用者，反而代表比較容易被抓到；算進 impact 等於「測試越多越危險」。`metrics.json` 的 `blast_radius` 含測試，所以這裡另算 |
| `churn`、`bugfix_count` | `metrics.json` | 常改、常修的檔案往上加權；沒有 git 歷史時視為 0 |
| `test_fan_in` | `metrics.json` | 直接 import 它的測試檔數（單元測試的代理） |
| `test_reach` | 從 `graph.json` 重算 | 直接或遞移 import 它的測試檔數。很多測試只 import 套件入口（flask 測試 import `flask`），只看 `test_fan_in` 會低估 |
| `coverage` | 覆蓋率檔（可選） | 行覆蓋率 0–1；沒有覆蓋率檔就是 0，也就是**可偵測性取保守的低值** |

`fan_in` 沒有另外進 impact：`blast_radius` 已經包含所有直接依賴者，再加會重複計算。leaf 另外要求 `prod_blast_radius ≤ 2`：用遞移而不是直接依賴者，是因為循環或入口檔會讓「只被 1 個檔 import」的檔案實際上被整個套件依賴（flask 的 `logging.py` 只被 `app.py` import，但 `app.py` 在循環裡，改壞它會波及 21 個檔）。`prod_fan_in` 只記錄在 `factors` 供解讀。權重是起始值，Phase 3 用標註資料校準。

### 敏感類別（預設）

| id | 例 |
|---|---|
| `auth` | `auth`、`login`、`session`、`oauth`、`jwt`、`password`、`permission`、`csrf`…；套件 `jwt`、`passlib`、`jsonwebtoken`、`passport`… |
| `crypto` | `crypto`、`encrypt`、`hmac`、`signing`、`tls`…；套件 `cryptography`、`itsdangerous`、`ssl`、`hmac`、`node:crypto`… |
| `secrets` | `secret`、`vault`、`keyring`、`dotenv`；套件 `secrets`、`hvac`、`dotenv`… |
| `payments` | `payment`、`billing`、`invoice`、`checkout`、`refund`、`stripe`…；套件 `stripe`、`braintree`… |
| `pii` | `pii`、`gdpr`、`hipaa`、`compliance`、`consent`、`privacy`、`kyc`… |
| `irreversible` | `purge`、`wipe`、`erase`、`shred`、`hard-delete` |
| `db_schema` | `migration`、`alembic`、`prisma`；glob `**/migrations/**`、`**/models.py`、`**/db/schema*`；套件 `alembic`、`@prisma/client`、`knex` |
| `public_api` | `api`、`openapi`、`graphql`、`grpc`、`endpoint`、`webhook`；glob `**/routes/**`；**套件入口**：頂層 Python package 的 `__init__.py`，以及 repo 根目錄、`src/`、含 `package.json` 的目錄（或其 `src/`）下的 `index.*` |

完整清單在 [`default_rules.toml`](default_rules.toml)。比對方式：

- **keyword** 跟路徑 token 完全比對：路徑以 `/ _ - .` 與 camelCase 切開、轉小寫（`src/AuthProvider/user_sessions.py` → `src auth provider user sessions py`）。token 加 `s`／`es` 的複數、或結尾帶數字（`auth2`）也算命中，但 `author` 不會命中 `auth`、`rapid` 不會命中 `api`。
- **paths** 是 CODEOWNERS／gitignore 式 glob：`*` 不跨 `/`、`**` 跨任意層；含 `/` 就從 repo 根目錄錨定，不含 `/` 則任何深度都可命中；命中目錄就涵蓋底下所有檔案。
- **packages** 跟 `graph.json` 的 `external[].package` 完全比對（Python 頂層模組名、npm 套件名）。

## 設定檔 `.aoa.toml`

放在被分析 repo 的根目錄，寫在 `[classify]` 底下，欄位與 `default_rules.toml` 相同。拼錯的欄位會直接報錯（exit 2），不會被默默忽略。

```toml
[classify]
version = "acme-2026.11"            # 記錄在 nodes.json 的 rules_version.repo
core_paths = ["src/billing/**", "src/ledger.ts"]   # 命中就是 core
not_sensitive = ["src/components/AuthorCard.tsx"]   # 敏感規則誤判豁免（不豁免循環與 core_paths）
disable = ["pii"]                   # 停用預設敏感類別
example_paths = ["**/examples/**"]  # 取代預設清單
coverage = "coverage/lcov.info"

[classify.thresholds]
core_top_percent = 15

[[classify.sensitive]]               # 同 id：keywords／paths／packages 併入預設（加 replace = true 則整筆取代）
id = "auth"
keywords = ["badge"]

[[classify.sensitive]]               # 新 id：附加一個類別
id = "export"
description = "對外資料匯出"
paths = ["src/export/**"]
```

清單欄位（`core_paths`、`not_sensitive`、`disable`、`example_paths`、`test_paths`）與 `coverage` 整個取代預設值；`thresholds`、`weights` 逐欄覆蓋。設定檔是人寫、進版控、會被 review 的，所以 `not_sensitive` 這種放寬可以寫在這裡；模型的放寬只能走 overrides 並等人工核准。

## 覆寫 `overrides.jsonl`

一行一筆 JSON，`#` 開頭與空行忽略。缺 `node`／`to`／`reason` 或 JSON 壞掉會報錯（exit 2）。

```json
{"node": "src/plugins/loader.ts", "to": "core", "by": "model", "reason": "dynamic import 載入所有外掛", "evidence": "src/plugins/loader.ts:12"}
{"node": "src/generated/icons.ts", "to": "leaf", "by": "model", "reason": "產生出來的檔案", "approved_by": "fredrick"}
```

| 方向（相對計算結果） | 生效條件 | `nodes.json` 裡 |
|---|---|---|
| 更嚴格（leaf → business → core） | 自動生效 | `overrides.applied`，kind `stricter` |
| 更寬鬆 | 有非空的 `approved_by`（人工）才生效；模型**不可**填 | 沒核准：`overrides.pending`；核准：`applied`，kind `looser_approved` |
| 相同、或節點不在圖裡 | 不生效 | `overrides.ignored` 附原因 |

## nodes.json

```json
{
  "rules_version": {"default": "2026.11-1", "repo": null},
  "summary": {"core": 12, "business": 8, "leaf": 63, "ranked": 24, "tests": 48, "examples": 11, "high_risk": 11, "...": "..."},
  "overrides": {"applied": [], "pending": [], "ignored": []},
  "inputs": {"config": null, "coverage": null, "overrides": null, "unresolved_json": true},
  "nodes": {
    "src/flask/sessions.py": {
      "class": "core", "computed_class": "core", "risk_level": "MEDIUM", "high_risk": false,
      "rules": ["sensitive:auth", "sensitive:crypto"],
      "reasons": ["sensitive:auth: path token 'sessions' matches keyword 'session' (認證、授權、session、權限)", "..."],
      "risk_score": 1.805456, "percentile": 39.58, "population": "ranked",
      "factors": {"impact": 5.6545, "cost_of_failure": 1.0, "detectability": 3.1319, "prod_blast_radius": 21, "prod_fan_in": 4,
                  "test_fan_in": 2, "test_reach": 40, "churn": 1, "bugfix_count": 0, "coverage": null},
      "overrides": []
    }
  }
}
```

（上例節錄自 pallets/flask @ `49943b5a` 的實際輸出，`reasons` 省略後兩筆。）

- `class` 是最終結果（含覆寫），`computed_class` 是規則算出來的；`rules` 是決定或影響類別的規則 id，`reasons` 是人讀得懂的理由（含分數拆解）。
- `risk_level`：`HIGH`＝high_risk 或（core 且 p ≥ 90）；`LOW`＝leaf；其餘 `MEDIUM`。
- `risk_score`／`percentile` 只有 ranked 檔案有值，測試與範例為 `null`。
- 決定性：同樣的輸入（三個 JSON、設定檔、覆蓋率檔、overrides）→ 位元相同；分數四捨五入到小數 6 位，不含時間戳與絕對路徑；`inputs` 記錄設定檔、覆蓋率檔、overrides 的相對路徑與 sha256。

## 已知限制

- 敏感類別只看路徑、import 的套件與套件入口，**不讀程式內容**：在 `utils.py` 裡處理密碼、或用 `fetch` 直接打金流 API 都抓不到 → 用 `core_paths` 或 overrides 補。
- `irreversible`（永久刪除）幾乎只能靠檔名，命中率最低。
- barrel 檔（`index.ts` 一次 re-export 全部）會讓被它 re-export 的檔案 blast radius 偏大，例如 zod 的 `locales/*.ts`。
- 百分位是 repo 內相對值：小 repo 的 ranked 檔案很少時，一兩個檔案就佔掉 10%。
- 耦合緊的套件（大循環、所有東西都被入口檔 import）幾乎沒有 ranked leaf：leaf 要求 `prod_blast_radius ≤ 2`，httpx @ `b5addb64` 的 23 個 ranked 檔案沒有一個是 leaf。這是刻意偏嚴；真的要放寬就調 `leaf_max_prod_blast_radius` 或寫需要核准的 override。
- 權重與門檻未經校準（Phase 3）。
