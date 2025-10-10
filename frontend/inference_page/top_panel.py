"""
Top Panel Module - Roller type, Date/Time, Machine Mode, Disc Status, Confidence Thresholds, AI Models
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import UI_COLORS


def setup_top_panel(app, parent):
    """
    Setup the top panel with roller type, date/time, mode, status, thresholds, and AI models
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Main top panel frame
    top_panel = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    top_panel.pack(fill=tk.X, padx=10, pady=(5, 5))
    
    # Create 6 sections in the top panel
    _create_roller_type_section(app, top_panel)
    _create_datetime_section(app, top_panel)
    _create_machine_mode_section(app, top_panel)
    _create_disc_status_section(app, top_panel)
    _create_confidence_section(app, top_panel)
    _create_ai_models_section(app, top_panel)
    
    # Configure grid weights for equal distribution
    for i in range(6):
        top_panel.grid_columnconfigure(i, weight=1)


def _create_roller_type_section(app, parent):
    """Create Roller Type dropdown section"""
    frame = tk.LabelFrame(
        parent,
        text="Roller type",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    
    # Dropdown for roller type
    app.roller_type_var = tk.StringVar(value="")
    roller_dropdown = ttk.Combobox(
        frame,
        textvariable=app.roller_type_var,
        font=("Arial", 13),
        state="readonly",
        width=15
    )
    roller_dropdown['values'] = ("Type A", "Type B", "Type C", "Type D")
    roller_dropdown.pack(padx=10, pady=10, fill=tk.X)


def _create_datetime_section(app, parent):
    """Create Date & Time display section"""
    frame = tk.LabelFrame(
        parent,
        text="Date & Time",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    # Date and time label
    app.datetime_label = tk.Label(
        frame,
        text=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"),
        font=("Arial", 13),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.datetime_label.pack(padx=10, pady=15)
    
    # Update datetime every second
    def update_datetime():
        # Check if widget still exists before updating
        if app.datetime_label.winfo_exists():
            try:
                app.datetime_label.config(text=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
                app.after(1000, update_datetime)
            except tk.TclError:
                # Widget was destroyed, stop updating
                pass
    
    update_datetime()


def _create_machine_mode_section(app, parent):
    """Create Machine Mode display section"""
    frame = tk.LabelFrame(
        parent,
        text="Machine Mode",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
    
    # Mode label with green AUTO text
    app.mode_label = tk.Label(
        frame,
        text="AUTO",
        font=("Arial", 13, "bold"),
        fg="#00FF00",  # Bright green
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.mode_label.pack(padx=10, pady=15)


def _create_disc_status_section(app, parent):
    """Create Disc Status display section"""
    frame = tk.LabelFrame(
        parent,
        text="Disc Status",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
    
    # Status label with red "Not Ready" text
    app.disc_status_label = tk.Label(
        frame,
        text="Not Ready",
        font=("Arial", 13, "bold"),
        fg="#FF0000",  # Red
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.disc_status_label.pack(padx=10, pady=15)


def _create_confidence_section(app, parent):
    """Create Confidence Thresholds display section"""
    frame = tk.LabelFrame(
        parent,
        text="Confidence Thresholds",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=4, padx=5, pady=5, sticky="nsew")
    
    # Inner frame for confidence values
    inner_frame = tk.Frame(frame, bg=UI_COLORS['PRIMARY_BG'])
    inner_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # BF confidence
    bf_label = tk.Label(
        inner_frame,
        text="BF:",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG']
    )
    bf_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
    
    app.bf_confidence_display = tk.Label(
        inner_frame,
        text="25.0%",
        font=("Arial", 13),
        fg="#00CED1",  # Cyan
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.bf_confidence_display.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # OD confidence
    od_label = tk.Label(
        inner_frame,
        text="OD:",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG']
    )
    od_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
    
    app.od_confidence_display = tk.Label(
        inner_frame,
        text="25.0%",
        font=("Arial", 13),
        fg="#00CED1",  # Cyan
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.od_confidence_display.grid(row=1, column=1, sticky="w", padx=5, pady=2)


def _create_ai_models_section(app, parent):
    """Create AI Models display section"""
    frame = tk.LabelFrame(
        parent,
        text="AI Models",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=5, padx=5, pady=5, sticky="nsew")
    
    # Inner frame for model info
    inner_frame = tk.Frame(frame, bg=UI_COLORS['PRIMARY_BG'])
    inner_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # BigFace Model
    bf_model_label = tk.Label(
        inner_frame,
        text="BigFace Model:",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG']
    )
    bf_model_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
    
    app.bf_model_status = tk.Label(
        inner_frame,
        text="No model selected",
        font=("Arial", 13),
        fg="#FF6347",  # Tomato red
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.bf_model_status.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # OD Model
    od_model_label = tk.Label(
        inner_frame,
        text="OD Model:",
        font=("Arial", 13, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG']
    )
    od_model_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
    
    app.od_model_status = tk.Label(
        inner_frame,
        text="No model selected",
        font=("Arial", 13),
        fg="#FF6347",  # Tomato red
        bg=UI_COLORS['PRIMARY_BG']
    )
    app.od_model_status.grid(row=1, column=1, sticky="w", padx=5, pady=2)


def update_confidence_display(app):
    """Update confidence threshold displays"""
    bf_conf = app.shared_data.get('bigface_confidence', 0.25) * 100
    od_conf = app.shared_data.get('od_confidence', 0.25) * 100
    
    app.bf_confidence_display.config(text=f"{bf_conf:.1f}%")
    app.od_confidence_display.config(text=f"{od_conf:.1f}%")


def update_model_status(app, bf_loaded=False, od_loaded=False):
    """Update AI model status displays"""
    if bf_loaded:
        app.bf_model_status.config(text="Loaded ✓", fg="#00FF00")
    else:
        app.bf_model_status.config(text="No model selected", fg="#FF6347")
    
    if od_loaded:
        app.od_model_status.config(text="Loaded ✓", fg="#00FF00")
    else:
        app.od_model_status.config(text="No model selected", fg="#FF6347")


def update_disc_status(app, ready=False):
    """Update disc status display"""
    if ready:
        app.disc_status_label.config(text="Ready", fg="#00FF00")
    else:
        app.disc_status_label.config(text="Not Ready", fg="#FF0000")
