"""
Model Confidence Slider Components
"""
import tkinter as tk
import tkinter.ttk as ttk


def setup_confidence_sliders(app, parent):
    """
    Setup model confidence threshold sliders
    
    Args:
        app: Main application instance
        parent: Parent container frame
    """
    # Model confidence section
    conf_frame = tk.LabelFrame(
        parent, 
        text="Model Confidence Thresholds", 
        font=("Arial", 14, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    conf_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # OD Model Confidence
    _setup_od_confidence_slider(app, conf_frame)
    
    # BIG FACE Model Confidence
    _setup_bf_confidence_slider(app, conf_frame)


def _setup_od_confidence_slider(app, parent):
    """Setup OD model confidence slider"""
    od_conf_frame = tk.Frame(parent, bg="#0a2158", pady=10)
    od_conf_frame.pack(fill=tk.X, padx=10)
    
    od_conf_label = tk.Label(
        od_conf_frame, 
        text="OD Model Confidence", 
        font=("Arial", 12), 
        fg="white", 
        bg="#0a2158", 
        width=20, 
        anchor="w"
    )
    od_conf_label.pack(side=tk.LEFT, padx=10)
    
    # Initialize with default value (25% = 0.25)
    if not hasattr(app, 'od_conf_threshold'):
        app.od_conf_threshold = 0.25
    app.od_conf_slider_value = tk.DoubleVar(value=app.od_conf_threshold * 100)
    
    od_conf_slider = ttk.Scale(
        od_conf_frame, 
        from_=1, 
        to=100, 
        orient=tk.HORIZONTAL, 
        length=300, 
        variable=app.od_conf_slider_value
    )
    od_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    app.od_conf_value_label = tk.Label(
        od_conf_frame, 
        text=f"{int(app.od_conf_threshold * 100)}%", 
        font=("Arial", 12), 
        fg="white", 
        bg="#0a2158", 
        width=5
    )
    app.od_conf_value_label.pack(side=tk.LEFT, padx=10)
    
    # Update OD confidence value label when slider is moved
    def update_od_conf_label(val):
        app.od_conf_value_label.config(text=f"{int(float(val))}%")
        app.od_conf_threshold = float(val) / 100
        if hasattr(app, 'inspection_running') and app.inspection_running:
            app.update_model_confidence()
    
    od_conf_slider.config(command=update_od_conf_label)


def _setup_bf_confidence_slider(app, parent):
    """Setup BIG FACE model confidence slider"""
    bf_conf_frame = tk.Frame(parent, bg="#0a2158", pady=10)
    bf_conf_frame.pack(fill=tk.X, padx=10)
    
    bf_conf_label = tk.Label(
        bf_conf_frame, 
        text="Bigface Model Confidence", 
        font=("Arial", 12), 
        fg="white", 
        bg="#0a2158", 
        width=20, 
        anchor="w"
    )
    bf_conf_label.pack(side=tk.LEFT, padx=10)
    
    # Initialize with default value (25% = 0.25)
    if not hasattr(app, 'bf_conf_threshold'):
        app.bf_conf_threshold = 0.25
    app.bf_conf_slider_value = tk.DoubleVar(value=app.bf_conf_threshold * 100)
    
    bf_conf_slider = ttk.Scale(
        bf_conf_frame, 
        from_=1, 
        to=100, 
        orient=tk.HORIZONTAL, 
        length=300, 
        variable=app.bf_conf_slider_value
    )
    bf_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    app.bf_conf_value_label = tk.Label(
        bf_conf_frame, 
        text=f"{int(app.bf_conf_threshold * 100)}%", 
        font=("Arial", 12), 
        fg="white", 
        bg="#0a2158", 
        width=5
    )
    app.bf_conf_value_label.pack(side=tk.LEFT, padx=10)
    
    # Update BF confidence value label when slider is moved
    def update_bf_conf_label(val):
        app.bf_conf_value_label.config(text=f"{int(float(val))}%")
        app.bf_conf_threshold = float(val) / 100
        if hasattr(app, 'inspection_running') and app.inspection_running:
            app.update_model_confidence()
    
    bf_conf_slider.config(command=update_bf_conf_label)
