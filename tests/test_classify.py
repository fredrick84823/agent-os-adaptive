"""aoa-classify：硬規則、風險分數、百分位切分、覆寫、設定檔、覆蓋率與決定性。"""
import json
import math
from pathlib import Path

import pytest
from aoa_graph import classify as C
from aoa_graph import cli, rules
from aoa_graph.metrics import compute
from conftest import make_repo

SOURCE = {"commit": "abc", "dirty": False}


def mk(nodes, edges=(), external=(), history=None, type_edges=()):
    """nodes：{id: {is_test, language, module}} 的簡寫；回傳 (graph, metrics)。"""
    ids = sorted(nodes)
    full = []
    for i in ids:
        n = {"language": "python", "is_test": False, **nodes[i], "id": i}
        if n["language"] == "python" and "module" not in n:
            n["module"] = i[:-3].replace("/", ".").removesuffix(".__init__")
        full.append(n)
    all_edges = sorted(set(edges) | set(type_edges))
    runtime = sorted(set(edges))
    per, cycles, rcycles = compute(ids, all_edges, {n["id"]: n["is_test"] for n in full}, runtime)
    history = history or {}
    for i in ids:
        churn, bug = history.get(i, (0, 0))
        per[i].update(churn=churn, churn_lines=churn, bugfix_count=bug, co_change=[])
    graph = {
        "source": SOURCE, "nodes": full,
        "edges": [{"source": s, "target": t, "kinds": ["type"] if (s, t) in type_edges else ["static"], "count": 1}
                  for s, t in all_edges],
        "external": [{"source": s, "package": p, "kinds": ["static"]} for s, p in external],
    }
    metrics = {"source": SOURCE, "nodes": per, "cycles": cycles, "runtime_cycles": rcycles}
    return graph, metrics


def cfg(**repo):
    return rules.merge(rules.load_default(), repo)


def run(graph, metrics, config=None, **kw):
    return C.classify(graph, metrics, kw.pop("unresolved", None), config or cfg(), **kw)


# ---------------------------------------------------------------------------
# 比對
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pattern,path,ok", [
    ("**/migrations/**", "app/migrations/0001_init.py", True),
    ("**/migrations/**", "migrations/0001.py", True),
    ("**/migrations/**", "app/migrations.py", False),
    ("src/billing/**", "src/billing/a/b.ts", True),
    ("src/billing/**", "lib/src/billing/a.ts", False),      # 含 / → 從根目錄錨定
    ("billing", "lib/billing/a.ts", True),                  # 不含 / → 任何深度，命中目錄涵蓋底下
    ("*.py", "a/b/c.py", True),
    ("/setup.py", "pkg/setup.py", False),
    ("**/models.py", "models.py", True),
    ("src/*.ts", "src/a/b.ts", False),                      # * 不跨 /
    ("src/?.ts", "src/a.ts", True),
])
def test_glob(pattern, path, ok):
    assert rules.glob_match(pattern, path) is ok


def test_tokens_and_keywords():
    toks = rules.path_tokens("src/AuthProvider/user_sessions.py")
    assert toks == ["src", "auth", "provider", "user", "sessions", "py"]
    assert rules.keyword_hit("session", toks) == "sessions"
    assert rules.keyword_hit("auth", rules.path_tokens("src/author.py")) is None
    assert rules.keyword_hit("api", rules.path_tokens("src/rapid.ts")) is None
    assert rules.keyword_hit("hard-delete", rules.path_tokens("jobs/hard_delete_users.py")) == "hard-delete"
    assert rules.keyword_hit("oauth2", rules.path_tokens("x/oauth2_client.py")) == "oauth2"
    assert rules.keyword_hit("auth", rules.path_tokens("x/OAuth2Client.ts")) == "auth2"
    assert rules.keyword_hit("api", rules.path_tokens("v2/api2.ts")) == "api2"


