import torch
import torch.nn as nn
from .wavenet import WaveNetExtractor
from .mamba import BiMambaBlock

class ECA_Layer(nn.Module):
    """Efficient Channel Attention (ECA) 模块"""
    def __init__(self, channels, k_size=3):
        super(ECA_Layer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=k_size, padding=(k_size - 1) // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (B, C, L)
        y = self.avg_pool(x) # (B, C, 1)
        y = self.conv(y.transpose(-1, -2)).transpose(-1, -2)
        y = self.sigmoid(y)
        return x * y.expand_as(x)

class SleepStateDetector(nn.Module):
    """
    统一的端到端网络架构: WaveNet + BiMamba
    """
    def __init__(self, in_features, hidden_channels=64, num_classes=2):
        super(SleepStateDetector, self).__init__()
        
        # 局部特征提取
        self.wavenet = WaveNetExtractor(in_features, hidden_channels)
        
        # 通道注意力过滤无用特征
        self.eca = ECA_Layer(hidden_channels)
        
        # 全局超长程依赖
        self.mamba_blocks = nn.Sequential(
            BiMambaBlock(d_model=hidden_channels),
            BiMambaBlock(d_model=hidden_channels)
        )
        
        # 概率打分头
        self.head = nn.Sequential(
            nn.Linear(hidden_channels, 32),
            nn.SiLU(),
            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        # x: (B, L, F)
        
        # 1. 微观生理特征提取 (WaveNet)
        x_local = self.wavenet(x) # (B, L, C)
        
        # 2. 注意力过滤 (需要先转维)
        x_local = x_local.transpose(1, 2) # (B, C, L)
        x_local = self.eca(x_local)
        x_local = x_local.transpose(1, 2) # (B, L, C)
        
        # 3. 宏观极长序列建模 (BiMamba)
        x_global = self.mamba_blocks(x_local) # (B, L, C)
        
        # 4. 预测打分
        logits = self.head(x_global) # (B, L, 2)
        return logits
