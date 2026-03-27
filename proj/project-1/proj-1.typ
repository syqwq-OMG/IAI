#import "../../lib.typ": *
#import "@preview/tdtr:0.5.4": *

#show: report.with(name: "孙育泉", course: "AI基础", exp-name: "Project 1", tutor: "杨彬")

= 实验任务

== 人狼羊菜
一个农民要带着一只狼、一只羊、一颗白菜过河。

+ 人不在的时候，狼会吃羊、羊会吃草

+ 人每次只能带一样东西过河。



#let rt = sym.triangle.stroked.r.small
#let lt = sym.triangle.stroked.l.small
#let sep = sym.bar.v.double

#[
  #show "F": text(fill: red)[F]
  #show "C": text(fill: green)[C]
  #show "G": text(fill: teal)[G]
  #show "W": text(fill: blue)[W]
  有8种可能的动作：F#rt, F#lt, FC#rt, FC#lt, FG#rt, FG#lt, FW#rt, FW#lt，其中符号表示为： F(Farmer), C(Cabbage), G(Goat), W(Wolf)，#rt 和 #lt 分别表示向右和向左过河。
]

要求：
+ 画出状态空间图

+ 基于你的状态空间图，分别用BFS和DFS算法画出搜索路径
+ 挑选BFS或DFS算法，写出搜索到最终状态的流程
  - BFS 展示每一步的队列

  - DFS 展示每一步的递归栈

== 图最短路问题

+ 在边权为 1 的有向图上，使用 BFS 算法求 SSSP。

+ 在正边权的有向图中，使用朴素 Dijkstra 算法求 SSSP。

+ 在正边权的有向图中，使用堆优化 Dijkstra 算法求 SSSP。

== 八数码问题

+ 使用 DFS 判断八数码问题的可解性。

+ 使用 BFS 求解八数码问题。

+ 使用 Dijkstra 算法求解八数码问题。

+ 使用 A\* 算法求解八数码问题。


= 使用环境
编程语言： Python 3

= 实验过程
== 人狼羊菜
*搜索树*如下：

#figure[
  #show "F": text(fill: red)[F]
  #show "C": text(fill: green)[C]
  #show "G": text(fill: teal)[G]
  #show "W": text(fill: blue)[W]
  #tidy-tree-graph()[
    - FCGW#sep
      - WC#sep\FG
        - FWC#sep\G
          - C#sep\FGW
            - FCG#sep\W
              - G#sep\FCW
                - FG#sep\CW
                  - #sep\FCGW
          - W#sep\FCG
            - FGW#sep\C
              - G#sep\FCW
                - FG#sep\CW
                  - #sep\FCGW
  ]
]

分别使用BFS和DFS算法搜索到最终状态的*路径*如下（使用编号来记录访问的状态顺序）：

#let num(x) = (
  math.space
    + box(stroke: none, baseline: .2pt, radius: 50%, fill: black, height: .8em, width: .8em, text(
      fill: white,
      size: 5pt,
      weight: "bold",
      font: "New Computer Modern Sans",
    )[#x])
)

#align(center, grid(
  columns: (1fr,) * 2,
  row-gutter: 1em,
  [DFS 搜索顺序], [BFS 搜索顺序],
  [
    #show "F": text(fill: red)[F]
    #show "C": text(fill: green)[C]
    #show "G": text(fill: teal)[G]
    #show "W": text(fill: blue)[W]
    #tidy-tree-graph()[
      - FCGW#sep#num(0)
        - WC#sep\FG#num(1)
          - FWC#sep\G#num(2)
            - C#sep\FGW#num(3)
              - FCG#sep\W#num(4)
                - G#sep\FCW#num(5)
                  - FG#sep\CW#num(6)
                    - #sep\FCGW#num(7)
            - W#sep\FCG#num(8)
              - FGW#sep\C#num(9)
                - G#sep\FCW#num(10)
                  - FG#sep\CW#num(11)
                    - #sep\FCGW#num(12)
    ]
  ],
  [
    #show "F": text(fill: red)[F]
    #show "C": text(fill: green)[C]
    #show "G": text(fill: teal)[G]
    #show "W": text(fill: blue)[W]
    #tidy-tree-graph()[
      - FCGW#sep#num(0)
        - WC#sep\FG#num(1)
          - FWC#sep\G#num(2)
            - C#sep\FGW#num(3)
              - FCG#sep\W#num(5)
                - G#sep\FCW#num(7)
                  - FG#sep\CW#num(9)
                    - #sep\FCGW#num(11)
            - W#sep\FCG#num(4)
              - FGW#sep\C#num(6)
                - G#sep\FCW#num(8)
                  - FG#sep\CW#num(10)
                    - #sep\FCGW#num(12)
    ]
  ],
))

