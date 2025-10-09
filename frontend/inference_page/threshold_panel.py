"""
Defect Threshold Panel for Inference Tab
"""
import tkinter as tk
import tkinter.ttk as ttk


def setup_threshold_panel(app, parent):
    """
    Setup defect threshold controls panel
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Defect threshold controls
    threshold_panel = tk.LabelFrame(
        parent, 
        text="Defect Threshold Controls", 
        font=("Arial", 14, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    threshold_panel.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
    
    # OD Thresholds Section
    _setup_od_thresholds(app, threshold_panel)
    
    # BIG FACE Thresholds Section
    _setup_bf_thresholds(app, threshold_panel)
    
    # Configure grid weights for threshold panel
    threshold_panel.grid_columnconfigure(0, weight=1)
    threshold_panel.grid_columnconfigure(1, weight=1)


def _setup_od_thresholds(app, parent):
    """Setup OD defect threshold sliders"""
    # Create a frame for OD thresholds
    od_threshold_frame = tk.LabelFrame(
        parent, 
        text="OD Defect Thresholds", 
        font=("Arial", 12, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=1
    )
    od_threshold_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    
    # Create a scrollable frame for OD thresholds
    od_canvas = tk.Canvas(od_threshold_frame, bg="#0a2158", highlightthickness=0)
    od_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    od_scrollbar = ttk.Scrollbar(od_threshold_frame, orient="vertical", command=od_canvas.yview)
    od_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    od_canvas.configure(yscrollcommand=od_scrollbar.set)
    od_canvas.bind('<Configure>', lambda e: od_canvas.configure(scrollregion=od_canvas.bbox("all")))
    
    od_sliders_frame = tk.Frame(od_canvas, bg="#0a2158")
    od_canvas.create_window((0, 0), window=od_sliders_frame, anchor="nw")
    
    # Create sliders for OD defects
    row = 0
    for defect, value in app.od_defect_thresholds.items():
        app.create_slider(od_sliders_frame, defect, 0, 100, value, row)
        row += 1


def _setup_bf_thresholds(app, parent):
    """Setup BIG FACE defect threshold sliders"""
    # Create a frame for BIG FACE thresholds
    bf_threshold_frame = tk.LabelFrame(
        parent, 
        text="BIG FACE Defect Thresholds", 
        font=("Arial", 12, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=1
    )
    bf_threshold_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # Create sliders for BIG FACE defects
    row = 0
    for defect, value in app.bf_defect_thresholds.items():
        app.create_slider(bf_threshold_frame, defect, 0, 100, value, row)
        row += 1
