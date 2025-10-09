"""
Control Buttons for Inference Tab
"""
import tkinter as tk
from .inspection_control import start_inspection, stop_inspection, toggle_allow_all_images


def setup_control_buttons(app, parent):
    """
    Setup inspection control buttons
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Control buttons frame
    control_buttons_frame = tk.Frame(parent, bg="#0a2158")
    control_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Start button
    app.start_button = tk.Button(
        control_buttons_frame, 
        text="Start Inspection", 
        font=("Arial", 10, "bold"), 
        bg="#28a745", 
        fg="white", 
        width=12, 
        height=1, 
        command=lambda: start_inspection(app)
    )
    app.start_button.pack(side=tk.LEFT, padx=20, pady=5)
    
    # Stop button
    app.stop_button = tk.Button(
        control_buttons_frame, 
        text="Stop Inspection", 
        font=("Arial", 10, "bold"), 
        bg="#dc3545", 
        fg="white", 
        width=12, 
        height=1, 
        command=lambda: stop_inspection(app), 
        state=tk.DISABLED
    )
    app.stop_button.pack(side=tk.LEFT, padx=20, pady=5)
    
    # Allow All Images toggle
    app.allow_all_images_var = tk.BooleanVar(value=False)
    allow_all_images_check = tk.Checkbutton(
        control_buttons_frame,
        text="Allow All Images",
        font=("Arial", 10, "bold"),
        variable=app.allow_all_images_var,
        bg="#0a2158",
        fg="white",
        selectcolor="#1a3168",
        activebackground="#0a2158",
        activeforeground="white",
        command=lambda: toggle_allow_all_images(app)
    )
    allow_all_images_check.pack(side=tk.LEFT, padx=20, pady=5)
