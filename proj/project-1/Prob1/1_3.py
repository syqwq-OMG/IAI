from heapq import heappop, heappush

N = int(1e5 + 5)
inf = int(1e10 + 7)

n, m = 0, 0
g = [[] for _ in range(N)]
d = [inf] * N

def read():
    global n, m, g
    n, m = map(int, input().split())
    for _ in range(m):
        u, v, w = map(int, input().split())
        g[u].append((v, w))

def dijkstra():
    global d
    d[1], pq = 0, [(0, 1)]
    
    while pq:
        dis, u = heappop(pq)
        
        if dis > d[u]:
            continue
            
        for v, w in g[u]:
            if d[v] > d[u] + w:
                d[v] = d[u] + w
                heappush(pq, (d[v], v))

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