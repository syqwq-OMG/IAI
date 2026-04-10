# benchmark.py
import time
import random
from generators import MazeGenerator
from solvers import MazeSolver

def benchmark_algorithm(generator_func, rows: int, cols: int, seed: int = None, **kwargs):
    """
    对指定的迷宫生成策略进行四大算法的性能评测
    """
    # 1. 设置全局随机种子，确保实验可重复
    if seed is not None:
        random.seed(seed)
    
    gen_name = generator_func.__name__.replace("generate_", "")
    print(f"=== 迷宫寻路算法性能评测 ===")
    print(f"地图类型: {gen_name:<18} | 尺寸: {rows}x{cols} | 随机种子: {seed}")
    
    # 2. 生成迷宫
    # 捕获并传递 kwargs，比如 wall_probability 或 iterations
    maze = generator_func(rows, cols, **kwargs)

    # 3. 准备评测算法集合
    algorithms = {
        "DFS": MazeSolver.dfs,
        "BFS": MazeSolver.bfs,
        "Dijkstra": MazeSolver.dijkstra,
        "A*": MazeSolver.a_star,
        "A*_cross": MazeSolver.a_star_robust,
        "JPS_4way": MazeSolver.jps_4way
    }

    # 表头格式化
    header = f"{'Algorithm':<15} | {'Path Length':<12} | {'Explored Nodes':<15} | {'Time (ms)':<10}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)
 
    # 4. 依次执行算法并统计指标
    for algo_name, solver_func in algorithms.items():
        solver_gen = solver_func(maze)
        
        # 使用高精度计时器
        start_time = time.perf_counter()
        
        # 快速消耗掉生成器，直到拿到最后一个状态 (也就是寻路结束时的状态)
        final_state = None
        for state in solver_gen:
            final_state = state
            
        end_time = time.perf_counter()

        # 计算各项指标
        time_ms = (end_time - start_time) * 1000
        path_len = len(final_state.path) if final_state.path else 0
        explored_count = len(final_state.explored)
        
        # 格式化输出
        print(f"{algo_name:<15} | {path_len:<12} | {explored_count:<15} | {time_ms:.2f}")
        
    print(separator + "\n")

def main():
    # 设定统一的测试参数
    TEST_ROWS = 151
    TEST_COLS = 151
    TEST_SEED = 2026

    # 1. 测试稀疏迷宫
    benchmark_algorithm(
        MazeGenerator.generate_random_density, 
        TEST_ROWS, TEST_COLS, seed=TEST_SEED, wall_probability=0.2
    )

    # 2. 测试完美迷宫 (DFS 生成)
    benchmark_algorithm(
        MazeGenerator.generate_perfect_maze, 
        TEST_ROWS, TEST_COLS, seed=TEST_SEED
    )

    # 3. 测试自然洞穴迷宫
    benchmark_algorithm(
        MazeGenerator.generate_cave_maze, 
        TEST_ROWS, TEST_COLS, seed=TEST_SEED
    )

    # 4. 测试 Prim 算法生成的多死胡同迷宫
    benchmark_algorithm(
        MazeGenerator.generate_prim_maze, 
        TEST_ROWS, TEST_COLS, seed=TEST_SEED
    )

if __name__ == "__main__":
    main()