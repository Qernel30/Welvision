"""
Control Buttons for Inference Tab
"""
import tkinter as tk
from config import UI_COLORS
from .inspection_control import start_inspection, stop_inspection, toggle_allow_all_images


def setup_control_buttons(app, parent):
    """
    Setup inspection control buttons (Start, Stop, Reset, Allow all images)
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Control buttons frame
    control_buttons_frame = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    control_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
    
    # Left side - buttons
    button_container = tk.Frame(control_buttons_frame, bg=UI_COLORS['PRIMARY_BG'])
    button_container.pack(side=tk.LEFT, padx=10)
    
    # Start button - Green (navbar style)
    app.start_button = tk.Button(
        button_container, 
        text="Start", 
        font=("Arial", 12, "bold"), 
        bg="#28a745",  # Green
        fg="white", 
        relief=tk.FLAT,
        bd=0,
        padx=40,  # Wider like navbar
        pady=10,  # Taller like navbar
        cursor="hand2",
        command=lambda: start_inspection(app)
    )
    app.start_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Stop button - Gray (disabled by default, navbar style)
    app.stop_button = tk.Button(
        button_container, 
        text="Stop", 
        font=("Arial", 12, "bold"), 
        bg="#6c757d",  # Gray
        fg="white", 
        relief=tk.FLAT,
        bd=0,
        padx=40,  # Wider like navbar
        pady=10,  # Taller like navbar
        cursor="hand2",
        command=lambda: stop_inspection(app), 
        state=tk.DISABLED
    )
    app.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Reset button - Orange (navbar style)
    app.reset_button = tk.Button(
        button_container, 
        text="Reset", 
        font=("Arial", 12, "bold"), 
        bg="#FF8C00",  # Orange
        fg="white", 
        relief=tk.FLAT,
        bd=0,
        padx=40,  # Wider like navbar
        pady=10,  # Taller like navbar
        cursor="hand2",
        command=lambda: reset_statistics(app)
    )
    app.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Right side - checkbox (larger)
    checkbox_container = tk.Frame(control_buttons_frame, bg=UI_COLORS['PRIMARY_BG'])
    checkbox_container.pack(side=tk.LEFT, padx=20)
    
    # Allow All Images checkbox - larger size
    app.allow_all_images_var = tk.BooleanVar(value=False)
    allow_all_images_check = tk.Checkbutton(
        checkbox_container,
        text="Allow all images",
        font=("Arial", 13, "bold"),  # Increased from 11 to 13
        variable=app.allow_all_images_var,
        bg=UI_COLORS['PRIMARY_BG'],
        fg="white",
        selectcolor=UI_COLORS['SECONDARY_BG'],
        activebackground=UI_COLORS['PRIMARY_BG'],
        activeforeground="white",
        cursor="hand2",
        command=lambda: toggle_allow_all_images(app)
    )
    allow_all_images_check.pack(pady=5)


def reset_statistics(app):
    """Reset all statistics to zero"""
    # Reset BF stats
    app.bf_inspected = 0
    app.bf_defective = 0
    app.bf_good = 0
    
    # Reset OD stats
    app.od_inspected = 0
    app.od_defective = 0
    app.od_good = 0
    
    # Update displays
    from .results_display import update_bf_results, update_od_results, update_overall_results
    update_bf_results(app)
    update_od_results(app)
    update_overall_results(app)
    
    print("📊 Statistics reset to zero")
