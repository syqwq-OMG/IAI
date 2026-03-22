from heapq import heappush, heappop

a = ""
tar = "12345678x"
d:dict[str, tuple[int, str]] = dict()
MOVES = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}


def read():
    global a
    a = "".join(input().split())


def valid(x:int, y:int) -> bool:
    return 0 <= x < 3 and 0 <= y < 3


def check(s: str) -> bool:
    cnt = 0
    for i in range(9):
        for j in range(i + 1, 9):
            if s[i] != "x" and s[j] != "x" and s[i] > s[j]:
                cnt += 1
    return cnt % 2 == 0


def g(s: str) -> int:
    return d[s][0]


def h(s: str) -> int:
    ret = 0
    for i, c in enumerate(s):
        if c != "x":
            ti = int(c) - 1
            ret += abs(ti // 3 - i // 3) + abs(ti % 3 - i % 3)
    return ret


def f(s: str) -> int:
    return g(s) + h(s)


def astar():
    q = []
    d[a] = (0, "")
    heappush(q, (f(a), a))
    while q:
        _, s = heappop(q)
        if s == tar:
            return
        i = s.index("x")
        x, y = i // 3, i % 3
        for op, (dx, dy) in MOVES.items():
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                ns = list(s)
                ns[i], ns[nx * 3 + ny] = ns[nx * 3 + ny], ns[i]
                ns = "".join(ns)
                if ns not in d or d[ns][0] > d[s][0] + 1:
                    d[ns] = (d[s][0] + 1, d[s][1] + op)
                    heappush(q, (f(ns), ns))


def main():
    read()
    if not check(a):
        return print("unsolvable")
    astar()
    print(d[tar][1])


if __name__ == "__main__":
    main()

"""  
2 3 4 1 5 x 7 6 8
"""
