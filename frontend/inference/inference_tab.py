"""
Inference Tab UI Component
"""

import tkinter as tk
import numpy as np
import time
import threading
from ..utils.styles import Colors
from ..utils.config import AppConfig
from .camera_feed import CameraFeedManager
from .control_panel import ControlPanel
from .threshold_panel import ThresholdPanel


class InferenceTab:
    """Inference tab for real-time inspection display and control."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the inference tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.camera_manager = None
        self.control_panel = None
        self.threshold_panel = None
        
    def setup(self):
        """Setup the inference tab UI."""
        # Setup camera feeds
        self.camera_manager = CameraFeedManager(self.parent)
        feeds = self.camera_manager.setup()
        
        # Setup control panel
        self.control_panel = ControlPanel(self.parent, self.app)
        self.control_panel.setup()
        
        # Setup threshold panel
        self.threshold_panel = ThresholdPanel(self.parent, self.app)
        self.threshold_panel.setup()
    
    def update_od_camera(self):
        """Update OD camera feed display."""
        od_feed = self.camera_manager.get_feed('od')
        
        while self.app.camera_running:
            with self.app.annotated_frame_lock_od:
                np_frame = np.frombuffer(
                    self.app.shared_annotated_od.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()

            # Update the camera feed
            od_feed.update_frame(frame)
            time.sleep(AppConfig.FRAME_UPDATE_RATE)

    def update_bf_camera(self):
        """Update Bigface camera feed display."""
        bf_feed = self.camera_manager.get_feed('bf')
        
        while self.app.camera_running:
            with self.app.annotated_frame_lock_bigface:
                np_frame = np.frombuffer(
                    self.app.shared_annotated_bigface.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()

            # Update the camera feed
            bf_feed.update_frame(frame)
            time.sleep(AppConfig.FRAME_UPDATE_RATE)
    
    def start_camera_threads(self):
        """Start camera feed update threads."""
        self.app.od_thread = threading.Thread(target=self.update_od_camera)
        self.app.od_thread.daemon = True
        self.app.od_thread.start()
        
        self.app.bf_thread = threading.Thread(target=self.update_bf_camera)
        self.app.bf_thread.daemon = True
        self.app.bf_thread.start()
