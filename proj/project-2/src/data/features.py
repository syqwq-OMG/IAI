import numpy as np
import pandas as pd

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    提取时间节律编码特征 (Circadian Rhythm).
    
    参数:
        df: 包含 'timestamp' (datetime) 的 DataFrame
    
    返回:
        df: 添加了时间特征的 DataFrame
    """
    # 提取基本的时间特征
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['weekday'] = df['timestamp'].dt.weekday
    
    # 极其重要的先验特征: minute % 15 (局部周期聚类效应)
    df['minute_mod_15'] = df['minute'] % 15
    
    # 正弦/余弦周期编码 (Sin/Cos embedding for cyclic time)
    # 一天有 24小时，引入以保留时区循环性
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
    
    return df

def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    提取基础统计聚合特征 (Basic Statistical Aggregation).
    基于多尺度的时间窗 (如 12步/1分钟, 60步/5分钟, 360步/30分钟).
    """
    windows = [12, 60, 360]  # 1分钟, 5分钟, 30分钟 (1步=5秒)
    
    for w in windows:
        # Anglez 均值与标准差 (宏观姿态与微小动作频率)
        df[f'anglez_mean_{w}'] = df['anglez'].rolling(w, center=True, min_periods=1).mean()
        df[f'anglez_std_{w}']  = df['anglez'].rolling(w, center=True, min_periods=1).std().fillna(0)
        
        # ENMO 均值与标准差
        df[f'enmo_mean_{w}'] = df['enmo'].rolling(w, center=True, min_periods=1).mean()
        df[f'enmo_std_{w}']  = df['enmo'].rolling(w, center=True, min_periods=1).std().fillna(0)
        
        # 波动率提取: 计算差值的绝对值的中位数 (Volatility)
        df[f'anglez_diff_abs_{w}'] = df['anglez'].diff().abs().rolling(w, center=True, min_periods=1).median().fillna(0)
        df[f'enmo_diff_abs_{w}']   = df['enmo'].diff().abs().rolling(w, center=True, min_periods=1).median().fillna(0)
        
    return df

def detect_homogeneous_artifacts(df: pd.DataFrame, threshold: int = 360) -> pd.DataFrame:
    """
    同质噪声标识 (Homogeneous Artifacts).
    检测由于设备脱落导致的软件均值插值 (连续出现完全相同的浮点数).
    """
    is_same = (df['anglez'].diff() == 0) & (df['enmo'].diff() == 0)
    group_ids = (~is_same).cumsum()
    group_lengths = is_same.groupby(group_ids).transform('size')
    
    # 生成噪声 Mask
    df['noise_mask'] = (group_lengths >= threshold).astype(np.float32)
    return df

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    主调函数：将原始的二维输入扩展为高阶多元特征矩阵.
    """
    df = add_time_features(df)
    df = add_rolling_features(df)
    df = detect_homogeneous_artifacts(df)
    return df
