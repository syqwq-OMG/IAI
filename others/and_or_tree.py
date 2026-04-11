""" 
假设你是一名正在编写自动战术规划 AI 的程序员。你的特工机器人需要潜入一个金库。

终极目标（Root节点）： 窃取机密文件。
为了达成这个目标，AI 必须生成一套行动逻辑树：

窃取机密文件 (AND 节点)：必须同时做到【进入金库】并且【打开保险箱】。

进入金库 (OR 节点)：可以通过【破解门禁】或者【炸开墙壁】。

叶子节点：身上是否有【C4炸药】？（如果为 True，则可以炸开墙壁）。

叶子节点：身上是否有【门禁卡】？（如果为 True，则可以破解门禁）。

打开保险箱 (AND 节点)：必须同时拥有【密码】和【视网膜数据】。

叶子节点：是否通过黑客手段窃取了【密码】？

叶子节点：是否绑架了主管获取了【视网膜数据】？

AI 的任务是：根据当前特工背包里的道具（叶子节点的状态），遍历这棵与或树，判断最终计划是否可行（能否返回 True）。
"""

class Node:
    def __init__(self, name, node_type, is_leaf=False, leaf_status=False):
        self.name = name
        self.node_type = node_type  # 'AND' 或 'OR'
        self.is_leaf = is_leaf      # 是否是底层的条件节点
        self.leaf_status = leaf_status # 如果是叶子节点，当前条件是否满足 (True/False)
        self.children = []          # 子节点列表

    def add_child(self, child_node):
        self.children.append(child_node)

    def evaluate(self, depth=0):
        """
        递归评估该节点的目标是否可以达成
        """
        indent = "  " * depth
        
        # 1. 如果是叶子节点（基础条件），直接返回它是否满足
        if self.is_leaf:
            status_str = "✅具备" if self.leaf_status else "❌缺失"
            print(f"{indent}- 检查条件: [{self.name}] -> {status_str}")
            return self.leaf_status

        print(f"{indent}开始评估目标: [{self.name}] (类型: {self.node_type})")

        # 2. 如果是 OR 节点：只要有一个子节点返回 True，整体就为 True
        if self.node_type == 'OR':
            for child in self.children:
                if child.evaluate(depth + 1):
                    print(f"{indent}✔ 目标 [{self.name}] 达成 (因为子目标 '{child.name}' 达成)")
                    return True
            print(f"{indent}✖ 目标 [{self.name}] 失败 (所有备选方案均不可行)")
            return False

        # 3. 如果是 AND 节点：必须所有子节点都返回 True，整体才为 True
        elif self.node_type == 'AND':
            for child in self.children:
                # 只要有一个关键步骤失败，整个 AND 计划就流产了 (短路评估)
                if not child.evaluate(depth + 1):
                    print(f"{indent}✖ 目标 [{self.name}] 失败 (卡在前提步骤 '{child.name}')")
                    return False
            print(f"{indent}✔ 目标 [{self.name}] 达成 (所有前提步骤均已完成)")
            return True


# ==========================================
# 场景构建：配置特工的与或树
# ==========================================

# 1. 创建叶子节点 (相当于特工当前的背包资产/状态)
c4_explosive = Node("拥有C4炸药", "LEAF", is_leaf=True, leaf_status=False)
access_card = Node("拥有门禁卡", "LEAF", is_leaf=True, leaf_status=True)  # 特工拿到了门禁卡

password = Node("获取了密码", "LEAF", is_leaf=True, leaf_status=True)     # 特工搞到了密码
retina_scan = Node("获取了视网膜", "LEAF", is_leaf=True, leaf_status=True)  # 特工搞到了视网膜

# 2. 创建逻辑中间节点
enter_vault = Node("进入金库", "OR")
enter_vault.add_child(c4_explosive) # 方案A
enter_vault.add_child(access_card)  # 方案B

open_safe = Node("打开保险箱", "AND")
open_safe.add_child(password)     # 前提1
open_safe.add_child(retina_scan)  # 前提2

# 3. 创建根节点
ultimate_goal = Node("窃取机密文件", "AND")
ultimate_goal.add_child(enter_vault) # 第一步
ultimate_goal.add_child(open_safe)   # 第二步

# ==========================================
# 执行评估
# ==========================================
print("🚨 战术 AI 启动，开始推演行动计划...\n")
success = ultimate_goal.evaluate()

print("\n===============================")
if success:
    print("🏆 最终评估：计划可行，特工可以成功窃取文件！")
else:
    print("💀 最终评估：计划不可行，缺少关键条件。")