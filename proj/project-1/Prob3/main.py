import maze_visualization
import maza_generator

if __name__ == "__main__":
    maze = maza_generator.MazeGenerator.generate_perfect_maze(8,8)
    st=(0,0)
    ed=(8,8)
    gen = maze_visualization.a_star_step_generator(maze, st, ed)
    
    ani = maze_visualization.visualize_maze_animation(maze, gen, goal_pos=ed)
    ani.save("a_star2020_maze_solution.gif", writer="pillow", fps=5)
