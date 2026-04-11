#include <iostream>
#include <utility>

#define fi first
#define se second

using namespace std;

// 星球地形图 (10x10)
// 注意观察：左上角有一个海拔为 8 的“小假山”，右下角有一个海拔为 9 的“大火山”
const int N = 10;
int grid[N][N] = {
    {1, 1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 2, 3, 2, 1, 1, 4, 5, 4, 1},
    {1, 3, 8, 3, 1, 1, 5, 7, 5, 1}, // (2, 2) 是局部最优坑
    {1, 2, 3, 2, 1, 1, 4, 5, 4, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 2, 3, 2, 1, 1}, {1, 1, 1, 1, 2, 4, 6, 4, 2, 1},
    {1, 1, 1, 2, 4, 7, 9, 7, 4, 1}, // (7, 6) 是全局最优峰
    {1, 1, 1, 1, 2, 4, 6, 4, 2, 1}, {1, 1, 1, 1, 1, 2, 3, 2, 1, 1}};

// 四个探测方向：上，下，左，右
int dx[] = {-1, 1, 0, 0};
int dy[] = {0, 0, -1, 1};

void hill_climbing(int start_x, int start_y) {
    pair<int, int> cur(start_x, start_y);
    int steps = 0;

    cout << "\n🚀 探测车空投至坐标 (" << cur.fi << ", " << cur.se
         << ")，初始海拔: " << grid[cur.fi][cur.se] << "\n";
    cout << "----------------------------------------\n";

    while (true) {
        int cur_h = grid[cur.fi][cur.se];
        int best_h = cur_h;
        pair<int, int> next_pos = cur;

        // 1. 试探四周的 4 个格子
        for (int i = 0; i < 4; i++) {
            int nx = cur.fi + dx[i];
            int ny = cur.se + dy[i];

            // 确保不越界
            if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                int neighbor_h = grid[nx][ny];
                // 记录四周海拔最高的位置（最陡上升）
                if (neighbor_h > best_h) {
                    best_h = neighbor_h;
                    next_pos = make_pair(nx, ny);
                }
            }
        }

        // 2. 核心判断：如果四周最高的地方都没有我现在脚下高，说明登顶了
        if (best_h == cur_h) {
            cout << "📡 四周没有更高的地势了。探测车在坐标 (" << cur.fi << ", "
                 << cur.se << ") 展开天线，最终海拔: " << cur_h << "。\n";

            if (cur_h == 9)
                cout << "✅ 恭喜！找到了全局最优通讯点！\n";
            else
                cout << "❌ 糟糕！陷入了局部最优解（假山顶），信号微弱！\n";
            break;
        }

        // 3. 贪心移动：开向最高点
        cur = next_pos;
        steps++;
        cout << "步数 " << steps << " -> 移动到坐标 (" << cur.fi << ", "
             << cur.se << ")，当前海拔: " << best_h << "\n";
    }
}

int main() {
    // 剧本 A：运气不好，降落在假山附近
    hill_climbing(0, 0);

    // 剧本 B：运气很好，降落在火山附近
    hill_climbing(5, 5);

    return 0;
}