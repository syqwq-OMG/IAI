import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from collections import deque
import heapq
import maza_generator

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def dfs_step_generator(maze, start, goal):
    """
    DFS 生成器：每进行一个核心步骤 (pop)，就 yield 当前算法状态。
    """
    rows = len(maze)
    cols = len(maze[0])

    # 栈内存储：(当前坐标, 走到当前坐标的路径)
    stack = [(start, [start])]
    visited = set()
    explored_order = []


    # 算法的核心循环
    while stack:
        current, path = stack.pop()

        # 排除已访问节点
        if current in visited:
            continue

        visited.add(current)
        explored_order.append(current)

        # 1. 获取栈内“下一个将要扩展的所有坐标” (Next)
        # 此时栈内的坐标都是已经准备好、但还没被取出扩展的
        next_to_be_explored = [node for (node, p) in stack if node not in visited]

        # 2. Yield 算法的“当前状态”给可视化函数
        # 数据包括: (当前点, 所有探索过的点, 栈内等待的点, 路径)
        yield current, list(explored_order), list(next_to_be_explored), path
        # -------------------

        # 如果到达终点，算法结束
        if current == goal:
            return  # 生成器结束

        # 遍历相邻的节点并将它们加入栈
        r, c = current
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))


def dijkstra_step_generator(maze, start, goal):
    """
    Dijkstra 生成器：利用优先队列，每次 yield 当前代价最小的节点状态。
    """
    rows = len(maze)
    cols = len(maze[0])

    # 优先队列内存储：(当前代价, 当前坐标, 走到当前坐标的路径)
    pq = [(0, start, [start])]

    # 记录到达每个节点的最短已知距离
    costs = {start: 0}
    explored_order = []


    while pq:
        # 弹出当前累计代价最小的节点
        current_cost, current, path = heapq.heappop(pq)

        # 如果这个节点之前已经找到过更短的路径，则跳过（处理优先队列中的冗余项）
        if current_cost > costs.get(current, float("inf")):
            continue

        explored_order.append(current)

        # 获取队列内“接下来等待扩展的所有坐标” (浅绿色格子)
        # 排除掉那些代价已经不是最优的陈旧记录
        next_to_be_explored = list(
            {node for cost, node, p in pq if cost <= costs.get(node, float("inf"))}
        )

        # Yield 当前状态
        yield current, list(explored_order), list(next_to_be_explored), path
        # -------------------

        if current == goal:
            return

        r, c = current
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                new_cost = current_cost + 1

                if new_cost < costs.get((nr, nc), float("inf")):
                    costs[(nr, nc)] = new_cost
                    heapq.heappush(pq, (new_cost, (nr, nc), path + [(nr, nc)]))


def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def a_star_step_generator(maze, start, goal):
    """
    A* 生成器：结合实际代价 (g) 和启发式预估代价 (h)，yield 最优探索状态。
    """
    rows = len(maze)
    cols = len(maze[0])

    g_score = {start: 0}
    f_start = manhattan_distance(start, goal)

    # 优先队列内存储：(f_score, 当前坐标, 走到当前坐标的路径)
    pq = [(f_start, start, [start])]

    explored_order = []
    explored_set = set()  # 用于快速检查是否已探索


    while pq:
        # 弹出 f_score (总预估代价) 最小的节点
        current_f, current, path = heapq.heappop(pq)

        if current in explored_set:
            continue

        explored_set.add(current)
        explored_order.append(current)

        # 获取队列内“接下来等待扩展的所有坐标” (浅绿色格子)，过滤掉已探索的
        next_to_be_explored = list(
            {node for f, node, p in pq if node not in explored_set}
        )

        # Yield 当前状态
        yield current, list(explored_order), list(next_to_be_explored), path
        # -------------------

        if current == goal:
            return

        r, c = current
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                tentative_g_score = g_score.get(current, float("inf")) + 1

                if tentative_g_score < g_score.get((nr, nc), float("inf")):
                    g_score[(nr, nc)] = tentative_g_score
                    f_score = tentative_g_score + manhattan_distance((nr, nc), goal)
                    heapq.heappush(pq, (f_score, (nr, nc), path + [(nr, nc)]))


def bfs_step_generator(maze, start, goal):
    """
    BFS 生成器：每弹出一个节点，就 yield 当前的搜索状态，用于生成动画。
    """
    rows = len(maze)
    cols = len(maze[0])

    # 队列内存储：(当前坐标, 走到当前坐标的路径)
    queue = deque([(start, [start])])

    # BFS 通常在入队时就标记为已访问，以防止同一个节点被多次加入队列
    visited = {start}
    explored_order = []


    while queue:
        # 从队首取出节点 (FIFO)
        current, path = queue.popleft()

        explored_order.append(current)

        # 获取队列内“接下来等待扩展的所有坐标” (浅绿色格子)
        next_to_be_explored = [node for (node, p) in queue]

        # Yield 算法的“当前状态”给可视化函数
        yield current, list(explored_order), list(next_to_be_explored), path
        # -------------------

        # 如果到达终点，算法结束
        if current == goal:
            return

        # 遍历相邻的节点
        r, c = current
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    # 将新节点加入队尾
                    queue.append(((nr, nc), path + [(nr, nc)]))


