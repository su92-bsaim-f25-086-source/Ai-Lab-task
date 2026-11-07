"""
Lab 4 - Informed Search: Heuristics & A*
CAI601400 Artificial Intelligence Lab | Rasikh Ali (42365)

What this script does
  1. Audits the supplied heuristic (admissibility + consistency).
  2. Runs A* with a full trace (g, h, f, frontier) on the S-A-B-C-G campus graph.
  3. Runs the zero-heuristic UCS control with the SAME function and tie-breaking.
  4. Runs the single-value overestimate experiments (h(C)=10 and h(B)=10).
  5. Runs edge-case tests (unreachable goal, missing heuristic, negative cost,
     stale queue entry, start == goal).

Run:    python lab4_astar_audit.py > lab4_output.txt
Needs:  Python 3.8+ (standard library only, no random numbers -> reproducible)

Queue tie-breaking: heap entries are tuples (f, g, node, path), so Python
compares f first, then g (smaller g first), then node name (alphabetical),
then path. Successors are examined in the order stored in the graph.

Expansion counting: a node counts as expanded only when its successors are
examined. Popping the goal is logged but NOT counted. Stale queue entries are
skipped and NOT counted.

Adapted from the A* skeleton in the CAI601400 Lab 4 manual (section 4.2).
"""
import heapq

INF = float("inf")

GRAPH = {
    "S": [("A", 1), ("B", 4)],
    "A": [("C", 2)],
    "B": [("G", 5)],
    "C": [("G", 3)],
    "G": [],
}
H = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}
START, GOAL = "S", "G"


# ---------------------------------------------------------------------------
# 1. Supplied lab code (unchanged) - kept only to demonstrate its edge cases
# ---------------------------------------------------------------------------
def astar_supplied(graph, h, start, goal):
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    while pq:
        f, g, node, path = heapq.heappop(pq)
        if node == goal:
            return g, path
        if g != best[node]:
            continue
        for nxt, w in graph.get(node, []):
            ng = g + w
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------
def validate_inputs(graph, h, start, goal):
    """Fail early with a clear message instead of a KeyError deep in the loop."""
    nodes = set(graph) | {v for edges in graph.values() for v, _ in edges}
    nodes |= {start, goal}
    missing = sorted(n for n in nodes if n not in h)
    if missing:
        raise ValueError(f"heuristic value missing for node(s): {missing}")
    for u, edges in graph.items():
        for v, w in edges:
            if w < 0:
                raise ValueError(f"negative edge cost {u}->{v}: {w}")
    for n, val in h.items():
        if val < 0:
            raise ValueError(f"negative heuristic value at {n}: {val}")


def path_cost(graph, path):
    """Independent check: add up the edge weights along a returned path."""
    total = 0
    for u, v in zip(path, path[1:]):
        total += dict(graph[u])[v]
    return total


def true_remaining_costs(graph, goal):
    """h*(n): exact cheapest cost from n to the goal (Dijkstra on reversed graph)."""
    rev = {}
    for u, edges in graph.items():
        for v, w in edges:
            rev.setdefault(v, []).append((u, w))
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist.get(n, INF):
            continue
        for p, w in rev.get(n, []):
            nd = d + w
            if nd < dist.get(p, INF):
                dist[p] = nd
                heapq.heappush(pq, (nd, p))
    return dist


def audit(graph, h, goal):
    """Return admissibility rows and consistency rows for a heuristic."""
    true_h = true_remaining_costs(graph, goal)
    adm = [(n, h[n], true_h.get(n, INF), h[n] <= true_h.get(n, INF)) for n in h]
    con = []
    for u, edges in graph.items():
        for v, w in edges:
            con.append((u, v, w, h[u], w + h[v], h[u] <= w + h[v]))
    return adm, con


def print_audit(graph, h, goal):
    adm, con = audit(graph, h, goal)
    print("Admissibility: h(n) <= true remaining cost h*(n)")
    print(f"  {'node':<6}{'h(n)':<7}{'h*(n)':<8}{'gap':<6}result")
    for n, hv, tv, ok in adm:
        print(f"  {n:<6}{hv:<7}{tv:<8}{tv - hv:<6}{'PASS' if ok else 'FAIL'}")
    print("Consistency: h(u) <= c(u,v) + h(v) for every directed edge")
    print(f"  {'edge':<8}{'c':<4}{'h(u)':<7}{'c+h(v)':<12}result")
    for u, v, w, hu, rhs, ok in con:
        rhs_txt = f"{w}+{h[v]}={rhs}"
        print(f"  {u + '->' + v:<8}{w:<4}{hu:<7}{rhs_txt:<12}{'PASS' if ok else 'FAIL'}")
    return adm, con


