"""
Control Panel Component
Contains start/stop/reset buttons and allow images checkbox
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
        self.reset_button = None
        self.allow_images_var = None
        
    def setup(self):
        """Setup the control panel UI."""
        # Control buttons frame with better spacing
        control_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Start button
        self.start_button = tk.Button(
            control_frame,
            text="Start",
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self.app.start_inspection
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Stop button
        self.stop_button = tk.Button(
            control_frame,
            text="Stop",
            font=Fonts.TEXT_BOLD,
            bg="#6c757d",  # Gray
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self.app.stop_inspection,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Reset button
        self.reset_button = tk.Button(
            control_frame,
            text="Reset",
            font=Fonts.TEXT_BOLD,
            bg="#ff8c00",  # Orange
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self._reset_results
        )
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Allow all images checkbox
        self.allow_images_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(
            control_frame,
            text="Allow all images",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.PRIMARY_BG,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE,
            variable=self.allow_images_var,
            command=self._toggle_allow_images
        )
        checkbox.pack(side=tk.LEFT, padx=30, pady=5)
        
        return control_frame
    
    def _reset_results(self):
        """Reset all inspection results."""
        print("Resetting results...")
        # Reset statistics
        self.app.od_inspected = 0
        self.app.od_defective = 0
        self.app.od_good = 0
        self.app.bf_inspected = 0
        self.app.bf_defective = 0
        self.app.bf_good = 0
    
    def _toggle_allow_images(self):
        """Toggle allow all images setting."""
        status = "enabled" if self.allow_images_var.get() else "disabled"
        print(f"Allow all images: {status}")
    
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
