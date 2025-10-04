"""
Frame capture module for camera feeds
"""
import cv2
import sys
import numpy as np
import time


def capture_frames_bigface(shared_frame_bigface, frame_lock_bigface, frame_shape):
    """Continuously capture frames from the camera."""
    print("Starting frame capture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    if not cap.isOpened():
        print("Failed to open camera.")
        sys.exit(1)

    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame.")
            time.sleep(0.1)


def capture_frames_od(shared_frame_od, frame_lock_od, frame_shape):
    """Continuously capture frames from the camera."""
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_shape[1])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_shape[0])

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, -1)
            with frame_lock_od:
                np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame.")
            time.sleep(0.01)