def fmt_frontier(pq, best):
    live = sorted((f, g, n) for f, g, n, _ in pq if g == best[n])
    return ", ".join(f"{n}(g={g},f={f})" for f, g, n in live) or "(empty)"


# ---------------------------------------------------------------------------
# 3. Instrumented A* (UCS = same function with every h equal to 0)
# ---------------------------------------------------------------------------
def astar(graph, h, start, goal):
    validate_inputs(graph, h, start, goal)
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    out = {"found": False, "cost": INF, "path": [], "expanded": [],
           "records": [], "popped": [], "pushes": 1, "pops": 0, "stale": 0,
           "trace": []}
    t = out["trace"]
    t.append(f"start: push {start} with g=0, h={h[start]}, f={h[start]}")
    while pq:
        f, g, node, path = heapq.heappop(pq)
        out["pops"] += 1
        out["popped"].append(node)
        if node == goal:
            t.append(f"POP {node}: g={g}, h={h[node]}, f={f} -> GOAL "
                     f"(logged, not counted as expansion)")
            out.update(found=True, cost=g, path=path)
            return out
        if g != best[node]:
            out["stale"] += 1
            t.append(f"POP {node}: g={g}, h={h[node]}, f={f} -> STALE "
                     f"(best g is {best[node]}), skipped")
            continue
        out["expanded"].append(node)
        out["records"].append((node, g, h[node], f))
        t.append(f"POP {node}: g={g}, h={h[node]}, f={g}+{h[node]}={f} "
                 f"-> EXPAND #{len(out['expanded'])}")
        for nxt, w in graph.get(node, []):
            ng = g + w
            if ng < best.get(nxt, INF):
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))
                out["pushes"] += 1
                t.append(f"    successor {nxt}: g={g}+{w}={ng}, h={h[nxt]}, "
                         f"f={ng}+{h[nxt]}={ng + h[nxt]} -> pushed")
            else:
                t.append(f"    successor {nxt}: g={g}+{w}={ng} is not better "
                         f"than best g={best[nxt]} -> ignored")
        t.append(f"    frontier now: {fmt_frontier(pq, best)}")
    t.append("frontier empty -> goal is not reachable")
    return out


def show_run(title, res, graph):
    print(f"\n--- {title} ---")
    for line in res["trace"]:
        print(line)
    if res["found"]:
        print(f"returned path : {' -> '.join(res['path'])}")
        print(f"returned cost : {res['cost']}")
        print(f"summed cost   : {path_cost(graph, res['path'])} "
              f"(independent sum of edge weights)")
    else:
        print("returned path : none (goal not reachable)")
    print(f"popped order  : {','.join(res['popped'])}")
    print(f"expanded nodes: {','.join(res['expanded']) or '(none)'} "
          f"-> expansion count = {len(res['expanded'])}")
    print(f"queue pushes = {res['pushes']}, pops = {res['pops']}, "
          f"stale entries skipped = {res['stale']}")


def summary_table(rows, graph):
    print(f"{'run':<16}{'path':<10}{'cost':<6}{'summed':<8}"
          f"{'popped (in order)':<20}{'expanded':<14}count")
    for label, res in rows:
        found = res["found"]
        path = "-".join(res["path"]) if found else "none"
        cost = res["cost"] if found else "-"
        summed = path_cost(graph, res["path"]) if found else "-"
        print(f"{label:<16}{path:<10}{cost:<6}{summed:<8}"
              f"{','.join(res['popped']):<20}{','.join(res['expanded']):<14}"
              f"{len(res['expanded'])}")


def banner(text):
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


