"""讀 repos.toml、準備 repo 快取、在暫存 worktree 檢出指定 commit。"""
from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - 3.10 only
    import tomli as tomllib

EVAL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_REPOS = EVAL_DIR / "repos.toml"
DEFAULT_LABELS = EVAL_DIR / "ground_truth"


class EvalError(RuntimeError):
    pass


@dataclass(frozen=True)
class RepoSpec:
    name: str
    url: str
    commit: str
    language: str
    stability_commits: int
    replay_days: int


def load_repos(path: Path = DEFAULT_REPOS) -> list[RepoSpec]:
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    d = doc.get("defaults", {})
    out = []
    for r in doc.get("repo", []):
        for k in ("name", "url", "commit"):
            if not isinstance(r.get(k), str) or not r[k]:
                raise EvalError(f"{path.name}: repo 缺少 {k}")
        if len(r["commit"]) != 40:
            raise EvalError(f"{path.name}: {r['name']} 的 commit 必須是完整 40 字元 SHA")
        out.append(RepoSpec(
            name=r["name"], url=r["url"], commit=r["commit"], language=r.get("language", ""),
            stability_commits=int(r.get("stability_commits", d.get("stability_commits", 4))),
            replay_days=int(r.get("replay_days", d.get("replay_days", 365))),
        ))
    names = [r.name for r in out]
    if len(set(names)) != len(names):
        raise EvalError(f"{path.name}: repo name 重複")
    return out


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "-c", "core.quotepath=off", *args],
            check=True, capture_output=True,
        ).stdout.decode("utf-8", "replace")
    except subprocess.CalledProcessError as e:
        raise EvalError(f"git {' '.join(args)} 失敗（{repo}）：{e.stderr.decode('utf-8', 'replace').strip()}") from e


def default_cache_dir() -> Path:
    env = os.environ.get("AOA_EVAL_CACHE")
    if env:
        return Path(env)
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "aoa-eval" / "repos"


def ensure_repo(spec: RepoSpec, cache: Path, fetch: bool = True) -> Path:
    """<cache>/<name> 是完整 clone（不能 shallow：歷史指標與回放要讀 git log）。commit 不在就 fetch。"""
    path = cache / spec.name
    if not (path / ".git").exists() and not (path / "HEAD").exists():
        if not fetch:
            raise EvalError(f"{path} 不存在，且指定了 --no-fetch")
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", spec.url, str(path)], check=True)
    if git(path, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise EvalError(f"{path} 是 shallow clone，歷史指標會不完整；請用完整 clone")
    try:
        git(path, "cat-file", "-e", f"{spec.commit}^{{commit}}")
    except EvalError:
        if not fetch:
            raise
        git(path, "fetch", "--quiet", "origin")
        git(path, "cat-file", "-e", f"{spec.commit}^{{commit}}")
    return path


@contextlib.contextmanager
def worktree(repo: Path, commit: str):
    """把 commit 檢出到暫存目錄（detached worktree），離開時移除。"""
    tmp = Path(tempfile.mkdtemp(prefix="aoa-eval-"))
    wt = tmp / repo.name
    git(repo, "worktree", "add", "--quiet", "--detach", str(wt), commit)
    try:
        yield wt
    finally:
        with contextlib.suppress(EvalError):
            git(repo, "worktree", "remove", "--force", str(wt))
        shutil.rmtree(tmp, ignore_errors=True)
        with contextlib.suppress(EvalError):
            git(repo, "worktree", "prune")


def first_parent_chain(repo: Path, commit: str, n: int) -> list[str]:
    """[commit, parent, grandparent, …]，共 n+1 個（歷史不足就少於）。"""
    out = git(repo, "rev-list", "--first-parent", f"--max-count={n + 1}", commit).split()
    return out


def commit_time(repo: Path, commit: str) -> int:
    return int(git(repo, "show", "-s", "--format=%ct", commit).strip())


def commit_before(repo: Path, commit: str, ts: int) -> str | None:
    out = git(repo, "rev-list", "--first-parent", "--max-count=1", f"--before={ts}", commit).strip()
    return out or None
