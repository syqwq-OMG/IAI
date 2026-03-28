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
