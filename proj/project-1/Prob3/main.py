# main.py
import random

from generators import MazeGenerator
from solvers import MazeSolver
from visualizer import MazeVisualizer


def main():
    seed_value = 42
    seed_value = 77
    seed_value = 20041116
    random.seed(seed_value)
    
    # 1. 选择生成策略：生成一个迷宫
    print("Generating Maze...")
    # maze = MazeGenerator.generate_random_density(15, 15)
    maze = MazeGenerator.generate_recursive_division(60, 60)
    # maze = MazeGenerator.generate_perfect_maze(40, 40)
    # maze = MazeGenerator.generate_perfect_maze(60, 60)

    # 2. 选择求解策略：创建一个求解状态生成器
    print("Initializing Solver...")
    # solver_gen = MazeSolver.dfs(maze)
    solver_gen = MazeSolver.a_star(maze)

    # 3. 将两者注入可视化器并启动
    print("Starting Animation...")
    visualizer = MazeVisualizer(maze)

    # 你可以只显示动画
    visualizer.animate(solver_gen, interval=1)

    # 或者保存为 GIF
    # visualizer.animate(solver_gen, interval=150, save_path="astar_solution.gif")


if __name__ == "__main__":
    main()
