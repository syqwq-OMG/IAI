# main.py
import random
import os
from generators import MazeGenerator
from solvers import MazeSolver
from visualizer import MazeVisualizer


def generate6gif(generator: MazeGenerator, seed=77, row=10, col=10):
    """生成六个算法的动画并保存为 GIF 文件"""

    gen_name = generator.__name__.replace("generate_", "")

    random.seed(seed)
    maze = generator(row, col)

    solvers = [MazeSolver.a_star, MazeSolver.dfs, MazeSolver.bfs, MazeSolver.dijkstra, MazeSolver.a_star_robust, MazeSolver.jps_4way]
    func_inst = zip(solvers, map(lambda f: f(maze), solvers))

    visualizer = MazeVisualizer(maze)

    dir_name = f"{gen_name}-{seed}-{row}x{col}"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    else:
        return print(f"Directory '{dir_name}' already exists. Skipping generation.")

    for func, inst in func_inst:
        visualizer.animate(
            inst,
            interval=1,
            save_path=dir_name + "/" + dir_name + "-" + func.__name__ + ".gif",
            title=f"{gen_name}-{seed}-{row}x{col} | {func.__name__}"
        )
    print(f"Generated GIFs for {gen_name} with seed={seed} at '{dir_name}/'.")
    print("-" * 60)


def main():
    generate6gif(MazeGenerator.generate_random_density, seed=10, row=10, col=10)
    generate6gif(MazeGenerator.generate_prim_maze, seed=10, row=10, col=10)
    generate6gif(MazeGenerator.generate_cave_maze, seed=10, row=10, col=10)
    generate6gif(MazeGenerator.generate_braid_maze, seed=10, row=10, col=10)
    generate6gif(MazeGenerator.generate_recursive_division, seed=10, row=10, col=10)
    generate6gif(MazeGenerator.generate_perfect_maze, seed=10, row=10, col=10)


if __name__ == "__main__":
    main()
