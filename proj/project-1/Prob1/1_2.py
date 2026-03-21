N = int(1e5 + 5)
inf = int(1e10 + 7)

n, m = 0, 0
g = [[] for _ in range(N)]
d = [inf] * N
flg = [False] * N


def read():
    global n, m, g
    n, m = map(int, input().split())
    for _ in range(m):
        u, v, w = map(int, input().split())
        g[u].append((v, w))


def dijkstra():
    global d, flg
    d[1] = 0
    for _ in range(n):
        u = -1
        for i in range(1, n + 1):
            if not flg[i] and (u == -1 or d[i] < d[u]):
                u = i
        if u == -1:
            break
        flg[u] = True
        for v, w in g[u]:
            if not flg[v] and d[v] > d[u] + w:
                d[v] = d[u] + w


def main():
    read()
    dijkstra()
    print(d[n] if d[n] != inf else -1)


if __name__ == "__main__":
    main()

""" 
3 3
1 2 2
2 3 1
1 3 4
"""