def test_merge_extend_replace_disable():
    merged = cfg(
        version="acme-1",
        thresholds={"core_top_percent": 20},
        sensitive=[
            {"id": "auth", "keywords": ["badge"]},
            {"id": "pii", "replace": True, "keywords": ["customer"]},
            {"id": "export", "paths": ["src/export/**"]},
        ],
        disable=["irreversible"],
    )
    by = {s["id"]: s for s in merged["sensitive"]}
    assert "badge" in by["auth"]["keywords"] and "login" in by["auth"]["keywords"]
    assert by["pii"]["keywords"] == ["customer"]
    assert "export" in by and "irreversible" not in by
    assert merged["thresholds"]["core_top_percent"] == 20
    assert merged["thresholds"]["leaf_bottom_percent"] == 40
    assert merged["default_version"] and merged["repo_version"] == "acme-1"


@pytest.mark.parametrize("bad", [
    {"core_path": ["x"]},                       # 拼錯欄位不可默默忽略
    {"thresholds": {"core_top": 5}},
    {"weights": {"churn": -1}},
    {"disable": ["nope"]},
    {"sensitive": [{"keywords": ["x"]}]},
])
def test_config_errors(bad):
    with pytest.raises(rules.ConfigError):
        rules._validate(bad, "t")
        rules.merge(rules.load_default(), bad)


# ---------------------------------------------------------------------------
# 硬規則
# ---------------------------------------------------------------------------

def test_hard_rules_sensitive_and_entrypoints(tmp_path):
    (tmp_path / "web").mkdir()
    (tmp_path / "web" / "package.json").write_text("{}")
    graph, metrics = mk(
        {
            "pkg/__init__.py": {},
            "pkg/sub/__init__.py": {},
            "pkg/auth/login.py": {},
            "pkg/author.py": {},
            "pkg/pay.py": {},
            "pkg/migrations/0001_init.py": {},
            "pkg/tokens.py": {},
            "web/src/index.ts": {"language": "typescript"},
            "web/src/lib/index.ts": {"language": "typescript"},
            "tests/test_auth.py": {"is_test": True},
            "examples/auth_demo.py": {},
        },
        external=[("pkg/pay.py", "stripe"), ("pkg/tokens.py", "jwt")],
    )
    out = run(graph, metrics, root=tmp_path)["nodes"]
    assert out["pkg/auth/login.py"]["class"] == "core"
    assert "sensitive:auth" in out["pkg/auth/login.py"]["rules"]
    assert "sensitive:auth" not in out["pkg/author.py"]["rules"]
    assert "sensitive:payments" in out["pkg/pay.py"]["rules"]
    assert "imports package 'stripe'" in " ".join(out["pkg/pay.py"]["reasons"])
    assert "sensitive:auth" in out["pkg/tokens.py"]["rules"]
    assert "sensitive:db_schema" in out["pkg/migrations/0001_init.py"]["rules"]
    assert "sensitive:public_api" in out["pkg/__init__.py"]["rules"]
    assert "sensitive:public_api" not in out["pkg/sub/__init__.py"]["rules"]   # 只有頂層 package
    assert "sensitive:public_api" in out["web/src/index.ts"]["rules"]          # web/package.json 的 src/index
    assert "sensitive:public_api" not in out["web/src/lib/index.ts"]["rules"]
    # 測試與範例不套敏感規則
    assert out["tests/test_auth.py"]["class"] == "leaf" and out["tests/test_auth.py"]["rules"] == ["test_file"]
    assert out["examples/auth_demo.py"]["rules"] == ["example_code"]
    assert out["examples/auth_demo.py"]["percentile"] is None


def test_not_sensitive_and_core_paths():
    graph, metrics = mk({"src/auth_banner.py": {}, "src/plain.py": {}, "tests/test_x.py": {"is_test": True}})
    out = run(graph, metrics, cfg(not_sensitive=["src/auth_banner.py"], core_paths=["src/plain.py", "tests/"]))["nodes"]
    assert not any(r.startswith("sensitive:") for r in out["src/auth_banner.py"]["rules"])
    assert out["src/plain.py"]["rules"] == ["config_core_path"] and out["src/plain.py"]["class"] == "core"
    assert out["tests/test_x.py"]["class"] == "core"   # core_paths 是人工設定，連測試檔也適用


