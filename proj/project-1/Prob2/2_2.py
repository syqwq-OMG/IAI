from collections import deque

a = ""
tar = "12345678x"
d = dict()


def read():
    global a
    a = "".join(input().split())


def valid(x, y):
    return 0 <= x < 3 and 0 <= y < 3


def bfs() -> bool:
    q = deque()
    q.append((a, a.index("x"), 0))
    d[a] = 0
    while len(q) != 0:
        s, x, step = q.popleft()
        
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
                
                if ns not in d:
                    d[ns] = step + 1
                    q.append((ns, nx, step + 1))
    return False


def main():
    read()
    print(d[tar] if bfs() else -1)


if __name__ == "__main__":
    main()

"""  
2 3 4 1 5 x 7 6 8
"""
