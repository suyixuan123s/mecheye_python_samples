# import numpy as np
# import cv2
# import pyrealsense2 as rs
# import os
#
# # 定义棋盘格参数
# CHECKERBOARD = (11, 8)  # 棋盘格的行数和列数（角点数量）
# square_size = 0.03  # 每个棋盘格方块的大小（单位：米，30毫米）
#
# # 准备3D点，棋盘格的世界坐标系点集
# objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
# objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)
# objp *= square_size
#
# # 用于存储3D点和2D点的列表
# objpoints = []  # 世界坐标系中的3D点
# imgpoints_left = []  # 左红外摄像头的2D点
# imgpoints_right = []  # 右红外摄像头的2D点
#
# # 保存路径
# save_path = 'E:\\ABB\\AI\\mecheye_python_samples\\data'
# os.makedirs(save_path, exist_ok=True)
#
# # 初始化 RealSense 相机
# pipeline = rs.pipeline()
# config = rs.config()
# config.enable_stream(rs.stream.infrared, 1, 1280, 720, rs.format.y8, 30)  # 左红外摄像头（Index 1）
# config.enable_stream(rs.stream.infrared, 2, 1280, 720, rs.format.y8, 30)  # 右红外摄像头（Index 2）
# pipeline.start(config)
#
# try:
#     # 收集样本
#     sample_count = 0
#     while len(objpoints) < 50:  # 增加采集的样本数量，提高标定精度
#         frames = pipeline.wait_for_frames()
#         infrared_left_frame = frames.get_infrared_frame(1)
#         infrared_right_frame = frames.get_infrared_frame(2)
#         if not infrared_left_frame or not infrared_right_frame:
#             print("Frame not received, retrying...")
#             continue
#
#         # 转换为NumPy数组
#         img_left = np.asanyarray(infrared_left_frame.get_data())
#         img_right = np.asanyarray(infrared_right_frame.get_data())
#         gray_left = img_left
#         gray_right = img_right
#
#         # 查找棋盘格角点
#         ret_left, corners_left = cv2.findChessboardCorners(gray_left, CHECKERBOARD, None)
#         ret_right, corners_right = cv2.findChessboardCorners(gray_right, CHECKERBOARD, None)
#
#         if ret_left and ret_right:
#             objpoints.append(objp)
#             imgpoints_left.append(corners_left)
#             imgpoints_right.append(corners_right)
#
#             # 绘制角点
#             cv2.drawChessboardCorners(img_left, CHECKERBOARD, corners_left, ret_left)
#             cv2.drawChessboardCorners(img_right, CHECKERBOARD, corners_right, ret_right)
#
#             # 保存检测到的图像
#             left_image_path = os.path.join(save_path, f"left_ir_{sample_count:02d}.png")
#             right_image_path = os.path.join(save_path, f"right_ir_{sample_count:02d}.png")
#             cv2.imwrite(left_image_path, img_left)
#             cv2.imwrite(right_image_path, img_right)
#             print(f"Saved images: {left_image_path}, {right_image_path}")
#
#             sample_count += 1
#
#             # 显示图像
#             cv2.imshow('Left IR', img_left)
#             cv2.imshow('Right IR', img_right)
#             cv2.waitKey(500)  # 暂停 500 毫秒，便于调整棋盘格位置
#
#         # 按下 'q' 键退出
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Exiting loop...")
#             break
#
#     cv2.destroyAllWindows()
#
#     # 获取图像的尺寸
#     image_size = (gray_left.shape[1], gray_left.shape[0])  # (width, height)
#
#     # 标定左红外摄像头的内参
#     ret_left, camera_matrix_left, dist_coeffs_left, rvecs_left, tvecs_left = cv2.calibrateCamera(
#         objpoints, imgpoints_left, image_size, None, None
#     )
#
#     # 标定右红外摄像头的内参
#     ret_right, camera_matrix_right, dist_coeffs_right, rvecs_right, tvecs_right = cv2.calibrateCamera(
#         objpoints, imgpoints_right, image_size, None, None
#     )
#
#     # 进行双目标定，计算外参
#     ret_stereo, camera_matrix_left, dist_coeffs_left, camera_matrix_right, dist_coeffs_right, R, T, E, F = cv2.stereoCalibrate(
#         objpoints, imgpoints_left, imgpoints_right, camera_matrix_left, dist_coeffs_left,
#         camera_matrix_right, dist_coeffs_right, image_size,
#         criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6),
#         flags=cv2.CALIB_FIX_INTRINSIC
#     )
#
#     # 输出双目系统的旋转矩阵 R 和 平移向量 T
#     print("Rotation Matrix R:\n", R)
#     print("Translation Vector T:\n", T)
#
# finally:
#     pipeline.stop()


import numpy as np
import cv2
import pyrealsense2 as rs
import os

# 定义棋盘格参数
CHECKERBOARD = (11, 8)  # 棋盘格的行数和列数（角点数量）
square_size = 0.03  # 每个棋盘格方块的大小（单位：米，30毫米）

# 准备3D点，棋盘格的世界坐标系点集
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)
objp *= square_size

# 用于存储3D点和2D点的列表
objpoints = []  # 世界坐标系中的3D点
imgpoints_left = []  # 左红外摄像头的2D点
imgpoints_right = []  # 右红外摄像头的2D点

# 保存路径
save_path = 'E:\\ABB\\AI\\mecheye_python_samples\\data'
os.makedirs(save_path, exist_ok=True)

