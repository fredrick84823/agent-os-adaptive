"""不需要 git 的小型邊界案例：直接在 tmp_path 寫檔，用 --no-git 跑。"""
from pathlib import Path

from conftest import analyze, edge_set


def write(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return root


def test_py_namespace_subdir_inside_package(tmp_path):
    """flask 的 src/flask/sansio/ 沒有 __init__.py，`from ..helpers import x` 仍要解析到上一層。"""
    repo = write(tmp_path / "r", {
        "src/pkg/__init__.py": "",
        "src/pkg/helpers.py": "X = 1\n",
        "src/pkg/ns/app.py": "from ..helpers import X\nfrom .. import helpers\n",
    })
    r = analyze(repo, "--no-git")
    mods = {n["id"]: n["module"] for n in r["graph"]["nodes"]}
    assert mods["src/pkg/ns/app.py"] == "pkg.ns.app"
    assert edge_set(r) == {("src/pkg/ns/app.py", "src/pkg/helpers.py")}
    assert r["unresolved"]["items"] == []


def test_ts_tsconfig_extends_and_workspace_source_dir(tmp_path):
    repo = write(tmp_path / "r", {
        "tsconfig.base.json": '{ "compilerOptions": { "baseUrl": ".", "paths": { "~/*": ["app/*"] } } }',
        "app/tsconfig.json": '{ "extends": "../tsconfig.base.json" }',
        "app/main.ts": 'import { u } from "~/util";\nimport ky from "ky";\nimport { y } from "ky/extra";\n',
        "app/util.ts": "export const u = 1;\n",
        # ky 的寫法：exports 指向未追蹤的 distribution/，原始碼在 source/
        "lib/ky/package.json": '{ "name": "ky", "exports": { "types": "./distribution/index.d.ts", "default": "./distribution/index.js" } }',
        "lib/ky/source/index.ts": "export default 1;\n",
        "lib/ky/source/extra.ts": "export const y = 1;\n",
    })
    r = analyze(repo, "--no-git")
    assert edge_set(r) == {
        ("app/main.ts", "app/util.ts"),
        ("app/main.ts", "lib/ky/source/index.ts"),
        ("app/main.ts", "lib/ky/source/extra.ts"),
    }


def test_lang_filter(tmp_path):
    repo = write(tmp_path / "r", {"a.py": "import b\n", "b.py": "", "c.ts": 'import "./d";\n', "d.ts": ""})
    assert {n["id"] for n in analyze(repo, "--no-git", "--lang", "py")["graph"]["nodes"]} == {"a.py", "b.py"}
    assert {n["id"] for n in analyze(repo, "--no-git", "--lang", "ts")["graph"]["nodes"]} == {"c.ts", "d.ts"}


def test_python_does_not_link_other_script_dirs(tmp_path):
    repo = write(tmp_path / "r", {
        "tools/utils.py": "",
        "bench/run.py": "import utils\n",
    })
    r = analyze(repo, "--no-git")
    assert edge_set(r) == set()
    assert {(e["source"], e["package"]) for e in r["graph"]["external"]} == {("bench/run.py", "utils")}


def test_ts_package_imports_field(tmp_path):
    """vite 用 package.json `imports` 的 `#types/*` 指向 types/ 目錄。"""
    repo = write(tmp_path / "r", {
        "pkg/package.json": '{ "name": "p", "imports": { "#types/*": "./types/*", "#dep": { "types": "./src/dep.ts", "default": "./dist/dep.js" } } }',
        "pkg/src/client.ts": 'import type { H } from "#types/hmr";\nimport { d } from "#dep";\nimport x from "#nope";\n',
        "pkg/src/dep.ts": "export const d = 1;\n",
        "pkg/types/hmr.d.ts": "export type H = 1;\n",
    })
    r = analyze(repo, "--no-git")
    assert edge_set(r) == {("pkg/src/client.ts", "pkg/types/hmr.d.ts"), ("pkg/src/client.ts", "pkg/src/dep.ts")}
    assert [(u["specifier"], u["reason"]) for u in r["unresolved"]["items"]] == [("#nope", "package_imports_no_match")]


def test_py_relative_import_from_non_identifier_filename(tmp_path):
    """Django migration 檔名 `0002_auto.py` 不是合法模組名，但檔內的 `from ..models import X` 仍要解析。"""
    repo = write(tmp_path / "r", {
        "app/__init__.py": "",
        "app/models.py": "X = 1\n",
        "app/migrations/__init__.py": "",
        "app/migrations/0002_auto.py": "from ..models import X\n",
    })
    r = analyze(repo, "--no-git")
    assert ("app/migrations/0002_auto.py", "app/models.py") in edge_set(r)
    assert r["unresolved"]["items"] == []
