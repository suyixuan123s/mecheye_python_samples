import numpy as np
import cv2
import pyrealsense2 as rs
import pickle
import os

# 设置棋盘格参数
CHECKERBOARD = (11, 8)  # 棋盘格的行数和列数（角点数量）
square_size = 0.03  # 每个棋盘格方块的大小，单位为米（例如30毫米）

# 创建棋盘格在世界坐标系中的3D点坐标

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)
objp *= square_size  # 乘以实际的方块尺寸

# 存储3D点和2D图像点
objpoints = []  # 存储3D点（世界坐标系）
imgpoints = []  # 存储2D点（图像坐标系）

# 创建保存图像的文件夹
output_dir = r'E:\ABB\AI\mecheye_python_samples\Point_Cloud_Dataset'
os.makedirs(output_dir, exist_ok=True)

# 初始化RealSense相机
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipeline.start(config)

try:
    print("Press 'Enter' to capture a chessboard image, or 'Esc' to quit and start calibration.")
    image_counter = 0  # 用于图像文件命名
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())

        # 转为灰度图像
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # 检测棋盘格角点
        ret, corners = cv2.findChessboardCorners(gray_image, CHECKERBOARD, None)

        # 显示检测到的角点
        if ret:
            cv2.drawChessboardCorners(color_image, CHECKERBOARD, corners, ret)

        # 显示彩色图像
        cv2.imshow('RealSense Chessboard', color_image)

        # 等待用户输入
        key = cv2.waitKey(1) & 0xFF

        if key == 13:
            print(f"Chessboard corners detected: {ret}")
            if ret:
                # 存储角点数据
                objpoints.append(objp)
                imgpoints.append(corners)
                print(f"Captured image {len(objpoints)} with detected corners.")

            # 保存当前图像到指定文件夹
            image_filename = os.path.join(output_dir, f'chessboard_image_{image_counter}.png')
            cv2.imwrite(image_filename, color_image)
            print(f"Saved image {image_filename}")
            image_counter += 1

        if key == 27:  # Esc键的ASCII码是27
            print("Exiting image capture loop.")
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()

# 检查是否采集到足够的图像
if len(objpoints) < 10:
    print("Not enough images for calibration. Need at least 10 images with detected corners.")
    exit()

# 执行内参标定
print("Starting camera calibration...")
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray_image.shape[::-1], None, None
)

# 输出标定结果
print("Calibration completed.")
print(f"Camera matrix:\n{camera_matrix}")
print(f"Distortion coefficients:\n{dist_coeffs}")

# 保存标定结果到文件
calibration_data = {
    'camera_matrix': camera_matrix,
    'dist_coeffs': dist_coeffs
}
output_path = os.path.join(output_dir, 'calibration_data.pkl')
with open(output_path, 'wb') as f:
    pickle.dump(calibration_data, f)
print(f"Calibration data saved to {output_path}")

# 使用标定结果进行图像矫正
pipeline.start(config)
try:
    print("Press 'Esc' to quit the undistortion demo.")
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())

        # 使用标定结果进行图像矫正
        undistorted_image = cv2.undistort(color_image, camera_matrix, dist_coeffs)

        # 显示原图和矫正后的图像
        cv2.imshow('Original Image', color_image)
        cv2.imshow('Undistorted Image', undistorted_image)

        if cv2.waitKey(1) & 0xFF == 27:  # Esc键
            print("Exiting undistortion demo.")
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