本次选择使用 BFS 算法。首先要考虑如何记录状态，由于每个角色有互斥关系，并且分为河的两侧，于是考虑使用状态压缩来表示一侧的状态，然后对于完整的两侧状态使用元组即可，也就是 `tuple[int, int]`。表示如下：

```py
FARMER, CABBAGE, GOAT, WOLF = 1, 2, 4, 8
ROLES = "FCGW"

initial_state = FARMER | CABBAGE | GOAT | WOLF, 0
final_state = 0, FARMER | CABBAGE | GOAT | WOLF
```

接下来，我们考虑如何判断一个状态是否合法。根据题目要求，农民不在的时候，狼会吃羊、羊会吃草，所以我们需要判断在某一侧如果没有农民，那么是否存在狼和羊或者羊和草同时存在的情况，如果存在则说明这个状态不合法。

```py
def valid(state: tuple[int, int]) -> bool:
    def check(side: int) -> bool:
        if (side & CABBAGE) and (side & GOAT):
            return False
        if (side & GOAT) and (side & WOLF):
            return False
        return True

    l, r = state
    return check(r) if l & FARMER else check(l)
```

然后，为了方便将状态转换成可读的字符串，我们可以写一个函数来将状态转换成字符串表示：

```py
def state_to_str(state: tuple[int, int]) -> str:
    def foo(side: int):
        return "".join(ROLES[i] for i in range(4) if (side & (1 << i)) != 0)

    l, r = state
    return f"{foo(l):<4} | {foo(r)}"
```

对于 BFS 部分，因为要输出不同的方案，因此我们考虑对于队列的每一项都记录一个到该状态的路径，同时使用 `vis` 字典来记录到当前状态的最短路径长度，保证最优解。然后，使用 `step` 计数每次层级的扩展，用于输出每层时的队列状态。在进行状态转移的时候，只需要使用异或操作来翻转对应角色的状态，然后检测是否是合法状态即可。最后，输出所有的方案。

```py
def bfs():
    # path of states
    q = deque([[initial_state]])

    vis = {initial_state: 0}

    solutions = []
    step = 1

    while q:
        print(f"=== step {step} queue ===")
        for path in q:
            print("  " + state_to_str(path[-1]))
        print()

        level_size = len(q)
        for _ in range(level_size):
            path = q.popleft()
            current_state = path[-1]
            current_depth = len(path) - 1

            if current_state == final_state:
                solutions.append(path)
                continue

            l, r = current_state
            for i in range(4):
                next_state = None
                if (l & FARMER) and (l & (1 << i)):
                    next_state = (l ^ (FARMER | (1 << i)), r ^ (FARMER | (1 << i)))
                elif (r & FARMER) and (r & (1 << i)):
                    next_state = (l ^ (FARMER | (1 << i)), r ^ (FARMER | (1 << i)))

                if next_state is not None and valid(next_state):
                    if next_state not in vis:
                        vis[next_state] = current_depth + 1
                        q.append(path + [next_state])
                    elif vis[next_state] == current_depth + 1:
                        q.append(path + [next_state])
        if solutions:
            break

        step += 1

    print("-" * 30)
    print(f"find {len(solutions)} best solutions：\n")
    for idx, sol in enumerate(solutions, 1):
        print(f"solution {idx}")
        for s in sol:
            print("  " + state_to_str(s))
        print()
```

最后，整个程序的输出如下：

```txt 
=== step 1 queue ===
  FCGW | 

=== step 2 queue ===
  CW   | FG

=== step 3 queue ===
  FCW  | G

=== step 4 queue ===
  W    | FCG
  C    | FGW

=== step 5 queue ===
  FGW  | C
  FCG  | W

=== step 6 queue ===
  G    | FCW
  G    | FCW

=== step 7 queue ===
  FG   | CW
  FG   | CW

=== step 8 queue ===
       | FCGW
       | FCGW

------------------------------
find 2 best solutions：

solution 1
  FCGW | 
  CW   | FG
  FCW  | G
  W    | FCG
  FGW  | C
  G    | FCW
  FG   | CW
       | FCGW

solution 2
  FCGW | 
  CW   | FG
  FCW  | G
  C    | FGW
  FCG  | W
  G    | FCW
  FG   | CW
       | FCGW
```

