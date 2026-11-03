"""[structure]：runtime 循環只取 hub、catalog barrel 不往下傳 blast radius（#7）。"""
import pytest
from aoa_graph import classify as C
from aoa_graph import rules
from test_classify import cfg, mk, run

OLD = {"structure": {"runtime_cycle_core": "all", "barrel_passthrough": "off"}}


def _ring_with_hub(n):
    """n 個檔案：0 ← 每個人都 import 它（hub）；其他人只靠一條環串起來。"""
    ids = [f"m{i}.py" for i in range(n)]
    edges = [(ids[i], ids[i + 1]) for i in range(1, n - 1)] + [(ids[-1], ids[1])]
    edges += [(ids[i], ids[0]) for i in range(1, n)] + [(ids[0], ids[1])]
    return ids, edges


def test_small_cycle_all_members_core():
    graph, metrics = mk({"a.py": {}, "b.py": {}, "c.py": {}},
                        edges=[("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")])
    out = run(graph, metrics)
    for n in ("a.py", "b.py", "c.py"):
        assert out["nodes"][n]["class"] == "core" and "runtime_cycle" in out["nodes"][n]["rules"]
    assert out["summary"]["runtime_cycle_hubs"] == 3


def test_large_cycle_only_hubs_core():
    ids, edges = _ring_with_hub(12)   # 12 個成員 → hub 門檻 max(2, ceil(1.2)) = 2
    graph, metrics = mk({i: {} for i in ids}, edges=edges)
    new = run(graph, metrics)["nodes"]
    old = run(graph, metrics, cfg(**OLD))["nodes"]
    assert new["m0.py"]["class"] == "core" and "runtime_cycle" in new["m0.py"]["rules"]
    assert new["m0.py"]["factors"]["runtime_cycle_fan_in"] == 11
    others = [i for i in ids[2:]]
    for n in others:
        assert "runtime_cycle" not in new[n]["rules"] and not new[n]["high_risk"]
        assert any("not a hub" in r for r in new[n]["reasons"])
        assert old[n]["class"] == "core" and "runtime_cycle" in old[n]["rules"]


def test_hub_threshold_configurable():
    ids, edges = _ring_with_hub(12)
    graph, metrics = mk({i: {} for i in ids}, edges=edges)
    out = run(graph, metrics, cfg(structure={"cycle_hub_all_max_size": 20}))["nodes"]
    assert all("runtime_cycle" in out[i]["rules"] for i in ids)


def _barrel_graph(internal_edges=()):
    """index.ts re-export 5 個 locale；app.ts 與 5 個 consumer import index.ts。"""
    locs = [f"locales/l{i}.ts" for i in range(5)]
    nodes = {p: {"language": "typescript"} for p in [*locs, "locales/index.ts", "app.ts"]}
    consumers = [f"c{i}.ts" for i in range(5)]
    nodes.update({c: {"language": "typescript"} for c in consumers})
    edges = [("locales/index.ts", l) for l in locs] + [("app.ts", "locales/index.ts")]
    edges += [(c, "app.ts") for c in consumers] + list(internal_edges)
    graph, metrics = mk(nodes, edges=edges)
    for e in graph["edges"]:
        if e["source"] == "locales/index.ts":
            e["kinds"] = ["reexport"]
    return graph, metrics, locs


def test_catalog_barrel_does_not_pass_blast_radius():
    graph, metrics, locs = _barrel_graph()
    new = run(graph, metrics)
    old = run(graph, metrics, cfg(**OLD))
    assert new["summary"]["barrels"] == {"barrel": 0, "catalog": 1}
    assert new["summary"]["barrel_edges_cut"] == 5
    for l in locs:
        assert new["nodes"][l]["factors"]["prod_blast_radius"] == 0
        assert old["nodes"][l]["factors"]["prod_blast_radius"] == 7   # index + app + 5 consumers
    # barrel 本身照常算：它的 dependents 沒變
    assert new["nodes"]["locales/index.ts"]["factors"]["prod_blast_radius"] == 6


def test_interdependent_barrel_is_not_catalog():
    edges = [("locales/l0.ts", "locales/l1.ts"), ("locales/l2.ts", "locales/l1.ts")]
    graph, metrics, _ = _barrel_graph(edges)
    out = run(graph, metrics)
    assert out["summary"]["barrels"] == {"barrel": 1, "catalog": 0}
    assert out["nodes"]["locales/l3.ts"]["factors"]["prod_blast_radius"] == 7
    cut_all = run(graph, metrics, cfg(structure={"barrel_passthrough": "all"}))
    assert cut_all["nodes"]["locales/l3.ts"]["factors"]["prod_blast_radius"] == 0


def test_barrel_cuts_tolerates_one_alias():
    graph, _, _ = _barrel_graph()
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = graph["edges"] + [{"source": "locales/l0.ts", "target": "locales/l1.ts", "kinds": ["static"], "count": 1}]
    cuts, barrels = C.barrel_cuts(nodes, edges, "catalog", 3, 0.2)
    assert barrels["locales/index.ts"]["kind"] == "catalog" and len(cuts) == 5
    cuts, barrels = C.barrel_cuts(nodes, edges, "catalog", 3, 0.0)
    assert barrels["locales/index.ts"]["kind"] == "barrel" and not cuts


def test_python_files_never_barrels():
    graph, _, _ = _barrel_graph()
    for n in graph["nodes"]:
        n["language"] = "python"
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert C.barrel_cuts(nodes, graph["edges"], "all", 3) == (set(), {})


@pytest.mark.parametrize("extra,msg", [
    ({"structure": {"runtime_cycle_core": "some"}}, "runtime_cycle_core"),
    ({"structure": {"barrel_passthrough": True}}, "barrel_passthrough"),
    ({"structure": {"barrel_min_entries": -1}}, "barrel_min_entries"),
    ({"structure": {"nope": 1}}, "nope"),
    ({"structure": 3}, "table"),
])
def test_structure_validation(extra, msg):
    with pytest.raises(rules.ConfigError, match=msg):
        rules._validate(extra, "x")


def test_structure_merge_is_per_key():
    c = rules.merge(rules.load_default(), {"structure": {"barrel_passthrough": "off"}})
    assert c["structure"]["barrel_passthrough"] == "off"
    assert c["structure"]["runtime_cycle_core"] == "hubs"
