"""aoa-graph：用 tree-sitter 為 TS/JS 與 Python repo 產生確定性的檔案級依賴圖與指標。

輸出（預設寫到 <repo>/agent-os-adaptive/architecture-analysis/）：
  graph.json       nodes + edges + external packages，固定排序
  metrics.json     每個節點的 fan_in / fan_out / blast_radius / SCC / churn / bugfix / co-change
  unresolved.json  動態或解析不到的 import，留給模型判讀

同一個 commit 重跑，三個檔案位元完全相同（不含時間戳、不含絕對路徑）。
"""

NAME = "aoa-graph"
VERSION = "0.1.0"
SCHEMA_VERSION = 1
