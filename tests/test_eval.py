"""aoa-eval：指標計算、標註檔、gate 與端到端 CLI（#7）。"""
import json
import subprocess

import pytest
from aoa_eval import cli, labels, pipeline, scoring
from aoa_eval.report import gates
from aoa_eval.repos import EvalError, load_repos
from conftest import DAY, make_repo

# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------

def test_perfect_agreement():
    pairs = [("core", "core"), ("business", "business"), ("leaf", "leaf")] * 3
    s = scoring.score(pairs)
    assert s["accuracy"] == 1.0 and s["kappa"] == 1.0 and s["weighted_kappa"] == 1.0
    assert s["cost_total"] == 0 and s["core_to_leaf"] == 0


def test_kappa_known_value():
    # 2×2 教科書例：20 yes/yes、5 yes/no、10 no/yes、15 no/no → po=0.7, pe=0.5, κ=0.4
    pairs = [("core", "core")] * 20 + [("core", "leaf")] * 5 + [("leaf", "core")] * 10 + [("leaf", "leaf")] * 15
    s = scoring.score(pairs)
    assert s["kappa"] == pytest.approx(0.4)
    assert s["core_to_leaf"] == 5 and s["under_classified"] == 5 and s["over_classified"] == 10


def test_chance_level_kappa_zero():
    pairs = [("core", "core"), ("core", "leaf"), ("leaf", "core"), ("leaf", "leaf")]
    assert scoring.score(pairs)["kappa"] == pytest.approx(0.0)


def test_weighted_kappa_penalises_distance():
    near = scoring.score([("core", "business"), ("business", "business"), ("leaf", "leaf"), ("core", "core")])
    far = scoring.score([("core", "leaf"), ("business", "business"), ("leaf", "leaf"), ("core", "core")])
    assert near["weighted_kappa"] > far["weighted_kappa"]


def test_asymmetric_cost_and_per_class():
    s = scoring.score([("core", "leaf"), ("leaf", "core")])
    assert s["cost_total"] == scoring.COST["core"]["leaf"] + scoring.COST["leaf"]["core"]
    assert scoring.COST["core"]["leaf"] > scoring.COST["core"]["business"] > scoring.COST["leaf"]["business"]
    pc = scoring.score([("core", "core"), ("core", "business"), ("business", "business")])["per_class"]
    assert pc["core"]["recall"] == 0.5 and pc["core"]["precision"] == 1.0
    assert pc["business"]["precision"] == 0.5 and pc["leaf"]["support"] == 0


def test_degenerate_kappa():
    assert scoring.score([("core", "core")] * 3)["kappa"] == 1.0   # 全部同類且全對
    assert scoring.score([("core", "leaf")] * 3)["kappa"] == 0.0   # 沒有任何一致
    assert scoring.score([])["kappa"] is None


# ---------------------------------------------------------------------------
# labels / repos.toml
# ---------------------------------------------------------------------------

