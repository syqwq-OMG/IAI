import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from models.detector import SleepStateDetector
from training.loss import OHEMNearMissLoss
from training.trainer import SleepDetectorTrainer
from data.dataset import SleepStatesDataset

def main():
    # 真实训练流的骨架代码 (本地微型测试模式)
    print("=== Initializing Real Training Pipeline (Micro Local Test) ===")
    
    # 自动探测硬件加速环境
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using compute device: {device}")
    
    # --- 阶段 1: 加载并重塑数据 ---
    print("Loading dataset via Parquet Engine (Restricted to 2 subjects)...")
    train_dataset = SleepStatesDataset(
        parquet_path="/Users/syqwq-omg/syqwq-workspace/ECNU-CS/IAI/proj/project-2/child-mind-institute-detect-sleep-states/train_series.parquet",
        events_path="/Users/syqwq-omg/syqwq-workspace/ECNU-CS/IAI/proj/project-2/child-mind-institute-detect-sleep-states/train_events.csv",
        chunk_size=17280, # 截取一天的长度作为单次前向传播的跨度
        max_subjects=2    # 极小数据集，专供本地调通流程
    )
    
    # 动态获取特征维度，防止硬编码崩溃
    sample_X, _ = train_dataset[0]
    in_features = sample_X.shape[1]
    print(f"Dynamically determined input features dimension: {in_features}")
    
    # 本地跑只用 2 个受试者，batch_size=2 即可
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
    val_loader = None 
    
    # --- 阶段 2: 初始化网络与 OHEM 损失函数 ---
    model = SleepStateDetector(in_features=in_features, hidden_channels=64)
    # 启用 Near-Miss 近失豁免机制
    criterion = OHEMNearMissLoss(near_miss_radius=24, ohem_ratio=0.5)
    
    # --- 阶段 3: 启动带有目标衰减机制的训练引擎 ---
    trainer = SleepDetectorTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        device=device,
        total_epochs=1  # 本地只跑 1 个 Epoch
    )
    
    print("Beginning Training Loop with Epoch-level Target Decay...")
    for epoch in range(5):
        train_loss = trainer.train_epoch(epoch)
        print(f"\n✅ Epoch {epoch+1} completed! Training Loss: {train_loss:.4f}")
        
        # 保存断点
        torch.save(model.state_dict(), f"sleep_detector_epoch_{epoch+1}_local_test.pth")
        print(f"Model checkpoint saved as sleep_detector_epoch_{epoch+1}_local_test.pth")
    
if __name__ == "__main__":
    main()
