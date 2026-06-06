import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np

from data.targets import apply_epoch_target_decay

class SleepDetectorTrainer:
    """
    负责训练过程的调度器。
    包含学习率衰减、梯度裁剪、以及核心的“纪元级目标动态衰减”策略。
    """
    def __init__(self, model, train_loader, val_loader, criterion, device, total_epochs=10):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.device = device
        self.total_epochs = total_epochs
        
        self.optimizer = optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=total_epochs)
        
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}/{self.total_epochs} [Train]")
        for X, Y in pbar:
            X, Y = X.to(self.device), Y.to(self.device)
            
            # --- 纪元级目标动态衰减 (Target Decay) ---
            # 根据当前 epoch 将目标 Y 进行压低，促使模型后期预测锋面更加尖锐
            Y_numpy = Y.cpu().numpy()
            Y_decayed = apply_epoch_target_decay(Y_numpy, epoch, self.total_epochs)
            Y_decayed = torch.tensor(Y_decayed, dtype=torch.float32).to(self.device)
            
            self.optimizer.zero_grad()
            logits = self.model(X)
            
            loss = self.criterion(logits, Y_decayed)
            loss.backward()
            
            # 梯度裁剪防止超长序列导致梯度爆炸
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            total_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
            
        self.scheduler.step()
        return total_loss / len(self.train_loader)
