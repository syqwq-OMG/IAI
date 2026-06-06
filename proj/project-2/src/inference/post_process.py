import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def bayesian_logits_update(logits: np.ndarray, minutes: np.ndarray) -> np.ndarray:
    """
    基于罕见模数周期特征的贝叶斯对数几率修正 (Bayesian Logits Update).
    拦截模型输出的原始对数几率 (Logits)，并进行惩罚.
    
    参数:
        logits: (N, 2) 形状的数组 [onset_logits, wakeup_logits]
        minutes: (N,) 形状的绝对分钟数时间戳
    """
    updated_logits = logits.copy()
    
    # 提取先验: minute % 15
    min_mod_15 = minutes % 15
    
    # 假设通过探索性数据分析发现某些分钟节点是极少出现事件的 (罕见生理点)
    # 对这些点施加强行阻尼矫正
    rare_mask = np.isin(min_mod_15, [0, 7, 8])
    
    # 将 logits 压低，极大地降低该处输出事件的概率
    updated_logits[rare_mask] -= 2.0 
    
    return updated_logits

def get_topk_events_nms(predictions: np.ndarray, event_type: str, min_distance: int = 120, top_k: int = 50):
    """
    带有非极大值抑制 (NMS) 和信息梯度优先级排序的拓扑峰值提取.
    
    参数:
        predictions: 连续的一维概率波 (长度为 L)
        event_type: 'onset' 或 'wakeup'
        min_distance: 两个预测点之间的最小间隔 (如 120 步 = 10 分钟)
        top_k: 每天最多保留多少个候选点
    """
    # 找到所有波峰
    peak_indices, _ = find_peaks(predictions, distance=min_distance, height=0.1)
    peak_scores = predictions[peak_indices]
    
    candidates = pd.DataFrame({
        'step': peak_indices,
        'score': peak_scores,
        'event': event_type
    })
    
    if candidates.empty:
        return candidates
        
    # --- Top-K 置信度差值降权排序法 (Information Gradient) ---
    # 先按绝对分数从高到低排序
    candidates = candidates.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    # 计算当前点与前序点的差值 (信息衰减梯度)
    diffs = [0.0]
    for i in range(1, len(candidates)):
        diffs.append(candidates.loc[i, 'score'] - candidates.loc[i-1, 'score'])
        
    candidates['info_gradient'] = diffs
    
    # 综合得分 = 绝对分数 + 权重 * 信息梯度
    # 这样分布平缓的连绵假峰就会被合法超越，极大地优化了多容差 AP 得分
    candidates['final_rank_score'] = candidates['score'] + 0.5 * candidates['info_gradient']
    
    # 最终排序截断
    candidates = candidates.sort_values(by='final_rank_score', ascending=False).head(top_k)
    return candidates
