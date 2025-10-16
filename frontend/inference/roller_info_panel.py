"""
Roller Info Panel Component
Displays detailed roller information on the right side
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class RollerInfoPanel:
    """Roller information display panel."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the roller info panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.info_vars = {}
        
    def create(self):
        """Create the roller info panel UI."""
        # Main container
        frame = tk.LabelFrame(
            self.parent,
            text="Roller Info:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create info rows
        self._create_info_row(inner_frame, "Outer Diameter :", "outer_diameter", "25 mm", 0)
        self._create_info_row(inner_frame, "Dimple Diameter:", "dimple_diameter", "20 mm", 1)
        self._create_info_row(inner_frame, "Small Diameter :", "small_diameter", "15 mm", 2)
        self._create_info_row(inner_frame, "Roller Length :", "roller_length", "40.25 mm", 3)
        self._create_info_row(inner_frame, "High Head (pixels):", "high_head", "0 pixels", 4)
        self._create_info_row(inner_frame, "Down Head (pixels):", "down_head", "0 pixels", 5)
        
        return frame
    
    def _create_info_row(self, parent, label_text, var_key, default_value, row):
        """Create a single info row."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=3)
        
        # Label
        label = tk.Label(
            row_frame,
            text=label_text,
            font=Fonts.TEXT_BOLD,  # Larger bold text
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Value
        self.info_vars[var_key] = tk.StringVar(value=default_value)
        value_label = tk.Label(
            row_frame,
            textvariable=self.info_vars[var_key],
            font=Fonts.TEXT_BOLD,  # Larger bold text
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="e"
        )
        value_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def update_info(self, **kwargs):
        """
        Update roller information.
        
        Args:
            **kwargs: Key-value pairs to update (e.g., outer_diameter="25 mm")
        """
        for key, value in kwargs.items():
            if key in self.info_vars:
                self.info_vars[key].set(value)
