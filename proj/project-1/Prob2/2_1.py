import sys

sys.setrecursionlimit(200000)

a = ""
tar = "12345678x"
flg = set()


def read():
    global a
    a = "".join(input().split())
    flg.add(a)


def valid(x, y):
    return 0 <= x < 3 and 0 <= y < 3


def dfs(s: str) -> bool:
    if s == tar:
        return True

    x = s.index("x")

    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nx, ny = x // 3 + dx, x % 3 + dy
        if valid(nx, ny):
            t = list(s)
            t[x], t[nx * 3 + ny] = t[nx * 3 + ny], t[x]
            t = "".join(t)
            if t not in flg:
                flg.add(t)
                if dfs(t):
                    return True

    return False


def main():
    read()
    print("1" if dfs(a) else "0")


if __name__ == "__main__":
    main()

"""  
2 3 4 1 5 x 7 6 8
"""