def visualize_maze_animation(maze, generator, goal_pos=(0,0)):
    """
    使用 FuncAnimation 实现迷宫寻路动画。
    """
    fig, ax = plt.figure(figsize=(10, 8)), plt.gca()

    # 绘制基础迷宫图 (Grey 为墙，White 为路)
    ax.imshow(maze, cmap="Greys", interpolation="nearest", aspect="equal")

    # 初始化需要动态更新的 Patch 集合
    explored_patches = []  # 已扩展 (Light Blue)
    stack_patches = []  # 栈内等待 (Light Green)
    current_patch = []  # 当前位置 (Yellow)
    goal_patch = []  # 终点位置 (Dark Green)
    path_line = []  # 路径红线

    # 设置坐标轴
    ax.set_xticks(range(len(maze[0])))
    ax.set_yticks(range(len(maze)))
    ax.set_xticks([x - 0.5 for x in range(1, len(maze[0]))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(maze))], minor=True)
    ax.grid(which="minor", color="lightgrey", linestyle="-", linewidth=2)
    ax.axis("on")
    ax.set_title("Maze Solver Animation")

    # 为了方便管理，定义一个清理 function 专门清除旧的状态 Patch
    def clear_dynamic_patches(patches_list):
        while patches_list:
            patches_list.pop().remove()

    # --- [动画更新函数] ---
    # 这个函数是 FuncAnimation 的核心，每帧会调用一次，
    # data 参数来自于生成器 yield 的值。
    def update(data):
        # 1. 拆包生成器提供的数据
        current, explored, stack_nodes, path = data

        # --- 2. 清除前一帧的动态状态 Patch ---
        clear_dynamic_patches(explored_patches)
        clear_dynamic_patches(stack_patches)
        clear_dynamic_patches(current_patch)
        clear_dynamic_patches(goal_patch)
        clear_dynamic_patches(path_line)

        # --- 3. 绘制最新状态 ---

        # (1) 绘制所有“已探索过的位置” (浅蓝色背景)
        for r, c in explored:
            if (r, c) != current:  # 避开当前点，防止颜色重叠
                rect = patches.Rectangle(
                    (c - 0.5, r - 0.5),
                    1,
                    1,
                    linewidth=0,
                    facecolor="lightblue",
                    alpha=0.6,
                )
                rect_ref = ax.add_patch(rect)
                explored_patches.append(rect_ref)

        # (2) 绘制“栈内所有等待扩展的位置” (浅绿色)
        # 注意: DFS 的 Next 位置通常只是栈顶的一个，这里画出所有在栈里的点
        for r, c in stack_nodes:
            rect = patches.Rectangle(
                (c - 0.5, r - 0.5), 1, 1, linewidth=0, facecolor="lightgreen", alpha=0.8
            )
            rect_ref = ax.add_patch(rect)
            stack_patches.append(rect_ref)

        # (3) 绘制“终点” (深绿色背景)
        goal_r, goal_c = goal_pos
        rect = patches.Rectangle(
            (goal_c - 0.5, goal_r - 0.5),
            1,
            1,
            linewidth=0,
            facecolor="darkgreen",
            alpha=0.9,
        )
        goal_ref = ax.add_patch(rect)
        goal_patch.append(goal_ref)

        # (4) 绘制“当前扩展的位置” (黄色小圆点或小方块)
        rect = patches.Rectangle(
            (current[1] - 0.5, current[0] - 0.5),
            1,
            1,
            linewidth=0,
            facecolor="yellow",
            alpha=1.0,
        )
        curr_ref = ax.add_patch(rect)
        current_patch.append(curr_ref)

        # (5) 绘制“到当前为止的路径” (红线)
        if path and len(path) > 1:
            path_x, path_y = zip(*path)
            (line_ref,) = ax.plot(
                path_y,
                path_x,
                marker="o",
                markersize=6,
                color="red",
                linewidth=3,
                alpha=0.7,
            )
            path_line.append(line_ref)

        # 返回被更新过的 artist 对象列表
        return explored_patches + stack_patches + current_patch + goal_patch + path_line

    # 3. 创建动画
    # fig: 画布
    # update: 更新函数
    # frames=generator: 数据源是我们的算法生成器
    # blit=False: 是否只重新绘制变化的部分 (True 性能好但实现复杂，False 方便调试)
    # interval=300: 帧之间间隔的毫秒数 (用于控制动画速度)
    # repeat=False: 动画运行完不重复
    ani = animation.FuncAnimation(
        fig, update, frames=generator, blit=True, interval=300, repeat=False
    )

    # plt.show()
    return ani  # 必须要保持这个引用，否则动画会被垃圾回收


# ---------------------------------------------------------
# 3. 测试与运行
# ---------------------------------------------------------
# 定义一个 10x10 的迷宫
maze_10x10 = [
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 1, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
]

# start_pos = (0, 0)
# goal_pos = (9,9)

# 1. 初始化生成器
# gen = a_star_step_generator(maze_10x10, start_pos, goal_pos)

# 2. 开始播放动画
# ani = visualize_maze_animation(maze_10x10, gen)
# ani.save("astar_maze_solution.gif", writer="pillow", fps=5)
