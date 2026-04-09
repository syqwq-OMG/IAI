#include <cstdio>
#include <iostream>
using namespace std;

// human: x
// ai: o
// empty: NULL

constexpr int N = 5;
constexpr int inf = 0x3f3f3f3f;

char board[N][N];

void init() {
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            board[i][j] = 0;
}

int evaluate() {
    /*
    since the game state space is small, we can directly check if there is a
    winner. If there is a winner, return 10 for ai and -10 for human. If there
    is no winner, return 0.

    otherwise, evaluate function should return a score based on the current
    board state.
    */
    auto ret_score = [&](int x, int y) -> int {
        return board[x][y] == 'o' ? 10 : -10;
    };

    auto &b = board;

    for (int i = 0; i < 3; i++) {
        if (b[i][0] && b[i][0] == b[i][1] && b[i][1] == b[i][2])
            return ret_score(i, 0); // row
        if (b[0][i] && b[0][i] == b[1][i] && b[1][i] == b[2][i])
            return ret_score(0, i); // column
    }
    // diagonal
    if (b[0][0] && b[0][0] == b[1][1] && b[1][1] == b[2][2])
        return ret_score(0, 0);
    if (b[0][2] && b[0][2] == b[1][1] && b[1][1] == b[2][0])
        return ret_score(0, 2);
    return 0;
}

bool is_moves_left() {
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            if (!board[i][j])
                return true;
    return false;
}

int minmax(int dep, bool is_max) {
    /*
    best outcome for ai is 10, worst outcome for ai is -10, and draw is 0.
    if ai wins, return 10 - depth (to prefer faster wins)
    if human wins, return -10 + depth (to prefer slower losses)
    return best score that can be achieved from the current board state,
    assuming both players play optimally.
    */
    int score = evaluate();
    if (score == 10)
        return score - dep;
    if (score == -10)
        return score + dep;
    if (!is_moves_left())
        return 0;

    if (is_max) { // ai's turn
        int best = -inf;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (!board[i][j]) {
                    board[i][j] = 'o';
                    best = max(best, minmax(dep + 1, false));
                    board[i][j] = 0;
                }
            }
        }
        return best;
    } else { // human's turn
        int best = inf;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (!board[i][j]) {
                    board[i][j] = 'x';
                    best = min(best, minmax(dep + 1, true));
                    board[i][j] = 0;
                }
            }
        }
        return best;
    }
}

tuple<int, int> find_best_move() {
    int bval = -inf, bx = -1, by = -1;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (!board[i][j]) {
                board[i][j] = 'o';
                int val = minmax(0, false);
                board[i][j] = 0;
                if (val > bval) {
                    bval = val;
                    bx = i;
                    by = j;
                }
            }
        }
    }
    return {bx, by};
}

void print_board() {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cout << (board[i][j] ? board[i][j] : '.') << " ";
        }
        cout << endl;
    }
}

int main() {
    init();

    while (true) {
        fflush(stdout);
        print_board();
        int x, y;
        cout << "Enter your move (row and column): ";
        cin >> x >> y;
        if (board[x][y]) {
            cout << "Invalid move. Try again." << endl;
            continue;
        }
        board[x][y] = 'x';
        if (evaluate() == -10) {
            print_board();
            cout << "You win!" << endl;
            break;
        }
        if (!is_moves_left()) {
            print_board();
            cout << "It's a draw!" << endl;
            break;
        }
        auto [bx, by] = find_best_move();
        board[bx][by] = 'o';
        if (evaluate() == 10) {
            print_board();
            cout << "AI wins!" << endl;
            break;
        }
    }

    return 0;
}