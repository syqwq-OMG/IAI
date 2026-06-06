import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
import pyarrow.dataset as ds

from .features import build_feature_matrix
from .targets import create_smoothed_targets

class SleepStatesDataset(Dataset):
    """
    睡眠状态数据集。
    采用块切分与动态数据增强。
    """
    def __init__(self, parquet_path: str, events_path: str, chunk_size: int = 17280, max_subjects: int = None):
        # 17280 = 24小时 (每分钟12步)
        self.dataset = ds.dataset(parquet_path, format='parquet')
        self.events_df = pd.read_csv(events_path).dropna()
        self.series_ids = self.events_df['series_id'].unique()
        if max_subjects is not None:
            self.series_ids = self.series_ids[:max_subjects]
        self.chunk_size = chunk_size
        
    def __len__(self):
        return len(self.series_ids)
        
    def __getitem__(self, idx):
        series_id = self.series_ids[idx]
        
        # 1. 从 Parquet 提取特定系列数据
        series_df = self.dataset.to_table(filter=ds.field('series_id') == series_id).to_pandas()
        if series_df.empty:
            # Fallback for safe dataloader
            return torch.zeros((self.chunk_size, 20)), torch.zeros((self.chunk_size, 2))

        series_df['timestamp'] = pd.to_datetime(series_df['timestamp'], utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
        
        # 2. 提取高阶特征
        series_df = build_feature_matrix(series_df)
        
        feature_cols = [c for c in series_df.columns if c not in ['series_id', 'step', 'timestamp', 'night', 'event']]
        X = series_df[feature_cols].fillna(0).values.astype(np.float32)
        
        # 3. 提取平滑的目标标签
        subject_events = self.events_df[self.events_df['series_id'] == series_id]
        targets_dict = create_smoothed_targets(subject_events, series_length=len(series_df))
        Y = np.stack([targets_dict['onset_target'], targets_dict['wakeup_target']], axis=-1)
        
        # 4. 时间反转增强 (Sequence Reversal Augmentation)
        # 以切断模型对时间顺序的简单记忆依赖
        if torch.rand(1).item() > 0.5:
            X = np.flip(X, axis=0).copy()
            Y = np.flip(Y, axis=0).copy()
            
        # 5. 切割 (Chunking)
        if len(X) > self.chunk_size:
            start_idx = np.random.randint(0, len(X) - self.chunk_size)
            X = X[start_idx : start_idx + self.chunk_size]
            Y = Y[start_idx : start_idx + self.chunk_size]
        else:
            pad_len = self.chunk_size - len(X)
            X = np.pad(X, ((0, pad_len), (0, 0)), mode='constant')
            Y = np.pad(Y, ((0, pad_len), (0, 0)), mode='constant')
            
        return torch.tensor(X), torch.tensor(Y)
