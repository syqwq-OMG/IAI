# benchmark.py
import time
import random
from generators import MazeGenerator
from solvers import MazeSolver

# 定义全局测试的算法池，你可以在这里随时添加或注释掉某个算法
ALGORITHMS = {
    "DFS": MazeSolver.dfs,
    "BFS": MazeSolver.bfs,
    "Dijkstra": MazeSolver.dijkstra,
    "A*": MazeSolver.a_star,
    "A* cross": MazeSolver.a_star_cross,
    "JPS (4-Way)": MazeSolver.jps_4way
}

def _run_solver(solver_func, maze):
    """底层辅助函数：运行单个算法并返回 (路径长度, 探索节点数, 耗时ms)"""
    start_time = time.perf_counter()
    final_state = None
    
    # 快速消耗生成器
    for state in solver_func(maze):
        final_state = state
        
    end_time = time.perf_counter()
    time_ms = (end_time - start_time) * 1000
    path_len = len(final_state.path) if final_state.path else 0
    explored_count = len(final_state.explored)
    
    return path_len, explored_count, time_ms


# =====================================================================
# 维度 1：不同算法在同一个种子的同一个地图下的表现 (横向对比)
# =====================================================================
def dif_algo_same_seed_maze(generator_func, rows: int, cols: int, seed: int = 42, **kwargs):
    gen_name = generator_func.__name__.replace("generate_", "")
    print(f"\n=== [维度 1] 同地图多算法横向对比 ===")
    print(f"地图: {gen_name} | 尺寸: {rows}x{cols} | 种子: {seed}")
    
    if seed is not None:
        random.seed(seed)
    maze = generator_func(rows, cols, **kwargs)

    header = f"{'Algorithm':<18} | {'Path Length':<12} | {'Explored Nodes':<15} | {'Time (ms)':<10}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for algo_name, solver_func in ALGORITHMS.items():
        path_len, explored, time_ms = _run_solver(solver_func, maze)
        print(f"{algo_name:<18} | {path_len:<12} | {explored:<15} | {time_ms:.2f}")


# =====================================================================
# 维度 2：同一个算法在不同种子，不同大小的地图下的表现 (扩展性测试)
# =====================================================================
def same_algo_dif_seed_mazesize(solver_name: str, generator_func, configs: list, **kwargs):
    """
    configs: 一个包含 (rows, cols, seed) 元组的列表
    """
    solver_func = ALGORITHMS[solver_name]
    gen_name = generator_func.__name__.replace("generate_", "")
    print(f"\n=== [维度 2] 单一算法跨尺度/跨种子测试 ===")
    print(f"算法: {solver_name} | 地图类型: {gen_name}")
    
    header = f"{'Size (RxC)':<12} | {'Seed':<6} | {'Path Length':<12} | {'Explored Nodes':<15} | {'Time (ms)':<10}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for rows, cols, seed in configs:
        random.seed(seed)
        maze = generator_func(rows, cols, **kwargs)
        path_len, explored, time_ms = _run_solver(solver_func, maze)
        size_str = f"{rows}x{cols}"
        print(f"{size_str:<12} | {seed:<6} | {path_len:<12} | {explored:<15} | {time_ms:.2f}")


# =====================================================================
# 维度 3：不同算法在同一个类型地图下的平均表现 (蒙特卡洛平均)
# =====================================================================
def dif_algo_same_mazetype(generator_func, rows: int, cols: int, trials: int = 10, **kwargs):
    gen_name = generator_func.__name__.replace("generate_", "")
    print(f"\n=== [维度 3] 同类型地图多次随机采样平均表现 ===")
    print(f"地图: {gen_name} | 尺寸: {rows}x{cols} | 采样次数: {trials}")

    # 初始化统计字典
    stats = {algo: {"path": 0, "explored": 0, "time": 0.0} for algo in ALGORITHMS}

    for i in range(trials):
        # 每次使用不同的随机种子
        seed = random.randint(1, 99999)
        random.seed(seed)
        maze = generator_func(rows, cols, **kwargs)

        for algo_name, solver_func in ALGORITHMS.items():
            p_len, exp, t_ms = _run_solver(solver_func, maze)
            stats[algo_name]["path"] += p_len
            stats[algo_name]["explored"] += exp
            stats[algo_name]["time"] += t_ms

    header = f"{'Algorithm':<18} | {'Avg Path Len':<12} | {'Avg Explored':<15} | {'Avg Time (ms)':<12}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for algo_name, data in stats.items():
        avg_path = data["path"] / trials
        avg_exp = data["explored"] / trials
        avg_time = data["time"] / trials
        print(f"{algo_name:<18} | {avg_path:<12.1f} | {avg_exp:<15.1f} | {avg_time:.2f}")


# =====================================================================
# 维度 4：不同地图在平均下的最优算法 (综合评估)
# =====================================================================
def opt_algo_under_dif_maze(generators_dict: dict, rows: int, cols: int, trials: int = 5):
    print(f"\n=== [维度 4] 各类型地图的平均最优算法盘点 ===")
    print(f"统一尺寸: {rows}x{cols} | 单图采样次数: {trials}")
    print("评判标准：平均探索节点数最少 (效率最高)\n")

    for gen_name, gen_func in generators_dict.items():
        best_algo = None
        min_explored = float('inf')
        best_time = 0.0

        stats = {algo: {"explored": 0, "time": 0.0} for algo in ALGORITHMS}

        for _ in range(trials):
            random.seed(random.randint(1, 99999))
            maze = gen_func(rows, cols)
            for algo_name, solver_func in ALGORITHMS.items():
                _, exp, t_ms = _run_solver(solver_func, maze)
                stats[algo_name]["explored"] += exp
                stats[algo_name]["time"] += t_ms

        for algo_name, data in stats.items():
            avg_exp = data["explored"] / trials
            avg_time = data["time"] / trials
            
            if avg_exp < min_explored:
                min_explored = avg_exp
                best_algo = algo_name
                best_time = avg_time

        print(f"地图类型: {gen_name:<20} => 👑 最佳算法: {best_algo:<15} (平均探索: {min_explored:.1f} 节点, {best_time:.2f} ms)")


# =====================================================================
# 主函数：运行所有维度的测试案例
# =====================================================================
def main():
    # 1. 运行维度 1：稀疏迷宫中的一次具体较量
    dif_algo_same_seed_maze(MazeGenerator.generate_random_density, rows=51, cols=51, seed=2026, wall_probability=0.2)

    # 2. 运行维度 2：观察 A* (Robust) 在不同规模洞穴迷宫中的时间复杂度增长
    test_configs = [
        (21, 21, 10),
        (41, 41, 42),
        (61, 61, 100),
        (81, 81, 999)
    ]
    same_algo_dif_seed_mazesize("A*", MazeGenerator.generate_cave_maze, test_configs)

    # 3. 运行维度 3：在完美迷宫中跑 10 次取平均，消除偶然性
    dif_algo_same_mazetype(MazeGenerator.generate_perfect_maze, rows=31, cols=31, trials=10)

    # 4. 运行维度 4：决出每种地形的真正王者
    generators_to_test = {
        "Random Density (20%)": lambda r, c: MazeGenerator.generate_random_density(r, c, 0.2),
        "Perfect/DFS Maze": MazeGenerator.generate_perfect_maze,
        "Cave/Cellular": MazeGenerator.generate_cave_maze,
        "Prim's Maze": MazeGenerator.generate_prim_maze,
        "Recursive Division": MazeGenerator.generate_recursive_division
    }
    opt_algo_under_dif_maze(generators_to_test, rows=41, cols=41, trials=5)


if __name__ == "__main__":
    main()