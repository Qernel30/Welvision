"""
Camera Statistics and Defect Breakdown Components
"""
import tkinter as tk
import numpy as np
from .stat_card import create_stat_label


def setup_camera_stats(app, parent):
    """
    Setup camera-specific statistics with defect breakdowns
    
    Args:
        app: Main application instance
        parent: Parent container frame
    """
    # Create two frames for OD and BF statistics
    stats_frame = tk.Frame(parent, bg="#0a2158")
    stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # OD Statistics
    _setup_od_stats(app, stats_frame)
    
    # BIG FACE Statistics
    _setup_bf_stats(app, stats_frame)
    
    # Configure grid weights for stats frame
    stats_frame.grid_columnconfigure(0, weight=1)
    stats_frame.grid_columnconfigure(1, weight=1)
    stats_frame.grid_rowconfigure(0, weight=1)


def _setup_od_stats(app, parent):
    """Setup OD camera statistics section"""
    od_stats_frame = tk.LabelFrame(
        parent, 
        text="OD Camera Statistics", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    od_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    # OD Stats variables
    app.od_inspected_var = tk.StringVar(value="0")
    app.od_defective_var = tk.StringVar(value="0")
    app.od_good_var = tk.StringVar(value="0")
    app.od_proportion_var = tk.StringVar(value="0%")
    
    od_stats_inner = tk.Frame(od_stats_frame, bg="#0a2158")
    od_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    create_stat_label(od_stats_inner, "Rollers Inspected:", app.od_inspected_var, 0)
    create_stat_label(od_stats_inner, "Defective Rollers:", app.od_defective_var, 1)
    create_stat_label(od_stats_inner, "Good Rollers:", app.od_good_var, 2)
    create_stat_label(od_stats_inner, "Defective Proportion:", app.od_proportion_var, 3)
    
    # OD Defect breakdown
    _setup_defect_breakdown(app, od_stats_frame, app.od_defect_thresholds)


def _setup_bf_stats(app, parent):
    """Setup BIG FACE camera statistics section"""
    bf_stats_frame = tk.LabelFrame(
        parent, 
        text="BIG FACE Camera Statistics", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    bf_stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # BIG FACE Stats variables
    app.bf_inspected_var = tk.StringVar(value="0")
    app.bf_defective_var = tk.StringVar(value="0")
    app.bf_good_var = tk.StringVar(value="0")
    app.bf_proportion_var = tk.StringVar(value="0%")
    
    bf_stats_inner = tk.Frame(bf_stats_frame, bg="#0a2158")
    bf_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    create_stat_label(bf_stats_inner, "Rollers Inspected:", app.bf_inspected_var, 0)
    create_stat_label(bf_stats_inner, "Defective Rollers:", app.bf_defective_var, 1)
    create_stat_label(bf_stats_inner, "Good Rollers:", app.bf_good_var, 2)
    create_stat_label(bf_stats_inner, "Defective Proportion:", app.bf_proportion_var, 3)
    
    # BF Defect breakdown
    _setup_defect_breakdown(app, bf_stats_frame, app.bf_defect_thresholds)


def _setup_defect_breakdown(app, parent, defect_thresholds):
    """
    Setup defect type breakdown table
    
    Args:
        app: Main application instance
        parent: Parent frame
        defect_thresholds: Dictionary of defect types
    """
    defect_frame = tk.LabelFrame(
        parent, 
        text="Defect Types", 
        font=("Arial", 14, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=1
    )
    defect_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create grid for defect stats
    defect_grid = tk.Frame(defect_frame, bg="#0a2158")
    defect_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Headers
    headers = ["Defect Type", "Count", "Percentage"]
    for col, header in enumerate(headers):
        label = tk.Label(
            defect_grid, 
            text=header, 
            font=("Arial", 12, "bold"), 
            fg="white", 
            bg="#0a2158", 
            padx=10, 
            pady=5
        )
        label.grid(row=0, column=col, sticky="w")
    
    # Defect rows (mock data for now)
    for row, defect in enumerate(defect_thresholds.keys()):
        # Defect name
        label = tk.Label(
            defect_grid, 
            text=defect, 
            font=("Arial", 10), 
            fg="white", 
            bg="#0a2158", 
            padx=10, 
            pady=5, 
            anchor="w"
        )
        label.grid(row=row+1, column=0, sticky="w")
        
        # Count (mock data)
        count = np.random.randint(0, 50)
        label = tk.Label(
            defect_grid, 
            text=str(count), 
            font=("Arial", 10), 
            fg="white", 
            bg="#0a2158", 
            padx=10, 
            pady=5
        )
        label.grid(row=row+1, column=1)
        
        # Percentage (mock data)
        percentage = np.random.randint(1, 30)
        label = tk.Label(
            defect_grid, 
            text=f"{percentage}%", 
            font=("Arial", 10), 
            fg="white", 
            bg="#0a2158", 
            padx=10, 
            pady=5
        )
        label.grid(row=row+1, column=2)