# 初始化 RealSense 相机
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.infrared, 1, 1280, 720, rs.format.y8, 30)  # 左红外摄像头（Index 1）
config.enable_stream(rs.stream.infrared, 2, 1280, 720, rs.format.y8, 30)  # 右红外摄像头（Index 2）
pipeline.start(config)

try:
    # 收集样本
    sample_count = 0
    while len(objpoints) < 50:  # 增加采集的样本数量，提高标定精度
        frames = pipeline.wait_for_frames()
        infrared_left_frame = frames.get_infrared_frame(1)
        infrared_right_frame = frames.get_infrared_frame(2)
        if not infrared_left_frame or not infrared_right_frame:
            print("Frame not received, retrying...")
            continue

        # 转换为NumPy数组
        img_left = np.asanyarray(infrared_left_frame.get_data())
        img_right = np.asanyarray(infrared_right_frame.get_data())
        gray_left = img_left
        gray_right = img_right

        # 查找棋盘格角点
        ret_left, corners_left = cv2.findChessboardCorners(gray_left, CHECKERBOARD, None)
        ret_right, corners_right = cv2.findChessboardCorners(gray_right, CHECKERBOARD, None)

        if ret_left and ret_right:
            objpoints.append(objp)
            imgpoints_left.append(corners_left)
            imgpoints_right.append(corners_right)

            # 绘制角点
            cv2.drawChessboardCorners(img_left, CHECKERBOARD, corners_left, ret_left)
            cv2.drawChessboardCorners(img_right, CHECKERBOARD, corners_right, ret_right)

            # 保存检测到的图像
            left_image_path = os.path.join(save_path, f"left_ir_{sample_count:02d}.png")
            right_image_path = os.path.join(save_path, f"right_ir_{sample_count:02d}.png")
            cv2.imwrite(left_image_path, img_left)
            cv2.imwrite(right_image_path, img_right)
            print(f"Saved images: {left_image_path}, {right_image_path}")

            sample_count += 1

            # 显示图像
            cv2.imshow('Left IR', img_left)
            cv2.imshow('Right IR', img_right)
            cv2.waitKey(500)  # 暂停 500 毫秒，便于调整棋盘格位置

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting loop...")
            break

    cv2.destroyAllWindows()

    # 获取图像的尺寸
    image_size = (gray_left.shape[1], gray_left.shape[0])  # (width, height)

    # 标定左红外摄像头的内参
    ret_left, camera_matrix_left, dist_coeffs_left, rvecs_left, tvecs_left = cv2.calibrateCamera(
        objpoints, imgpoints_left, image_size, None, None
    )

    # 标定右红外摄像头的内参
    ret_right, camera_matrix_right, dist_coeffs_right, rvecs_right, tvecs_right = cv2.calibrateCamera(
        objpoints, imgpoints_right, image_size, None, None
    )

    # 进行双目标定，计算外参
    ret_stereo, camera_matrix_left, dist_coeffs_left, camera_matrix_right, dist_coeffs_right, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpoints_left, imgpoints_right, camera_matrix_left, dist_coeffs_left,
        camera_matrix_right, dist_coeffs_right, image_size,
        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6),
        flags=cv2.CALIB_FIX_INTRINSIC
    )

    # 输出双目系统的旋转矩阵 R 和 平移向量 T
    print("Rotation Matrix R:\n", R)
    print("Translation Vector T:\n", T)

    # 计算重投影误差
    total_error = 0
    total_points = 0
    for i in range(len(objpoints)):
        # 重新投影到左图像
        imgpoints2_left, _ = cv2.projectPoints(objpoints[i], rvecs_left[i], tvecs_left[i], camera_matrix_left, dist_coeffs_left)
        error_left = cv2.norm(imgpoints_left[i], imgpoints2_left, cv2.NORM_L2) / len(imgpoints2_left)

        # 重新投影到右图像
        imgpoints2_right, _ = cv2.projectPoints(objpoints[i], rvecs_right[i], tvecs_right[i], camera_matrix_right, dist_coeffs_right)
        error_right = cv2.norm(imgpoints_right[i], imgpoints2_right, cv2.NORM_L2) / len(imgpoints2_right)

        total_error += error_left + error_right
        total_points += 2 * len(imgpoints2_left)

    mean_error = total_error / total_points
    print(f"Mean reprojection error: {mean_error}")

    # 使用 cv2.stereoRectify 进行图像矫正
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        camera_matrix_left, dist_coeffs_left,
        camera_matrix_right, dist_coeffs_right,
        image_size, R, T, alpha=0
    )

    # 计算矫正映射
    map1_left, map2_left = cv2.initUndistortRectifyMap(
        camera_matrix_left, dist_coeffs_left, R1, P1, image_size, cv2.CV_16SC2
    )
    map1_right, map2_right = cv2.initUndistortRectifyMap(
        camera_matrix_right, dist_coeffs_right, R2, P2, image_size, cv2.CV_16SC2
    )

    # 对图像进行矫正并显示
    rectified_left = cv2.remap(img_left, map1_left, map2_left, cv2.INTER_LINEAR)
    rectified_right = cv2.remap(img_right, map1_right, map2_right, cv2.INTER_LINEAR)
    cv2.imshow('Rectified Left', rectified_left)
    cv2.imshow('Rectified Right', rectified_right)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

finally:
    pipeline.stop()
