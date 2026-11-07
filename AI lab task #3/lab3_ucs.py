"""Lab 3, Task 3: Uniform Cost Search on a weighted version of the graph.
The weights are my own choice (the manual does not list them); they are chosen so that
A->B->E->G costs 3 and A->C->G costs 12, as described in section 3.7.
C -> G is an ADDED corridor, it is not in the original manual graph.
Queue entries: (cost, insertion_counter, node, path); ties go to the entry inserted first.
Counting: goal processing is included in the processed list."""
import heapq
from collections import deque

WEIGHTED = {
    "A": [("B", 1), ("C", 5)],
    "B": [("D", 4), ("E", 1)],
    "C": [("F", 3), ("G", 7)],     # C -> G is the added corridor
    "D": [], "E": [("G", 1)], "F": [], "G": [],
}


def check_weights(g):
    for u in g:
        for v, w in g[u]:
            if w < 0:
                raise ValueError(f"negative weight on {u}->{v}: UCS needs non-negative costs")


def ucs(g, start, goal):
    check_weights(g)
    counter = 0
    pq = [(0, counter, start, [start])]
    best = {start: 0}
    processed, stale = [], 0
    while pq:
        cost, _, node, path = heapq.heappop(pq)
        if cost != best[node]:
            stale += 1
            continue
        processed.append((node, cost))
        if node == goal:
            return cost, path, processed, stale
        for nxt, w in g.get(node, []):
            nc = cost + w
            if nc < best.get(nxt, float("inf")):
                best[nxt] = nc
                counter += 1
                heapq.heappush(pq, (nc, counter, nxt, path + [nxt]))
    return None, None, processed, stale


def bfs_topology(g, start, goal):
    """BFS on the same graph, ignoring weights (fewest edges)."""
    q = deque([(start, [start])]); seen = {start}; order = []
    while q:
        node, path = q.popleft()
        order.append(node)
        if node == goal:
            return path, order
        for nxt, _ in g.get(node, []):
            if nxt not in seen:
                seen.add(nxt); q.append((nxt, path + [nxt]))
    return None, order


def path_cost(g, path):
    return sum(dict(g[u])[v] for u, v in zip(path, path[1:]))


if __name__ == "__main__":
    print("== Weighted graph (edge: weight)")
    for u in WEIGHTED:
        for v, w in WEIGHTED[u]:
            print(f"  {u} -> {v}: {w}", "(added corridor)" if (u, v) == ("C", "G") else "")
    print()
    cost, path, processed, stale = ucs(WEIGHTED, "A", "G")
    print("== UCS")
    print("path:", path, "| returned cost:", cost, "| independent sum:", path_cost(WEIGHTED, path), "| hops:", len(path) - 1)
    print("processing order (node, cost):", processed, "| stale entries:", stale)
    bpath, border = bfs_topology(WEIGHTED, "A", "G")
    print("\n== BFS on the same topology")
    print("path:", bpath, "| independent cost:", path_cost(WEIGHTED, bpath), "| hops:", len(bpath) - 1)
    print("processing order:", border)

    print("\n== Edge cases")
    print("start == goal :", ucs(WEIGHTED, "A", "A")[:2])
    g2 = dict(WEIGHTED); g2["H"] = []
    r = ucs(g2, "A", "H")
    print("unreachable H :", r[0], r[1], "| nodes processed:", [n for n, _ in r[2]])
    cyc = {"A": [("B", 1)], "B": [("A", 1), ("C", 2)], "C": []}
    print("cycle graph   :", ucs(cyc, "A", "C")[:2])
    bad = {"A": [("B", 2)], "B": [("C", -5)], "C": []}
    try:
        ucs(bad, "A", "C")
    except ValueError as e:
        print("negative edge :", e)
