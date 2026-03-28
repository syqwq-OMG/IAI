#import "../../lib.typ": *

#show: report.with(name: "孙育泉", course: "AI基础", exp-name: "Maze", tutor: "杨彬")


= 实验任务

给定一个 $n  times m$ 的⼆维整数数组，⽤来表示⼀个迷宫，数组中只包含 $0$ 或 $1$，其中 $0$ 表示可以⾛的路，$1$ 表示不可通过的墙壁。最初，有个人位于左上角 $(1,1)$ 处，已知该⼈每次可以向上、下、左、右任意⼀个⽅向移动⼀个位置。

请问，该人从左上角移动至右下角 $(n,m)$ 处最少需要移动多少次。数据保证 $(1,1)$ 与 $(n,m)$ 处的值均为 $0$，且至少存在⼀条路径可以到达。 并且需要进行可视化。

考虑使用这些算法： DFS, BFS, Dijkstra, A\*。

= 使用环境
编程语言： Python 3

= 实验过程

#idea[
  为了代码的可维护性与解藕性，这里对代码进行了很大的改动，进行了模块化。
]

首先，为了进行后续的可视化与维护每次探索的状态，我们将迷宫分装成了一个 `Maze` 类。
```py
# maze.py
from dataclasses import dataclass
from typing import List, Tuple, Set


@dataclass
class SolverState:
    """用于寻路算法与可视化解耦的数据模型，保存每一步的快照"""

    current: Tuple[int, int]
    explored: List[Tuple[int, int]]
    frontier: List[Tuple[int, int]]  # 待探索队列（栈/队列/优先队列）
    path: List[Tuple[int, int]]


class Maze:
    """迷宫的基础数据结构"""

    def __init__(
        self,
        grid: List[List[int]],
        start: Tuple[int, int] = (0, 0),
        goal: Tuple[int, int] = None,
    ):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = start
        self.goal = goal if goal else (self.rows - 1, self.cols - 1)

    def is_wall(self, r: int, c: int) -> bool:
        return self.grid[r][c] == 1

    def is_valid_move(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and not self.is_wall(r, c)

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_valid_move(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

```

然后，我们需要生成迷宫，用于探究算法在不同的迷宫类型下的性能表现。

```py
# generators.py
import random
from collections import deque
from maze import Maze


class MazeGenerator:
    """
    迷宫生成器：包含多种不同拓扑结构的迷宫生成策略。
    所有生成方法均返回 maze.Maze 类的实例。
    """

    @staticmethod
    def _is_solvable(grid: list[list[int]]) -> bool:
        """内部辅助函数：使用轻量级 BFS 快速验证网格是否至少存在一条解"""
        ......

    @staticmethod
    def generate_random_density(
        rows: int, cols: int, wall_probability: float = 0.25
    ) -> Maze:
        """生成随机密度的迷宫（保证有解）"""
        ......

    @staticmethod
    def generate_perfect_maze(rows: int, cols: int) -> Maze:
        """使用 Randomized DFS 生成完美迷宫（高曲折度，长且深的死胡同）"""
        ......

    @staticmethod
    def generate_braid_maze(
        rows: int, cols: int, braid_probability: float = 0.5
    ) -> Maze:
        """生成编织迷宫（多解迷宫，存在环路）"""
        ......

    @staticmethod
    def generate_cave_maze(
        rows: int, cols: int, initial_wall_prob: float = 0.45, iterations: int = 4
    ) -> Maze:
        """利用细胞自动机生成类似自然洞穴的迷宫"""
        ......

    @staticmethod
    def generate_recursive_division(rows: int, cols: int) -> Maze:
        """使用递归分割法生成迷宫（拥有长直走廊和整齐的矩形区块）"""
        ......

    @staticmethod
    def generate_prim_maze(rows: int, cols: int) -> Maze:
        """使用随机 Prim 算法生成迷宫（极多超短死胡同，强烈的中心辐射感）"""
        ......

```

= 总结


#info[
  完整代码见压缩包其余代码文件。
]