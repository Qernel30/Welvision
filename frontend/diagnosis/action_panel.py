"""
Action Panel Component
Buttons for generating reports, saving charts, and exporting data
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class ActionPanel:
    """Action panel with report generation and export buttons."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize the action panel.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to DiagnosisTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
    def create(self):
        """Create the action panel UI."""
        # Container frame
        container = tk.LabelFrame(
            self.parent,
            text="Actions",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        container.pack(fill=tk.BOTH, expand=True)
        
        # Inner frame for padding (reduced padding)
        inner_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, padx=8, pady=5)
        
        # Generate Report button
        generate_btn = tk.Button(
            inner_frame,
            text="Generate Report",
            font=Fonts.SMALL_BOLD,
            bg="#00FF00",  # Green
            fg="#000000",
            command=self.tab.generate_report,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            height=1,
            pady=3
        )
        generate_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Save Chart button
        save_chart_btn = tk.Button(
            inner_frame,
            text="Save Chart",
            font=Fonts.SMALL_BOLD,
            bg="#FFFF00",  # Yellow
            fg="#000000",
            command=self.tab.save_chart,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            height=1,
            pady=3
        )
        save_chart_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Export to Excel button
        export_btn = tk.Button(
            inner_frame,
            text="Export to Excel",
            font=Fonts.SMALL_BOLD,
            bg="#FF0000",  # Red
            fg="#FFFFFF",
            command=self.tab.export_to_excel,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            height=1,
            pady=3
        )
        export_btn.pack(fill=tk.X, pady=(0, 0))
