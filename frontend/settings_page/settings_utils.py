"""
Settings Utilities - Model confidence and threshold management
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from config import UI_COLORS


def update_model_confidence(app):
    """
    Updates the confidence thresholds of the YOLO models in real-time.
    
    Args:
        app: Main application instance
    """
    if not hasattr(app, 'inspection_running') or not app.inspection_running:
        return
    
    # Get current confidence values from sliders
    od_conf = app.od_conf_threshold
    bf_conf = app.bf_conf_threshold
    
    print(f"Updating model confidence: OD={od_conf:.2f}, Bigface={bf_conf:.2f}")
    
    # Update the shared data dictionary with new confidence values
    if hasattr(app, 'shared_data'):
        app.shared_data['od_conf_threshold'] = od_conf
        app.shared_data['bf_conf_threshold'] = bf_conf
    
    # If you need to update the models directly (if they're in the main process)
    if hasattr(app, 'model_od'):
        app.model_od.conf = od_conf
    
    if hasattr(app, 'model_bigface'):
        app.model_bigface.conf = bf_conf


def save_thresholds(app):
    """
    Saves the current threshold settings.
    
    Args:
        app: Main application instance
    """
    # Save model confidence thresholds
    app.od_conf_threshold = float(app.od_conf_slider_value.get()) / 100
    app.bf_conf_threshold = float(app.bf_conf_slider_value.get()) / 100
    
    # Update the shared data dictionary with new confidence values
    if hasattr(app, 'shared_data'):
        app.shared_data['od_conf_threshold'] = app.od_conf_threshold
        app.shared_data['bf_conf_threshold'] = app.bf_conf_threshold
    
    # If inspection is running, update the model in real-time
    if hasattr(app, 'inspection_running') and app.inspection_running:
        update_model_confidence(app)

    messagebox.showinfo("Settings Saved", "Model confidence settings have been saved successfully.")
    print(f"OD Confidence: {app.od_conf_threshold}, BF Confidence: {app.bf_conf_threshold}")


def create_slider(app, parent, label_text, min_val, max_val, default_val, row, is_od=True):
    """
    Create a slider widget for threshold adjustment.
    
    Args:
        app: Main application instance
        parent: Parent widget
        label_text: Label for the slider
        min_val: Minimum slider value
        max_val: Maximum slider value
        default_val: Default slider value
        row: Grid row position
        is_od: Whether this is for OD camera (True) or Bigface (False)
    
    Returns:
        The created slider widget
    """
    if not hasattr(app, "slider_values"):  
        app.slider_values = {}

    frame = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

    label = tk.Label(frame, text=label_text, font=("Arial", 10), fg=UI_COLORS['WHITE'], 
                    bg=UI_COLORS['PRIMARY_BG'], width=20, anchor="w")
    label.pack(side=tk.LEFT, padx=5)

    slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200)
    slider.set(default_val)  
    slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    value_label = tk.Label(frame, text=f"{default_val}%", font=("Arial", 10), 
                          fg=UI_COLORS['WHITE'], bg=UI_COLORS['PRIMARY_BG'], width=5)
    value_label.pack(side=tk.RIGHT, padx=5)

    slider.configure(command=lambda val, lbl=value_label, defect=label_text, is_od=is_od: 
                    update_threshold(app, val, lbl, defect, is_od))

    app.slider_values[label_text] = slider
    
    return slider


def update_threshold(app, val, label, defect, is_od):
    """
    Update threshold value when slider is moved.
    
    Args:
        app: Main application instance
        val: New slider value
        label: Label widget to update
        defect: Defect type name
        is_od: Whether this is for OD camera
    """
    label.config(text=f"{int(float(val))}%")
