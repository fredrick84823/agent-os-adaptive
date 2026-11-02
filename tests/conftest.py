import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from aoa_graph.cli import build, dump, parse_args

FIXTURES = Path(__file__).parent / "fixtures"
# HEAD 時間：2026-01-01T00:00:00Z
HEAD_TIME = 1767225600
DAY = 86400


def git(repo: Path, *args: str, when: int = HEAD_TIME) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
        "GIT_AUTHOR_DATE": f"@{when} +0000", "GIT_COMMITTER_DATE": f"@{when} +0000",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
    }
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


def make_repo(name: str, dest: Path, history=()) -> Path:
    """把 fixture 複製到 dest 並建立 git repo。

    history：[(相對 HEAD 的秒數（負值）, commit subject, [要追加一行的檔案])]，依序 commit；
    最後一個 commit 一律在 HEAD_TIME。
    """
    repo = dest / name
    shutil.copytree(FIXTURES / name, repo)
    git(repo, "init", "-q", "-b", "main")
    first = history[0][0] if history else 0
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: initial import", when=HEAD_TIME + first - DAY)
    for offset, subject, files in history:
        for f in files:
            with open(repo / f, "a", encoding="utf-8") as fh:
                fh.write("\n# touch\n" if f.endswith(".py") else "\n// touch\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", subject, when=HEAD_TIME + offset)
    if not history or history[-1][0] != 0:
        git(repo, "commit", "-q", "--allow-empty", "-m", "chore: head", when=HEAD_TIME)
    return repo


def analyze(repo: Path, *extra: str) -> dict:
    return build(repo, parse_args([str(repo), *extra]))


def edge_set(result: dict) -> set[tuple[str, str]]:
    return {(e["source"], e["target"]) for e in result["graph"]["edges"]}


@pytest.fixture
def ts_result(tmp_path):
    return analyze(make_repo("ts_repo", tmp_path))


@pytest.fixture
def py_result(tmp_path):
    return analyze(make_repo("py_repo", tmp_path))


__all__ = ["make_repo", "analyze", "edge_set", "dump", "json", "HEAD_TIME", "DAY"]
