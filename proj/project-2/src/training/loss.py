import torch
import torch.nn as nn
import torch.nn.functional as F

class OHEMNearMissLoss(nn.Module):
    """
    带有在线难例挖掘 (OHEM) 和“近失”(Near Miss) 豁免机制的非对称损失函数。
    极大地保护了模型对于潜在临界点的概率置信度。
    """
    def __init__(self, near_miss_radius=24, ohem_ratio=0.5):
        # 24 steps = 2 minutes (1 step = 5 seconds)
        super(OHEMNearMissLoss, self).__init__()
        self.near_miss_radius = near_miss_radius
        self.ohem_ratio = ohem_ratio
        
    def forward(self, logits, targets):
        # logits: (B, L, 2), targets: (B, L, 2)
        # 计算每一帧的 BCE Loss (未做 reduction)
        loss = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        
        # --- 近失豁免 (Near Misses Ignorance) ---
        # 寻找真实事件发生点 (平滑后 > 0.9 认为是核心事件区)
        event_mask = targets > 0.9 
        
        # 使用 1D 膨胀 (Max Pooling) 找到事件附近 2 分钟内的区域
        # 如果模型在这几分钟内出现了微小的预测偏差，网络并不会对其施加负向惩罚
        with torch.no_grad():
            event_mask_float = event_mask.float().permute(0, 2, 1) # (B, 2, L)
            kernel_size = self.near_miss_radius * 2 + 1
            # 膨胀掩码
            dilated_mask = F.max_pool1d(
                event_mask_float, 
                kernel_size=kernel_size, 
                stride=1, 
                padding=self.near_miss_radius
            )
            # 纯粹的 Near Miss 区域 = 膨胀区域 - 实际事件点
            near_miss_mask = (dilated_mask > 0.5) & (~event_mask.permute(0, 2, 1))
            near_miss_mask = near_miss_mask.permute(0, 2, 1) # (B, L, 2)
            
        # 把 near miss 区域的 loss 清零
        loss = loss * (~near_miss_mask)
        
        # --- OHEM (Online Hard Example Mining) ---
        # 展平 loss，只取 Top 50% 最大的 Loss 进行反向传播
        loss_flat = loss.view(-1)
        k = int(self.ohem_ratio * loss_flat.numel())
        if k > 0:
            topk_losses, _ = torch.topk(loss_flat, k)
            return topk_losses.mean()
        else:
            return loss.mean()
