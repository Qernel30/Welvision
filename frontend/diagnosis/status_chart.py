"""
Status Chart Component
Overall status bar chart (Inspected, Accepted, Rejected)
"""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..utils.styles import Colors, Fonts


class StatusChart:
    """Status chart displaying overall inspection statistics."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize the status chart.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to DiagnosisTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        self.canvas = None
        self.figure = None
        self.ax = None
        
    def create(self):
        """Create the status chart UI."""
        # Container frame
        container = tk.LabelFrame(
            self.parent,
            text="Status Chart",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create matplotlib figure with increased height
        self.figure = Figure(figsize=(7, 6), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize with empty chart
        self._draw_empty_chart()
    
    def _draw_empty_chart(self):
        """Draw empty chart with placeholder."""
        self.ax.clear()
        self.ax.set_title("Overall Status Chart", fontsize=14, fontweight='bold')
        self.ax.set_ylabel("Count", fontsize=12)
        
        # Empty bars
        categories = ['Overall Inspected', 'Overall Accepted', 'Overall Rejected']
        values = [0, 0, 0]
        
        bars = self.ax.bar(categories, values, color=['#4472C4', '#70AD47', '#FF0000'], width=0.6)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(val)}',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Rotate x-axis labels for better readability (fix matplotlib warning)
        self.ax.set_xticks(range(len(categories)))
        self.ax.set_xticklabels(categories, rotation=15, ha='right')
        
        # Set y-axis to start from 0 with minimum scale
        self.ax.set_ylim(bottom=0, top=1)
        
        # Add grid
        self.ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout
        self.figure.tight_layout()
        
        self.canvas.draw()
    
    def update_chart(self, data, report_type='Overall'):
        """
        Update chart with new data.
        
        Args:
            data: Dictionary with status counts based on report type
            report_type: 'BF', 'OD', or 'Overall'
        """
        self.ax.clear()
        
        # Set title and categories based on report type
        if report_type == 'BF':
            self.ax.set_title("BF Status Chart", fontsize=14, fontweight='bold')
            categories = ['BF Inspected', 'BF Accepted', 'BF Rejected']
            values = [
                data.get('BF Inspected', 0),
                data.get('BF Accepted', 0),
                data.get('BF Rejected', 0)
            ]
        elif report_type == 'OD':
            self.ax.set_title("OD Status Chart", fontsize=14, fontweight='bold')
            categories = ['OD Inspected', 'OD Accepted', 'OD Rejected']
            values = [
                data.get('OD Inspected', 0),
                data.get('OD Accepted', 0),
                data.get('OD Rejected', 0)
            ]
        else:  # Overall
            self.ax.set_title("Overall Status Chart", fontsize=14, fontweight='bold')
            categories = ['Overall Inspected', 'Overall Accepted', 'Overall Rejected']
            values = [
                data.get('Overall Inspected', 0),
                data.get('Overall Accepted', 0),
                data.get('Overall Rejected', 0)
            ]
        
        # Set ylabel
        self.ax.set_ylabel("Count", fontsize=12)
        
        # Create bars with specific colors
        bars = self.ax.bar(categories, values, color=['#4472C4', '#70AD47', '#FF0000'], width=0.6)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(val)}',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Rotate x-axis labels (fix matplotlib warning by setting ticks first)
        self.ax.set_xticks(range(len(categories)))
        self.ax.set_xticklabels(categories, rotation=15, ha='right')
        
        # Set y-axis limits (handle case when all values are 0)
        max_val = max(values) if values else 1
        if max_val == 0:
            max_val = 1  # Set minimum scale to avoid singular transformation
        self.ax.set_ylim(bottom=0, top=max_val * 1.15)
        
        # Add grid
        self.ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout
        self.figure.tight_layout()
        
        self.canvas.draw()
