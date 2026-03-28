# visualizer.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from typing import Iterator
from maze import Maze, SolverState


class MazeVisualizer:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self._setup_plot()

        # 保存动态绘制对象的引用以便清除
        self.dynamic_patches = {
            "explored": [],
            "frontier": [],
            "current": [],
            "goal": [],
            "path": [],
        }

    def _setup_plot(self):
        self.ax.imshow(
            self.maze.grid, cmap="Greys", interpolation="nearest", aspect="equal"
        )
        self.ax.set_xticks(range(self.maze.cols))
        self.ax.set_yticks(range(self.maze.rows))
        self.ax.set_xticks([x - 0.5 for x in range(1, self.maze.cols)], minor=True)
        self.ax.set_yticks([y - 0.5 for y in range(1, self.maze.rows)], minor=True)
        self.ax.grid(which="minor", color="lightgrey", linestyle="-", linewidth=2)
        self.ax.axis("on")
        self.ax.set_title("Maze Solver Animation")

    def _clear_patches(self, key: str):
        while self.dynamic_patches[key]:
            self.dynamic_patches[key].pop().remove()

    def _add_rect(self, r, c, color, alpha=1.0) -> patches.Rectangle:
        rect = patches.Rectangle(
            (c - 0.5, r - 0.5), 1, 1, linewidth=0, facecolor=color, alpha=alpha
        )
        return self.ax.add_patch(rect)

    def _update_frame(self, state: SolverState):
        for key in self.dynamic_patches.keys():
            self._clear_patches(key)

        # 1. 绘制已探索节点
        for r, c in state.explored:
            if (r, c) != state.current:
                self.dynamic_patches["explored"].append(
                    self._add_rect(r, c, "lightblue", 0.6)
                )

        # 2. 绘制待探索节点 (Frontier)
        for r, c in state.frontier:
            self.dynamic_patches["frontier"].append(
                self._add_rect(r, c, "purple", 0.8)
            )

        # 3. 绘制终点
        goal_r, goal_c = self.maze.goal
        self.dynamic_patches["goal"].append(
            self._add_rect(goal_r, goal_c, "darkgreen", 0.9)
        )

        # 4. 绘制当前节点
        curr_r, curr_c = state.current
        self.dynamic_patches["current"].append(
            self._add_rect(curr_r, curr_c, "yellow", 1.0)
        )

        # 5. 绘制路径
        if state.path and len(state.path) > 1:
            path_x, path_y = zip(*state.path)
            (line_ref,) = self.ax.plot(
                path_y,
                path_x,
                marker="o",
                markersize=6,
                color="red",
                linewidth=3,
                alpha=0.7,
            )
            self.dynamic_patches["path"].append(line_ref)

        return [patch for group in self.dynamic_patches.values() for patch in group]

    def animate(
        self, solver_generator: Iterator[SolverState], interval=100, save_path=None
    ):
        ani = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            frames=solver_generator,
            blit=True,
            interval=interval,
            repeat=False,
        )
        if save_path:
            ani.save(save_path, writer="pillow", fps=1000 // interval)
        plt.show()
        return ani
