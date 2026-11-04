"""Monorepo：每個 Python 專案自己的匯入根目錄、服務目錄名不觸發敏感 keyword、Django migration 分組（#11）。

fixture `py_monorepo`：多個服務各有同名的 config.py／cache.py（flat layout），兩個服務都有 `server/` package，
一個 src-layout 服務、一個用 setup.cfg `package_dir = =lib` 的共用函式庫、一個有 migrations 的 Django app。
"""
import pytest
from aoa_graph import classify as C
from aoa_graph import projects, rules
from conftest import analyze, edge_set, make_repo
from test_classify import cfg, mk, run

PAYMENT = "services/payment-service"
SIGNER = "services/signer-service"
CHAT = "services/chat-bot"
WEB = "services/web-app"
LIB = "libs/shared-lib/lib/shared_lib"
MIG = "services/portal/orders/migrations"


def _service(path: str) -> str:
    return "/".join(path.split("/")[:2])


@pytest.fixture(scope="module")
def mono(tmp_path_factory):
    return make_repo("py_monorepo", tmp_path_factory.mktemp("mono"))


@pytest.fixture(scope="module")
def mono_result(mono):
    return analyze(mono, "--no-history")


# ---------------------------------------------------------------------------
# 1. 匯入根目錄
# ---------------------------------------------------------------------------

def test_detects_projects_and_import_roots(mono_result):
    g = mono_result["graph"]
    assert {p["dir"]: p["import_roots"] for p in g["python_projects"]} == {
        "libs/shared-lib": ["libs/shared-lib", "libs/shared-lib/lib"],   # setup.cfg package_dir = =lib
        PAYMENT: [PAYMENT], SIGNER: [SIGNER], "services/portal": ["services/portal"], CHAT: [CHAT],
        WEB: [WEB, f"{WEB}/src"],                                         # src-layout
    }
    assert g["package_roots"] == sorted(p["dir"] for p in g["python_projects"])


def test_same_named_modules_stay_inside_their_service(mono_result):
    edges = edge_set(mono_result)
    assert (f"{PAYMENT}/main.py", f"{PAYMENT}/config.py") in edges
    assert (f"{PAYMENT}/main.py", f"{PAYMENT}/cache.py") in edges
    assert (f"{SIGNER}/server/app.py", f"{SIGNER}/config.py") in edges
    assert (f"{CHAT}/server/app.py", f"{CHAT}/config.py") in edges
    # 測試檔（tests/ 沒有 __init__.py）也解析到自己服務的模組
    assert (f"{PAYMENT}/tests/test_main.py", f"{PAYMENT}/config.py") in edges
    assert (f"{SIGNER}/tests/test_app.py", f"{SIGNER}/server/app.py") in edges
    assert (f"{WEB}/tests/test_views.py", f"{WEB}/src/webapp/views.py") in edges
    cross = {(s, t) for s, t in edges if _service(s) != _service(t) and not t.startswith("libs/")}
    assert cross == set()


def test_unique_library_package_is_shared(mono_result):
    edges = edge_set(mono_result)
    assert (f"{WEB}/src/webapp/views.py", f"{LIB}/helpers.py") in edges
    assert (f"{CHAT}/server/app.py", f"{LIB}/helpers.py") in edges


def test_ambiguous_package_reported_as_likely_internal(mono_result):
    items = mono_result["unresolved"]["likely_internal"]
    assert [(i["source"], i["specifier"]) for i in items] == [("scripts/smoke.py", "server.app")]
    assert items[0]["candidates"] == sorted([f"{SIGNER}/server/app.py", f"{CHAT}/server/app.py"])
    assert mono_result["metrics"]["summary"]["likely_internal_external"] == 1
    assert not any(_service(s) == "scripts" for s, _ in edge_set(mono_result))


def test_without_auto_roots_internal_imports_look_external(mono):
    old = analyze(mono, "--no-history", "--no-auto-py-roots")
    assert old["graph"]["python_projects"] == []
    ext = {(e["source"], e["package"]) for e in old["graph"]["external"]}
    assert (f"{PAYMENT}/tests/test_main.py", "config") in ext
    li = {(i["source"], i["specifier"]) for i in old["unresolved"]["likely_internal"]}
    assert (f"{PAYMENT}/tests/test_main.py", "config") in li
    assert old["metrics"]["summary"]["likely_internal_external"] > 1


def test_py_root_override_keeps_nearest_root_first(mono):
    roots = [PAYMENT, SIGNER, CHAT]
    args = [a for r in roots for a in ("--py-root", r)]
    old = analyze(mono, "--no-history", "--no-auto-py-roots", *args)
    new = analyze(mono, "--no-history", *args)

    def bogus(res):
        return {(s, t) for s, t in edge_set(res)
                if _service(s) != _service(t) and not t.startswith("libs/") and not s.startswith("scripts/")}

    assert bogus(old)          # 只靠共用 root：tests/ 的 `import config` 連到別的服務
    assert bogus(new) == set()  # 自動偵測後，importer 自己的專案優先


def test_detect_reads_declared_dirs(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a/pyproject.toml").write_text(
        '[tool.hatch.build.targets.wheel]\npackages = ["python/pkg"]\n', encoding="utf-8")
    (tmp_path / "b").mkdir()
    (tmp_path / "b/pyproject.toml").write_text(
        '[tool.poetry]\npackages = [{include = "pkg", from = "lib"}]\n', encoding="utf-8")
    (tmp_path / "c").mkdir()
    (tmp_path / "c/setup.py").write_text('setup(package_dir={"": "code"})\n', encoding="utf-8")
    (tmp_path / "d").mkdir()
    (tmp_path / "d/pyproject.toml").write_text("not = [valid toml", encoding="utf-8")
    files = ["a/pyproject.toml", "a/python/pkg/x.py", "b/pyproject.toml", "b/lib/pkg/x.py",
             "c/setup.py", "c/code/pkg/x.py", "d/pyproject.toml", "d/src/x.py", "e/package.json"]
    py, roots = projects.detect(tmp_path, files)
    assert py == {"a": ["a", "a/python"], "b": ["b", "b/lib"], "c": ["c", "c/code"], "d": ["d", "d/src"]}
    assert roots == ["a", "b", "c", "d", "e"]


