import torch
import pandas as pd
import numpy as np
import pyarrow.dataset as ds
from tqdm import tqdm
import os

from data.features import build_feature_matrix
from models.detector import SleepStateDetector
from inference.post_process import bayesian_logits_update, get_topk_events_nms

def generate_submission(parquet_path: str, model_path: str, output_csv: str = "submission.csv"):
    """
    Kaggle 比赛标准推理管道：加载测试集 -> 提特征 -> 模型推理 -> NMS 后处理 -> 生成 submission.csv
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device for inference: {device}")
    
    # 读取 Parquet
    print(f"Loading test data from {parquet_path}...")
    dataset = ds.dataset(parquet_path, format='parquet')
    
    # Kaggle 隐藏的测试集通常不大，但如果是跑完整的 train_series 会很慢
    # 这里我们只读取前几个序列用于演示
    df_test = dataset.to_table().to_pandas()
    series_ids = df_test['series_id'].unique()
    
    # 仅为本地演示，强制限制推理规模以防内存爆掉
    if len(series_ids) > 2:
        print("Limiting to 2 subjects for local memory safety...")
        series_ids = series_ids[:2]
        
    all_predictions = []
    model = None
    
    print(f"Beginning inference on {len(series_ids)} series...")
    
    for series_id in tqdm(series_ids, desc="Predicting"):
        series_df = df_test[df_test['series_id'] == series_id].copy()
        
        # 必须保存原始的 step，这是 Kaggle submission 文件必须匹配的唯一时间坐标
        original_steps = series_df['step'].values
        
        # 预处理时间戳
        series_df['timestamp'] = pd.to_datetime(series_df['timestamp'], utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
        minutes_array = series_df['timestamp'].dt.minute.values
        
        # 提取同款高阶特征
        series_df = build_feature_matrix(series_df)
        feature_cols = [c for c in series_df.columns if c not in ['series_id', 'step', 'timestamp', 'night', 'event']]
        X_np = series_df[feature_cols].fillna(0).values.astype(np.float32)
        
        in_features = X_np.shape[1]
        
        # 延迟初始化模型：由于特征数量是动态计算的，必须等到拿到第一条数据才知道 input dimension
        if model is None:
            print(f"\nInitializing model with in_features={in_features}")
            model = SleepStateDetector(in_features=in_features, hidden_channels=64)
            model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
            model.to(device)
            model.eval()
            
        # 将整个时间序列一次性送入网络
        # 传统 Transformer 会在这里直接 OOM 显存爆炸，但 BiMamba 拥有完美的 O(N) 线性复杂度，可以一口气吞掉几十万步！
        X_tensor = torch.tensor(X_np).unsqueeze(0).to(device) # 形状: (1, Seq_Len, Features)
        
        with torch.no_grad():
            logits = model(X_tensor)
            logits_np = logits.squeeze(0).cpu().numpy() # 形状: (Seq_Len, 2)
            
        # ==========================================
        # 核心逻辑：Kaggle 比赛夺冠后处理策略
        # ==========================================
        
        # 1. 贝叶斯对数几率修正 (利用作息先验强行压低不可能的时段)
        updated_logits = bayesian_logits_update(logits_np, minutes_array)
        
        # 2. 转换为概率
        probs = 1.0 / (1.0 + np.exp(-updated_logits))
        onset_probs = probs[:, 0]
        wakeup_probs = probs[:, 1]
        
        # 3. 带信息梯度的拓扑峰值提取 (NMS)
        # 这也是为什么你在 proj-2.md 中提到需要放弃简单二分类的原因：
        # 这里能智能剔除“连绵不绝的山脉”，只留下最陡峭的几十个山峰！
        onset_candidates = get_topk_events_nms(onset_probs, event_type='onset', min_distance=120, top_k=20)
        wakeup_candidates = get_topk_events_probs = get_topk_events_nms(wakeup_probs, event_type='wakeup', min_distance=120, top_k=20)
        
        # 将这些候选点打包
        if not onset_candidates.empty:
            onset_candidates['step'] = original_steps[onset_candidates['step']]
            onset_candidates['series_id'] = series_id
            all_predictions.append(onset_candidates[['series_id', 'step', 'event', 'score']])
            
        if not wakeup_candidates.empty:
            wakeup_candidates['step'] = original_steps[wakeup_candidates['step']]
            wakeup_candidates['series_id'] = series_id
            all_predictions.append(wakeup_candidates[['series_id', 'step', 'event', 'score']])

    # 聚合并生成最终的 Kaggle Submission 提交文件
    if len(all_predictions) > 0:
        submission = pd.concat(all_predictions, ignore_index=True)
        # 按照 Kaggle 要求添加 row_id
        submission = submission.reset_index(names='row_id')
        submission.to_csv(output_csv, index=False)
        print(f"\n🎉 Successfully generated Kaggle submission file: {output_csv}")
    else:
        print("\n⚠️ No valid events detected.")
        pd.DataFrame(columns=['row_id', 'series_id', 'step', 'event', 'score']).to_csv(output_csv, index=False)

if __name__ == "__main__":
    # 假设你刚刚把 main.py 里的 range(1) 改成了 range(5) 并跑完了，生成了这个文件
    MODEL_WEIGHTS = "sleep_detector_epoch_5_local_test.pth"
    
    # 这里用测试集的 parquet 路径 (因为咱们本地没有下完整的 Kaggle 测试集，所以先拿 train_series 代替用来演示)
    TEST_PARQUET = "/Users/syqwq-omg/syqwq-workspace/ECNU-CS/IAI/proj/project-2/child-mind-institute-detect-sleep-states/train_series.parquet"
    
    # 检查权重是否存在
    if not os.path.exists(MODEL_WEIGHTS):
        print(f"Error: {MODEL_WEIGHTS} not found. Please run main.py first to train the model and save the weights!")
    else:
        generate_submission(
            parquet_path=TEST_PARQUET,
            model_path=MODEL_WEIGHTS,
            output_csv="submission.csv"
        )
