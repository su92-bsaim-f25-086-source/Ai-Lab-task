"""Lab 3, Task 2: Depth-Limited Search (DLS) and Iterative Deepening (IDDFS).
Depth counts edges, so the start node has depth 0.
Statuses: FOUND, CUTOFF (a deeper unexplored continuation exists), FAILURE (branch exhausted).
Cycle check is path-local (a node is skipped only if it is already on the current path).
No global visited set is shared across limits.
Counting: every node that is entered is logged, and the goal counts when it is reached."""

graph = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["G"], "F": [], "G": []}


def dls(g, node, goal, limit, path, log):
    log.append(node)
    if node == goal:
        return "FOUND", path
    if len(path) - 1 == limit:            # depth of node = edges used so far
        if any(n not in path for n in g.get(node, [])):
            return "CUTOFF", None         # deeper unexplored continuation exists
        return "FAILURE", None
    cutoff = False
    for n in g.get(node, []):
        if n in path:                     # path-local cycle check
            continue
        status, res = dls(g, n, goal, limit, path + [n], log)
        if status == "FOUND":
            return status, res
        if status == "CUTOFF":
            cutoff = True
    return ("CUTOFF" if cutoff else "FAILURE"), None


def run_dls(g, start, goal, limit):
    log = []
    status, path = dls(g, start, goal, limit, [start], log)
    return status, path, log


def iddfs(g, start, goal, max_depth):
    attempted, total_visits, status, path = [], 0, None, None
    for limit in range(0, max_depth + 1):
        status, path, log = run_dls(g, start, goal, limit)
        attempted.append(limit)
        total_visits += len(log)
        if status == "FOUND":
            return status, path, attempted, total_visits
        if status == "FAILURE":           # whole graph exhausted, deeper limits are pointless
            break
    return status, path, attempted, total_visits


if __name__ == "__main__":
    print("== DLS on the original graph, start A, goal G")
    for limit in (1, 2, 3, 4):
        status, path, log = run_dls(graph, "A", "G", limit)
        print(f"limit {limit}: {status:7s} path={path} nodes entered={log} (count {len(log)})")

    print("\n== IDDFS on the original graph (limits start at 0)")
    for m in (1, 2, 3, 4):
        status, path, attempted, visits = iddfs(graph, "A", "G", m)
        print(f"max depth {m}: {status:7s} path={path} limits attempted={attempted} total nodes entered={visits}")

    print("\n== Edge cases")
    print("start == goal      :", run_dls(graph, "A", "A", 0))
    g2 = dict(graph); g2["H"] = []
    print("unreachable H, limit 5:", run_dls(g2, "A", "H", 5)[:2])
    print("unreachable H, limit 2:", run_dls(g2, "A", "H", 2)[:2])
    cyc = {"A": ["B"], "B": ["A", "C"], "C": []}
    print("cycle graph, goal C, limit 3:", run_dls(cyc, "A", "C", 3))
    print("cycle graph, goal Z, limit 5:", run_dls(cyc, "A", "Z", 5)[:2])
