"""
Processing Counters Component
Displays processing statistics for BigFace, OD, and Total
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class ProcessingCounters:
    """Processing counters display component."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize processing counters.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Counter labels
        self.bf_processed_label = None
        self.bf_accepted_label = None
        self.bf_rejected_label = None
        
        self.od_processed_label = None
        self.od_accepted_label = None
        self.od_rejected_label = None
        
        self.total_passed_label = None
        self.total_accepted_label = None
        self.total_rejected_label = None
    
    def create(self):
        """Create the processing counters UI."""
        # Main frame
        counters_frame = tk.LabelFrame(
            self.parent,
            text="Processing Counters",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        counters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Inner container
        inner_frame = tk.Frame(counters_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # Create three columns
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        inner_frame.grid_columnconfigure(2, weight=1)
        
        # BigFace Inspection
        self._create_bf_counters(inner_frame)
        
        # OD Inspection
        self._create_od_counters(inner_frame)
        
        # Total Processing
        self._create_total_counters(inner_frame)
    
    def _create_bf_counters(self, parent):
        """Create BigFace inspection counters."""
        # Frame
        bf_frame = tk.LabelFrame(
            parent,
            text="BigFace Inspection",
            font=("Arial", 9, "bold"),
            fg="#00FFFF",  # Cyan
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        bf_frame.grid(row=0, column=0, padx=3, pady=2, sticky="nsew")
        
        # Inner frame
        bf_inner = tk.Frame(bf_frame, bg=Colors.PRIMARY_BG)
        bf_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Processed
        self._create_counter_row(bf_inner, "Processed:", "0", "bf_processed")
        
        # Accepted
        self._create_counter_row(bf_inner, "Accepted:", "0", "bf_accepted")
        
        # Rejected
        self._create_counter_row(bf_inner, "Rejected:", "0", "bf_rejected")
    
    def _create_od_counters(self, parent):
        """Create OD inspection counters."""
        # Frame
        od_frame = tk.LabelFrame(
            parent,
            text="OD Inspection",
            font=("Arial", 9, "bold"),
            fg="#00FFFF",  # Cyan
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        od_frame.grid(row=0, column=1, padx=3, pady=2, sticky="nsew")
        
        # Inner frame
        od_inner = tk.Frame(od_frame, bg=Colors.PRIMARY_BG)
        od_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Processed
        self._create_counter_row(od_inner, "Processed:", "0", "od_processed")
        
        # Accepted
        self._create_counter_row(od_inner, "Accepted:", "0", "od_accepted")
        
        # Rejected
        self._create_counter_row(od_inner, "Rejected:", "0", "od_rejected")
    
    def _create_total_counters(self, parent):
        """Create total processing counters."""
        # Frame
        total_frame = tk.LabelFrame(
            parent,
            text="Total Processing",
            font=("Arial", 9, "bold"),
            fg="#FFD700",  # Gold
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        total_frame.grid(row=0, column=2, padx=3, pady=2, sticky="nsew")
        
        # Inner frame
        total_inner = tk.Frame(total_frame, bg=Colors.PRIMARY_BG)
        total_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Total Passed
        self._create_counter_row(total_inner, "Total Passed:", "0", "total_passed")
        
        # Total Accepted
        self._create_counter_row(total_inner, "Total Accepted:", "0", "total_accepted")
        
        # Total Rejected
        self._create_counter_row(total_inner, "Total Rejected:", "0", "total_rejected")
    
    def _create_counter_row(self, parent, label_text, value, counter_id):
        """Create a counter row with label and value."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=3)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="w"
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        value_label = tk.Label(
            row_frame,
            text=value,
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="e"
        )
        value_label.pack(side=tk.RIGHT)
        
        # Store reference
        setattr(self, f"{counter_id}_label", value_label)
    
    def update_counters(self, shared_data):
        """
        Update counter displays from shared data.
        
        Args:
            shared_data: Dictionary containing processing statistics
        """
        # BigFace counters - from System Check PLC controller
        bf_processed = shared_data.get('system_check_bf_processed', 0)
        bf_accepted = shared_data.get('system_check_bf_accepted', 0)
        bf_rejected = shared_data.get('system_check_bf_rejected', 0)
        
        self.bf_processed_label.config(text=str(bf_processed))
        self.bf_accepted_label.config(text=str(bf_accepted))
        self.bf_rejected_label.config(text=str(bf_rejected))
        
        # OD counters - from System Check PLC controller
        od_processed = shared_data.get('system_check_od_processed', 0)
        od_accepted = shared_data.get('system_check_od_accepted', 0)
        od_rejected = shared_data.get('system_check_od_rejected', 0)
        
        self.od_processed_label.config(text=str(bf_accepted))
        self.od_accepted_label.config(text=str(od_accepted))
        self.od_rejected_label.config(text=str(od_rejected))
        
        # Total counters - from System Check PLC controller
        # Total Passed = BF Processed
        # Total Accepted = OD Accepted
        # Total Rejected = BF Rejected + OD Rejected
        total_passed = shared_data.get('system_check_total_passed', 0)
        total_accepted = shared_data.get('system_check_total_accepted', 0)
        total_rejected = shared_data.get('system_check_total_rejected', 0)
        
        self.total_passed_label.config(text=str(bf_processed))
        self.total_accepted_label.config(text=str(od_accepted))
        self.total_rejected_label.config(text=str(total_rejected))
