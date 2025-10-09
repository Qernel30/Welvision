"""
Camera feed management and display
"""
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
import tkinter as tk
import time
import threading


def start_camera_feeds(app):
    """Start the camera feed update threads."""
    app.camera_running = True
    
    app.od_thread = threading.Thread(target=lambda: update_od_camera(app))
    app.od_thread.daemon = True
    app.od_thread.start()
    
    app.bf_thread = threading.Thread(target=lambda: update_bf_camera(app))
    app.bf_thread.daemon = True
    app.bf_thread.start()


def update_od_camera(app):
    """Update OD camera feed on canvas."""
    while app.camera_running:
        with app.annotated_frame_lock_od:
            np_frame = np.frombuffer(app.shared_annotated_od.get_obj(), dtype=np.uint8).reshape(app.frame_shape)
            frame = np_frame.copy()

        resized_frame = cv2.resize(frame, (400, 250))
        # Convert frame to a format compatible with Tkinter
        img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
        imgtk = PIL.ImageTk.PhotoImage(image=img)

        # Update the canvas
        app.od_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        app.od_canvas.image = imgtk

        time.sleep(0.03)  # Limit update rate


def update_bf_camera(app):
    """Update Bigface camera feed on canvas."""
    while app.camera_running:
        with app.annotated_frame_lock_bigface:
            np_frame = np.frombuffer(app.shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(app.frame_shape)
            frame = np_frame.copy()

        resized_frame = cv2.resize(frame, (400, 250))
        # Convert frame to a format compatible with Tkinter
        img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
        imgtk = PIL.ImageTk.PhotoImage(image=img)

        # Update the canvas
        app.bf_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        app.bf_canvas.image = imgtk

        time.sleep(0.03)  # Limit update rate
