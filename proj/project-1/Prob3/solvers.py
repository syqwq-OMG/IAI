# solvers.py
from collections import deque
import heapq
from typing import Iterator
from maze import Maze, SolverState


class MazeSolver:
    """
    寻路算法基类/命名空间
    所有算法接收 Maze 对象，yield SolverState 对象
    """

    @staticmethod
    def dfs(maze: Maze) -> Iterator[SolverState]:
        stack = [(maze.start, [maze.start])]
        visited = set()
        explored_order = []

        while stack:
            current, path = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            explored_order.append(current)

            # 提取栈中等待探索的节点
            frontier = [node for (node, p) in stack if node not in visited]
            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            for nr, nc in maze.get_neighbors(*current):
                if (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))

    @staticmethod
    def bfs(maze: Maze) -> Iterator[SolverState]:
        queue = deque([(maze.start, [maze.start])])
        visited = {maze.start}
        explored_order = []

        while queue:
            current, path = queue.popleft()
            explored_order.append(current)

            frontier = [node for (node, p) in queue]
            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            for nr, nc in maze.get_neighbors(*current):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

    @staticmethod
    def a_star(maze: Maze) -> Iterator[SolverState]:
        def manhattan(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        g_score = {maze.start: 0}
        pq = [(manhattan(maze.start, maze.goal), maze.start, [maze.start])]
        explored_order = []
        explored_set = set()

        while pq:
            _, current, path = heapq.heappop(pq)

            if current in explored_set:
                continue

            explored_set.add(current)
            explored_order.append(current)
            frontier = list({node for f, node, p in pq if node not in explored_set})

            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            for nr, nc in maze.get_neighbors(*current):
                tentative_g = g_score.get(current, float("inf")) + 1
                if tentative_g < g_score.get((nr, nc), float("inf")):
                    g_score[(nr, nc)] = tentative_g
                    f_score = tentative_g + manhattan((nr, nc), maze.goal)
                    heapq.heappush(pq, (f_score, (nr, nc), path + [(nr, nc)]))
    @staticmethod
    def dijkstra(maze: Maze) -> Iterator[SolverState]:
        pq = [(0, maze.start, [maze.start])]
        costs = {maze.start: 0}
        
        explored_order = []
        explored_set = set()

        while pq:
            current_cost, current, path = heapq.heappop(pq)

            if current in explored_set:
                continue

            explored_set.add(current)
            explored_order.append(current)
            
            frontier = list({node for cost, node, p in pq if node not in explored_set})

            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            for nr, nc in maze.get_neighbors(*current):
                new_cost = current_cost + 1  # 迷宫中每走一步的代价视为 1
                if new_cost < costs.get((nr, nc), float("inf")):
                    costs[(nr, nc)] = new_cost
                    heapq.heappush(pq, (new_cost, (nr, nc), path + [(nr, nc)]))
                    
    @staticmethod
    def a_star_robust(maze: Maze) -> Iterator[SolverState]:
        """
        高鲁棒性的 A* 算法：使用向量叉积打破平局，完美兼顾开阔地形与复杂迷宫。
        """
        def manhattan(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        g_score = {maze.start: 0}
        
        # 提前获取起点和终点，用于计算基础向量
        sr, sc = maze.start
        gr, gc = maze.goal

        def heuristic(current):
            cr, cc = current
            h = manhattan(current, maze.goal)
            
            # 【核心逻辑】：计算向量叉积 (Cross Product)
            # 衡量当前点到终点的向量，偏离起点到终点“绝对直线”的程度
            dx1 = cr - gr
            dy1 = cc - gc
            dx2 = sr - gr
            dy2 = sc - gc
            cross_product = abs(dx1 * dy2 - dx2 * dy1)
            
            # 将叉积乘以一个极小的系数作为次要惩罚项
            # 它小到不足以破坏寻路的最优性，但能完美打破开阔平地上的平局！
            return h + cross_product * 0.001

        pq = [(heuristic(maze.start), maze.start, [maze.start])]
        explored_order = []
        explored_set = set()

        while pq:
            _, current, path = heapq.heappop(pq)

            if current in explored_set:
                continue

            explored_set.add(current)
            explored_order.append(current)
            
            frontier = list({node for f, node, p in pq if node not in explored_set})
            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            for nr, nc in maze.get_neighbors(*current):
                tentative_g = g_score.get(current, float("inf")) + 1
                if tentative_g < g_score.get((nr, nc), float("inf")):
                    g_score[(nr, nc)] = tentative_g
                    f_score = tentative_g + heuristic((nr, nc))
                    heapq.heappush(pq, (f_score, (nr, nc), path + [(nr, nc)]))

    @staticmethod
    def jps_4way(maze: Maze) -> Iterator[SolverState]:
        """
        四向跳跃点搜索 (Junction Point Search / 4-way JPS)
        在长直走廊中直接“跳过”中间节点，只在路口（交汇点）或死胡同停下。
        """
        def manhattan(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        g_score = {maze.start: 0}
        pq = [(manhattan(maze.start, maze.goal), maze.start, [maze.start])]
        explored_order = []
        explored_set = set()

        def jump(r, c, dr, dc):
            """核心跳跃函数：沿特定方向狂奔，直到遇到墙壁、终点或路口"""
            path = []
            while True:
                nr, nc = r + dr, c + dc
                if not maze.is_valid_move(nr, nc):
                    return None, path # 撞墙，此路不通
                
                path.append((nr, nc))
                if (nr, nc) == maze.goal:
                    return (nr, nc), path # 找到终点

                # 【检测路口】：对于四向网格，如果当前移动方向是 (dr, dc)
                # 那么它的正交（垂直）方向必定是 (dc, dr) 和 (-dc, -dr)
                for odr, odc in [(dc, dr), (-dc, -dr)]:
                    if maze.is_valid_move(nr + odr, nc + odc):
                        # 侧边有路可以走！这是一个路口（Junction），停止跳跃
                        return (nr, nc), path 
                
                # 如果没有遇到路口，继续沿着原方向迭代跳跃
                r, c = nr, nc

        while pq:
            _, current, path = heapq.heappop(pq)

            if current in explored_set:
                continue

            # 【可视化适配】：由于 JPS 跳过了中间节点
            # 为了让动画渲染出完整的光束，我们需要把跳跃经过的节点全部染色
            for node in path:
                if node not in explored_set:
                    explored_order.append(node)
                    explored_set.add(node)
            
            frontier = list({node for f, node, p in pq if node not in explored_set})
            yield SolverState(current, list(explored_order), frontier, path)

            if current == maze.goal:
                return

            # 不再一格一格试探，而是向四个方向发射“跳跃探测射线”
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                if not maze.is_valid_move(current[0] + dr, current[1] + dc):
                    continue
                
                jump_result, jump_path = jump(current[0], current[1], dr, dc)
                
                if jump_result is not None:
                    # 代价不再是 +1，而是要加上这次跳跃跨越的格数
                    tentative_g = g_score[current] + len(jump_path)
                    
                    if tentative_g < g_score.get(jump_result, float("inf")):
                        g_score[jump_result] = tentative_g
                        f_score = tentative_g + manhattan(jump_result, maze.goal)
                        # 将跳跃终点压入优先队列
                        heapq.heappush(pq, (f_score, jump_result, path + jump_path))
