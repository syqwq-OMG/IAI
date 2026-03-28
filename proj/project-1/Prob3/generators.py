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
        rows, cols = len(grid), len(grid[0])
        start, goal = (0, 0), (rows - 1, cols - 1)

        if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
            return False

        queue = deque([start])
        visited = {start}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                return True

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    @staticmethod
    def generate_random_density(
        rows: int, cols: int, wall_probability: float = 0.25
    ) -> Maze:
        """生成随机密度的迷宫（保证有解）"""
        wall_probability = min(wall_probability, 0.4)

        while True:
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    if random.random() < wall_probability:
                        grid[r][c] = 1

            grid[0][0] = 0
            grid[rows - 1][cols - 1] = 0

            if MazeGenerator._is_solvable(grid):
                return Maze(grid)

    @staticmethod
    def generate_perfect_maze(rows: int, cols: int) -> Maze:
        """使用 Randomized DFS 生成完美迷宫（高曲折度，长且深的死胡同）"""
        rows, cols = rows | 1, cols | 1
        grid = [[1 for _ in range(cols)] for _ in range(rows)]
        grid[0][0] = 0
        stack = [(0, 0)]

        while stack:
            r, c = stack[-1]
            neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    neighbors.append((nr, nc, dr, dc))

            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                grid[r + dr // 2][c + dc // 2] = 0
                grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        grid[rows - 1][cols - 1] = 0
        return Maze(grid)

    @staticmethod
    def generate_braid_maze(
        rows: int, cols: int, braid_probability: float = 0.5
    ) -> Maze:
        """生成编织迷宫（多解迷宫，存在环路）"""
        # 利用刚刚生成的完美迷宫打底，直接提取其内部的 grid
        base_maze = MazeGenerator.generate_perfect_maze(rows, cols)
        grid = base_maze.grid
        rows, cols = base_maze.rows, base_maze.cols

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == 0:
                    walls = []
                    if grid[r - 1][c] == 1:
                        walls.append((r - 1, c))
                    if grid[r + 1][c] == 1:
                        walls.append((r + 1, c))
                    if grid[r][c - 1] == 1:
                        walls.append((r, c - 1))
                    if grid[r][c + 1] == 1:
                        walls.append((r, c + 1))

                    # 消除死胡同
                    if len(walls) == 3 and random.random() < braid_probability:
                        wr, wc = random.choice(walls)
                        if 0 < wr < rows - 1 and 0 < wc < cols - 1:
                            grid[wr][wc] = 0

        return Maze(grid)

    @staticmethod
    def generate_cave_maze(
        rows: int, cols: int, initial_wall_prob: float = 0.45, iterations: int = 4
    ) -> Maze:
        """利用细胞自动机生成类似自然洞穴的迷宫"""
        while True:
            grid = [
                [1 if random.random() < initial_wall_prob else 0 for _ in range(cols)]
                for _ in range(rows)
            ]

            for _ in range(iterations):
                new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        wall_count = 0
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < rows and 0 <= nc < cols:
                                    if grid[nr][nc] == 1:
                                        wall_count += 1
                                else:
                                    wall_count += 1
                        new_grid[r][c] = 1 if wall_count >= 5 else 0
                grid = new_grid

            for dr in [0, 1]:
                for dc in [0, 1]:
                    grid[dr][dc] = 0
                    grid[rows - 1 - dr][cols - 1 - dc] = 0

            if MazeGenerator._is_solvable(grid):
                return Maze(grid)

    @staticmethod
    def generate_recursive_division(rows: int, cols: int) -> Maze:
        """使用递归分割法生成迷宫（拥有长直走廊和整齐的矩形区块）"""
        rows, cols = rows | 1, cols | 1
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            grid[r][0] = grid[r][cols - 1] = 1
        for c in range(cols):
            grid[0][c] = grid[rows - 1][c] = 1

        def divide(r1, r2, c1, c2):
            if r2 - r1 < 2 or c2 - c1 < 2:
                return

            horizontal = (r2 - r1) > (c2 - c1)

            if horizontal:
                wall_r = random.randrange(r1 + 1, r2, 2)
                for c in range(c1, c2 + 1):
                    grid[wall_r][c] = 1
                door_c = random.randrange(c1, c2 + 1, 2)
                grid[wall_r][door_c] = 0

                divide(r1, wall_r - 1, c1, c2)
                divide(wall_r + 1, r2, c1, c2)
            else:
                wall_c = random.randrange(c1 + 1, c2, 2)
                for r in range(r1, r2 + 1):
                    grid[r][wall_c] = 1
                door_r = random.randrange(r1, r2 + 1, 2)
                grid[door_r][wall_c] = 0

                divide(r1, r2, c1, wall_c - 1)
                divide(r1, r2, wall_c + 1, c2)

        divide(1, rows - 2, 1, cols - 2)
        grid[0][0] = grid[0][1] = grid[1][0] = 0
        grid[rows - 1][cols - 1] = grid[rows - 1][cols - 2] = grid[rows - 2][
            cols - 1
        ] = 0

        return Maze(grid)

    @staticmethod
    def generate_prim_maze(rows: int, cols: int) -> Maze:
        """使用随机普林算法生成迷宫（极多超短死胡同，强烈的中心辐射感）"""
        rows, cols = rows | 1, cols | 1
        grid = [[1 for _ in range(cols)] for _ in range(rows)]

        start_r = random.randrange(1, rows, 2)
        start_c = random.randrange(1, cols, 2)
        grid[start_r][start_c] = 0

        walls = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = start_r + dr, start_c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                walls.append((nr, nc, start_r + 2 * dr, start_c + 2 * dc))

        while walls:
            wall_index = random.randint(0, len(walls) - 1)
            wr, wc, tr, tc = walls.pop(wall_index)

            if grid[tr][tc] == 1:
                grid[wr][wc] = 0
                grid[tr][tc] = 0

                for dr, dc in directions:
                    nnr, nnc = tr + dr, tc + dc
                    ntr, ntc = tr + 2 * dr, tc + 2 * dc

                    if 0 < ntr < rows - 1 and 0 < ntc < cols - 1:
                        if grid[ntr][ntc] == 1:
                            walls.append((nnr, nnc, ntr, ntc))

        grid[0][0] = grid[0][1] = grid[1][0] = 0
        grid[rows - 1][cols - 1] = grid[rows - 1][cols - 2] = grid[rows - 2][
            cols - 1
        ] = 0

        return Maze(grid)
