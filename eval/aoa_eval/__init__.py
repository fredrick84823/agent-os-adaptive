"""aoa-eval：用人工標註的 ground truth 驗證 aoa-classify 的分類準確度。

流程：pinned commit 的開源 repo → aoa-graph → aoa-classify → 與 ground_truth/*.jsonl 比對，
另做確定性（同 commit 跑兩次）、穩定性（相鄰 commit 的分類 churn）與歷史回放檢查。
"""

NAME = "aoa-eval"
VERSION = "0.1.0"
