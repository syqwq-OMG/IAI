class Player:
    HUMAN = -1
    AI = 1


class Board:
    N = 15

    def __init__(self):
        self.board = [[0 for _ in range(Board.N)] for _ in range(Board.N)]

    def display(self):
        # column headers
        print("   ", end="")
        for col in range(Board.N):
            print(f"{col:3}", end="")
        print()

        # row headers and board content
        for row in range(Board.N):
            print(f"{row:2} ", end="")
            for col in range(Board.N):
                if (t := self.board[row][col]) == Player.HUMAN:
                    piece = "X"
                elif t == Player.AI:
                    piece = "O"
                else:
                    piece = "."
                print(f"{piece:>3}", end="")
            print()

    def valid(self, x: int, y: int) -> bool:
        return 0 <= x < Board.N and 0 <= y < Board.N and self.board[x][y] == 0

    def move(self, x: int, y: int, player: Player):
        if not self.valid(x, y):
            raise ValueError(f"invalid move at position ({x}, {y})!")
        self.board[x][y] = player

    def undo(self, x: int, y: int):
        if not (0 <= x < Board.N and 0 <= y < Board.N):
            raise ValueError(f"invalid undo at position ({x}, {y})!")
        self.board[x][y] = 0

    def empty_cells(self):
        return [
            (x, y)
            for x in range(Board.N)
            for y in range(Board.N)
            if self.board[x][y] == 0
        ]

    def any(self):
        return len(self.empty_cells()) > 0

    def check_win(self):
        for x in range(Board.N):
            for y in range(Board.N):
                if self.board[x][y] != 0:
                    player = self.board[x][y]
                    # --
                    if y + 4 < Board.N and all(
                        self.board[x][y + i] == player for i in range(5)
                    ):
                        return player
                    # |
                    if x + 4 < Board.N and all(
                        self.board[x + i][y] == player for i in range(5)
                    ):
                        return player
                    # \
                    if (
                        x + 4 < Board.N
                        and y + 4 < Board.N
                        and all(self.board[x + i][y + i] == player for i in range(5))
                    ):
                        return player
                    # /
                    if (
                        x + 4 < Board.N
                        and y - 4 >= 0
                        and all(self.board[x + i][y - i] == player for i in range(5))
                    ):
                        return player
        return None


def evaluate(board: Board) -> int:
    """
    evaluate the board state and return a score. Positive scores favor the AI, while negative scores favor the human player.
    """
    return 1


def get_moves(board: Board):
    """
    get potential moves from the current board state. For simplicity, we can return all empty cells, but in a more optimized version, we might want to return only those that are adjacent to existing pieces.
    """
    
    return board.empty_cells()


def minmax(board: Board, depth: int, alpha: int, beta: int, is_maximizing: bool) -> int:
    if depth == 0 or board.check_win() is not None:
        return evaluate(board)
    if is_maximizing:
        mxval = float("-inf")
        for x, y in get_moves(board):
            board.move(x, y, Player.AI)
            score = minmax(board, depth - 1, alpha, beta, False)
            board.undo(x, y)

            mxval = max(mxval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return mxval
    else:
        mnval = float("inf")
        for x, y in get_moves(board):
            board.move(x, y, Player.HUMAN)
            score = minmax(board, depth - 1, alpha, beta, True)
            board.undo(x, y)

            mnval = min(mnval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break

        return mnval


def find_best_move(board: Board, depth: int):
    bval = float("-inf")
    bmove = None
    alpha, beta = float("-inf"), float("inf")

    for x, y in get_moves(board):
        board.move(x, y, Player.AI)
        val = minmax(board, depth - 1, alpha, beta, False)
        board.undo(x, y)

        if val > bval:
            bval = val
            bmove = (x, y)
            
        alpha = max(alpha, bval)

    return bmove


if __name__ == "__main__":
    board = Board()
    while True:
        board.display()
        x, y = map(int, input("Enter your move (row col): ").split())
        board.move(x, y, Player.HUMAN)

        if board.check_win() == Player.HUMAN:
            print("Congratulations! You win!")
            break

        ai_move = find_best_move(board, depth=3)
        if ai_move:
            board.move(ai_move[0], ai_move[1], Player.AI)
            print(f"AI moves at ({ai_move[0]}, {ai_move[1]})")

            if board.check_win() == Player.AI:
                print("AI wins! Better luck next time.")
                break
        else:
            print("It's a draw!")
            break


"""
MCTS todo
"""
