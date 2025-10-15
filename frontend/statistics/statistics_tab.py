"""
Statistics Tab UI Component
"""

import tkinter as tk
import numpy as np
from ..utils.styles import Colors, Fonts


class StatisticsTab:
    """Statistics tab for displaying inspection metrics."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the statistics tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
    def setup(self):
        """Setup the statistics tab UI."""
        # Main statistics container
        stats_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            stats_container, 
            text="Inspection Statistics", 
            font=Fonts.LARGE,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 30))
        
        # Total statistics
        total_stats_frame = tk.LabelFrame(
            stats_container, 
            text="Total Statistics", 
            font=Fonts.HEADER,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=2
        )
        total_stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Total statistics variables
        self.app.total_inspected_var = tk.StringVar(value="0")
        self.app.total_defective_var = tk.StringVar(value="0")
        self.app.total_good_var = tk.StringVar(value="0")
        self.app.total_proportion_var = tk.StringVar(value="0%")
        
        total_stats_inner = tk.Frame(total_stats_frame, bg=Colors.PRIMARY_BG)
        total_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create grid for total stats
        total_grid = tk.Frame(total_stats_inner, bg=Colors.PRIMARY_BG)
        total_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Total stats labels
        self._create_stat_label(total_grid, "Total Rollers Inspected:", self.app.total_inspected_var, 0)
        self._create_stat_label(total_grid, "Total Defective Rollers:", self.app.total_defective_var, 1)
        self._create_stat_label(total_grid, "Total Good Rollers:", self.app.total_good_var, 2)
        self._create_stat_label(total_grid, "Total Defective Proportion:", self.app.total_proportion_var, 3)
        
        # Create two frames for OD and BF statistics
        stats_frame = tk.Frame(stats_container, bg=Colors.PRIMARY_BG)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # OD Statistics
        od_stats_frame = tk.LabelFrame(
            stats_frame, 
            text="OD Camera Statistics", 
            font=Fonts.HEADER,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=2
        )
        od_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # OD Stats labels
        self.app.od_inspected_var = tk.StringVar(value="0")
        self.app.od_defective_var = tk.StringVar(value="0")
        self.app.od_good_var = tk.StringVar(value="0")
        self.app.od_proportion_var = tk.StringVar(value="0%")
        
        od_stats_inner = tk.Frame(od_stats_frame, bg=Colors.PRIMARY_BG)
        od_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._create_stat_label(od_stats_inner, "Rollers Inspected:", self.app.od_inspected_var, 0)
        self._create_stat_label(od_stats_inner, "Defective Rollers:", self.app.od_defective_var, 1)
        self._create_stat_label(od_stats_inner, "Good Rollers:", self.app.od_good_var, 2)
        self._create_stat_label(od_stats_inner, "Defective Proportion:", self.app.od_proportion_var, 3)
        
        # OD Defect statistics
        od_defect_frame = tk.LabelFrame(
            od_stats_frame, 
            text="Defect Types", 
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=1
        )
        od_defect_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create grid for OD defect stats
        od_defect_grid = tk.Frame(od_defect_frame, bg=Colors.PRIMARY_BG)
        od_defect_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # OD Defect headers
        od_headers = ["Defect Type", "Count", "Percentage"]
        for col, header in enumerate(od_headers):
            label = tk.Label(
                od_defect_grid, 
                text=header, 
                font=Fonts.TEXT_BOLD,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=0, column=col, sticky="w")
        
        # OD Defect rows (mock data)
        for row, defect in enumerate(self.app.od_defect_thresholds.keys()):
            # Defect name
            label = tk.Label(
                od_defect_grid, 
                text=defect, 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5, 
                anchor="w"
            )
            label.grid(row=row+1, column=0, sticky="w")
            
            # Count (mock data)
            count = np.random.randint(0, 50)
            label = tk.Label(
                od_defect_grid, 
                text=str(count), 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=row+1, column=1)
            
            # Percentage (mock data)
            percentage = np.random.randint(1, 30)
            label = tk.Label(
                od_defect_grid, 
                text=f"{percentage}%", 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=row+1, column=2)
        
        # BIG FACE Statistics
        bf_stats_frame = tk.LabelFrame(
            stats_frame, 
            text="BIG FACE Camera Statistics", 
            font=Fonts.HEADER,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=2
        )
        bf_stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # BIG FACE Stats labels
        self.app.bf_inspected_var = tk.StringVar(value="0")
        self.app.bf_defective_var = tk.StringVar(value="0")
        self.app.bf_good_var = tk.StringVar(value="0")
        self.app.bf_proportion_var = tk.StringVar(value="0%")
        
        bf_stats_inner = tk.Frame(bf_stats_frame, bg=Colors.PRIMARY_BG)
        bf_stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._create_stat_label(bf_stats_inner, "Rollers Inspected:", self.app.bf_inspected_var, 0)
        self._create_stat_label(bf_stats_inner, "Defective Rollers:", self.app.bf_defective_var, 1)
        self._create_stat_label(bf_stats_inner, "Good Rollers:", self.app.bf_good_var, 2)
        self._create_stat_label(bf_stats_inner, "Defective Proportion:", self.app.bf_proportion_var, 3)
        
        # BIG FACE Defect statistics
        bf_defect_frame = tk.LabelFrame(
            bf_stats_frame, 
            text="Defect Types", 
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=1
        )
        bf_defect_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create grid for BF defect stats
        bf_defect_grid = tk.Frame(bf_defect_frame, bg=Colors.PRIMARY_BG)
        bf_defect_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # BF Defect headers
        bf_headers = ["Defect Type", "Count", "Percentage"]
        for col, header in enumerate(bf_headers):
            label = tk.Label(
                bf_defect_grid, 
                text=header, 
                font=Fonts.TEXT_BOLD,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=0, column=col, sticky="w")
        
        # BF Defect rows (mock data)
        for row, defect in enumerate(self.app.bf_defect_thresholds.keys()):
            # Defect name
            label = tk.Label(
                bf_defect_grid, 
                text=defect, 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5, 
                anchor="w"
            )
            label.grid(row=row+1, column=0, sticky="w")
            
            # Count (mock data)
            count = np.random.randint(0, 50)
            label = tk.Label(
                bf_defect_grid, 
                text=str(count), 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=row+1, column=1)
            
            # Percentage (mock data)
            percentage = np.random.randint(1, 30)
            label = tk.Label(
                bf_defect_grid, 
                text=f"{percentage}%", 
                font=Fonts.SMALL,
                fg=Colors.WHITE, 
                bg=Colors.PRIMARY_BG, 
                padx=10, 
                pady=5
            )
            label.grid(row=row+1, column=2)
        
        # Configure grid weights for stats frame
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
    
    def _create_stat_label(self, parent, label_text, var, row):
        """Create a statistics label widget."""
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        
        label = tk.Label(
            frame, 
            text=label_text, 
            font=Fonts.SMALL, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=20, 
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=5)
        
        value_label = tk.Label(
            frame, 
            textvariable=var, 
            font=Fonts.SMALL_BOLD, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=10
        )
        value_label.pack(side=tk.LEFT, padx=5)
