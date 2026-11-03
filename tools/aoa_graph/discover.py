"""列出要分析的原始碼檔，並判斷語言與是否為測試檔。"""
from __future__ import annotations

import fnmatch
import os
import subprocess
from pathlib import Path

# 任何一層目錄名稱命中就整個略過（vendored 依賴、虛擬環境、建置產物、快取）
IGNORE_DIRS = frozenset({
    "node_modules", "bower_components", "jspm_packages",
    ".git", ".hg", ".svn",
    "venv", ".venv", "virtualenv", "site-packages", "__pypackages__",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".nox",
    "dist", "build", ".next", ".nuxt", ".svelte-kit", ".turbo", ".cache",
    "coverage", ".nyc_output", ".eggs",
    "vendor",  # 慣例上放第三方程式碼（Django admin 的 static/.../vendor/、Go/PHP vendor）
})

LANG_BY_EXT = {
    ".ts": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".py": "python",
}

LANG_GROUPS = {"ts": {"typescript", "tsx", "javascript"}, "py": {"python"}}

MAX_FILE_BYTES = 1_000_000  # 超過視為產生檔／打包檔，略過


def language_of(path: str) -> str | None:
    if path.endswith(".min.js"):
        return None
    return LANG_BY_EXT.get(os.path.splitext(path)[1])


def is_test(path: str) -> bool:
    parts = path.split("/")
    name = parts[-1]
    if any(p in ("test", "tests", "__tests__", "spec", "__mocks__") for p in parts[:-1]):
        return True
    if name == "conftest.py" or name.startswith("test_") or name.endswith("_test.py"):
        return True
    stem = name.split(".")
    return len(stem) >= 3 and stem[-2] in ("test", "spec")


def _git_ls_files(root: Path) -> list[str] | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached"],
            check=True, capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]


def _walk(root: Path) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in IGNORE_DIRS and not (Path(dirpath, d, "pyvenv.cfg").exists())
        )
        rel = os.path.relpath(dirpath, root)
        for f in filenames:
            found.append(f if rel == "." else f"{rel}/{f}".replace(os.sep, "/"))
    return found


def list_repo_files(root: Path, use_git: bool = True, excludes: tuple[str, ...] = ()) -> list[str]:
    """回傳 repo 內所有（未被忽略的）檔案相對路徑，已排序。

    git repo 用 `git ls-files`（只看追蹤中的檔案，與 commit 綁定、天然排除 .gitignore）；
    否則退回 os.walk。
    """
    files = _git_ls_files(root) if use_git else None
    if files is None:
        files = _walk(root)
    keep = []
    for p in files:
        parts = p.split("/")
        if any(seg in IGNORE_DIRS for seg in parts[:-1]):
            continue
        if any(fnmatch.fnmatch(p, g) for g in excludes):
            continue
        full = root / p
        if full.is_symlink() or not full.is_file():
            continue
        keep.append(p)
    return sorted(keep)


def source_files(root: Path, all_files: list[str], langs: set[str]) -> tuple[list[str], list[str]]:
    """篩出要解析的原始碼檔；回傳 (要解析的, 因超過 MAX_FILE_BYTES 而略過的)。"""
    picked, skipped = [], []
    for p in all_files:
        lang = language_of(p)
        if lang is None or lang not in langs:
            continue
        if (root / p).stat().st_size > MAX_FILE_BYTES:
            skipped.append(p)
            continue
        picked.append(p)
    return picked, skipped
