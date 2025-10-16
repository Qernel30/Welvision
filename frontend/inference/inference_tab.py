"""
Inference Tab UI Component
Modularized layout with status panel, camera feeds, results, and roller info
"""

import tkinter as tk
import numpy as np
import time
import threading
from ..utils.styles import Colors
from ..utils.config import AppConfig
from .status_panel import StatusPanel
from .camera_feed import CameraFeedManager
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .roller_info_panel import RollerInfoPanel


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
        self.status_panel = None
        self.camera_manager = None
        self.control_panel = None
        self.results_panel = None
        self.roller_info_panel = None
        
    def setup(self):
        """Setup the inference tab UI in a single-frame layout."""
        # Main container
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top section: Status panel
        self.status_panel = StatusPanel(main_container, self.app)
        self.status_panel.create()
        
        # Start monitoring status updates
        self._monitor_status_updates()
        
        # Middle section: Camera feeds only (full width)
        middle_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.camera_manager = CameraFeedManager(middle_frame)
        self.camera_manager.setup()
        
        # Bottom section: Results with roller info and control panel
        bottom_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Results panel (includes roller info now)
        self.results_panel = ResultsPanel(bottom_frame, self.app)
        self.results_panel.create()
        
        # Control panel
        self.control_panel = ControlPanel(bottom_frame, self.app)
        self.control_panel.setup()
    
    def update_od_camera(self):
        """Update OD camera feed display."""
        od_feed = self.camera_manager.get_feed('od')
        
        while self.app.camera_running:
            try:
                # Check if feed still exists
                if od_feed is None or od_feed.canvas is None:
                    break
                
                with self.app.annotated_frame_lock_od:
                    np_frame = np.frombuffer(
                        self.app.shared_annotated_od.get_obj(), 
                        dtype=np.uint8
                    ).reshape(self.app.frame_shape)
                    frame = np_frame.copy()

                # Update the camera feed
                od_feed.update_frame(frame)
                time.sleep(AppConfig.FRAME_UPDATE_RATE)
            except Exception as e:
                # Handle exceptions and exit gracefully
                print(f"OD camera thread error: {e}")
                break

    def update_bf_camera(self):
        """Update Bigface camera feed display."""
        bf_feed = self.camera_manager.get_feed('bf')
        
        while self.app.camera_running:
            try:
                # Check if feed still exists
                if bf_feed is None or bf_feed.canvas is None:
                    break
                
                with self.app.annotated_frame_lock_bigface:
                    np_frame = np.frombuffer(
                        self.app.shared_annotated_bigface.get_obj(), 
                        dtype=np.uint8
                    ).reshape(self.app.frame_shape)
                    frame = np_frame.copy()

                # Update the camera feed
                bf_feed.update_frame(frame)
                time.sleep(AppConfig.FRAME_UPDATE_RATE)
            except Exception as e:
                # Handle exceptions and exit gracefully
                print(f"BF camera thread error: {e}")
                break
    
    def start_camera_threads(self):
        """Start camera feed update threads."""
        self.app.od_thread = threading.Thread(target=self.update_od_camera)
        self.app.od_thread.daemon = True
        self.app.od_thread.start()
        
        self.app.bf_thread = threading.Thread(target=self.update_bf_camera)
        self.app.bf_thread.daemon = True
        self.app.bf_thread.start()
    
    def _monitor_status_updates(self):
        """Monitor shared_data for status updates and update status panel."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data and self.status_panel:
            # Get system_ready flag (master control)
            system_ready = self.app.shared_data.get('system_ready', False)
            
            if system_ready:
                # System is ready - show actual status
                
                # Update Machine Mode based on system_mode flag
                system_mode = self.app.shared_data.get('system_mode', False)
                if system_mode:
                    self.status_panel.update_machine_mode("AUTO", "#00ff00")  # Green
                else:
                    self.status_panel.update_machine_mode("MANUAL", "#ff0000")  # Red
                
                # Update Disc Status based on disc_status flag
                disc_status = self.app.shared_data.get('disc_status', False)
                if disc_status:
                    self.status_panel.update_disc_status("READY", "#00ff00")  # Green
                else:
                    self.status_panel.update_disc_status("NOT READY", "#ff0000")  # Red
            else:
                # System is not ready - show "Not Available" in yellow for both
                self.status_panel.update_machine_mode("Not Available", "#ffff00")  # Yellow
                self.status_panel.update_disc_status("Not Available", "#ffff00")  # Yellow
        
        # Continue monitoring every 500ms
        self.parent.after(500, self._monitor_status_updates)
