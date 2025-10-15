"""
Camera Feed Component
Displays live camera feeds with annotations
"""

import tkinter as tk
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
import time
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig


class CameraFeed:
    """Component for displaying a single camera feed."""
    
    def __init__(self, parent, title, canvas_id):
        """
        Initialize a camera feed display.
        
        Args:
            parent: Parent frame
            title: Camera title (e.g., "Camera 1 - OD")
            canvas_id: Identifier for this camera (e.g., "od" or "bf")
        """
        self.parent = parent
        self.title = title
        self.canvas_id = canvas_id
        self.canvas = None
        
    def create(self, row, column):
        """
        Create the camera feed UI.
        
        Args:
            row: Grid row position
            column: Grid column position
        """
        # Create frame for this camera
        camera_frame = tk.LabelFrame(
            self.parent,
            text=self.title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        camera_frame.grid(row=row, column=column, padx=10, pady=5, sticky="nsew")
        
        # Create canvas for displaying video
        self.canvas = tk.Canvas(
            camera_frame,
            bg=Colors.BLACK,
            width=AppConfig.CAMERA_WIDTH,
            height=AppConfig.CAMERA_HEIGHT
        )
        self.canvas.pack(padx=10, pady=5)
        
        return camera_frame
    
    def update_frame(self, frame):
        """
        Update the displayed frame.
        
        Args:
            frame: OpenCV frame (BGR format)
        """
        if self.canvas is None:
            return
        
        try:
            # Check if canvas still exists (not destroyed)
            if not self.canvas.winfo_exists():
                return
            
            # Resize frame to fit canvas
            resized_frame = cv2.resize(frame, (AppConfig.CAMERA_WIDTH, AppConfig.CAMERA_HEIGHT))
            
            # Convert from BGR to RGB
            img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk  # Keep a reference to prevent garbage collection
        except tk.TclError:
            # Widget has been destroyed, stop updating
            return
        except Exception as e:
            # Handle any other exceptions silently
            print(f"Error updating camera feed: {e}")
            return


class CameraFeedManager:
    """Manages multiple camera feeds."""
    
    def __init__(self, parent):
        """
        Initialize the camera feed manager.
        
        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.feeds = {}
        self.camera_frame = None
        
    def setup(self):
        """Setup all camera feeds."""
        # Create main camera frame
        self.camera_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        self.camera_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=10)
        
        # Configure grid weights
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(1, weight=1)
        self.camera_frame.grid_rowconfigure(0, weight=1)
        
        # Create OD camera feed
        od_feed = CameraFeed(self.camera_frame, "Camera 1 - OD", "od")
        od_feed.create(row=0, column=0)
        self.feeds['od'] = od_feed
        
        # Create Bigface camera feed
        bf_feed = CameraFeed(self.camera_frame, "Camera 2 - BIG FACE", "bf")
        bf_feed.create(row=0, column=1)
        self.feeds['bf'] = bf_feed
        
        return self.feeds
    
    def get_feed(self, feed_id):
        """
        Get a specific camera feed.
        
        Args:
            feed_id: Camera feed identifier ('od' or 'bf')
            
        Returns:
            CameraFeed instance or None
        """
        return self.feeds.get(feed_id)