# ---------------------------------------------------------------------------
# 2. keyword 只比對套件根目錄以下
# ---------------------------------------------------------------------------

def _sensitive(node):
    return [r for r in node["rules"] if r.startswith("sensitive:")]


def test_service_dir_name_does_not_trigger_keywords(mono, mono_result):
    out = C.classify(mono_result["graph"], mono_result["metrics"], mono_result["unresolved"], cfg(), mono)["nodes"]
    assert _sensitive(out[f"{PAYMENT}/main.py"]) == []          # payment-service/ 不再讓每個檔案都是 payments
    assert _sensitive(out[f"{SIGNER}/server/app.py"]) == []         # signer-service/ 不再命中 crypto 的 signer
    assert _sensitive(out[f"{PAYMENT}/invoices.py"]) == ["sensitive:payments"]  # 檔名本身仍然命中
    assert "in 'invoices.py', below package root" in " ".join(out[f"{PAYMENT}/invoices.py"]["reasons"])
    old = C.classify(mono_result["graph"], mono_result["metrics"], mono_result["unresolved"],
                     cfg(keyword_scope="repo"), mono)["nodes"]
    assert _sensitive(old[f"{PAYMENT}/main.py"]) == ["sensitive:payments"]
    assert _sensitive(old[f"{SIGNER}/server/app.py"]) == ["sensitive:crypto"]


def test_keyword_scope_without_package_roots_uses_full_path():
    graph, metrics = mk({"payment-service/main.py": {}})
    assert "sensitive:payments" in run(graph, metrics)["nodes"]["payment-service/main.py"]["rules"]
    graph["package_roots"] = ["payment-service"]
    assert "sensitive:payments" not in run(graph, metrics)["nodes"]["payment-service/main.py"]["rules"]


def test_keyword_scope_validated():
    with pytest.raises(rules.ConfigError, match="keyword_scope"):
        rules._validate({"keyword_scope": "nope"}, "t")


# ---------------------------------------------------------------------------
# 3. Django migration 分組
# ---------------------------------------------------------------------------

def test_migration_facts_extracted(mono_result):
    nodes = {n["id"]: n for n in mono_result["graph"]["nodes"]}
    assert nodes[f"{MIG}/0003_backfill_totals.py"]["django_migration"] == {
        "number": 3, "data_ops": ["RunPython"], "replaces": []}
    assert nodes[f"{MIG}/0001_squashed_0002_order_total.py"]["django_migration"]["replaces"] == [
        "0001_initial", "0002_order_total"]
    assert "django_migration" not in nodes[f"{MIG}/__init__.py"]
    assert "django_migration" not in nodes["services/portal/orders/models.py"]


def _classes(res, config, root):
    out = C.classify(res["graph"], res["metrics"], res["unresolved"], config, root)
    return {k[len(MIG) + 1:]: (v["class"], v["rules"][0]) for k, v in out["nodes"].items() if k.startswith(MIG)}, out


def test_migrations_grouped(mono, mono_result):
    got, out = _classes(mono_result, cfg(), mono)
    assert got == {
        "0005_order_note.py": ("core", "migration_latest"),
        "0003_backfill_totals.py": ("core", "migration_data_ops"),
        "0001_initial.py": ("leaf", "migration_superseded"),
        "0002_order_total.py": ("leaf", "migration_superseded"),
        "0001_squashed_0002_order_total.py": ("business", "migration_history"),
        "0004_order_status.py": ("business", "migration_history"),
        "__init__.py": ("business", "migration_package"),
    }
    assert out["summary"]["django_migrations"] == {"leaf": 2, "business": 3, "core": 2}
    # models.py 仍由 db_schema 判 core
    assert out["nodes"]["services/portal/orders/models.py"]["class"] == "core"


def test_migrations_configurable(mono, mono_result):
    off, _ = _classes(mono_result, cfg(migrations={"mode": "off"}), mono)
    assert {c for c, _ in off.values()} == {"core"}
    tuned, _ = _classes(mono_result, cfg(migrations={"latest_core": 2, "data_ops_core": False,
                                                     "history_class": "leaf"}), mono)
    assert tuned["0004_order_status.py"] == ("core", "migration_latest")
    assert tuned["0003_backfill_totals.py"] == ("leaf", "migration_history")
    assert tuned["__init__.py"] == ("leaf", "migration_package")


def test_config_core_path_beats_migration_rule(mono, mono_result):
    got, _ = _classes(mono_result, cfg(core_paths=[f"{MIG}/0004_order_status.py"]), mono)
    assert got["0004_order_status.py"] == ("core", "config_core_path")


@pytest.mark.parametrize("table,match", [
    ({"mode": "all"}, "mode"),
    ({"latest_core": -1}, "latest_core"),
    ({"data_ops_core": "yes"}, "data_ops_core"),
    ({"history_class": "core"}, "history_class"),
    ({"bogus": 1}, "bogus"),
])
def test_migrations_config_validated(table, match):
    with pytest.raises(rules.ConfigError, match=match):
        rules._validate({"migrations": table}, "t")
