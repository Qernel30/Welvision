"""
Control Panel Component
Contains start/stop buttons and inspection controls
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class ControlPanel:
    """Control panel for inspection operations."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the control panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.start_button = None
        self.stop_button = None
        
    def setup(self):
        """Setup the control panel UI."""
        # Control buttons frame
        control_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start Inspection button
        self.start_button = tk.Button(
            control_frame,
            text="Start Inspection",
            font=Fonts.SMALL_BOLD,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self.app.start_inspection
        )
        self.start_button.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Stop Inspection button
        self.stop_button = tk.Button(
            control_frame,
            text="Stop Inspection",
            font=Fonts.SMALL_BOLD,
            bg=Colors.DANGER,
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self.app.stop_inspection,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=5)
        
        return control_frame
    
    def enable_start(self):
        """Enable the start button and disable stop button."""
        if self.start_button:
            self.start_button.config(state=tk.NORMAL)
        if self.stop_button:
            self.stop_button.config(state=tk.DISABLED)
    
    def enable_stop(self):
        """Enable the stop button and disable start button."""
        if self.start_button:
            self.start_button.config(state=tk.DISABLED)
        if self.stop_button:
            self.stop_button.config(state=tk.NORMAL)
