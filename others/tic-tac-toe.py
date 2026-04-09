def evaluate(board):
    # 所有的获胜组合：3行，3列，2条对角线
    win_patterns = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],  # 行
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],  # 列
        [0, 4, 8],
        [2, 4, 6],  # 对角线
    ]

    for pattern in win_patterns:
        if board[pattern[0]] == board[pattern[1]] == board[pattern[2]]:
            if board[pattern[0]] == "X":
                return 10  # AI 赢
            elif board[pattern[0]] == "O":
                return -10  # 人类赢
    return 0  # 没分出胜负或平局


def is_moves_left(board):
    return " " in board


def minimax(board, depth, is_maximizing):
    score = evaluate(board)

    # 1. 递归终止条件：有人赢了，或者棋盘满了（平局）
    if score == 10:
        return score - depth  # AI 赢，步数越少越好
    if score == -10:
        return score + depth  # 人类赢，步数越多越好（尽可能拖延）
    if not is_moves_left(board):
        return 0

    # 2. 如果轮到 AI (Maximizer) 走棋
    if is_maximizing:
        best_score = -float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "X"  # 假设 AI 走这一步
                # 递归计算这一步的最终得分，下一轮轮到 Minimizer
                current_score = minimax(board, depth + 1, False)
                board[i] = " "  # 撤销这一步（回溯）
                best_score = max(best_score, current_score)
        return best_score

    # 3. 如果轮到人类 (Minimizer) 走棋
    else:
        best_score = float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"  # 假设人类走这一步
                # 递归计算这一步的最终得分，下一轮轮到 Maximizer
                current_score = minimax(board, depth + 1, True)
                board[i] = " "  # 撤销这一步（回溯）
                best_score = min(best_score, current_score)
        return best_score


def find_best_move(board):
    best_score = -float("inf")
    best_move = -1

    for i in range(9):
        if board[i] == " ":
            board[i] = "X"  # 尝试落子
            # 计算这步棋的价值（由于这步是 AI 走的，下一层递归应该是 False/人类的回合）
            move_val = minimax(board, 0, False)
            board[i] = " "  # 撤销落子

            # 记录产生最高分数的移动位置
            if move_val > best_score:
                best_move = i
                best_score = move_val

    return best_move


def print_board(board):
    for i in range(0, 9, 3):
        print(f" {board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("---+---+---")


# 初始棋盘
current_board = [" "] * 9

while is_moves_left(current_board) and evaluate(current_board) == 0:
    # 假设人类先手 (O)
    human_move = int(input("轮到你了 (输入 0-8 选择位置): "))
    if current_board[human_move] == " ":
        current_board[human_move] = "O"
    else:
        print("这个位置已经被占用了！")
        continue

    print_board(current_board)
    print("=" * 15)

    if not is_moves_left(current_board) or evaluate(current_board) != 0:
        break

    # AI 回合 (X)
    print("AI 正在思考...")
    ai_move = find_best_move(current_board)
    current_board[ai_move] = "X"
    print_board(current_board)
    print("=" * 15)

# 判断最终结果
final_score = evaluate(current_board)
if final_score > 0:
    print("AI 赢了！")
elif final_score < 0:
    print("你赢了！(这理论上是不可能的)")
else:
    print("平局！")
