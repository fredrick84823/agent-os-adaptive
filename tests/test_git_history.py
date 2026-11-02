from conftest import DAY, analyze, make_repo


def test_churn_bugfix_cochange(tmp_path):
    repo = make_repo("py_repo", tmp_path, history=[
        (-400 * DAY, "fix: ancient bug", ["src/app/utils.py"]),          # 視窗外
        (-30 * DAY, "fix: core crash", ["src/app/core.py", "src/app/models.py"]),
        (-20 * DAY, "feat: add field", ["src/app/core.py", "src/app/models.py"]),
        (-10 * DAY, "Hotfix db pool", ["src/app/db.py", "src/app/core.py"]),
        (0, "docs: clarify prefixes", ["src/app/utils.py"]),
    ])
    m = analyze(repo, "--since-days", "180")["metrics"]
    core = m["nodes"]["src/app/core.py"]
    assert (core["churn"], core["bugfix_count"]) == (3, 2)
    assert core["churn_lines"] == 6  # 每次追加 2 行
    assert core["co_change"] == [{"node": "src/app/models.py", "count": 2, "ratio": 0.6667}]
    utils = m["nodes"]["src/app/utils.py"]
    assert (utils["churn"], utils["bugfix_count"]) == (1, 0)
    db = m["nodes"]["src/app/db.py"]
    assert (db["churn"], db["bugfix_count"], db["co_change"]) == (1, 1, [])
    p = m["params"]
    assert p["window_end"] == "2026-01-01T00:00:00Z"
    assert p["window_start"] == "2025-07-05T00:00:00Z"
    # 初始 import 也在 400 天前之前 → 視窗內 4 個 commit
    assert p["commits_in_window"] == 4


def test_custom_bugfix_pattern(tmp_path):
    repo = make_repo("py_repo", tmp_path, history=[
        (-5 * DAY, "fix: core crash", ["src/app/core.py"]),
        (0, "PATCH-123 core", ["src/app/core.py"]),
    ])
    m = analyze(repo, "--bugfix-pattern", r"^PATCH-\d+")["metrics"]
    assert m["nodes"]["src/app/core.py"]["bugfix_count"] == 1
