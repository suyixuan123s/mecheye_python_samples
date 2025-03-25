"""
Author: Yixuan Su
Date: 2025/01/05 15:59
File: demo.py
Description: 
"""

import time
from MechEye import MechEyeAPI

# 创建 Mech-Eye 相机对象
camera = MechEyeAPI.Mecheye()

# 连接到相机（假设相机已连接）
if camera.connect():
    print("Camera connected successfully.")
else:
    print("Failed to connect to the camera.")
    exit()

# 获取相机的深度缩放因子
depth_scale = camera.get_depth_scale()

# 输出深度缩放因子
print(f"Depth scale: {depth_scale}")

# 断开连接
camera.disconnect()
