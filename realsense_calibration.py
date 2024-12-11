import pyrealsense2 as rs

# 创建相机管道
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # 启用左红外流
config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)  # 启用右红外流

try:
    # 启动相机管道
    pipeline.start(config)

    # 获取相机流的配置（包括内参）
    profile = pipeline.get_active_profile()
    infrared_stream_left = profile.get_stream(rs.stream.infrared, 1)
    infrared_stream_right = profile.get_stream(rs.stream.infrared, 2)

    # 获取左右红外相机的内参
    intrinsics_left = infrared_stream_left.as_video_stream_profile().get_intrinsics()
    intrinsics_right = infrared_stream_right.as_video_stream_profile().get_intrinsics()

    # 打印左相机内参
    print("Left Infrared Camera Intrinsics:")
    print(f"Width: {intrinsics_left.width}")
    print(f"Height: {intrinsics_left.height}")
    print(f"PPX (Principal Point X): {intrinsics_left.ppx}")
    print(f"PPY (Principal Point Y): {intrinsics_left.ppy}")
    print(f"FX (Focal Length X): {intrinsics_left.fx}")
    print(f"FY (Focal Length Y): {intrinsics_left.fy}")
    print(f"Distortion Model: {intrinsics_left.model}")
    print(f"Distortion Coefficients: {intrinsics_left.coeffs}")

    # 打印右相机内参
    print("\nRight Infrared Camera Intrinsics:")
    print(f"Width: {intrinsics_right.width}")
    print(f"Height: {intrinsics_right.height}")
    print(f"PPX (Principal Point X): {intrinsics_right.ppx}")
    print(f"PPY (Principal Point Y): {intrinsics_right.ppy}")
    print(f"FX (Focal Length X): {intrinsics_right.fx}")
    print(f"FY (Focal Length Y): {intrinsics_right.fy}")
    print(f"Distortion Model: {intrinsics_right.model}")
    print(f"Distortion Coefficients: {intrinsics_right.coeffs}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # 确保在退出时停止相机管道
    pipeline.stop()
