import torch
import torch.nn as nn
import torch.nn.functional as F

class WaveNetBlock(nn.Module):
    """
    WaveNet 模块中的膨胀因果卷积块 (Dilated Causal Convolution Block).
    能在极少计算开销下，保留高时间分辨率，同时呈指数级扩大感受野。
    """
    def __init__(self, in_channels, out_channels, dilation, kernel_size=3):
        super(WaveNetBlock, self).__init__()
        # 膨胀卷积 padding
        self.padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(in_channels, out_channels * 2, kernel_size, 
                              dilation=dilation, padding=self.padding)
        self.proj = nn.Conv1d(out_channels, out_channels, 1)
        
    def forward(self, x):
        res = x
        # Causal padding - remove output from future
        out = self.conv(x)
        out = out[:, :, :-self.padding] if self.padding > 0 else out
        
        # Gated activation (tanh * sigmoid)
        gate, filter_ = torch.chunk(out, 2, dim=1)
        out = torch.tanh(filter_) * torch.sigmoid(gate)
        out = self.proj(out)
        
        return out + res  # Residual connection

class WaveNetExtractor(nn.Module):
    """
    局部微观生理特征提取底座.
    """
    def __init__(self, in_features, hidden_channels=64, num_blocks=4):
        super(WaveNetExtractor, self).__init__()
        self.init_conv = nn.Conv1d(in_features, hidden_channels, 1)
        
        self.blocks = nn.ModuleList()
        for i in range(num_blocks):
            dilation = 2 ** i
            self.blocks.append(WaveNetBlock(hidden_channels, hidden_channels, dilation))
            
    def forward(self, x):
        # 输入 x 形状 (Batch, Seq, Features)，需转为 (Batch, Features, Seq) 适应 Conv1d
        x = x.transpose(1, 2)
        x = self.init_conv(x)
        
        for block in self.blocks:
            x = block(x)
            
        # 转回 (Batch, Seq, Channels) 供给后端 Mamba/Transformer
        return x.transpose(1, 2)
