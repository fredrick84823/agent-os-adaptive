"""把 Python import 解析成 repo 內的模組檔。

模組名稱怎麼來：
  1. 推斷的 root：檔案最上層「含 __init__.py 的祖先目錄」的父目錄
     （`src/pkg/a.py` + `src/pkg/__init__.py` → root `src`、模組 `pkg.a`）；中間沒有 __init__.py
     的 namespace 子目錄會被跨過（`src/pkg/ns/b.py` → `pkg.ns.b`）。沒有任何祖先是 package
     （例如 `scripts/run.py`）就以檔案所在目錄為 root。
  2. 專案匯入根目錄（projects.detect）：檔案所屬的最近一個 Python 專案（含 pyproject.toml／setup.py／
     setup.cfg 的目錄）的專案目錄、src/ 與設定檔宣告的目錄，以相對路徑再登記一次。
  3. 共用 root：repo 根目錄、`src/`、以及 `--py-root` 指定的目錄，以完整相對路徑再登記一次
     （涵蓋沒有 __init__.py 的 namespace package）。

解析時同名候選的優先順序（越前面越優先）：
  與 importer 同一個推斷 root → importer 所屬專案的匯入根目錄（專案目錄 → src → 宣告的）→ repo 根目錄 →
  `src` / `--py-root` → 其他專案的 package（唯一一個專案提供時）；同級再比路徑長度、字典序。
其他專案頂層的「單檔模組」（`servers/a/config.py` 的 `config`）對別的專案永遠不可見——
monorepo 裡每個服務各有一個 config.py／cache.py 是常態，連過去就是假的跨服務依賴。
其他專案的 package（目錄）只有在恰好一個專案提供時才連（例如 `libs/x` 的 `x_lib`）；
多個專案都有同名 package（每個服務都有 `server/`）就不連。
非共用、非專案的腳本目錄，只對同目錄的 importer 可見。
"""
from __future__ import annotations

import posixpath

from .extract import RawImport
from .projects import nearest