def test_runtime_cycle_vs_type_only_cycle():
    graph, metrics = mk(
        {"a.py": {}, "b.py": {}, "c.py": {}, "d.py": {}},
        edges=[("a.py", "b.py"), ("b.py", "a.py"), ("c.py", "d.py")],
        type_edges=[("d.py", "c.py")],
    )
    out = run(graph, metrics)["nodes"]
    for n in ("a.py", "b.py"):
        assert out[n]["class"] == "core" and out[n]["high_risk"] and "runtime_cycle" in out[n]["rules"]
        assert out[n]["risk_level"] == "HIGH"
    for n in ("c.py", "d.py"):
        assert "runtime_cycle" not in out[n]["rules"] and not out[n]["high_risk"]
        assert any("type-only cycle" in r for r in out[n]["reasons"])


# ---------------------------------------------------------------------------
# 分數與切分
# ---------------------------------------------------------------------------

def chain(n, **kw):
    """m00 ← m01 ← … ← m{n-1}：m00 的 blast radius 最大，m{n-1} 為 0。"""
    ids = [f"m{i:02d}.py" for i in range(n)]
    edges = [(ids[i + 1], ids[i]) for i in range(n - 1)]
    return ids, mk({i: {} for i in ids}, edges=edges, **kw)


def test_percentile_cuts_and_boundaries():
    ids, (graph, metrics) = chain(20)
    out = run(graph, metrics)["nodes"]
    p = {i: out[i]["percentile"] for i in ids}
    assert p["m00.py"] == 97.5 and p["m19.py"] == 2.5
    rule = {i: out[i]["rules"][0] for i in ids}
    assert [rule[i] for i in ids[:3]] == ["score_top", "score_top", "score_boundary"]  # 97.5、92.5 → top；87.5 → 邊界
    assert all(out[i]["class"] == "core" for i in ids[:3])
    # business 是預設類別：不是 core、也不符合 leaf 條件的都是 default
    assert rule["m12.py"] == "default"   # p37.5：在 leaf 門檻 40 的 5 點內 → 不是 leaf → business
    assert out["m12.py"]["class"] == "business"
    assert out["m12.py"]["reasons"][0].startswith("default: not core, not leaf — not leaf because risk p37.5 ≥ leaf cut p35")
    # p < 35 的 m13–m19：blast radius 6..0，只有 ≤ 2 的 m17–m19 能是 leaf
    for i in ids[13:17]:
        assert out[i]["class"] == "business" and out[i]["rules"] == ["default"]
        assert "non-test files depend on it (> 2)" in out[i]["reasons"][0] and "leaf cut" not in out[i]["reasons"][0]
    assert all(out[i]["class"] == "leaf" and rule[i] == "score_low" for i in ids[17:])
    assert all(out[i]["class"] == "business" and out[i]["rules"] == ["default"] for i in ids[3:13])


def test_leaf_blast_guard():
    hub = "hub.py"
    users = [f"u{i}.py" for i in range(3)]
    others = [f"z{i:02d}.py" for i in range(17)]
    graph, metrics = mk({n: {} for n in [hub, *users, *others]}, edges=[(u, hub) for u in users])
    # 門檻放到「全部都是 leaf 候選」：hub 仍因為有 3 個非測試檔依賴它而不能是 leaf
    t = cfg(thresholds={"core_top_percent": 0, "boundary_margin_percent": 0, "leaf_bottom_percent": 100})
    out = run(graph, metrics, t)["nodes"]
    assert out[hub]["rules"] == ["default"] and out[hub]["class"] == "business"
    assert "3 non-test files depend on it" in out[hub]["reasons"][0]
    assert out["z00.py"]["class"] == "leaf"


def test_tests_raise_detectability_not_impact():
    nodes = {"tested.py": {}, "untested.py": {}, "user1.py": {}, "user2.py": {},
             **{f"tests/test_{i}.py": {"is_test": True} for i in range(5)}}
    edges = [("user1.py", "tested.py"), ("user2.py", "untested.py")] + [(f"tests/test_{i}.py", "tested.py") for i in range(5)]
    graph, metrics = mk(nodes, edges=edges)
    out = run(graph, metrics)["nodes"]
    a, b = out["tested.py"]["factors"], out["untested.py"]["factors"]
    assert a["prod_blast_radius"] == b["prod_blast_radius"] == 1      # 測試檔不算進 impact
    assert a["impact"] == b["impact"]
    assert a["test_fan_in"] == 5 and a["test_reach"] == 5 and a["detectability"] > b["detectability"]
    assert out["tested.py"]["risk_score"] < out["untested.py"]["risk_score"]
    # transitive：測試 import user1，user1 import tested → tested 的 test_reach 也算
    graph, metrics = mk({"lib.py": {}, "api.py": {}, "tests/t.py": {"is_test": True}},
                        edges=[("api.py", "lib.py"), ("tests/t.py", "api.py")])
    f = run(graph, metrics)["nodes"]["lib.py"]["factors"]
    assert f["test_fan_in"] == 0 and f["test_reach"] == 1


