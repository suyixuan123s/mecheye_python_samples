# import pyrealsense2 as rs
#
# # 定义函数获取深度摄像头的内参矩阵
# def get_intrinsics_matrix(intrinsics):
#     """
#     Converts the intrinsics data into a matrix form.
#     """
#     return [
#         [intrinsics.fx, 0, intrinsics.ppx],
#         [0, intrinsics.fy, intrinsics.ppy],
#         [0, 0, 1]
#     ]
#
# # 初始化 RealSense 相机
# pipeline = rs.pipeline()
# config = rs.config()
# config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # 左红外摄像头（Index 1）
# config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)  # 右红外摄像头（Index 2）
# config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)       # 深度流
# pipeline.start(config)
#
# try:
#     # 获取一帧数据以获取内参
#     frames = pipeline.wait_for_frames()
#     infrared_left_frame = frames.get_infrared_frame(1)  # 获取左红外帧
#     infrared_right_frame = frames.get_infrared_frame(2)  # 获取右红外帧
#     depth_frame = frames.get_depth_frame()  # 获取深度帧
#
#     # 获取左红外摄像头的内参
#     left_intrinsics = infrared_left_frame.profile.as_video_stream_profile().intrinsics
#     print("Left Infrared Camera Intrinsics:")
#     print(f"  Width: {left_intrinsics.width}")
#     print(f"  Height: {left_intrinsics.height}")
#     print(f"  fx: {left_intrinsics.fx}")
#     print(f"  fy: {left_intrinsics.fy}")
#     print(f"  cx: {left_intrinsics.ppx}")
#     print(f"  cy: {left_intrinsics.ppy}")
#     print(f"  Distortion coefficients: {left_intrinsics.coeffs}")
#     print(f"  Distortion model: {left_intrinsics.model}\n")
#
#     # 获取右红外摄像头的内参
#     right_intrinsics = infrared_right_frame.profile.as_video_stream_profile().intrinsics
#     print("Right Infrared Camera Intrinsics:")
#     print(f"  Width: {right_intrinsics.width}")
#     print(f"  Height: {right_intrinsics.height}")
#     print(f"  fx: {right_intrinsics.fx}")
#     print(f"  fy: {right_intrinsics.fy}")
#     print(f"  cx: {right_intrinsics.ppx}")
#     print(f"  cy: {right_intrinsics.ppy}")
#     print(f"  Distortion coefficients: {right_intrinsics.coeffs}")
#     print(f"  Distortion model: {right_intrinsics.model}\n")
#
#     # 获取深度摄像头的内参
#     depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
#     print("Depth Camera Intrinsics:")
#     print(f"  Width: {depth_intrinsics.width}")
#     print(f"  Height: {depth_intrinsics.height}")
#     print(f"  fx: {depth_intrinsics.fx}")
#     print(f"  fy: {depth_intrinsics.fy}")
#     print(f"  cx: {depth_intrinsics.ppx}")
#     print(f"  cy: {depth_intrinsics.ppy}")
#     print(f"  Distortion coefficients: {depth_intrinsics.coeffs}")
#     print(f"  Distortion model: {depth_intrinsics.model}\n")
#
#     # 输出深度相机的内参矩阵形式
#     depth_intrinsics_matrix = get_intrinsics_matrix(depth_intrinsics)
#     print("Intrinsic matrix for RealSense D435 depth camera:")
#     for row in depth_intrinsics_matrix:
#         print(row)
#
# finally:
#     # 停止相机管道
#     pipeline.stop()
#


import pyrealsense2 as rs

def get_intrinsics():
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    config = rs.config()

    # Configure the pipeline to stream the depth stream
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)

    # Get frames from the camera to get the intrinsic parameters
    profile = pipeline.get_active_profile()
    depth_stream = profile.get_stream(rs.stream.depth)
    intr = depth_stream.as_video_stream_profile().get_intrinsics()

    # Stop the pipeline
    pipeline.stop()

    # Intrinsics matrix
    intrinsics_matrix = [
        [intr.fx, 0, intr.ppx],
        [0, intr.fy, intr.ppy],
        [0, 0, 1]
    ]

    # Distortion coefficients
    distortion_coefficients = intr.coeffs

    return intrinsics_matrix, distortion_coefficients

if __name__ == "__main__":
    intrinsics_matrix, distortion_coefficients = get_intrinsics()
    print("Intrinsic matrix for RealSense D435 depth camera:")
    for row in intrinsics_matrix:
        print(row)
    print("\nDistortion coefficients for RealSense D435 depth camera:")
    print(distortion_coefficients)
