import pyrealsense2 as rs
import numpy as np
import cv2
import os

import time

# 创建一个上下文对象
pipeline = rs.pipeline()
config = rs.config()

# 配置流格式
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # 左目红外相机
config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)  # 右目红外相机

# 设置保存路径
left_folder = r"E:\ABB\AI\mecheye_python_samples\data\data_left"
right_folder = r"E:\ABB\AI\mecheye_python_samples\data\data_right"
os.makedirs(left_folder, exist_ok=True)
os.makedirs(right_folder, exist_ok=True)


last_save_time = time.time()
save_interval = 2



# 开始流
pipeline.start(config)

try:
    frame_count = 0  # 用于命名文件

    while True:
        # 获取图像帧
        frames = pipeline.wait_for_frames()
        left_frame = frames.get_infrared_frame(1)  # 左目相机
        right_frame = frames.get_infrared_frame(2)  # 右目相机

        # 将帧转换为numpy数组
        left_image = np.asanyarray(left_frame.get_data())
        right_image = np.asanyarray(right_frame.get_data())

        # 显示图像
        cv2.imshow('Left Camera', left_image)
        cv2.imshow('Right Camera', right_image)

        key = cv2.waitKey(1)

        # 按下'Enter'键保存图像，按下'Esc'键退出
        if time.time() -last_save_time > save_interval:
            last_save_time = time.time()


        # if key == 13:  # Enter键的ASCII码是13
            left_image_path = os.path.join(left_folder, f"left_{frame_count:04d}.png")
            right_image_path = os.path.join(right_folder, f"right_{frame_count:04d}.png")
            cv2.imwrite(left_image_path, left_image)
            cv2.imwrite(right_image_path, right_image)
            print(f"Saved left image: {left_image_path}")
            print(f"Saved right image: {right_image_path}")
            frame_count += 1
        elif key == 27:  # Esc键的ASCII码是27
            break

finally:
    # 停止流并关闭窗口
    pipeline.stop()
    cv2.destroyAllWindows()

#  camera1 intrinsics.K 内参矩阵

# 383.905266265649	0	325.425937554606
# 0	383.997916689355	242.088312865496
# 0	0	1

#  camera2 intrinsics.K 内参矩阵
# 384.756853303731	0	325.881628853657
# 0	384.888376194341	242.542765063833
# 0	0	1