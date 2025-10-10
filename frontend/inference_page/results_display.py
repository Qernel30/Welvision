"""
Results Display Module - BF Result, OD Result, and Overall Result at bottom
"""
import tkinter as tk
from config import UI_COLORS


def setup_results_panel(app, parent):
    """
    Setup the results panel with BF, OD, and Overall results (bottom section)
    
    Args:
        app: Main application instance
        parent: Parent frame (below camera feeds)
    """
    # Main results container
    results_container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    results_container.pack(fill=tk.X, expand=False, padx=10, pady=(0, 5))
    
    # Left - BF Result
    _setup_bf_result(app, results_container)
    
    # Middle - OD Result
    _setup_od_result(app, results_container)
    
    # Right - Overall Result
    _setup_overall_result(app, results_container)
    
    # Configure grid weights for 3 equal columns
    results_container.grid_columnconfigure(0, weight=1)
    results_container.grid_columnconfigure(1, weight=1)
    results_container.grid_columnconfigure(2, weight=1)
    results_container.grid_rowconfigure(0, weight=1)


def _setup_bf_result(app, parent):
    """Setup Bigface Result section"""
    frame = tk.LabelFrame(
        parent,
        text="Bigface Result:",
        font=("Arial", 12, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    
    # Inner frame for stats
    inner_frame = tk.Frame(frame, bg=UI_COLORS['PRIMARY_BG'])
    inner_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Inspected
    _create_stat_row(inner_frame, "Inspected :", "0", row=0, app_var_name='bf_inspected_label', app=app)
    
    # Ok rollers
    _create_stat_row(inner_frame, "Ok rollers :", "0", row=1, app_var_name='bf_ok_label', app=app)
    
    # Not OK rollers
    _create_stat_row(inner_frame, "Not OK rollers:", "0", row=2, app_var_name='bf_not_ok_label', app=app)
    
    # Percentage
    _create_stat_row(inner_frame, "Percentage:", "0.0%", row=3, app_var_name='bf_percentage_label', app=app)


def _setup_od_result(app, parent):
    """Setup OD Result section"""
    frame = tk.LabelFrame(
        parent,
        text="OD Result:",
        font=("Arial", 12, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    # Inner frame for stats
    inner_frame = tk.Frame(frame, bg=UI_COLORS['PRIMARY_BG'])
    inner_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Inspected
    _create_stat_row(inner_frame, "Inspected :", "0", row=0, app_var_name='od_inspected_label', app=app)
    
    # Ok rollers
    _create_stat_row(inner_frame, "Ok rollers :", "0", row=1, app_var_name='od_ok_label', app=app)
    
    # Not OK rollers
    _create_stat_row(inner_frame, "Not OK rollers:", "0", row=2, app_var_name='od_not_ok_label', app=app)
    
    # Percentage
    _create_stat_row(inner_frame, "Percentage:", "0.0%", row=3, app_var_name='od_percentage_label', app=app)


def _setup_overall_result(app, parent):
    """Setup Overall Result section"""
    frame = tk.LabelFrame(
        parent,
        text="Overall Result:",
        font=("Arial", 12, "bold"),
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        bd=2,
        relief=tk.GROOVE
    )
    frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
    
    # Inner frame for stats
    inner_frame = tk.Frame(frame, bg=UI_COLORS['PRIMARY_BG'])
    inner_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Inspected
    _create_stat_row(inner_frame, "Inspected :", "0", row=0, app_var_name='overall_inspected_label', app=app)
    
    # Ok rollers
    _create_stat_row(inner_frame, "Ok rollers :", "0", row=1, app_var_name='overall_ok_label', app=app)
    
    # Not OK rollers
    _create_stat_row(inner_frame, "Not OK rollers:", "0", row=2, app_var_name='overall_not_ok_label', app=app)
    
    # Percentage
    _create_stat_row(inner_frame, "Percentage:", "0.0%", row=3, app_var_name='overall_percentage_label', app=app)


def _create_stat_row(parent, label_text, value_text, row, app_var_name, app):
    """
    Create a stat row with label and value (bold text for values)
    
    Args:
        parent: Parent frame
        label_text: Text for the label
        value_text: Initial value text
        row: Grid row number
        app_var_name: Name to store label in app instance
        app: Application instance
    """
    # Label
    label = tk.Label(
        parent,
        text=label_text,
        font=("Arial", 11, "bold"),  # Increased from 10 to 11 and made bold
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="w"
    )
    label.grid(row=row, column=0, sticky="w", pady=3, padx=(5, 10))
    
    # Value - even bolder
    value_label = tk.Label(
        parent,
        text=value_text,
        font=("Arial", 12, "bold"),  # Increased from 10 to 12
        fg="white",
        bg=UI_COLORS['PRIMARY_BG'],
        anchor="e"
    )
    value_label.grid(row=row, column=1, sticky="e", pady=3, padx=(10, 5))
    
    # Store reference in app
    setattr(app, app_var_name, value_label)
    
    # Configure column weights
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)


def update_bf_results(app):
    """Update Bigface results display"""
    inspected = app.bf_inspected
    ok_count = app.bf_good
    not_ok = app.bf_defective
    percentage = (not_ok / inspected * 100) if inspected > 0 else 0.0
    
    app.bf_inspected_label.config(text=str(inspected))
    app.bf_ok_label.config(text=str(ok_count))
    app.bf_not_ok_label.config(text=str(not_ok))
    app.bf_percentage_label.config(text=f"{percentage:.1f}%")


def update_od_results(app):
    """Update OD results display"""
    inspected = app.od_inspected
    ok_count = app.od_good
    not_ok = app.od_defective
    percentage = (not_ok / inspected * 100) if inspected > 0 else 0.0
    
    app.od_inspected_label.config(text=str(inspected))
    app.od_ok_label.config(text=str(ok_count))
    app.od_not_ok_label.config(text=str(not_ok))
    app.od_percentage_label.config(text=f"{percentage:.1f}%")


def update_overall_results(app):
    """Update Overall results display"""
    inspected = app.bf_inspected + app.od_inspected
    ok_count = app.bf_good + app.od_good
    not_ok = app.bf_defective + app.od_defective
    percentage = (not_ok / inspected * 100) if inspected > 0 else 0.0
    
    # Update overall labels if they exist
    if hasattr(app, 'overall_inspected_label'):
        app.overall_inspected_label.config(text=str(inspected))
    if hasattr(app, 'overall_ok_label'):
        app.overall_ok_label.config(text=str(ok_count))
    if hasattr(app, 'overall_not_ok_label'):
        app.overall_not_ok_label.config(text=str(not_ok))
    if hasattr(app, 'overall_percentage_label'):
        app.overall_percentage_label.config(text=f"{percentage:.1f}%")