def test_churn_and_bugfix_raise_score():
    graph, metrics = mk({"a.py": {}, "b.py": {}, "c.py": {}}, history={"a.py": (10, 5), "b.py": (10, 0)})
    out = run(graph, metrics)["nodes"]
    assert out["a.py"]["risk_score"] > out["b.py"]["risk_score"] > out["c.py"]["risk_score"]
    f = out["a.py"]["factors"]
    assert f["impact"] == round(1 * (1 + 0.25 * math.log2(11)), 4)
    assert f["cost_of_failure"] == round(1 + 0.5 * math.log2(6), 4)


def test_parse_error_never_leaf():
    _ids, (graph, metrics) = chain(20)
    out = run(graph, metrics, unresolved={"parse_errors": ["m19.py"]})["nodes"]
    assert out["m19.py"]["class"] == "business" and out["m19.py"]["rules"] == ["default"]
    assert "parse error" in out["m19.py"]["reasons"][0]


def test_source_mismatch_rejected():
    graph, metrics = mk({"a.py": {}})
    metrics["source"] = {"commit": "other", "dirty": False}
    with pytest.raises(C.InputError):
        run(graph, metrics)


# ---------------------------------------------------------------------------
# 覆蓋率
# ---------------------------------------------------------------------------

def test_coverage_formats(tmp_path):
    ids = ["src/app/a.py", "src/app/b.py", "web/x.ts"]
    (tmp_path / "coverage.json").write_text(json.dumps({"files": {
        "src/app/a.py": {"summary": {"covered_lines": 9, "num_statements": 10}},
        str(tmp_path / "src/app/b.py"): {"summary": {"covered_lines": 0, "num_statements": 4}},
        "/elsewhere/not/ours.py": {"summary": {"covered_lines": 1, "num_statements": 1}},
    }}))
    cov, info = __import__("aoa_graph.coverage_input", fromlist=["load"]).load(tmp_path / "coverage.json", tmp_path, ids)
    assert cov == {"src/app/a.py": 0.9, "src/app/b.py": 0.0}
    assert info["format"] == "coverage.py-json" and info["files_unmatched"] == 1
    (tmp_path / "lcov.info").write_text("TN:\nSF:./web/x.ts\nLF:4\nLH:1\nend_of_record\n")
    cov, info = __import__("aoa_graph.coverage_input", fromlist=["load"]).load(tmp_path / "lcov.info", tmp_path, ids)
    assert cov == {"web/x.ts": 0.25} and info["format"] == "lcov"


def test_coverage_lowers_risk():
    graph, metrics = mk({"a.py": {}, "b.py": {}})
    out = run(graph, metrics, coverage={"a.py": 1.0})["nodes"]
    assert out["a.py"]["factors"]["detectability"] == 2.0
    assert out["a.py"]["risk_score"] < out["b.py"]["risk_score"]


# ---------------------------------------------------------------------------
# 覆寫
# ---------------------------------------------------------------------------

