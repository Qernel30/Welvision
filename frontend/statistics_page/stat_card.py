"""
Statistics Card Components
"""
import tkinter as tk


def create_stat_label(parent, label_text, var, row):
    """
    Create a statistics label with text and value
    
    Args:
        parent: Parent frame
        label_text: Label text to display
        var: StringVar for the value
        row: Grid row number
    """
    frame = tk.Frame(parent, bg="#0a2158")
    frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
    
    label = tk.Label(
        frame, 
        text=label_text, 
        font=("Arial", 10), 
        fg="white", 
        bg="#0a2158", 
        width=20, 
        anchor="w"
    )
    label.pack(side=tk.LEFT, padx=5)
    
    value_label = tk.Label(
        frame, 
        textvariable=var, 
        font=("Arial", 10, "bold"), 
        fg="white", 
        bg="#0a2158", 
        width=10
    )
    value_label.pack(side=tk.LEFT, padx=5)


def setup_total_stats(app, parent):
    """
    Setup total statistics section
    
    Args:
        app: Main application instance
        parent: Parent container frame
    """
    # Total statistics
    total_stats_frame = tk.LabelFrame(
        parent, 
        text="Total Statistics", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg="#0a2158", 
        bd=2
    )
    total_stats_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Total statistics variables
    app.total_inspected_var = tk.StringVar(value="0")
    app.total_defective_var = tk.StringVar(value="0")
    app.total_good_var = tk.StringVar(value="0")
    app.total_proportion_var = tk.StringVar(value="0%")
    
    total_stats_inner = tk.Frame(total_stats_frame, bg="#0a2158")
    total_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create grid for total stats
    total_grid = tk.Frame(total_stats_inner, bg="#0a2158")
    total_grid.pack(fill=tk.X, padx=10, pady=10)
    
    # Total stats labels
    create_stat_label(total_grid, "Total Rollers Inspected:", app.total_inspected_var, 0)
    create_stat_label(total_grid, "Total Defective Rollers:", app.total_defective_var, 1)
    create_stat_label(total_grid, "Total Good Rollers:", app.total_good_var, 2)
    create_stat_label(total_grid, "Total Defective Proportion:", app.total_proportion_var, 3)
