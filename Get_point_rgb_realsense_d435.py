import open3d as o3d
import time
from typing import Literal
import numpy as np
import pyrealsense2 as rs
import cv2
import os

# 设置保存路径
point_cloud_dir = r'E:\ABB\AI\mecheye_python_samples\area_scan_3d_camera\point_cloud'
rgb_image_dir = r'E:\ABB\AI\mecheye_python_samples\area_scan_3d_camera\rgb_images'
os.makedirs(point_cloud_dir, exist_ok=True)
os.makedirs(rgb_image_dir, exist_ok=True)

DEPTH_RESOLUTION_MID = (640, 480)
COLOR_RESOLUTION_MID = (640, 480)
DEPTH_RESOLUTION_HIGH = (1280, 720)
COLOR_RESOLUTION_HIGH = (1280, 720)
DEPTH_FPS = 30
COLOR_FPS = 30


def find_devices():
    '''
    Find the Realsense device connected to the computer
    :return:
    '''
    ctx = rs.context()
    serials = []
    if len(ctx.devices) > 0:
        for dev in ctx.devices:
            print('Found device: ', dev.get_info(rs.camera_info.name), ' ', dev.get_info(rs.camera_info.serial_number))
            serials.append(dev.get_info(rs.camera_info.serial_number))
    else:
        print("No Intel Device connected")
    return serials, ctx

def stream_data(pipe: rs.pipeline, pc: rs.pointcloud) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    frames = pipe.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    points = pc.calculate(depth_frame)
    pc.map_to(color_frame)
    v, t = points.get_vertices(), points.get_texture_coordinates()
    verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
    texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv
    cw, ch = color_image.shape[:2][::-1]
    v, u = (texcoords * (cw, ch) + 0.5).astype(np.uint32).T
    np.clip(u, 0, ch - 1, out=u)
    np.clip(v, 0, cw - 1, out=v)
    pc_color = color_image[u, v] / 255
    pc_color[:, [0, 2]] = pc_color[:, [2, 0]]
    return verts, pc_color, depth_image, color_image

class RealSenseD400s(object):
    def __init__(self, resolution: Literal['mid', 'high'] = 'high', device: str = None):
        assert resolution in ['mid', 'high']
        self._pipeline = rs.pipeline()
        self._config = rs.config()
        if device is not None:
            self._config.enable_device(device)
        depth_resolution = (640, 480)
        color_resolution = (640, 480)
        depth_fps = 15
        color_fps = 15
        self._config.enable_stream(rs.stream.depth, depth_resolution[0], depth_resolution[1], rs.format.z16, depth_fps)
        self._config.enable_stream(rs.stream.color, color_resolution[0], color_resolution[1], rs.format.bgr8, color_fps)
        try:
            self._profile = self._pipeline.start(self._config)
        except RuntimeError as e:
            print(f"Failed to start RealSense pipeline for device {device}: {e}")
            self._pipeline = None
            return
        self._pc = rs.pointcloud()
        color_frame = self._pipeline.wait_for_frames().get_color_frame()
        self._color_intr = color_frame.profile.as_video_stream_profile().intrinsics
        self.intr_mat = np.array([[self._color_intr.fx, 0, self._color_intr.ppx],
                                  [0, self._color_intr.fy, self._color_intr.ppy],
                                  [0, 0, 1]])
        self.intr_distcoeffs = np.asarray(self._color_intr.coeffs)

    def req_data(self):
        if self._pipeline:
            return stream_data(pipe=self._pipeline, pc=self._pc)
        else:
            raise RuntimeError("Pipeline not initialized")

    def get_pcd(self, return_color=False):
        pcd, pcd_color, _, _ = self.req_data()
        if return_color:
            return pcd, pcd_color
        return pcd

    def get_color_img(self):
        _, _, _, color_img = self.req_data()
        return color_img

    def get_depth_img(self):
        _, _, depth_img, _ = self.req_data()
        return depth_img

    def stop(self):
        if self._pipeline:
            self._pipeline.stop()

    def __del__(self):
        self.stop()

if __name__ == "__main__":
    serials, ctx = find_devices()
    rs_pipelines = []
    for ser in serials:
        try:
            rs_pipelines.append(RealSenseD400s(device=ser))
        except Exception as e:
            print(f"Failed to initialize RealSense device {ser}: {e}")

    while True:
        for ind, pipeline in enumerate(rs_pipelines):
            try:
                pcd, pcd_color, depth_img, color_img = pipeline.req_data()
                cv2.imshow(f"color image {ind}", color_img)
            except RuntimeError as e:
                print(f"Error during data streaming for device {ind}: {e}")
        k = cv2.waitKey(1)

        if k == 13:  # Enter key to save point cloud and image
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                pcd_filename = os.path.join(point_cloud_dir, f'point_cloud_{timestamp}.ply')
                rgb_image_filename = os.path.join(rgb_image_dir, f'rgb_image_{timestamp}.png')

                # Save point cloud
                o3d_pcd = o3d.geometry.PointCloud()
                o3d_pcd.points = o3d.utility.Vector3dVector(pcd)
                o3d_pcd.colors = o3d.utility.Vector3dVector(pcd_color)
                o3d.io.write_point_cloud(pcd_filename, o3d_pcd)
                print(f"Point cloud saved successfully: {pcd_filename}")

                # Save RGB image
                cv2.imwrite(rgb_image_filename, color_img)
                print(f"RGB image saved successfully: {rgb_image_filename}")

            except Exception as e:
                print(f"Failed to save point cloud or RGB image: {e}")

        if k == 27:  # ESC key to exit
            break

    for pipeline in rs_pipelines:
        pipeline.stop()


cv2.waitKey(0)

cv2.destroyAllWindows()