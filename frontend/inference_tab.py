"""
Inference tab UI components
"""
import tkinter as tk
import tkinter.ttk as ttk


def setup_inference_tab(app, parent):
    """Setup the inference tab with camera feeds and controls."""
    # Create frames for camera feeds
    camera_frame = tk.Frame(parent, bg="#0a2158")
    camera_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=10)
    
    # OD Camera frame
    od_frame = tk.LabelFrame(camera_frame, text="Camera 1 - OD", font=("Arial", 12, "bold"), 
                            fg="white", bg="#0a2158", bd=2)
    od_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    
    app.od_canvas = tk.Canvas(od_frame, bg="black", width=400, height=250)
    app.od_canvas.pack(padx=10, pady=5)
    
    # BIG FACE Camera frame
    bf_frame = tk.LabelFrame(camera_frame, text="Camera 2 - BIG FACE", font=("Arial", 12, "bold"), 
                            fg="white", bg="#0a2158", bd=2)
    bf_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
    
    app.bf_canvas = tk.Canvas(bf_frame, bg="black", width=400, height=250)
    app.bf_canvas.pack(padx=10, pady=5)
    
    # Configure grid weights
    camera_frame.grid_columnconfigure(0, weight=1)
    camera_frame.grid_columnconfigure(1, weight=1)
    camera_frame.grid_rowconfigure(0, weight=1)
    
    # Control buttons frame
    control_buttons_frame = tk.Frame(parent, bg="#0a2158")
    control_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    app.start_button = tk.Button(control_buttons_frame, text="Start Inspection", font=("Arial", 10, "bold"), 
                                bg="#28a745", fg="white", width=12, height=1, 
                                command=app.start_inspection)
    app.start_button.pack(side=tk.LEFT, padx=20, pady=5)
    
    app.stop_button = tk.Button(control_buttons_frame, text="Stop Inspection", font=("Arial", 10, "bold"), 
                                bg="#dc3545", fg="white", width=12, height=1, 
                                command=app.stop_inspection, state=tk.DISABLED)
    app.stop_button.pack(side=tk.LEFT, padx=20, pady=5)
    
    # Defect threshold controls
    threshold_panel = tk.LabelFrame(parent, text="Defect Threshold Controls", font=("Arial", 14, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
    threshold_panel.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
    
    # Create a frame for OD thresholds
    od_threshold_frame = tk.LabelFrame(threshold_panel, text="OD Defect Thresholds", font=("Arial", 12, "bold"), 
                                     fg="white", bg="#0a2158", bd=1)
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
    
    # Create a frame for BIG FACE thresholds
    bf_threshold_frame = tk.LabelFrame(threshold_panel, text="BIG FACE Defect Thresholds", font=("Arial", 12, "bold"), 
                                     fg="white", bg="#0a2158", bd=1)
    bf_threshold_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # Create sliders for BIG FACE defects
    row = 0
    for defect, value in app.bf_defect_thresholds.items():
        app.create_slider(bf_threshold_frame, defect, 0, 100, value, row)
        row += 1
    
    # Configure grid weights for threshold panel
    threshold_panel.grid_columnconfigure(0, weight=1)
    threshold_panel.grid_columnconfigure(1, weight=1)
