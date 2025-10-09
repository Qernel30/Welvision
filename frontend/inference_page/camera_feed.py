"""
Camera Feed Components for Inference Tab
"""
import tkinter as tk


def setup_camera_frames(app, parent):
    """
    Setup camera feed display frames
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Create frames for camera feeds
    camera_frame = tk.Frame(parent, bg="#0a2158")
    camera_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=10)
    
    # OD Camera frame
    od_frame = tk.LabelFrame(
        camera_frame, 
        text="Camera 1 - OD", 
        font=("Arial", 12, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    od_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    
    app.od_canvas = tk.Canvas(od_frame, bg="black", width=400, height=250)
    app.od_canvas.pack(padx=10, pady=5)
    
    # BIG FACE Camera frame
    bf_frame = tk.LabelFrame(
        camera_frame, 
        text="Camera 2 - BIG FACE", 
        font=("Arial", 12, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    bf_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
    
    app.bf_canvas = tk.Canvas(bf_frame, bg="black", width=400, height=250)
    app.bf_canvas.pack(padx=10, pady=5)
    
    # Configure grid weights
    camera_frame.grid_columnconfigure(0, weight=1)
    camera_frame.grid_columnconfigure(1, weight=1)
    camera_frame.grid_rowconfigure(0, weight=1)
