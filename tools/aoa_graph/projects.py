"""偵測 repo 裡的「套件根目錄」（monorepo 每個服務／函式庫各自一個）。

- Python 專案：含 `pyproject.toml`、`setup.py` 或 `setup.cfg` 的目錄。每個專案的匯入根目錄（import root）=
  專案目錄本身、`<專案>/src`（src-layout），再加上設定檔宣告的目錄：
  `[tool.setuptools] package-dir = {"" = "src"}`、`[tool.setuptools.packages.find] where`、
  `[tool.hatch.build.targets.wheel] packages`（`"src/foo"` → `src`）、`[tool.poetry] packages[].from`、
  setup.cfg `[options] package_dir = =src`／`[options.packages.find] where`、setup.py `package_dir={"": "src"}`。
  宣告的目錄只有在 repo 裡真的有檔案時才採用。
- 套件根目錄（classify 用來忽略「服務容器目錄名」的路徑 token）：上面的 Python 專案目錄，加上含
  `package.json` 的目錄。repo 根目錄記成 ""。

只讀設定檔、不執行任何東西；設定檔壞掉就只用專案目錄與 src/。
"""
from __future__ import annotations

import configparser
import posixpath
import re
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - 3.10 only
    import tomli as tomllib

PY_PROJECT_FILES = ("pyproject.toml", "setup.py", "setup.cfg")
PACKAGE_ROOT_FILES = (*PY_PROJECT_FILES, "package.json")

_SETUP_PY_PKG_DIR = re.compile(r"""package_dir\s*=\s*\{\s*(['"])\1\s*:\s*['"]([^'"]+)['"]""")


def _dir_of(path: str) -> str:
    return posixpath.dirname(path)


def _join(base: str, rel: str) -> str | None:
    rel = rel.strip().strip("/")
    if rel in ("", "."):
        return base
    if rel.startswith("..") or "/../" in f"/{rel}/":
        return None
    out = posixpath.normpath(posixpath.join(base, rel)) if base else posixpath.normpath(rel)
    return "" if out == "." else out


def _declared_dirs(root: Path, project: str, present: set[str]) -> list[str]:
    """回傳設定檔宣告的匯入根目錄（相對專案目錄的字串，可能有重複）。"""
    out: list[str] = []
    base = root / project if project else root
    if "pyproject.toml" in present:
        try:
            doc = tomllib.loads((base / "pyproject.toml").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
            doc = {}
        tool = doc.get("tool", {}) if isinstance(doc.get("tool"), dict) else {}
        st = tool.get("setuptools", {}) if isinstance(tool.get("setuptools"), dict) else {}
        pkg_dir = st.get("package-dir")
        if isinstance(pkg_dir, dict) and isinstance(pkg_dir.get(""), str):
            out.append(pkg_dir[""])
        pk = st.get("packages")
        if isinstance(pk, dict) and isinstance(pk.get("find"), dict):
            where = pk["find"].get("where")
            if isinstance(where, list):
                out.extend(w for w in where if isinstance(w, str))
        hatch = tool.get("hatch", {}) if isinstance(tool.get("hatch"), dict) else {}
        wheel = hatch.get("build", {}).get("targets", {}).get("wheel", {}) if isinstance(hatch.get("build"), dict) else {}
        if isinstance(wheel, dict) and isinstance(wheel.get("packages"), list):
            out.extend(posixpath.dirname(p.strip("/")) for p in wheel["packages"] if isinstance(p, str))
        poetry = tool.get("poetry", {}) if isinstance(tool.get("poetry"), dict) else {}
        if isinstance(poetry.get("packages"), list):
            out.extend(p["from"] for p in poetry["packages"] if isinstance(p, dict) and isinstance(p.get("from"), str))
    if "setup.cfg" in present:
        cp = configparser.ConfigParser(interpolation=None)
        try:
            cp.read_string((base / "setup.cfg").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, configparser.Error):
            cp = configparser.ConfigParser(interpolation=None)
        if cp.has_option("options", "package_dir"):
            for line in cp.get("options", "package_dir").splitlines():
                k, sep, v = line.partition("=")
                if sep and not k.strip():
                    out.append(v)
        if cp.has_option("options.packages.find", "where"):
            out.extend(cp.get("options.packages.find", "where").split())
    if "setup.py" in present:
        try:
            m = _SETUP_PY_PKG_DIR.search((base / "setup.py").read_text(encoding="utf-8", errors="replace"))
        except OSError:
            m = None
        if m:
            out.append(m.group(2))
    return out


def detect(root: Path | None, all_files: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    """回傳 (python_projects, package_roots)。

    python_projects：{專案目錄: [匯入根目錄…]}，第一個一定是專案目錄本身，其餘依 src → 宣告的順序、去重。
    package_roots：所有套件根目錄（含 package.json 的目錄），已排序。
    root 為 None 時不讀設定檔內容（只看檔名）。
    """
    by_dir: dict[str, set[str]] = {}
    for f in all_files:
        name = posixpath.basename(f)
        if name in PACKAGE_ROOT_FILES:
            by_dir.setdefault(_dir_of(f), set()).add(name)
    dirs_with_files = set()
    for f in all_files:
        d = _dir_of(f)
        while True:
            if d in dirs_with_files:
                break
            dirs_with_files.add(d)
            if not d:
                break
            d = _dir_of(d)
    projects: dict[str, list[str]] = {}
    for d, present in sorted(by_dir.items()):
        if not present & set(PY_PROJECT_FILES):
            continue
        roots = [d]
        cands = ["src"] + (_declared_dirs(root, d, present) if root is not None else [])
        for c in cands:
            r = _join(d, c)
            if r is not None and r not in roots and r in dirs_with_files and r != d:
                roots.append(r)
        projects[d] = roots
    return projects, sorted(by_dir)


def nearest(path: str, dirs) -> str | None:
    """path 所在的最近（最深）一個 dirs 成員；"" 代表 repo 根目錄。都不是祖先就回傳 None。"""
    d = _dir_of(path)
    while True:
        if d in dirs:
            return d
        if not d:
            return None
        d = _dir_of(d)
