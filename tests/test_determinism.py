"""同一個 commit 連跑 5 次，三個輸出檔位元完全相同；換一個 clone 路徑也相同。"""
import pytest
from aoa_graph.cli import main
from conftest import DAY, make_repo

HISTORY = [
    (-9 * DAY, "fix: a", ["src/a.ts", "src/b.ts"]),
    (-3 * DAY, "feat: b", ["src/a.ts", "src/b.ts", "src/c.ts"]),
    (0, "fix: c", ["src/lib/helpers.ts"]),
]


def _run(repo, out):
    assert main([str(repo), "--out", str(out)]) == 0
    return {n: (out / f"{n}.json").read_bytes() for n in ("graph", "metrics", "unresolved")}


@pytest.mark.parametrize("fixture,history", [("ts_repo", HISTORY), ("py_repo", ())])
def test_five_runs_identical(tmp_path, fixture, history):
    repo_a = make_repo(fixture, tmp_path / "clone_a", history)
    repo_b = make_repo(fixture, tmp_path / "clone_b", history)
    runs = [_run(repo_a, tmp_path / f"out{i}") for i in range(5)]
    runs.append(_run(repo_b, tmp_path / "out_b"))
    assert all(r == runs[0] for r in runs)
    assert str(tmp_path).encode() not in runs[0]["graph"] + runs[0]["metrics"] + runs[0]["unresolved"]


def test_default_out_dir_does_not_change_results(tmp_path):
    """輸出寫進 repo 內（未追蹤）後再跑一次，結果不變。"""
    repo = make_repo("ts_repo", tmp_path, HISTORY)
    out = repo / "agent-os-adaptive" / "architecture-analysis"
    assert main([str(repo)]) == 0
    first = (out / "metrics.json").read_bytes()
    assert main([str(repo)]) == 0
    assert (out / "metrics.json").read_bytes() == first