class PyResolver:
    def __init__(self, py_files: list[str], extra_roots: tuple[str, ...] = (),
                 projects: dict[str, list[str]] | None = None):
        self.files = set(py_files)
        shared = {""}
        if any(f.startswith("src/") for f in py_files):
            shared.add("src")
        shared.update(r.strip("/") for r in extra_roots)
        self.shared_roots = shared
        # 專案 → 匯入根目錄（依優先順序）；root → 所屬專案
        self.projects = {p: list(rs) for p, rs in (projects or {}).items()}
        self.root_project = {r: p for p, rs in sorted(self.projects.items()) for r in rs}
        self.file_project: dict[str, str | None] = {f: nearest(f, self.projects) for f in py_files}
        self.index: dict[str, set[tuple[str, str]]] = {}
        self.file_module: dict[str, tuple[str, str]] = {}
        # 檔名不是合法識別字（例如 Django migration `0002_auto.py`）時，仍記下所在 package，
        # 讓檔內的相對 import 能解析
        self.file_package: dict[str, tuple[str, list[str]]] = {}
        for f in sorted(py_files):
            root = self._inferred_root(f)
            rel_dir = posixpath.dirname(f)[len(root) + 1:] if root else posixpath.dirname(f)
            pkg_parts = rel_dir.split("/") if rel_dir else []
            if all(p.isidentifier() for p in pkg_parts):
                self.file_package[f] = (root, pkg_parts)
            mod = self._module_name(f, root)
            if mod is None:
                continue
            self.file_module[f] = (root, mod)
            self._register(mod, root, f)
        for f in sorted(py_files):
            if f not in self.file_module:
                continue
            proj = self.file_project[f]
            extra = [r for r in self.projects.get(proj, []) if r == "" or f.startswith(r + "/")] if proj is not None else []
            for r in sorted(shared) + extra:
                if r != self.file_module.get(f, (None,))[0] and (r == "" or f.startswith(r + "/")):
                    alt = self._module_name(f, r)
                    if alt:
                        self._register(alt, r, f)

    def _inferred_root(self, f: str) -> str:
        """最上層「含 __init__.py 的祖先目錄」的父目錄；沒有任何祖先是 package 就用檔案所在目錄。

        跳過中間沒有 __init__.py 的 namespace 子目錄（例如 flask 的 `src/flask/sansio/`）。
        """
        top_pkg = None
        d = posixpath.dirname(f)
        while d:
            if posixpath.join(d, "__init__.py") in self.files:
                top_pkg = d
            d = posixpath.dirname(d)
        return posixpath.dirname(top_pkg) if top_pkg is not None else posixpath.dirname(f)

    @staticmethod
    def _module_name(f: str, root: str) -> str | None:
        rel = f[len(root) + 1:] if root else f
        parts = rel[:-3].split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts or not all(p.isidentifier() for p in parts):
            return None
        return ".".join(parts)

    def _register(self, mod: str, root: str, f: str) -> None:
        self.index.setdefault(mod, set()).add((root, f))

    def module_of(self, f: str) -> str | None:
        hit = self.file_module.get(f)
        return hit[1] if hit else None

    def _lookup(self, mod: str, importer: str, same_root_only: bool = False) -> str | None:
        cands = self.index.get(mod)
        if not cands:
            return None
        my_root = self.file_package.get(importer, ("", []))[0]
        my_proj = self.file_project.get(importer)
        my_roots = self.projects.get(my_proj, []) if my_proj is not None else []
        ranked = []
        foreign: dict[str, list[tuple]] = {}
        for root, f in cands:
            if root == my_root:
                key = (0, 0)
            elif same_root_only:
                continue
            elif root in my_roots and (self.file_project.get(f) == my_proj):
                key = (1, my_roots.index(root))
            elif root == "":
                key = (2, 0)
            elif root in self.shared_roots:
                key = (3, 0)
            elif root in self.root_project and self.file_project.get(f) == self.root_project[root]:
                # 別的專案：只看得到它的 package（目錄），看不到頂層單檔模組
                if "." in mod or f.endswith("/__init__.py"):
                    foreign.setdefault(self.root_project[root], []).append((len(f), f))
                continue
            else:
                continue  # 別人的腳本目錄，不可見
            ranked.append((key, len(f), f))
        if ranked:
            return min(ranked)[2]
        if len(foreign) == 1:
            return min(next(iter(foreign.values())))[1]
        return None  # 沒有候選，或多個專案都有同名 package（不猜）

    def hidden_candidates(self, dotted: str, importer: str) -> list[str]:
        """被判成 external 的 import，在 repo 裡其實有同名模組（不可見或有歧義）時，回傳那些檔案。

        用來回報「可能是內部模組卻被當成外部套件」：通常代表缺了 --py-root、專案設定沒被偵測到，
        或是 monorepo 裡多個服務有同名 package。
        """
        parts = dotted.split(".")
        for i in range(len(parts), 0, -1):
            cands = self.index.get(".".join(parts[:i]))
            if cands:
                return sorted({f for _, f in cands if f != importer})
        return []

    def _longest_prefix(self, dotted: str, importer: str, same_root_only: bool = False) -> str | None:
        parts = dotted.split(".")
        for i in range(len(parts), 0, -1):
            hit = self._lookup(".".join(parts[:i]), importer, same_root_only)
            if hit:
                return hit
        return None

    def resolve(self, importer: str, raw: RawImport) -> list[tuple[str, str]]:
        """回傳 [(status, value)]，status ∈ internal | external | unresolved。"""
        spec = raw.spec
        assert spec is not None
        if spec.startswith("."):
            level = len(spec) - len(spec.lstrip("."))
            rest = spec[level:]
            info = self.file_package.get(importer)
            if info is None:
                return [("unresolved", "importer_not_a_module")]
            pkg = list(info[1])
            if level - 1 > len(pkg):
                return [("unresolved", "relative_beyond_top_level")]
            base = pkg[: len(pkg) - (level - 1)]
            full = ".".join(base + (rest.split(".") if rest else []))
            return self._from_targets(full, raw.names, importer, relative=True)
        if raw.names:
            return self._from_targets(spec, raw.names, importer, relative=False)
        hit = self._longest_prefix(spec, importer)
        return [("internal", hit)] if hit else [("external", spec.split(".")[0])]

    def _from_targets(self, full: str, names: tuple[str, ...], importer: str, relative: bool):
        out: list[tuple[str, str]] = []
        need_base = not names or "*" in names
        for n in names:
            if n == "*":
                continue
            sub = f"{full}.{n}" if full else n
            hit = self._lookup(sub, importer, same_root_only=relative)
            if hit:
                out.append(("internal", hit))
            else:
                need_base = True  # n 是模組內的屬性
        if need_base:
            if not full:
                if not out:
                    out.append(("unresolved", "not_found"))
            else:
                hit = self._lookup(full, importer, same_root_only=relative) if relative else self._longest_prefix(full, importer)
                if hit:
                    out.append(("internal", hit))
                elif relative:
                    out.append(("unresolved", "not_found"))
                else:
                    out.append(("external", full.split(".")[0]))
        return out
