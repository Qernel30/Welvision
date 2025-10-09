"""
Frame capture module for camera feeds
"""
import cv2
import sys
import numpy as np
import time
from .camera_detector import get_camera_index_by_name


def capture_frames_bigface(shared_frame_bigface, frame_lock_bigface, frame_shape, camera_name):
    """
    Continuously capture frames from the Bigface camera.
    
    Args:
        shared_frame_bigface: Shared memory array for frame storage
        frame_lock_bigface: Lock for thread-safe frame access
        frame_shape: Shape of the frame (height, width, channels)
        camera_name: Name of the camera to find dynamically
    """
    
    # Dynamically find camera index
    camera_index = get_camera_index_by_name(camera_name)
    
    if camera_index is None:
        print(f"⚠️ Camera '{camera_name}' not found. Using fallback index 0")
        camera_index = 0
    
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    if not cap.isOpened():
        print(f"❌ Failed to open Bigface camera at index {camera_index}.")
        sys.exit(1)


    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame from Bigface camera.")
            time.sleep(0.1)


def capture_frames_od(shared_frame_od, frame_lock_od, frame_shape, camera_name):
    """
    Continuously capture frames from the OD camera.
    
    Args:
        shared_frame_od: Shared memory array for frame storage
        frame_lock_od: Lock for thread-safe frame access
        frame_shape: Shape of the frame (height, width, channels)
        camera_name: Name of the camera to find dynamically
    """    
    # Dynamically find camera index
    camera_index = get_camera_index_by_name(camera_name)
    
    if camera_index is None:
        print(f"⚠️ Camera '{camera_name}' not found. Using fallback index 1")
        camera_index = 1
    
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_shape[1])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_shape[0])

    if not cap.isOpened():
        print(f"❌ Failed to open OD camera at index {camera_index}.")
        return


    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, -1)
            with frame_lock_od:
                np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame from OD camera.")
            time.sleep(0.01)
