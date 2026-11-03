from conftest import edge_set


def test_ts_nodes_ignore_node_modules(ts_result):
    ids = [n["id"] for n in ts_result["graph"]["nodes"]]
    assert ids == sorted(ids)
    assert not any("node_modules" in i for i in ids)
    assert "src/s.css" not in ids
    langs = {n["id"]: n["language"] for n in ts_result["graph"]["nodes"]}
    assert langs["src/legacy.js"] == "javascript"
    assert langs["src/component.tsx"] == "typescript"


def test_ts_resolution(ts_result):
    assert edge_set(ts_result) == {
        ("src/index.ts", "src/a.ts"),                 # 相對路徑 + 補副檔名
        ("src/index.ts", "src/types.ts"),             # import type
        ("src/index.ts", "src/util/x.ts"),            # tsconfig paths "@/*"
        ("src/index.ts", "packages/shared/src/index.ts"),  # workspace 套件，main 指向未追蹤的 dist/
        ("src/index.ts", "src/lib/index.ts"),         # export * from 目錄 → index.ts
        ("src/index.ts", "src/lazy.ts"),              # 字面 dynamic import
        ("src/a.ts", "src/b.ts"),                     # "./b.js" → b.ts（TS ESM 慣例）
        ("src/b.ts", "src/c.ts"),
        ("src/c.ts", "src/a.ts"),
        ("src/lib/index.ts", "src/lib/helpers.ts"),
        ("src/legacy.js", "src/lib/helpers.ts"),      # require()
        ("src/component.tsx", "src/lib/index.ts"),    # tsconfig paths 精確比對 "@lib"
        ("src/__tests__/a.test.ts", "src/a.ts"),
    }


def test_ts_edge_kinds(ts_result):
    kinds = {(e["source"], e["target"]): e["kinds"] for e in ts_result["graph"]["edges"]}
    assert kinds[("src/index.ts", "src/types.ts")] == ["type"]
    assert kinds[("src/index.ts", "src/lib/index.ts")] == ["reexport"]
    assert kinds[("src/index.ts", "src/lazy.ts")] == ["dynamic"]
    assert kinds[("src/legacy.js", "src/lib/helpers.ts")] == ["require"]


def test_ts_external_and_unresolved(ts_result):
    ext = {(e["source"], e["package"]) for e in ts_result["graph"]["external"]}
    assert ("src/index.ts", "react") in ext
    assert ("src/index.ts", "node:fs") in ext
    reasons = {(u["specifier"], u["reason"]) for u in ts_result["unresolved"]["items"]}
    assert ("./nope", "not_found") in reasons
    assert ("@ghost/thing", "tsconfig_paths_target_not_found") in reasons
    assert (None, "dynamic_expression") in reasons
    dyn = [u for u in ts_result["unresolved"]["items"] if u["reason"] == "dynamic_expression"]
    assert dyn[0]["expression"] == "import(`./plugins/${name}`)"
    assert ts_result["unresolved"]["parse_errors"] == []


def test_ts_cycle_and_blast_radius(ts_result):
    m = ts_result["metrics"]
    assert m["cycles"] == [{"id": "scc-1", "size": 3, "members": ["src/a.ts", "src/b.ts", "src/c.ts"]}]
    a = m["nodes"]["src/a.ts"]
    assert a["in_cycle"] and a["scc_id"] == "scc-1"
    # a 的依賴者：b、c（同一個循環）+ index.ts + a.test.ts
    assert a["blast_radius"] == 4
    assert a["fan_in"] == 3 and a["fan_out"] == 1 and a["test_fan_in"] == 1
    helpers = m["nodes"]["src/lib/helpers.ts"]
    # lib/index.ts、legacy.js 直接依賴；index.ts、component.tsx 經由 lib/index.ts
    assert helpers["fan_in"] == 2 and helpers["blast_radius"] == 4
    assert m["nodes"]["src/index.ts"]["blast_radius"] == 0
    assert m["nodes"]["src/index.ts"]["fan_out"] == 6
    assert not m["nodes"]["src/lazy.ts"]["in_cycle"]


def test_ts_runtime_cycle_kept_for_value_imports(ts_result):
    m = ts_result["metrics"]
    assert m["runtime_cycles"] == m["cycles"]
    assert m["nodes"]["src/a.ts"]["runtime_scc_id"] == "scc-1"
