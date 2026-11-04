from conftest import analyze, edge_set, make_repo


def test_py_nodes_and_modules(py_result):
    nodes = {n["id"]: n for n in py_result["graph"]["nodes"]}
    assert not any(".venv" in i for i in nodes)
    assert nodes["src/app/__init__.py"]["module"] == "app"
    assert nodes["src/app/plugins/loader.py"]["module"] == "app.plugins.loader"
    assert nodes["scripts/run.py"]["module"] == "run"
    assert nodes["tests/test_core.py"]["is_test"] is True


def test_py_resolution(py_result):
    assert edge_set(py_result) == {
        ("src/app/__init__.py", "src/app/core.py"),      # from .core import run
        ("src/app/core.py", "src/app/utils.py"),         # from . import utils（子模組）
        ("src/app/core.py", "src/app/models.py"),
        ("src/app/core.py", "src/app/db.py"),            # import app.db
        ("src/app/models.py", "src/app/db.py"),          # from app.db import Base（屬性 → 模組本身）
        ("src/app/models.py", "src/app/core.py"),        # TYPE_CHECKING 內的 import
        ("src/app/plugins/loader.py", "src/app/utils.py"),   # from ..utils import os
        ("src/app/plugins/loader.py", "src/app/plugins/extra.py"),  # importlib 字面字串
        ("scripts/run.py", "scripts/helpers.py"),        # 腳本目錄自己的 sys.path
        ("scripts/run.py", "src/app/core.py"),           # src/ layout
        ("tests/test_core.py", "src/app/core.py"),
    }


def test_py_kinds_external_unresolved(py_result):
    kinds = {(e["source"], e["target"]): e["kinds"] for e in py_result["graph"]["edges"]}
    assert kinds[("src/app/models.py", "src/app/core.py")] == ["type"]
    assert kinds[("src/app/plugins/loader.py", "src/app/plugins/extra.py")] == ["dynamic"]
    ext = {(e["source"], e["package"]) for e in py_result["graph"]["external"]}
    assert {("src/app/utils.py", "os"), ("src/app/utils.py", "json"), ("src/app/db.py", "sqlalchemy")} <= ext
    # tests/ 看不到 scripts/helpers.py（不同的腳本目錄）
    assert ("tests/test_core.py", "helpers") in ext
    reasons = {(u["source"], u["reason"]) for u in py_result["unresolved"]["items"]}
    assert reasons == {
        ("src/app/plugins/loader.py", "relative_beyond_top_level"),
        ("src/app/plugins/loader.py", "dynamic_expression"),
    }


def test_py_cycle_and_blast_radius(py_result):
    m = py_result["metrics"]
    assert m["cycles"] == [{"id": "scc-1", "size": 2, "members": ["src/app/core.py", "src/app/models.py"]}]
    db = m["nodes"]["src/app/db.py"]
    # core、models 直接；__init__、run.py、test_core.py 經由 core
    assert (db["fan_in"], db["fan_out"], db["blast_radius"]) == (2, 0, 5)
    utils = m["nodes"]["src/app/utils.py"]
    assert (utils["fan_in"], utils["blast_radius"]) == (2, 6)
    core = m["nodes"]["src/app/core.py"]
    assert core["in_cycle"] and core["fan_in"] == 4 and core["test_fan_in"] == 1
    assert core["blast_radius"] == 4  # models、__init__、run、test_core
    assert m["summary"]["nodes"] == 11 and m["summary"]["edges"] == 11


def test_no_git_mode_skips_venv(tmp_path):
    import shutil

    from conftest import FIXTURES
    repo = tmp_path / "plain"
    shutil.copytree(FIXTURES / "py_repo", repo)
    r = analyze(repo, "--no-git")
    assert not any(".venv" in n["id"] for n in r["graph"]["nodes"])
    assert r["metrics"]["params"]["git_available"] is False
    assert r["metrics"]["nodes"]["src/app/core.py"]["churn"] is None
    assert edge_set(r) == edge_set(analyze(make_repo("py_repo", tmp_path)))


def test_runtime_cycle_excludes_type_only_edges(py_result):
    m = py_result["metrics"]
    # core ↔ models 的回邊只在 TYPE_CHECKING 內 → 執行期沒有循環
    assert m["runtime_cycles"] == []
    core = m["nodes"]["src/app/core.py"]
    assert core["in_cycle"] is True and core["in_runtime_cycle"] is False
