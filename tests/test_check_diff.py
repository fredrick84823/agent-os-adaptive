"""aoa-classify --check-diff：改動碰到的最嚴格類別、新檔推估、依賴清單升級與 exit code。"""
import json

import pytest
from aoa_graph import check_diff as D
from aoa_graph import classify as C
from aoa_graph import cli
from conftest import git, make_repo


@pytest.fixture
def repo(tmp_path):
    r = make_repo("py_repo", tmp_path)
    (r / "pyproject.toml").write_text('[project]\nname = "app"\ndependencies = ["requests>=2"]\n', encoding="utf-8")
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "chore: pyproject")
    assert cli.main([str(r)]) == 0 and C.main([str(r)]) == 0
    git(r, "checkout", "-q", "-b", "feature")
    return r


def check(repo, capsys, *extra):
    code = C.main([str(repo), "--check-diff", "main", "--json", *extra])
    return code, json.loads(capsys.readouterr().out)


def nodes(repo):
    return json.loads((repo / "agent-os-adaptive/architecture-analysis/nodes.json").read_text())["nodes"]


def touch(repo, path, text="\n# touch\n"):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(text)


def test_fixture_classes(repo):
    n = nodes(repo)
    assert n["scripts/run.py"]["class"] == "leaf"
    assert n["src/app/core.py"]["class"] == "business"
    assert n["src/app/models.py"]["class"] == "core"


def test_no_changes(repo, capsys):
    code, res = check(repo, capsys)
    assert code == 0 and res["strictest"] is None and res["files"] == []   # 自己的輸出目錄不算改動


def test_leaf_only(repo, capsys):
    touch(repo, "scripts/run.py")
    touch(repo, "tests/test_core.py")
    code, res = check(repo, capsys)
    assert code == 0 and res["strictest"] == "leaf" and res["workflow"] == "instructions/leaf-workflow.md"
    assert not res["escalate"]


def test_business_and_fail_on(repo, capsys):
    touch(repo, "src/app/core.py")
    touch(repo, "README.md", "x\n")
    code, res = check(repo, capsys)
    assert code == 0 and res["strictest"] == "business" and res["workflow_class"] == "business"
    readme = next(f for f in res["files"] if f["path"] == "README.md")
    assert readme["class"] is None and readme["source"] == "not classified"
    assert res["counts"] == {"leaf": 0, "business": 1, "core": 0, "unclassified": 1}
    assert check(repo, capsys, "--fail-on", "business")[0] == D.EXIT_FLAG


def test_core_touched_exits_3(repo, capsys):
    touch(repo, "src/app/core.py")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: business change")   # 已 commit 的改動也算
    touch(repo, "src/app/models.py")                            # 未 commit 的改動也算
    code, res = check(repo, capsys)
    assert code == D.EXIT_FLAG and res["strictest"] == "core" and res["escalate"]
    assert "src/app/models.py" in res["escalations"][0]
    assert check(repo, capsys, "--fail-on", "never")[0] == 0


def test_deleted_core_file_counts(repo, capsys):
    (repo / "src/app/models.py").unlink()
    code, res = check(repo, capsys)
    f = next(f for f in res["files"] if f["path"] == "src/app/models.py")
    assert f["status"] == "D" and f["class"] == "core" and code == D.EXIT_FLAG


def test_new_files_inferred_from_path(repo, capsys):
    touch(repo, "src/app/report.py", "x = 1\n")
    touch(repo, "src/app/auth/tokens.py", "x = 1\n")
    touch(repo, "tests/test_report.py", "x = 1\n")
    code, res = check(repo, capsys)
    by = {f["path"]: f for f in res["files"]}
    assert by["src/app/report.py"]["class"] == "business" and by["src/app/report.py"]["rules"] == ["default"]
    assert by["src/app/report.py"]["source"] == "inferred"
    assert by["src/app/auth/tokens.py"]["class"] == "core" and "sensitive:auth" in by["src/app/auth/tokens.py"]["rules"]
    assert by["tests/test_report.py"]["class"] == "leaf"
    assert code == D.EXIT_FLAG


def test_new_dependency_escalates(repo, capsys):
    touch(repo, "scripts/run.py")
    (repo / "pyproject.toml").write_text('[project]\nname = "app"\ndependencies = ["requests>=2", "Py_Yaml"]\n', encoding="utf-8")
    code, res = check(repo, capsys)
    assert res["strictest"] == "leaf" and res["new_dependencies"] == ["py:py-yaml (pyproject.toml)"]
    assert code == D.EXIT_FLAG and res["escalate"] and res["workflow_class"] == "core"
    assert check(repo, capsys, "--max-new-deps", "1")[0] == 0


def test_version_bump_is_not_a_new_dependency(repo, capsys):
    (repo / "pyproject.toml").write_text('[project]\nname = "app"\ndependencies = ["requests>=3"]\n', encoding="utf-8")
    code, res = check(repo, capsys)
    assert code == 0 and res["new_dependencies"] == []


@pytest.mark.parametrize("name,before,after,added", [
    ("package.json", '{"dependencies": {"a": "1"}}', '{"dependencies": {"a": "2"}, "devDependencies": {"b": "1"}}', {"npm:b"}),
    ("requirements-dev.txt", "flask==3\n# c\n-r base.txt\n", "flask==3\nhttpx[http2]>=0.27  # x\n", {"py:httpx"}),
    ("pyproject.toml", '[dependency-groups]\ndev = ["pytest"]\n', '[dependency-groups]\ndev = ["pytest", "ruff"]\n', {"py:ruff"}),
    ("package.json", "not json", '{"dependencies": {"a": "1"}}', {"npm:a"}),
])
def test_manifest_deps(name, before, after, added):
    assert D.manifest_deps(name, after) - D.manifest_deps(name, before) == added


def test_text_output_and_bad_base(repo, capsys):
    touch(repo, "src/app/models.py")
    assert C.main([str(repo), "--check-diff", "main"]) == D.EXIT_FLAG
    out = capsys.readouterr().out
    assert "ESCALATE: diff touches core nodes: src/app/models.py" in out
    assert "→ workflow: core (instructions/core-workflow.md)" in out
    assert C.main([str(repo), "--check-diff", "no-such-branch"]) == D.EXIT_ERROR


def test_stale_nodes_json_warns(repo, capsys):
    doc_path = repo / "agent-os-adaptive/architecture-analysis/nodes.json"
    doc = json.loads(doc_path.read_text())
    doc["source"]["commit"] = "0" * 40
    doc_path.write_text(json.dumps(doc))
    _, res = check(repo, capsys)
    assert any("not an ancestor of HEAD" in w for w in res["warnings"])


def test_missing_nodes_json(tmp_path, capsys):
    r = make_repo("py_repo", tmp_path)
    assert C.main([str(r), "--check-diff", "main"]) == D.EXIT_ERROR

