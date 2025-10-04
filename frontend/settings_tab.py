"""
Settings tab UI components
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox


def setup_settings_tab(app, parent):
    """
    Creates the UI for the settings tab, only adjusting the confidence thresholds
    of the OD and Bigface YOLO models in real-time.
    
    Args:
        app: The main application instance
        parent: The parent frame (settings tab)
    """
    # Main container for settings
    settings_container = tk.Frame(parent, bg="#0a2158")
    settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Settings Title
    title_label = tk.Label(settings_container, text="Model Confidence Settings", 
                           font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
    title_label.pack(pady=(0, 20))
    
    # ===== MODEL CONFIDENCE SECTION =====
    conf_frame = tk.LabelFrame(settings_container, text="Model Confidence Thresholds", 
                               font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
    conf_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # OD Model Confidence Slider
    od_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=10)
    od_conf_frame.pack(fill=tk.X, padx=10)
    
    od_conf_label = tk.Label(od_conf_frame, text="OD Model Confidence", font=("Arial", 12), 
                             fg="white", bg="#0a2158", width=20, anchor="w")
    od_conf_label.pack(side=tk.LEFT, padx=10)
    
    # Initialize with default value (25% = 0.25)
    if not hasattr(app, 'od_conf_threshold'):
        app.od_conf_threshold = 0.25
    app.od_conf_slider_value = tk.DoubleVar(value=app.od_conf_threshold * 100)
    
    od_conf_slider = ttk.Scale(od_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                               length=300, variable=app.od_conf_slider_value)
    od_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    app.od_conf_value_label = tk.Label(od_conf_frame, text=f"{int(app.od_conf_threshold * 100)}%", 
                                        font=("Arial", 12), fg="white", bg="#0a2158", width=5)
    app.od_conf_value_label.pack(side=tk.LEFT, padx=10)
    
    # Update OD confidence value label when slider is moved
    def update_od_conf_label(val):
        app.od_conf_value_label.config(text=f"{int(float(val))}%")
        # Update the actual threshold value
        app.od_conf_threshold = float(val) / 100
        # If inspection is running, update the model in real-time
        if hasattr(app, 'inspection_running') and app.inspection_running:
            app.update_model_confidence()
    
    od_conf_slider.config(command=update_od_conf_label)
    
    # BIG FACE Model Confidence Slider
    bf_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=10)
    bf_conf_frame.pack(fill=tk.X, padx=10)
    
    bf_conf_label = tk.Label(bf_conf_frame, text="Bigface Model Confidence", font=("Arial", 12), 
                             fg="white", bg="#0a2158", width=20, anchor="w")
    bf_conf_label.pack(side=tk.LEFT, padx=10)
    
    # Initialize with default value (25% = 0.25)
    if not hasattr(app, 'bf_conf_threshold'):
        app.bf_conf_threshold = 0.25
    app.bf_conf_slider_value = tk.DoubleVar(value=app.bf_conf_threshold * 100)
    
    bf_conf_slider = ttk.Scale(bf_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                               length=300, variable=app.bf_conf_slider_value)
    bf_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    app.bf_conf_value_label = tk.Label(bf_conf_frame, text=f"{int(app.bf_conf_threshold * 100)}%", 
                                        font=("Arial", 12), fg="white", bg="#0a2158", width=5)
    app.bf_conf_value_label.pack(side=tk.LEFT, padx=10)
    
    # Update BF confidence value label when slider is moved
    def update_bf_conf_label(val):
        app.bf_conf_value_label.config(text=f"{int(float(val))}%")
        # Update the actual threshold value
        app.bf_conf_threshold = float(val) / 100
        # If inspection is running, update the model in real-time
        if hasattr(app, 'inspection_running') and app.inspection_running:
            app.update_model_confidence()
    
    bf_conf_slider.config(command=update_bf_conf_label)
    
    # Save button for settings
    save_button = tk.Button(settings_container, text="Save Settings", font=("Arial", 12, "bold"),
                            bg="#28a745", fg="white", command=app.save_thresholds)
    save_button.pack(pady=20)
