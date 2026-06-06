import pandas as pd
import numpy as np

def extract_chunk_meta_features(logits: np.ndarray, anglez: np.ndarray, enmo: np.ndarray, chunk_size: int = 720) -> pd.DataFrame:
    """
    将序列切块并提取元特征，用于第二阶段 GBDT 校准。
    720 步 = 1 小时
    """
    num_chunks = len(logits) // chunk_size
    meta_features = []
    
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        
        chunk_logits = logits[start:end]
        chunk_anglez = anglez[start:end]
        chunk_enmo = enmo[start:end]
        
        # 提取第一阶段深度学习的概率特征谱
        onset_logits = chunk_logits[:, 0]
        wakeup_logits = chunk_logits[:, 1]
        
        feats = {
            'chunk_id': i,
            'onset_max': np.max(onset_logits),
            'onset_mean': np.mean(onset_logits),
            'wakeup_max': np.max(wakeup_logits),
            
            # 提取传感器底层物理方差 (判断深度模型是否由于感受野有限而产生了幻觉)
            'anglez_std': np.std(chunk_anglez),
            'enmo_max': np.max(chunk_enmo),
            'enmo_median': np.median(chunk_enmo)
        }
        meta_features.append(feats)
        
    return pd.DataFrame(meta_features)

class GBDTCalibrator:
    """
    第二阶段基于 LightGBM 的残差校准与事件提纯网络。
    它能够极其精确地捕捉非线性残差规律，彻底抹平孤立的假峰值。
    """
    def __init__(self):
        self.model = None
        
    def train(self, X_meta: pd.DataFrame, y_true: np.ndarray):
        """
        训练 GBDT 校准器。
        注意：运行此函数需要你的环境中安装了 lightgbm 库。
        """
        try:
            import lightgbm as lgb
        except ImportError:
            raise ImportError("Please install lightgbm via 'pip install lightgbm' to use the 2nd stage ensemble.")
            
        train_data = lgb.Dataset(X_meta, label=y_true)
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'num_leaves': 31,
            'verbose': -1
        }
        self.model = lgb.train(params, train_data, num_boost_round=100)
        
    def predict(self, X_meta: pd.DataFrame):
        if self.model is None:
            raise ValueError("GBDT model is not trained yet!")
        return self.model.predict(X_meta)
