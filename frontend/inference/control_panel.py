"""
Control Panel Component
Contains start/stop/reset buttons and allow images checkbox
"""

import tkinter as tk
from tkinter import messagebox
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
            command=self._on_start_inspection
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
    
    def _on_start_inspection(self):
        """Handle start button click and monitor system readiness."""
        # Start the inspection process
        self.app.start_inspection()
        
        # Start monitoring for system readiness
        self._check_system_ready()
    
    def _check_system_ready(self):
        """Check if both BF and OD models are ready and show popup."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # Check if overall system is ready
            if self.app.shared_data.get('overall_system_ready', False):
                # Show success popup
                messagebox.showinfo(
                    "System Ready",
                    "✅ System is Ready!\n\nBoth BF and OD models have been loaded and warmed up successfully.\nLights are ON and the system is ready for inspection."
                )
                return
            
            # If not ready yet, check again after 500ms
            if self.app.inspection_running:
                self.parent.after(500, self._check_system_ready)
    
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