# ---------------------------------------------------------------------------
# 4. Experiments
# ---------------------------------------------------------------------------
def main():
    zero = {n: 0 for n in H}

    banner("INPUTS")
    print("Directed weighted graph (edge cost = travel-time units):")
    for u, edges in GRAPH.items():
        print(f"  {u}: {edges}")
    print(f"Start = {START}, Goal = {GOAL}")
    print(f"Supplied heuristic h = {H}")
    r1 = path_cost(GRAPH, ["S", "A", "C", "G"])
    r2 = path_cost(GRAPH, ["S", "B", "G"])
    print(f"Complete routes: S-A-C-G costs {r1}; S-B-G costs {r2}")

    banner("HEURISTIC AUDIT (supplied h)")
    adm, con = print_audit(GRAPH, H, GOAL)
    print(f"All admissible: {all(r[3] for r in adm)} | "
          f"All consistent: {all(r[5] for r in con)}")

    banner("TASK 1 - A* TRACE WITH g, h, f (supplied heuristic)")
    res_a = astar(GRAPH, H, START, GOAL)
    show_run("A* with supplied heuristic", res_a, GRAPH)
    expected = [("S", 0, 5, 5), ("A", 1, 4, 5), ("C", 3, 2, 5)]
    ok = res_a["records"][:3] == expected
    print(f"Cross-check with hand calculation (S, A, C): "
          f"{'PASS' if ok else 'FAIL'}")

    banner("TASK 2 - A* vs UCS (same graph, same code; UCS uses h = 0)")
    res_u = astar(GRAPH, zero, START, GOAL)
    show_run("UCS control (all h = 0)", res_u, GRAPH)
    print("\n--- Comparison table (task 2) ---")
    summary_table([("A* (supplied h)", res_a), ("UCS (h = 0)", res_u)], GRAPH)
    saved = len(res_u["expanded"]) - len(res_a["expanded"])
    print(f"Expansions saved by A*: {saved} "
          f"({saved / len(res_u['expanded']):.0%} fewer on this graph)")

    banner("TASK 3 - SINGLE-VALUE OVERESTIMATE EXPERIMENTS")
    true_h = true_remaining_costs(GRAPH, GOAL)
    runs = [("A* (original h)", res_a)]
    for node, new in (("C", 10), ("B", 10)):
        h2 = dict(H)
        h2[node] = new
        print(f"\nChange only h({node}): {H[node]} -> {new}; "
              f"true remaining cost h*({node}) = {true_h[node]}; "
              f"overestimate by {new - true_h[node]}")
        adm2, con2 = audit(GRAPH, h2, GOAL)
        bad_adm = [r[0] for r in adm2 if not r[3]]
        bad_con = [r[0] + "->" + r[1] for r in con2 if not r[5]]
        print(f"Admissibility violated at: {bad_adm}")
        print(f"Consistency violated on  : {bad_con}")
        res = astar(GRAPH, h2, START, GOAL)
        show_run(f"A* with h({node}) = {new}", res, GRAPH)
        runs.append((f"A* h({node})={new}", res))
    print("\n--- Comparison table (task 3) ---")
    summary_table(runs, GRAPH)
    print(f"Optimal cost on this graph = {true_h[START]}")

    banner("EDGE CASES AND FAILURE INVESTIGATION")

    print("\n--- E1: goal unreachable (isolated node Z used as the goal) ---")
    g1 = dict(GRAPH)
    g1["Z"] = []
    h1 = dict(H)
    h1["Z"] = 0
    out = astar_supplied(g1, h1, "S", "Z")
    print(f"supplied code returned: {out!r}")
    try:
        cost, path = out
    except TypeError as e:
        print("caller line 'cost, path = result' then fails with:")
        print(f"  TypeError: {e}")
    res = astar(g1, h1, "S", "Z")
    print(f"improved code: found={res['found']}, cost={res['cost']}, "
          f"path={res['path']}")
    print(f"improved code: expanded={','.join(res['expanded'])} "
          f"(count {len(res['expanded'])}), reports 'not reachable'")

    print("\n--- E2: heuristic value missing for node D ---")
    g2 = {"S": [("A", 1), ("B", 4)], "A": [("C", 2), ("D", 1)],
          "B": [("G", 5)], "C": [("G", 3)], "D": [("G", 1)], "G": []}
    for label, fn in (("supplied code", astar_supplied), ("improved code", astar)):
        try:
            fn(g2, H, "S", "G")
        except Exception as e:
            print(f"{label}: {type(e).__name__}: {e}")

    print("\n--- E3: negative edge cost B->G = -5 ---")
    g3 = {"S": [("A", 1), ("B", 4)], "A": [("C", 2)], "B": [("G", -5)],
          "C": [("G", 3)], "G": []}
    try:
        astar(g3, H, "S", "G")
    except Exception as e:
        print(f"improved code: {type(e).__name__}: {e}")

    g4 = {"S": [("A", 5), ("B", 1)], "B": [("A", 1)], "A": [("G", 10)], "G": []}
    h4 = {"S": 0, "A": 0, "B": 0, "G": 0}
    res4 = astar(g4, h4, "S", "G")
    show_run("E4: stale queue entry (A first reached at g=5, later at g=2)",
             res4, g4)

    res5 = astar(GRAPH, H, "G", "G")
    show_run("E5: start equals goal", res5, GRAPH)

    banner("SUMMARY OF MEASURED RESULTS")
    print(f"A* (supplied h): cost {res_a['cost']}, "
          f"expanded {len(res_a['expanded'])}")
    print(f"UCS (h = 0)    : cost {res_u['cost']}, "
          f"expanded {len(res_u['expanded'])}")
    for label, res in runs[1:]:
        print(f"{label:<15}: cost {res['cost']}, "
              f"expanded {len(res['expanded'])}")


if __name__ == "__main__":
    main()
