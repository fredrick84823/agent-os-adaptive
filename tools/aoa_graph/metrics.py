"""圖指標：fan-in / fan-out、SCC（Tarjan）、blast radius（遞移依賴者數）。

邊的方向是 importer → imported。blast radius(X) = 能沿著邊走到 X 的其他節點數，
也就是「改了 X，可能被波及的模組數」。
"""
from __future__ import annotations


def tarjan_scc(nodes: list[str], adj: dict[str, list[str]]) -> list[list[str]]:
    """迭代版 Tarjan。回傳 SCC 清單，順序為反向拓樸序（被依賴者先出）。"""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    out: list[list[str]] = []
    counter = 0
    for start in nodes:
        if start in index:
            continue
        work = [(start, 0)]
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            v, i = work[-1]
            succ = adj.get(v, [])
            if i < len(succ):
                work[-1] = (v, i + 1)
                w = succ[i]
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, 0))
                elif w in on_stack:
                    low[v] = min(low[v], index[w])
                continue
            work.pop()
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                out.append(sorted(comp))
    return out


def _cycles(nodes: list[str], edges: list[tuple[str, str]]) -> tuple[list[dict], dict[str, str]]:
    """大小 > 1 的 SCC，依最小成員排序後編號 scc-1、scc-2…（編號與走訪順序無關）。"""
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for s, t in edges:
        adj[s].append(t)
    for n in nodes:
        adj[n].sort()
    cyclic = sorted((c for c in tarjan_scc(nodes, adj) if len(c) > 1), key=lambda c: c[0])
    cycles, member = [], {}
    for k, comp in enumerate(cyclic, 1):
        cid = f"scc-{k}"
        cycles.append({"id": cid, "size": len(comp), "members": comp})
        for n in comp:
            member[n] = cid
    return cycles, member


def compute(
    nodes: list[str],
    edges: list[tuple[str, str]],
    is_test: dict[str, bool],
    runtime_edges: list[tuple[str, str]] | None = None,
) -> tuple[dict, list[dict], list[dict]]:
    """回傳 (每個節點的圖指標, cycles, runtime_cycles)。nodes 必須已排序，edges 不含自我迴圈。

    runtime_edges：排除「只有型別引用」的邊（TS `import type`、Python `if TYPE_CHECKING:`），
    用來判斷執行期是否真的有循環。
    """
    runtime_cycles, runtime_member = _cycles(nodes, runtime_edges if runtime_edges is not None else edges)
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    radj: dict[str, list[str]] = {n: [] for n in nodes}
    for s, t in edges:
        adj[s].append(t)
        radj[t].append(s)
    for n in nodes:
        adj[n].sort()
        radj[n].sort()

    sccs = tarjan_scc(nodes, adj)
    comp_of: dict[str, int] = {}
    for ci, comp in enumerate(sccs):
        for n in comp:
            comp_of[n] = ci

    cycles, scc_id = _cycles(nodes, edges)

    # 反向可達集合：以節點索引的 bitset（Python int）累積，依拓樸序（依賴者先）傳遞
    bit = {n: 1 << i for i, n in enumerate(nodes)}
    comp_mask = [0] * len(sccs)
    for ci, comp in enumerate(sccs):
        for n in comp:
            comp_mask[ci] |= bit[n]
    reach = [0] * len(sccs)  # 依賴此 SCC 的所有節點（不含 SCC 本身）
    for ci in range(len(sccs) - 1, -1, -1):  # Tarjan 輸出是反拓樸序 → 倒著走就是依賴者先
        acc = 0
        for n in sccs[ci]:
            for d in radj[n]:
                dc = comp_of[d]
                if dc != ci:
                    acc |= comp_mask[dc] | reach[dc]
        reach[ci] = acc

    per_node = {}
    for n in nodes:
        ci = comp_of[n]
        blast = (reach[ci] | comp_mask[ci]).bit_count() - 1
        per_node[n] = {
            "fan_in": len(radj[n]),
            "fan_out": len(adj[n]),
            "test_fan_in": sum(1 for d in radj[n] if is_test.get(d)),
            "blast_radius": blast,
            "in_cycle": n in scc_id,
            "scc_id": scc_id.get(n),
            "in_runtime_cycle": n in runtime_member,
            "runtime_scc_id": runtime_member.get(n),
        }
    return per_node, cycles, runtime_cycles
