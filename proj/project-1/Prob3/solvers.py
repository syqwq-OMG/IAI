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