def write_overrides(path: Path, entries) -> Path:
    path.write_text("# comment\n\n" + "".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    return path


def test_overrides_stricter_auto_looser_needs_human(tmp_path):
    _ids, (graph, metrics) = chain(20)
    entries = C.load_overrides(write_overrides(tmp_path / "o.jsonl", [
        {"node": "m19.py", "to": "core", "by": "model", "reason": "loads plugins dynamically", "evidence": "m19.py:3"},
        {"node": "m00.py", "to": "leaf", "by": "model", "reason": "looks trivial"},
        {"node": "m01.py", "to": "business", "by": "human", "approved_by": "fredrick", "reason": "generated file"},
        {"node": "gone.py", "to": "core", "by": "model", "reason": "x"},
        {"node": "m05.py", "to": "business", "by": "model", "reason": "same"},
    ]))
    doc = run(graph, metrics, overrides=entries)
    out = doc["nodes"]
    assert out["m19.py"]["computed_class"] == "leaf" and out["m19.py"]["class"] == "core"
    assert out["m19.py"]["overrides"][0]["kind"] == "stricter" and out["m19.py"]["risk_level"] == "MEDIUM"
    assert out["m00.py"]["class"] == "core"                     # 放寬但沒有人工核准 → 不生效
    assert out["m01.py"]["class"] == "business"                 # 人工核准的放寬 → 生效
    assert [o["kind"] for o in doc["overrides"]["applied"]] == ["stricter", "looser_approved"]
    assert [(o["node"], o["kind"]) for o in doc["overrides"]["pending"]] == [("m00.py", "looser_needs_approval")]
    assert {o["why"] for o in doc["overrides"]["ignored"]} == {"node not in graph", "same as computed class"}
    assert doc["summary"]["core"] == doc["summary"]["computed"]["core"]  # +m19（嚴格）、−m01（核准的放寬）


@pytest.mark.parametrize("line", ['{"node": "a.py", "to": "core"', '{"node": "a.py", "to": "critical", "reason": "x"}',
                                  '{"node": "a.py", "to": "core"}'])
def test_overrides_invalid(tmp_path, line):
    (tmp_path / "o.jsonl").write_text(line + "\n")
    with pytest.raises(C.InputError):
        C.load_overrides(tmp_path / "o.jsonl")


# ---------------------------------------------------------------------------
# CLI、設定檔、決定性
# ---------------------------------------------------------------------------

def run_cli(repo: Path, *extra) -> bytes:
    assert cli.main([str(repo)]) == 0
    assert C.main([str(repo), *extra]) == 0
    return (repo / C.DEFAULT_DIR / "nodes.json").read_bytes()


def test_cli_end_to_end_deterministic(tmp_path):
    repo = make_repo("py_repo", tmp_path / "one")
    (repo / ".aoa.toml").write_text('[classify]\nversion = "t-1"\ncore_paths = ["scripts/run.py"]\n')
    first = run_cli(repo)
    for _ in range(4):
        assert run_cli(repo) == first
    other = make_repo("py_repo", tmp_path / "two-other-path")
    (other / ".aoa.toml").write_text('[classify]\nversion = "t-1"\ncore_paths = ["scripts/run.py"]\n')
    assert run_cli(other) == first
    doc = json.loads(first)
    assert str(tmp_path) not in first.decode()
    assert doc["inputs"]["config"]["path"] == ".aoa.toml" and doc["rules_version"]["repo"] == "t-1"
    n = doc["nodes"]
    assert n["scripts/run.py"]["rules"][0] == "config_core_path"
    assert "sensitive:public_api" in n["src/app/__init__.py"]["rules"]
    assert "sensitive:db_schema" in n["src/app/models.py"]["rules"]
    assert n["tests/test_core.py"]["class"] == "leaf"
    assert doc["summary"]["nodes"] == sum(doc["summary"][c] for c in ("core", "business", "leaf"))


def test_cli_dispatch_overrides_and_errors(tmp_path, capsys):
    repo = make_repo("ts_repo", tmp_path)
    assert cli.main([str(repo)]) == 0
    out_dir = repo / C.DEFAULT_DIR
    write_overrides(out_dir / C.OVERRIDES_NAME, [{"node": "src/legacy.js", "to": "core", "by": "model", "reason": "r"}])
    assert cli.main(["classify", str(repo), "--no-config"]) == 0          # aoa-graph classify 轉給 aoa-classify
    doc = json.loads((out_dir / "nodes.json").read_text())
    assert doc["nodes"]["src/legacy.js"]["class"] == "core"
    assert doc["inputs"]["overrides"]["entries"] == 1
    assert "sensitive:public_api" in doc["nodes"]["src/index.ts"]["rules"]
    assert "sensitive:public_api" in doc["nodes"]["packages/shared/src/index.ts"]["rules"]
    (repo / ".aoa.toml").write_text("[classify]\ncore_path = []\n")
    assert C.main([str(repo)]) == 2
    assert "不認得的欄位" in capsys.readouterr().err
    assert C.main([str(tmp_path / "missing")]) == 2
