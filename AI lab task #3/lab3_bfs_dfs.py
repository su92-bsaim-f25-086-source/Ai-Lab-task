"""Lab 3, Task 1: BFS and DFS on the original A-G graph.
bfs() and dfs() are the guided code from the lab manual (section 3.2).
bfs_trace() and dfs_trace() are my additions: same logic, but they also record
the visit order and the frontier after every processed node."""
from collections import deque

graph = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["G"], "F": [], "G": []}


# ---- code from the lab manual (unchanged logic) ----
def bfs(start, goal):
    q = deque([(start, [start])]); seen = {start}
    while q:
        node, path = q.popleft()
        if node == goal: return path
        for n in graph[node]:
            if n not in seen:
                seen.add(n); q.append((n, path + [n]))


def dfs(start, goal):
    stack = [(start, [start])]; seen = set()
    while stack:
        node, path = stack.pop()
        if node == goal: return path
        if node in seen: continue
        seen.add(node)
        for n in reversed(graph[node]): stack.append((n, path + [n]))


# ---- my tracing versions ----
def bfs_trace(start, goal):
    q = deque([(start, [start])]); seen = {start}
    order, steps = [], []
    while q:
        node, path = q.popleft()
        order.append(node)
        if node == goal:
            steps.append((node, path, [n for n, _ in q]))
            return path, order, steps
        for n in graph[node]:
            if n not in seen:
                seen.add(n); q.append((n, path + [n]))
        steps.append((node, path, [n for n, _ in q]))
    return None, order, steps


def dfs_trace(start, goal):
    stack = [(start, [start])]; seen = set()
    order, steps = [], []
    while stack:
        node, path = stack.pop()
        if node in seen:
            continue                      # duplicate, skipped
        order.append(node)
        if node == goal:
            steps.append((node, path, [n for n, _ in stack]))
            return path, order, steps
        seen.add(node)
        for n in reversed(graph[node]): stack.append((n, path + [n]))
        steps.append((node, path, [n for n, _ in stack]))   # bottom ... top
    return None, order, steps


def show(name, res):
    path, order, steps = res
    print("==", name)
    for i, (node, p, fr) in enumerate(steps, 1):
        label = "queue (front first)" if name == "BFS" else "stack (bottom -> top)"
        print(f"step {i}: processed {node}  path={'->'.join(p)}  {label} after step = {fr}")
    print("final path :", path)
    print("visit order:", order, "| nodes processed (goal included) =", len(order))
    print()


if __name__ == "__main__":
    b = bfs_trace("A", "G"); d = dfs_trace("A", "G")
    show("BFS", b); show("DFS", d)
    print("manual-code check: bfs ->", bfs("A", "G"), "| dfs ->", dfs("A", "G"))
    print("traces match manual code:", b[0] == bfs("A", "G") and d[0] == dfs("A", "G"))

    # edge cases
    print("\n== Edge cases")
    print("start == goal  : BFS", bfs("A", "A"), "| DFS", dfs("A", "A"))
    graph["H"] = []                                  # isolated node, unreachable
    print("unreachable H  : BFS", bfs("A", "H"), "| DFS", dfs("A", "H"))
    cyc = {"A": ["B"], "B": ["A", "C"], "C": []}     # contains a cycle A <-> B
    graph.update(cyc)
    print("cycle graph, goal C: BFS", bfs("A", "C"), "| DFS", dfs("A", "C"))
    print("cycle graph, goal Z (unreachable): BFS", bfs("A", "Z"), "| DFS", dfs("A", "Z"))
