from heapq import heappush, heappop

a = ""
tar = "12345678x"
d = dict()


def read():
    global a
    a = "".join(input().split())


def valid(x, y):
    return 0 <= x < 3 and 0 <= y < 3

def dijkstra() -> bool:
    q = []
    heappush(q, (0, a, a.index("x")))
    d[a] = 0
    while len(q) != 0:
        step, s, x = heappop(q)
        
        if s == tar:
            return True
        
        r, c = x // 3, x % 3  
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dx, c + dy
            
            if valid(nr, nc):
                nx = nr * 3 + nc
                
                ns = list(s)
                ns[x], ns[nx] = ns[nx], ns[x]
                ns = "".join(ns)
                
                if ns not in d or step + 1 < d[ns]:
                    d[ns] = step + 1
                    heappush(q, (step + 1, ns, nx))
    return False

def main():
    read()
    print(d[tar] if dijkstra() else -1)

if __name__ == "__main__":
    main()

"""  
2 3 4 1 5 x 7 6 8
"""
