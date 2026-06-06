import torch
import torch.nn as nn
import torch.nn.functional as F

# 手动开关：设置为 True 时将使用官方 mamba-ssm (需在 GPU 环境安装)
# 设置为 False 时将使用纯 PyTorch 模拟版 (适合 Mac 本地调试)
USE_OFFICIAL_MAMBA = False

if USE_OFFICIAL_MAMBA:
    from mamba_ssm import Mamba as OfficialMamba
    print("Mamba Hardware Acceleration: ENABLED")
else:
    print("Mamba Hardware Acceleration: DISABLED. Using pure PyTorch emulation.")

class PyTorchMambaEmulation(nn.Module):
    """
    纯 PyTorch 编写的极简版 Mamba SSM 模拟层。
    没有官方版本的高度并行优化，但支持完全相同的输入输出形状，
    完美用于 Mac 本地 CPU/MPS 的代码逻辑调通和演示验证。
    """
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.d_model = d_model
        d_inner = int(expand * d_model)
        
        # 简化的线性投影层来模拟 Selective Mechanism 
        self.in_proj = nn.Linear(d_model, d_inner * 2)
        self.conv1d = nn.Conv1d(
            in_channels=d_inner, out_channels=d_inner, 
            kernel_size=d_conv, padding=d_conv - 1, groups=d_inner
        )
        self.x_proj = nn.Linear(d_inner, d_state * 2 + d_model)
        self.dt_proj = nn.Linear(d_model, d_inner)
        self.out_proj = nn.Linear(d_inner, d_model)
        
        # 一个非常粗糙的类似于 SSM 的时间循环池化模拟
        self.gru_fallback = nn.GRU(d_inner, d_inner, batch_first=True)
        
    def forward(self, x):
        # x: (B, L, D)
        B, L, D = x.shape
        xz = self.in_proj(x)
        x_, z = xz.chunk(2, dim=-1)
        
        x_ = x_.transpose(1, 2)
        x_ = self.conv1d(x_)[:, :, :L]
        x_ = x_.transpose(1, 2)
        x_ = F.silu(x_)
        
        # 实际 Mamba 会在这里进行 Selective Scan。
        # 本地模拟中我们用快速的 GRU 做替代，以保证序列上下文传递。
        out, _ = self.gru_fallback(x_)
        
        out = out * F.silu(z)
        out = self.out_proj(out)
        return out

class BiMambaBlock(nn.Module):
    """
    双向选择性状态空间模型 (BiMamba)。
    整合前向与后向信息，避免单向扫描带来的迟滞误报。
    """
    def __init__(self, d_model):
        super().__init__()
        if USE_OFFICIAL_MAMBA:
            self.forward_mamba = OfficialMamba(d_model=d_model)
            self.backward_mamba = OfficialMamba(d_model=d_model)
        else:
            self.forward_mamba = PyTorchMambaEmulation(d_model=d_model)
            self.backward_mamba = PyTorchMambaEmulation(d_model=d_model)
            
        # 通道融合特征压缩
        self.merge = nn.Linear(d_model * 2, d_model)
        
    def forward(self, x):
        # 前向扫描
        out_f = self.forward_mamba(x)
        # 后向扫描
        x_reversed = torch.flip(x, dims=[1])
        out_b_reversed = self.backward_mamba(x_reversed)
        out_b = torch.flip(out_b_reversed, dims=[1])
        
        # 双向交汇
        out = torch.cat([out_f, out_b], dim=-1)
        return self.merge(out)
