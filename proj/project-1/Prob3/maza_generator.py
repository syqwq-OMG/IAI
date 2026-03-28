import random
from collections import deque

class MazeGenerator:
    @staticmethod
    def _is_solvable(maze):
        """
        内部辅助函数：使用最轻量的 BFS 快速验证迷宫是否至少存在一条解。
        """
        rows, cols = len(maze), len(maze[0])
        start, goal = (0, 0), (rows - 1, cols - 1)
        
        # 如果起点或终点本身就是墙（以防万一），直接无解
        if maze[start[0]][start[1]] == 1 or maze[goal[0]][goal[1]] == 1:
            return False
            
        queue = deque([start])
        visited = {start}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                return True  # 只要找到一条路，就证明有解
                
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    @staticmethod
    def generate_random_density(rows, cols, wall_probability=0.25):
        """
        生成随机密度的迷宫，并保证一定有解。
        """
        # 为了防止陷入死循环，给 wall_probability 设一个合理的上限
        # 当概率超过 0.4 时，根据渗流理论，网格连通的概率会呈指数级骤降
        wall_probability = min(wall_probability, 0.4) 
        
        attempts = 0
        while True:
            attempts += 1
            # 1. 随机生成
            maze = [[0 for _ in range(cols)] for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    if random.random() < wall_probability:
                        maze[r][c] = 1
                        
            # 强制清空起点和终点
            maze[0][0] = 0
            maze[rows-1][cols-1] = 0
            
            # 2. 验证连通性
            if MazeGenerator._is_solvable(maze):
                # print(f"生成成功！尝试次数: {attempts}") 
                return maze
                
    @staticmethod
    def generate_perfect_maze(rows, cols):
        """
        生成完美迷宫（任意两点间只有一条唯一路径，无回路）。
        保证有解，且非常曲折。
        """
        rows = rows | 1 
        cols = cols | 1
        
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        start_r, start_c = 0, 0
        maze[start_r][start_c] = 0
        
        stack = [(start_r, start_c)]
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1:
                    neighbors.append((nr, nc, dr, dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                maze[r + dr//2][c + dc//2] = 0
                maze[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()
                
        maze[rows-1][cols-1] = 0
        return maze
    
    @classmethod
    def generate_braid_maze(cls, rows, cols, braid_probability=0.5):
        """
        生成编织迷宫（多解迷宫，存在环路）。
        braid_probability 控制打通死胡同的概率，1.0 表示消除所有死胡同。
        """
        # 1. 先生成一个完美迷宫（需要用到前面写的生成方法）
        maze = cls.generate_perfect_maze(rows, cols)
        
        # 2. 遍历迷宫，寻找死胡同 (周围有3堵墙的道路)
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if maze[r][c] == 0:  # 如果当前是路
                    # 检查上下左右的墙壁数量
                    walls = []
                    if maze[r-1][c] == 1: walls.append((r-1, c))
                    if maze[r+1][c] == 1: walls.append((r+1, c))
                    if maze[r][c-1] == 1: walls.append((r, c-1))
                    if maze[r][c+1] == 1: walls.append((r, c+1))
                    
                    # 如果是死胡同，根据概率随机打通一堵墙
                    if len(walls) == 3 and random.random() < braid_probability:
                        wr, wc = random.choice(walls)
                        # 确保不破坏迷宫的最外层边界
                        if 0 < wr < rows - 1 and 0 < wc < cols - 1:
                            maze[wr][wc] = 0
                            
        return maze
    
    
    @classmethod
    def generate_cave_maze(cls, rows, cols, initial_wall_prob=0.45, iterations=4):
        """
        利用细胞自动机生成类似自然洞穴的迷宫。
        """
        while True:
            # 1. 随机初始化网格
            maze = [[1 if random.random() < initial_wall_prob else 0 for _ in range(cols)] for _ in range(rows)]
            
            # 2. 细胞自动机平滑迭代
            for _ in range(iterations):
                new_maze = [[0 for _ in range(cols)] for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        # 统计 3x3 邻域内的墙壁数量 (超出边界的视为墙壁)
                        wall_count = 0
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < rows and 0 <= nc < cols:
                                    if maze[nr][nc] == 1:
                                        wall_count += 1
                                else:
                                    wall_count += 1
                        
                        # 核心规则：周围墙多，自己就变成墙；否则变成路
                        if wall_count >= 5:
                            new_maze[r][c] = 1
                        else:
                            new_maze[r][c] = 0
                maze = new_maze
                
            # 3. 强制清空起点和终点周围的区域，防止被封死
            for dr in [0, 1]:
                for dc in [0, 1]:
                    maze[dr][dc] = 0
                    maze[rows-1-dr][cols-1-dc] = 0
                    
            # 4. 验证连通性 (使用之前写的快速 BFS)
            if cls._is_solvable(maze):
                return maze
            
            
    @classmethod
    def generate_recursive_division(cls, rows, cols):
        """
        使用递归分割法生成迷宫。拥有长直的走廊和整齐的矩形房间。
        """
        rows = rows | 1 
        cols = cols | 1
        # 初始化：全部是路 (0)，周围围上一圈墙 (1)
        maze = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            maze[r][0] = maze[r][cols-1] = 1
        for c in range(cols):
            maze[0][c] = maze[rows-1][c] = 1

        def divide(r1, r2, c1, c2):
            # 如果区域太小，则停止分割
            if r2 - r1 < 2 or c2 - c1 < 2:
                return

            # 根据区域的长宽比决定是横切还是竖切
            horizontal = (r2 - r1) > (c2 - c1)

            if horizontal:
                # 随机选择一个偶数行作为墙壁位置
                wall_r = random.randrange(r1 + 1, r2, 2)
                for c in range(c1, c2 + 1):
                    maze[wall_r][c] = 1
                # 在墙上随机开一个奇数列的门
                door_c = random.randrange(c1, c2 + 1, 2)
                maze[wall_r][door_c] = 0
                
                # 递归分割上、下两块区域
                divide(r1, wall_r - 1, c1, c2)
                divide(wall_r + 1, r2, c1, c2)
            else:
                # 随机选择一个偶数列作为墙壁位置
                wall_c = random.randrange(c1 + 1, c2, 2)
                for r in range(r1, r2 + 1):
                    maze[r][wall_c] = 1
                # 在墙上随机开一个奇数行的门
                door_r = random.randrange(r1, r2 + 1, 2)
                maze[door_r][wall_c] = 0
                
                # 递归分割左、右两块区域
                divide(r1, r2, c1, wall_c - 1)
                divide(r1, r2, wall_c + 1, c2)

        # 从内部区域开始递归分割
        divide(1, rows - 2, 1, cols - 2)
        
        # 确保起点和终点畅通
        maze[0][0] = maze[0][1] = maze[1][0] = 0
        maze[rows-1][cols-1] = maze[rows-1][cols-2] = maze[rows-2][cols-1] = 0
        
        return maze
    
    @classmethod
    def generate_prim_maze(cls, rows, cols):
        """
        使用随机普林算法 (Randomized Prim's) 生成迷宫。
        特征：极多的超短死胡同，呈现出强烈的中心辐射感，没有长直走廊。
        """
        # 保证行列数为奇数，以便有明确的墙壁和道路交替
        rows = rows | 1
        cols = cols | 1

        # 初始状态：整个网格全部是墙 (1)
        maze = [[1 for _ in range(cols)] for _ in range(rows)]

        # 随机选择一个内部的奇数坐标作为“生长起点”
        start_r = random.randrange(1, rows, 2)
        start_c = random.randrange(1, cols, 2)
        maze[start_r][start_c] = 0

        # 维护一个“待处理墙壁”的列表
        # 列表里存储的元组格式为：(墙壁本身的坐标 r, 墙壁本身的坐标 c, 墙壁背后的目标格子坐标 r, 墙壁背后的目标格子坐标 c)
        walls = []

        # 将起点的上下左右相邻墙壁加入列表
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = start_r + dr, start_c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                walls.append((nr, nc, start_r + 2 * dr, start_c + 2 * dc))

        # 核心循环
        while walls:
            # 1. 从列表中随机抽出并移除一堵墙
            wall_index = random.randint(0, len(walls) - 1)
            wr, wc, tr, tc = walls.pop(wall_index)

            # 2. 检查墙壁背后的目标格子是否还没有被访问过（依然是墙 1）
            if maze[tr][tc] == 1:
                # 拆除这堵墙，使其变成路
                maze[wr][wc] = 0
                # 将目标格子变成路
                maze[tr][tc] = 0

                # 3. 将新路格子周围的墙壁加入待处理列表
                for dr, dc in directions:
                    nnr, nnc = tr + dr, tc + dc          # 新墙壁的坐标
                    ntr, ntc = tr + 2 * dr, tc + 2 * dc  # 新墙壁背后的目标格子坐标
                    
                    # 确保不越过迷宫的物理边界
                    if 0 < ntr < rows - 1 and 0 < ntc < cols - 1:
                        # 只有当目标格子还是未访问的墙时，才把中间的墙加入候选
                        if maze[ntr][ntc] == 1:
                            walls.append((nnr, nnc, ntr, ntc))

        # 确保左上角 (0, 0) 起点和右下角终点畅通，并与内部迷宫网络连通
        maze[0][0] = maze[0][1] = maze[1][0] = 0
        maze[rows-1][cols-1] = maze[rows-1][cols-2] = maze[rows-2][cols-1] = 0

        return maze