== 图最短路问题

为了简化代码的复用，这里统一一些变量和记号的定义:

#show raw.where(block: false): set text(size: 10pt)

#figure(
  table(
    columns: 2,
    align: (horizon,) * 2,
    //   rows: (auto, 2em),
    stroke: none,
    table.hline(y: 0, stroke: 2pt),
    table.hline(y: 1),
    table.hline(y: 7, stroke: 2pt),

    [*记号*], [*定义*],
    `n`, [图中节点的数量],
    `m`, [图中边的数量],
    `g[][]`, [图的邻接表表示],
    `d[]`, [距离数组],
    `q[]`, [队列 / 优先队列],
    `flg[]`, [访问标记数组],
  ),
  caption: [SSSP 记号],
  supplement: "表",
)


=== BFS
因为边权都是 1，所以扩展的步数就是最短路长度，因此可以直接使用 BFS 来求解 SSSP 问题。

```py
def bfs():
    global d
    q, d[1] = deque([1]), 0
    while len(q):
        u = q.popleft()
        for v in g[u]:
            if d[v] > d[u] + 1:
                d[v] = d[u] + 1
                q.append(v)
```

=== 朴素 Dijkstra
因为没有负权边，所以可以利用贪心：每次选择当前距离最小的没有扩展过的节点进行扩展，直到所有节点都被访问过或者无法访问为止。

```py
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
```

=== 堆优化 Dijkstra
可以使用小根堆来优化 Dijkstra 算法中寻找当前距离最小的节点的过程，从而将算法的时间复杂度从 $O(n^2)$ 降低到 $O(m log n)$。

```py
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
```


== 八数码问题

同样，这里声明一些记号：

#figure(
  table(
    columns: 2,
    align: (horizon,) * 2,
    stroke: none,
    table.hline(y: 0, stroke: 2pt),
    table.hline(y: 1),
    table.hline(y: 6, stroke: 2pt),
    [*记号*], [*定义*],
    `a`, [初始状态],
    `tar`, [目标状态],
    `d[]`, [距离哈希表],
    `valid()`, [判断状态是否合法的函数],
    `flg`, [访问标记],
  ),
  caption: [八数码问题记号],
  supplement: "表",
)

=== DFS
因为 DFS 可能会重复搜索，所以用一个集合来记录已经访问过的状态，避免重复搜索。同时，因为 python 默认的递归深度较小，可以手动维护栈，但这里直接将递归深度限制调大。

#zcode(
  highlight-lines: (1, 2),
  ```py
  import sys
  sys.setrecursionlimit(200000)

  # ......

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

  # ......
  ```,
)

=== BFS
维护一个队列，每次扩展一个状态时，将其所有合法的下一步状态加入队列，并记录它们的距离。直到找到目标状态或者队列为空为止。


```py
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
```

=== Dijkstra
将状态空间看成一个图，每个状态是一个节点，每条合法的状态转移是一条边，边权为 1，所以问题就转换成 SSSP 问题。

```py
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
```

=== A\*
启发式搜索，启发函数可以使用曼哈顿距离，即每个数字与其目标位置的行距和列距之和，保证不会高估实际距离，从而保证算法的正确性。

#zcode(
  highlight-lines: (16, 20, 29, 30, 36, 51),
  ```py
  from heapq import heappush, heappop

  d:dict[str, tuple[int, str]] = dict()
  MOVES = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}


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
  ```,
)

#idea[
  这里判断是否有解利用了八数码问题的一个结论：
  有解 $<=>$ 初始状态和目标状态的逆序对数量奇偶性相同。
]



= 总结

本次实验总结如下：

+ *SSSP算法选择*：单位边权图直接使用BFS求解 。正权图使用Dijkstra ，结合小根堆优化可将复杂度从 $O(n^2)$ 降至 $O(m log n)$ 。

+ *状态空间搜索*：八数码问题本质可转化为图论中的SSSP。 DFS、BFS与朴素Dijkstra作为盲目搜索，存在状态重复、易达递归极限或可能导致资源消耗过高的问题 。

+ *启发式优化*：采用曼哈顿距离作为启发函数的A\*算法，是控制状态搜索规模的有效手段 。它保证了不被高估的实际距离，从而得到最优解 。

+ *理论剪枝*：通过逆序对奇偶性判定八数码的可解性 。可以避免无意义算力浪费。

#info[
  完整代码见压缩包其余代码文件。
]
