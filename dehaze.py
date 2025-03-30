import torch
import cv2
import numpy as np

def dehaze_image(image, model):
    """图像去雾处理"""
    # 预处理
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)
    img = torch.from_numpy(img).unsqueeze(0).cuda()
    img = img * 2 - 1  # 归一化到[-1, 1]
    # 推理
    with torch.no_grad():
        output = model(img).clamp_(-1, 1)
        output = output * 0.5 + 0.5  # 反归一化到[0, 1]
    # 后处理
    output_np = output.squeeze(0).cpu().numpy().transpose(1, 2, 0)
    output_np = (output_np * 255).astype(np.uint8)
    return cv2.cvtColor(output_np, cv2.COLOR_RGB2BGR)