def test_labels_loader(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('# comment\n{"path": "a.py", "label": "core", "rationale": "everything imports it"}\n\n')
    assert [e["path"] for e in labels.load(p)] == ["a.py"]


@pytest.mark.parametrize("body,msg", [
    ('{"path": "a.py", "label": "critical", "rationale": "r"}', "label"),
    ('{"path": "a.py", "label": "core"}', "rationale"),
    ('{"path": "a.py", "label": "core", "rationale": "r"}\n{"path": "a.py", "label": "leaf", "rationale": "r"}', "重複"),
    ("not json", "JSON"),
    ("# only comments", "沒有"),
])
def test_labels_loader_rejects(tmp_path, body, msg):
    p = tmp_path / "x.jsonl"
    p.write_text(body)
    with pytest.raises(EvalError, match=msg):
        labels.load(p)


def test_shipped_labels_and_repos_are_valid():
    specs = load_repos()
    assert {"flask", "httpx", "zod"} <= {s.name for s in specs}
    for s in specs:
        assert len(s.commit) == 40
        entries = labels.load(cli.DEFAULT_LABELS / f"{s.name}.jsonl")
        assert 30 <= len(entries) <= 80
        assert {e["label"] for e in entries} == set(scoring.CLASSES)


def test_repos_toml_requires_full_sha(tmp_path):
    p = tmp_path / "r.toml"
    p.write_text('[[repo]]\nname = "x"\nurl = "u"\ncommit = "abc123"\n')
    with pytest.raises(EvalError, match="40"):
        load_repos(p)


def test_gates():
    ok = {"repo": "r", "determinism": {"ok": True},
          "variants": {"current": {"accuracy": {"all": {"core_to_leaf": 0, "kappa": 0.5}, "core_to_leaf_paths": []}}}}
    bad = {"repo": "r", "determinism": {"ok": False},
           "variants": {"current": {"accuracy": {"all": {"core_to_leaf": 1, "kappa": 0.1}, "core_to_leaf_paths": ["a.py"]}}}}
    assert gates([ok], "current", None) == []
    assert gates([ok], "current", 0.6) == ["r: kappa 0.500 < 0.6"]
    fails = gates([bad], "current", None)
    assert len(fails) == 2 and "a.py" in fails[0]


# ---------------------------------------------------------------------------
# 端到端：fixture repo → aoa-eval run
# ---------------------------------------------------------------------------

@pytest.fixture
def eval_env(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    history = [(-3 * DAY, "fix: core bug", ["src/app/core.py"]),
               (-2 * DAY, "feat: db", ["src/app/db.py"]),
               (-DAY, "fix: models", ["src/app/models.py", "src/app/core.py"]),
               (0, "chore: utils", ["src/app/utils.py"])]
    repo = make_repo("py_repo", cache, history)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    repos = tmp_path / "repos.toml"
    repos.write_text(f'[defaults]\nstability_commits = 2\nreplay_days = 2\n\n'
                     f'[[repo]]\nname = "py_repo"\nurl = "file:///unused"\ncommit = "{head}"\n')
    a = pipeline.analyze(repo, {"current": {}})
    predicted = pipeline.classes(a["nodes"]["current"])
    lab = tmp_path / "labels"
    lab.mkdir()
    return {"tmp": tmp_path, "cache": cache, "repos": repos, "labels": lab, "predicted": predicted}


def _write_labels(env, entries):
    (env["labels"] / "py_repo.jsonl").write_text(
        "".join(json.dumps({"path": p, "label": c, "rationale": "test"}) + "\n" for p, c in entries))


def _run(env, out, *extra):
    return cli.main(["run", "--repos-file", str(env["repos"]), "--labels-dir", str(env["labels"]),
                     "--cache-dir", str(env["cache"]), "--no-fetch", "--out", str(out), "--replay", *extra])


def test_cli_end_to_end_pass_and_deterministic(eval_env):
    env = eval_env
    _write_labels(env, sorted(env["predicted"].items()))
    assert _run(env, env["tmp"] / "o1") == 0
    assert _run(env, env["tmp"] / "o2") == 0
    j1 = (env["tmp"] / "o1" / "report.json").read_bytes()
    assert j1 == (env["tmp"] / "o2" / "report.json").read_bytes()
    doc = json.loads(j1)
    r = doc["results"][0]
    assert r["determinism"]["ok"]
    cur = r["variants"]["current"]
    assert cur["accuracy"]["all"]["accuracy"] == 1.0
    assert set(r["variants"]) == set(cli.VARIANTS)
    assert len(cur["stability"]["pairs"]) == 2
    assert "replay" in cur
    md = (env["tmp"] / "o1" / "report.md").read_text()
    assert "PASS" in md and "尚未經人工複核" in md
    assert str(env["tmp"]) not in md and str(env["tmp"]) not in j1.decode()


def test_cli_core_to_leaf_fails_run(eval_env, capsys):
    env = eval_env
    leaf = min(p for p, c in env["predicted"].items() if c == "leaf")
    _write_labels(env, [(p, "core" if p == leaf else c) for p, c in sorted(env["predicted"].items())])
    assert _run(env, env["tmp"] / "o", "--no-stability", "--variants", "current") == 1
    assert "core→leaf" in capsys.readouterr().err
    doc = json.loads((env["tmp"] / "o" / "report.json").read_text())
    assert doc["gate_failures"] and leaf in doc["gate_failures"][0]


def test_cli_missing_cache_with_no_fetch(eval_env, tmp_path):
    env = eval_env
    rc = cli.main(["run", "--repos-file", str(env["repos"]), "--labels-dir", str(env["labels"]),
                   "--cache-dir", str(tmp_path / "empty"), "--no-fetch", "--out", str(tmp_path / "o")])
    assert rc == 2


def test_cli_sample_prints_paths_only(eval_env, capsys):
    env = eval_env
    rc = cli.main(["sample", "py_repo", "--repos-file", str(env["repos"]), "--labels-dir", str(env["labels"]),
                   "--cache-dir", str(env["cache"]), "--no-fetch", "--per-class", "1", "--non-ranked", "1"])
    assert rc == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert rows and all(set(r) == {"path"} for r in rows)
