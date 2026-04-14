import random

def slot(mu, sigma):
    def f(m, s):
        while True:
            yield random.gauss(m, s)
    return f(mu, sigma)

def solve(T, N, slots, init_val=1300.0, eps=0.1):
    # Q 记录每个动作的估计价值
    Q = [init_val] * N
    # counts 记录每个动作被选中的次数
    counts = [0] * N 
    
    for t in range(T):
        prob = random.random()
        # 探索 (Exploration)：以 eps 的概率随机选择
        if prob < eps:
            action = random.randint(0, N - 1)
        # 利用 (Exploitation)：选择当前 Q 值最大的动作
        else:
            action = Q.index(max(Q))
            
        reward = next(slots[action])
        
        # 更新该动作的计数
        counts[action] += 1
        
        # 使用增量公式更新 Q 值（更稳定，且基于动作自己的专属计数）
        Q[action] = Q[action] + (reward - Q[action]) / counts[action]

    return Q, counts

if __name__ == "__main__":
    # 老虎机 1：平均收益 500，波动较小
    s1 = slot(500, 10)
    # 老虎机 2：平均收益 600，波动较大
    s2 = slot(600, 30)
    slots = [s1, s2]

    # 注意：通常 eps 会设置得稍微大一点，比如 0.1 (10%的概率探索)
    Q_values, action_counts = solve(T=10000, N=2, slots=slots, eps=0.1)
    
    print(f"最终估计的 Q 值: {Q_values}")
    print(f"每个老虎机被拉动的次数: {action_counts}")