from collections import deque

N = int(1e5 + 5)
inf = int(1e10 + 7)

n, m = 0, 0
g = [[] for _ in range(N)]
d = [inf] * N


def read():
    global n, m, g
    n, m = map(int, input().split())
    for _ in range(m):
        u, v = map(int, input().split())
        g[u].append(v)


def bfs():
    global d
    q, d[1] = deque([1]), 0
    while len(q):
        u = q.popleft()
        for v in g[u]:
            if d[v] > d[u] + 1:
                d[v] = d[u] + 1
                q.append(v)


def main():
    read()
    bfs()
    print(d[n] if d[n] != inf else -1)


if __name__ == "__main__":
    main()

""" 
4 5
1 2
2 3
3 4
1 3
1 4
"""
