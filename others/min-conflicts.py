import random

def min_conflicts(n, max_steps=1000):
    """
    使用 Min-Conflicts 启发式解决 N 皇后问题
    :param n: 皇后的数量 (N)
    :param max_steps: 最大迭代步数
    :return: 成功返回 board 列表，失败返回 None
    """
    # 1. 状态初始化：随机给每列的皇后分配一个行位置
    board = [random.randint(0, n - 1) for _ in range(n)]

    def count_conflicts(var, val, current_board):
        """
        计算将第 var 列的皇后放在第 val 行时，会和多少个现有的皇后产生冲突
        """
        conflicts = 0
        for i in range(n):
            if i == var:
                continue
            # 检查是否在同一行 (val == current_board[i]) 
            # 检查是否在对角线上 (行差的绝对值 == 列差的绝对值)
            if current_board[i] == val or abs(current_board[i] - val) == abs(i - var):
                conflicts += 1
        return conflicts

    # 2. 迭代改进 (局部搜索)
    for step in range(max_steps):
        # 找出当前所有存在冲突的皇后（记录她们的列号）
        conflicted_vars = []
        for i in range(n):
            if count_conflicts(i, board[i], board) > 0:
                conflicted_vars.append(i)

        # 如果没有冲突的皇后，说明达到了全局最优解
        if not conflicted_vars:
            print(f"🎉 成功！在第 {step} 步找到解。")
            return board

        # 随机挑选一个有冲突的皇后
        var = random.choice(conflicted_vars)

        # 遍历该皇后所在列的所有行，找到能让冲突数最小化的行
        min_c = float('inf')
        best_vals = []

        for val in range(n):
            c = count_conflicts(var, val, board)
            if c < min_c:
                min_c = c
                best_vals = [val]  # 发现更小的冲突数，重置最佳候选列表
            elif c == min_c:
                best_vals.append(val) # 冲突数一样，加入候选列表

        # 如果有多个行的冲突数同为最小，随机选择一个（打破平局，防止陷入局部死循环）
        board[var] = random.choice(best_vals)

    print("❌ 达到最大步数，未能找到解。")
    return None

def print_board(board):
    """在终端打印可视化棋盘"""
    if not board:
        return
    n = len(board)
    for row in range(n):
        line = ""
        for col in range(n):
            if board[col] == row:
                line += " Q "
            else:
                line += " . "
        print(line)

# 测试运行 8 皇后
if __name__ == "__main__":
    n = 200
    # 局部搜索具有随机性，通常在几十步内就能收敛
    solution = min_conflicts(n, max_steps=1000)
    
    if solution:
        print_board(solution)
        print(f"最终的内部状态表示 (数组索引为列，值为行): {solution}")