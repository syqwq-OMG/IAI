import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

def create_smoothed_targets(events_df: pd.DataFrame, series_length: int, sigma: float = 2.0) -> dict:
    """
    标签重塑 (Target Shaping) 与高斯平滑.
    将原本孤立的尖锐标签 (One-Hot) 转换为宽峰热力图.
    """
    onset_target = np.zeros(series_length, dtype=np.float32)
    wakeup_target = np.zeros(series_length, dtype=np.float32)
    
    for _, row in events_df.iterrows():
        step = row['step']
        if pd.isna(step):
            continue
        step = int(step)
        if step >= series_length or step < 0:
            continue
            
        # 施加正向偏移修正 (Positive Offset, 约3个时间步)
        # 纠正模型由于历史数据积累惯性导致的预测重心滞后问题
        step = min(series_length - 1, step + 3)
        
        if row['event'] == 'onset':
            onset_target[step] = 1.0
        elif row['event'] == 'wakeup':
            wakeup_target[step] = 1.0
            
    # 高斯平滑 (Gaussian Smoothing) - 将一根针变成一座山
    onset_target = gaussian_filter1d(onset_target, sigma=sigma)
    wakeup_target = gaussian_filter1d(wakeup_target, sigma=sigma)
    
    # 归一化使得峰值为1.0
    if onset_target.max() > 0:
        onset_target /= onset_target.max()
    if wakeup_target.max() > 0:
        wakeup_target /= wakeup_target.max()
        
    return {
        'onset_target': onset_target,
        'wakeup_target': wakeup_target
    }

def apply_epoch_target_decay(targets: np.ndarray, current_epoch: int, total_epochs: int) -> np.ndarray:
    """
    纪元级目标动态衰减机制 (Target Decay Every Epoch).
    随着训练进行，压低目标的强度，促使网络汇聚出更尖锐的锋面.
    """
    decay_factor = 1.0 / total_epochs
    decay_amount = current_epoch * decay_factor
    
    # Targets^(e) = max(0, Targets^(e-1) - decay_amount)
    decayed_targets = np.maximum(0.0, targets - decay_amount)
    
    return decayed_targets
