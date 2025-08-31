import sys
import heapq

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    M = int(data[idx]); idx += 1

    dist = [[0]*M for _ in range(M)]
    for i in range(M):
        for j in range(M):
            dist[i][j] = int(data[idx]); idx += 1

    employees = [0]*M
    for i in range(1, M):
        employees[i] = int(data[idx]); idx += 1

    capacity = int(data[idx])

    # Dijkstra from office
    INF = float('inf')
    d = [INF]*M
    parent = [-1]*M
    d[0] = 0
    pq = [(0, 0)]
    while pq:
        du, u = heapq.heappop(pq)
        if du != d[u]:
            continue
        for v in range(M):
            if u == v:
                continue
            nd = du + dist[u][v]
            if nd < d[v]:
                d[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    tree = [[] for _ in range(M)]
    for v in range(M):
        if parent[v] != -1:
            tree[parent[v]].append(v)

    def dfs(u):
        total_people = employees[u]
        buses_from_children = 0
        for v in tree[u]:
            p, b = dfs(v)
            total_people += p
            buses_from_children += b
        required_buses = (total_people + capacity - 1) // capacity
        return total_people, max(required_buses, buses_from_children)

    _, result = dfs(0)
    #  Print only one integer with newline, no extra spaces
    sys.stdout.write(str(result) + "\n")

if __name__ == "__main__":
    solve()
