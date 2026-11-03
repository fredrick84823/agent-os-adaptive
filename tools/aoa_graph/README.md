# aoa-graph

用 tree-sitter 為 **TypeScript / JavaScript 與 Python** repo 產生確定性的檔案級依賴圖與指標。
`instructions/analyze-node-classes.md` 第一步就是跑這支工具；模型只解讀輸出，不再自己估度數。

```bash
uv sync                                   # 在本 repo 根目錄；依 uv.lock 建立 .venv（安裝 uv：https://docs.astral.sh/uv/getting-started/installation/）
uv run python tools/aoa_graph <repo> [--out DIR] [options]
uv run aoa-graph <repo> [options]         # 同上，pyproject.toml 的 [project.scripts] 入口
uv run --project ~/agent-os-adaptive aoa-graph .   # 從別的專案根目錄執行
uv run pytest                             # 測試
```

預設輸出到 `<repo>/agent-os-adaptive/architecture-analysis/`。`uv run aoa-graph --help` 列出所有選項。

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
