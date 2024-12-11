import open3d

"""
Interface for Realsense D400 Series.
Realsense API Python example: https://dev.intelrealsense.com/docs/python2
Realsense D405 Datasheet: https://dev.intelrealsense.com/docs/intel-realsense-d400-series-product-family-datasheet
Author: Chen Hao (chen960216@gmail.com), osaka
Requirement libs: 'pyrealsense2', 'numpy'
Importance: This program needs to connect to USB3 to work 
Update Notes: '0.0.1'/20220719: Implement the functions to capture the point clouds and depth camera
              '0.0.2'/20221110: 1,Implement the functions to stream multiple cameras, 2, remove multiprocessing
"""
import time
from typing import Literal
import multiprocessing as mp
import numpy as np
import pyrealsense2 as rs


try:
    import cv2
    aruco = cv2.aruco
except:
    print("Cv2 aruco does not exist, some functions will stop")


__VERSION__ = '0.0.2'

# Read chapter 4 of datasheet for details
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
    ctx = rs.context()  # Create librealsense context for managing devices
    serials = []
    if len(ctx.devices) > 0:
        for dev in ctx.devices:
            print('Found device: ', dev.get_info(rs.camera_info.name), ' ', dev.get_info(rs.camera_info.serial_number))
            serials.append(dev.get_info(rs.camera_info.serial_number))
    else:
        print("No Intel Device connected")

    return serials, ctx


def stream_data(pipe: rs.pipeline, pc: rs.pointcloud) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    '''
    Stream data for RealSense
    :param pipe: rs.piepline
    :param pc: rs.pointcloud
    :return: point cloud, point cloud color, depth image and color image
    '''
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
        """
        :param resolution: Resolution setting for the stream
        :param device: Serial number of the device
        """
        assert resolution in ['mid', 'high']
        self._pipeline = rs.pipeline()
        self._config = rs.config()
        if device is not None:
            self._config.enable_device(device)

        # Use a more compatible resolution and frame rate
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
        """Require 1) point cloud, 2) point cloud color, 3) depth image and 4) color image"""
        if self._pipeline:
            return stream_data(pipe=self._pipeline, pc=self._pc)
        else:
            raise RuntimeError("Pipeline not initialized")

    def get_pcd(self, return_color=False):
        """Get point cloud data."""
        pcd, pcd_color, _, _ = self.req_data()
        if return_color:
            return pcd, pcd_color
        return pcd

    def get_color_img(self):
        """Get color image"""
        _, _, _, color_img = self.req_data()
        return color_img

    def get_depth_img(self):
        """Get depth image"""
        _, _, depth_img, _ = self.req_data()
        return depth_img

    def stop(self):
        """Stops the pipeline."""
        if self._pipeline:
            self._pipeline.stop()

    def __del__(self):
        self.stop()


if __name__ == "__main__":
    import cv2

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

        if k == 13:
            try:
                o3d_pcd = open3d.geometry.PointCloud()
                o3d_pcd.points = open3d.utility.Vector3dVector(pcd)
                o3d_pcd.colors = open3d.utility.Vector3dVector(pcd_color)
                open3d.io.write_point_cloud(
                    r'E:\ABB\AI\mecheye_python_samples\area_scan_3d_camera\point_cloud\point_cloud.ply', o3d_pcd)
                print("Point cloud saved successfully.")
            except Exception as e:
                print(f"Failed to save point cloud: {e}")



        if k == 27:
            break

    for pipeline in rs_pipelines:
        pipeline.stop()
