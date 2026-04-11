import random
import matplotlib.pyplot as plt

# ==========================================
# 1. 极限环境设定 (30门课 完美填满 30个坑位)
# ==========================================
ROOMS = ['Room_101', 'Room_102', 'Room_103']
TIMESLOTS = [f'Day{d}_Slot{s}' for d in range(1, 6) for s in (1, 2)] # 一周5天，每天上下午2节，共10节
TEACHERS = ['Teacher_A', 'Teacher_B', 'Teacher_C']

# 生成30门课，每个老师均摊10门
COURSES = []
for i in range(30):
    COURSES.append({
        'id': f'C{i+1:02d}', 
        'teacher': TEACHERS[i % 3] # 老师A, B, C循环分配
    })

# 遗传算法超参数
POPULATION_SIZE = 100  # 种群数量加大，增加基因多样性
GENERATIONS = 600      # 繁衍代数增加，因为问题变难了
MUTATION_RATE = 0.15   # 变异率稍微调高，防止早熟陷入局部最优

# ==========================================
# 2. 核心适应度函数 (计算冲突)
# ==========================================
def create_individual():
    """生成一个个体：为每门课随机分配 (教室, 时间)"""
    return [(random.choice(ROOMS), random.choice(TIMESLOTS)) for _ in COURSES]

def calculate_conflicts(individual):
    """
    计算冲突数（越小越好，完美课表冲突为0）
    """
    room_time_usage = set()
    teacher_time_usage = set()
    conflicts = 0
    
    for idx, (room, time) in enumerate(individual):
        teacher = COURSES[idx]['teacher']
        
        # 1. 教室冲突：这个时间，这个教室已经有课了吗？
        rt_key = (room, time)
        if rt_key in room_time_usage:
            conflicts += 1
        else:
            room_time_usage.add(rt_key)
            
        # 2. 教师冲突：这个时间，这个老师已经在其他教室上课了吗？
        tt_key = (teacher, time)
        if tt_key in teacher_time_usage:
            conflicts += 1
        else:
            teacher_time_usage.add(tt_key)
            
    return conflicts

# ==========================================
# 3. 遗传算子 (交叉与变异)
# ==========================================
def selection(population):
    """锦标赛选择：随机抓3个，选冲突最少（最优秀）的那个"""
    tournament = random.sample(population, 3)
    return min(tournament, key=calculate_conflicts)

def crossover(parent1, parent2):
    """均匀交叉：掷硬币决定每门课继承父亲还是母亲的排班"""
    child = []
    for i in range(len(COURSES)):
        if random.random() < 0.5:
            child.append(parent1[i])
        else:
            child.append(parent2[i])
    return child

def mutate(individual):
    """变异：每门课有概率被重新随机分配"""
    for i in range(len(individual)):
        if random.random() < MUTATION_RATE:
            individual[i] = (random.choice(ROOMS), random.choice(TIMESLOTS))
    return individual

# ==========================================
# 4. 主循环 (物竞天择，适者生存)
# ==========================================
print("🚀 开始排课演化，请稍候...\n")

population = [create_individual() for _ in range(POPULATION_SIZE)]
best_history = []

for gen in range(GENERATIONS):
    # 按照冲突数从小到大排序 (0冲突在最前面)
    population.sort(key=calculate_conflicts)
    best_conflicts = calculate_conflicts(population[0])
    best_history.append(best_conflicts)
    
    if gen % 50 == 0:
        print(f"第 {gen} 代 -> 当前最少冲突数: {best_conflicts}")
        
    if best_conflicts == 0:
        print(f"\n✅ 奇迹出现！在第 {gen} 代找到了 0 冲突的完美课表！")
        break
        
    # 精英保留策略 (Elitism)：把目前最好的前 5 张课表直接保送到下一代，防止好基因丢失
    next_gen = population[:5]
    
    # 繁衍剩余的子代
    while len(next_gen) < POPULATION_SIZE:
        p1 = selection(population)
        p2 = selection(population)
        child = crossover(p1, p2)
        child = mutate(child)
        next_gen.append(child)
        
    population = next_gen

# ==========================================
# 5. 打印结果与绘制曲线
# ==========================================
best_schedule = min(population, key=calculate_conflicts)
final_conflicts = calculate_conflicts(best_schedule)

print(f"\n🎯 最终课表冲突数: {final_conflicts}")
if final_conflicts > 0:
    print("⚠️ 资源太紧张，未能完全消除冲突，可以尝试增加 GENERATIONS 或 POPULATION_SIZE。")

# 简单打印一下前 10 门课的排期感受一下
print("\n部分排期结果展示：")
for i in range(10):
    c = COURSES[i]
    r, t = best_schedule[i]
    print(f"课程 {c['id']} ({c['teacher']}) -> 被安排在 {t} 的 {r}")

# 绘制冲突下降曲线
plt.figure(figsize=(10, 5))
plt.plot(best_history, color='red', linewidth=2)
plt.title('Genetic Algorithm: Conflict Resolution Over Generations')
plt.xlabel('Generations')
plt.ylabel('Number of Conflicts (Hard Constraints)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.fill_between(range(len(best_history)), best_history, color='red', alpha=0.1)
plt.show()