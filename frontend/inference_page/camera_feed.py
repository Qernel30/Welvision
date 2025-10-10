"""
Camera Feed Components for Inference Tab
"""
import tkinter as tk
from config import UI_COLORS
from .status_indicators import create_status_indicator


def setup_camera_frames(app, parent):
    """
    Setup camera feed display frames with status indicators and roller info
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Main camera container
    camera_container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    camera_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
    
    # Left side - BF Feed
    _setup_bf_feed(app, camera_container)
    
    # Middle - OD Feed
    _setup_od_feed(app, camera_container)
    
    # Right side - Overall Result and Roller Info
    _setup_right_panel(app, camera_container)
    
    # Configure grid weights - 3 columns
    camera_container.grid_columnconfigure(0, weight=2)  # BF Feed
    camera_container.grid_columnconfigure(1, weight=2)  # OD Feed
    camera_container.grid_columnconfigure(2, weight=1)  # Right panel
    camera_container.grid_rowconfigure(0, weight=1)


def _setup_bf_feed(app, parent):
    """Setup BF Feed section with status indicator"""
    # BF Feed Frame
    bf_container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    bf_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    
    # Header with label
    bf_label = tk.Label(
        bf_container,
        text="BF Feed",
        font=("Arial", 14, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="w"
    )
    bf_label.pack(fill=tk.X, padx=10, pady=(0, 5))
    
    # Status indicator button (separate, boxed)
    app.bf_status_indicator = tk.Button(
        bf_container,
        text="● Not Ready",
        font=("Arial", 10, "bold"),
        fg="white",
        bg="#FF0000",  # Red background
        relief=tk.RAISED,
        bd=2,
        state=tk.DISABLED,
        disabledforeground="white"
    )
    app.bf_status_indicator.pack(padx=10, pady=(0, 5))
    
    # Camera canvas - optimized size to fit screen without scrollbar
    app.bf_canvas = tk.Canvas(
        bf_container,
        bg="black",
        width=400,
        height=300,
        highlightthickness=2,
        highlightbackground="#333333"
    )
    app.bf_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)


def _setup_od_feed(app, parent):
    """Setup OD Feed section with status indicator"""
    # OD Feed Frame
    od_container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    od_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    # Header with label
    od_label = tk.Label(
        od_container,
        text="OD Feed",
        font=("Arial", 14, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="w"
    )
    od_label.pack(fill=tk.X, padx=10, pady=(0, 5))
    
    # Status indicator button (separate, boxed)
    app.od_status_indicator = tk.Button(
        od_container,
        text="● Not Ready",
        font=("Arial", 10, "bold"),
        fg="white",
        bg="#FF0000",  # Red background
        relief=tk.RAISED,
        bd=2,
        state=tk.DISABLED,
        disabledforeground="white"
    )
    app.od_status_indicator.pack(padx=10, pady=(0, 5))
    
    # Camera canvas - optimized size to fit screen without scrollbar
    app.od_canvas = tk.Canvas(
        od_container,
        bg="black",
        width=400,
        height=300,
        highlightthickness=2,
        highlightbackground="#333333"
    )
    app.od_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)


def _setup_right_panel(app, parent):
    """Setup right panel with Roller Info only"""
    # Right panel container
    right_container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    right_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
    
    # Roller Info section
    roller_frame = tk.LabelFrame(
        right_container,
        text="Roller Info:",
        font=("Arial", 12, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    roller_frame.pack(fill=tk.BOTH, padx=5, pady=(130, 5))
    
    # Roller info
    info_frame = tk.Frame(roller_frame, bg=UI_COLORS['PRIMARY_BG'])
    info_frame.pack(padx=15, pady=10, fill=tk.BOTH)
    
    _create_stat_row(info_frame, "Outer Diameter :", "25 mm", row=0, app_var_name='roller_outer_diameter', app=app)
    _create_stat_row(info_frame, "Dimple Diameter:", "20 mm", row=1, app_var_name='roller_dimple_diameter', app=app)
    _create_stat_row(info_frame, "Small Diameter :", "15 mm", row=2, app_var_name='roller_small_diameter', app=app)
    _create_stat_row(info_frame, "Roller Length :", "40.25 mm", row=3, app_var_name='roller_length', app=app)
    _create_stat_row(info_frame, "High Head (pixels):", "0 pixels", row=4, app_var_name='roller_high_head', app=app)
    _create_stat_row(info_frame, "Down Head (pixels):", "0 pixels", row=5, app_var_name='roller_down_head', app=app)


def _create_stat_row(parent, label_text, value_text, row, app_var_name, app):
    """Create a stat row with label and value (bold text)"""
    # Label - bold
    label = tk.Label(
        parent,
        text=label_text,
        font=("Arial", 11, "bold"),  # Increased from 10 to 11 and made bold
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="w"
    )
    label.grid(row=row, column=0, sticky="w", pady=5, padx=(5, 10))
    
    # Value - even bolder
    value_label = tk.Label(
        parent,
        text=value_text,
        font=("Arial", 12, "bold"),  # Increased from 10 to 12
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="e"
    )
    value_label.grid(row=row, column=1, sticky="e", pady=5, padx=(10, 5))
    
    # Store reference in app
    setattr(app, app_var_name, value_label)
    
    # Configure column weights
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)
