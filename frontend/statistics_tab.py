"""
Statistics tab UI components
"""
import tkinter as tk
import numpy as np


def create_stat_label(parent, label_text, var, row):
    """Create a statistics label with text and value."""
    frame = tk.Frame(parent, bg="#0a2158")
    frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
    
    label = tk.Label(frame, text=label_text, font=("Arial", 10), fg="white", bg="#0a2158", width=20, anchor="w")
    label.pack(side=tk.LEFT, padx=5)
    
    value_label = tk.Label(frame, textvariable=var, font=("Arial", 10, "bold"), fg="white", bg="#0a2158", width=10)
    value_label.pack(side=tk.LEFT, padx=5)


def setup_statistics_tab(app, parent):
    """Setup the statistics tab with inspection metrics."""
    # Main statistics container
    stats_container = tk.Frame(parent, bg="#0a2158")
    stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(stats_container, text="Inspection Statistics", font=("Arial", 24, "bold"), 
                          fg="white", bg="#0a2158")
    title_label.pack(pady=(0, 30))
    
    # Total statistics
    total_stats_frame = tk.LabelFrame(stats_container, text="Total Statistics", font=("Arial", 16, "bold"), 
                                     fg="white", bg="#0a2158", bd=2)
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
    
    # Create two frames for OD and BF statistics
    stats_frame = tk.Frame(stats_container, bg="#0a2158")
    stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # OD Statistics
    od_stats_frame = tk.LabelFrame(stats_frame, text="OD Camera Statistics", font=("Arial", 16, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
    od_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    # OD Stats labels
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
    
    # OD Defect statistics
    od_defect_frame = tk.LabelFrame(od_stats_frame, text="Defect Types", font=("Arial", 14, "bold"), 
                                   fg="white", bg="#0a2158", bd=1)
    od_defect_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create grid for OD defect stats
    od_defect_grid = tk.Frame(od_defect_frame, bg="#0a2158")
    od_defect_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # OD Defect headers
    od_headers = ["Defect Type", "Count", "Percentage"]
    for col, header in enumerate(od_headers):
        label = tk.Label(od_defect_grid, text=header, font=("Arial", 12, "bold"), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=0, column=col, sticky="w")
    
    # OD Defect rows (mock data)
    for row, defect in enumerate(app.od_defect_thresholds.keys()):
        # Defect name
        label = tk.Label(od_defect_grid, text=defect, font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5, anchor="w")
        label.grid(row=row+1, column=0, sticky="w")
        
        # Count (mock data)
        count = np.random.randint(0, 50)
        label = tk.Label(od_defect_grid, text=str(count), font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=row+1, column=1)
        
        # Percentage (mock data)
        percentage = np.random.randint(1, 30)
        label = tk.Label(od_defect_grid, text=f"{percentage}%", font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=row+1, column=2)
    
    # BIG FACE Statistics
    bf_stats_frame = tk.LabelFrame(stats_frame, text="BIG FACE Camera Statistics", font=("Arial", 16, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
    bf_stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # BIG FACE Stats labels
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
    
    # BIG FACE Defect statistics
    bf_defect_frame = tk.LabelFrame(bf_stats_frame, text="Defect Types", font=("Arial", 14, "bold"), 
                                   fg="white", bg="#0a2158", bd=1)
    bf_defect_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create grid for BF defect stats
    bf_defect_grid = tk.Frame(bf_defect_frame, bg="#0a2158")
    bf_defect_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # BF Defect headers
    bf_headers = ["Defect Type", "Count", "Percentage"]
    for col, header in enumerate(bf_headers):
        label = tk.Label(bf_defect_grid, text=header, font=("Arial", 12, "bold"), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=0, column=col, sticky="w")
    
    # BF Defect rows (mock data)
    for row, defect in enumerate(app.bf_defect_thresholds.keys()):
        # Defect name
        label = tk.Label(bf_defect_grid, text=defect, font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5, anchor="w")
        label.grid(row=row+1, column=0, sticky="w")
        
        # Count (mock data)
        count = np.random.randint(0, 50)
        label = tk.Label(bf_defect_grid, text=str(count), font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=row+1, column=1)
        
        # Percentage (mock data)
        percentage = np.random.randint(1, 30)
        label = tk.Label(bf_defect_grid, text=f"{percentage}%", font=("Arial", 10), 
                        fg="white", bg="#0a2158", padx=10, pady=5)
        label.grid(row=row+1, column=2)
    
    # Configure grid weights for stats frame
    stats_frame.grid_columnconfigure(0, weight=1)
    stats_frame.grid_columnconfigure(1, weight=1)
    stats_frame.grid_rowconfigure(0, weight=1)
