"""
Status Panel Component
Displays roller type, date/time, machine mode, disc status, confidence thresholds, and AI models
"""

import tkinter as tk
from datetime import datetime
from ..utils.styles import Colors, Fonts


class StatusPanel:
    """Status information panel at the top of inference tab."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the status panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.status_vars = {}
        
    def create(self):
        """Create the status panel UI."""
        # Main container - not expanding to full width
        container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        container.pack(anchor=tk.W, padx=5, pady=5)
        
        # Create status sections
        self._create_roller_type_section(container, 0)
        self._create_datetime_section(container, 1)
        self._create_machine_mode_section(container, 2)
        self._create_disc_status_section(container, 3)
        self._create_confidence_section(container, 4)
        self._create_ai_models_section(container, 5)
        
        # Configure grid weights - optimized width for all columns
        for i in range(5):
            container.grid_columnconfigure(i, weight=0, minsize=200)
        # AI Models column gets extra width
        container.grid_columnconfigure(5, weight=0, minsize=250)
        
        return container
    
    def _create_section_frame(self, parent, title, column):
        """Create a labeled frame for a status section."""
        frame = tk.LabelFrame(
            parent,
            text=title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.grid(row=0, column=column, padx=6, pady=2, sticky="nsew")
        return frame
    
    def _create_roller_type_section(self, parent, column):
        """Create roller type section."""
        frame = self._create_section_frame(parent, "Roller Type", column)
        
        self.status_vars['roller_type'] = tk.StringVar(value="")
        label = tk.Label(
            frame,
            textvariable=self.status_vars['roller_type'],
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            height=1
        )
        label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    
    def _create_datetime_section(self, parent, column):
        """Create date & time section."""
        frame = self._create_section_frame(parent, "Date & Time", column)
        
        self.status_vars['datetime'] = tk.StringVar(value=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
        label = tk.Label(
            frame,
            textvariable=self.status_vars['datetime'],
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            height=1
        )
        label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
        
        # Update time every second
        self._update_time()
    
    def _update_time(self):
        """Update the time display."""
        self.status_vars['datetime'].set(datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
        self.parent.after(1000, self._update_time)
    
    def _create_machine_mode_section(self, parent, column):
        """Create machine mode section."""
        frame = self._create_section_frame(parent, "Machine Mode", column)
        
        self.status_vars['machine_mode'] = tk.StringVar(value="Not Available")
        self.machine_mode_label = tk.Label(
            frame,
            textvariable=self.status_vars['machine_mode'],
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",  # Yellow (default Not Available)
            bg=Colors.PRIMARY_BG,
            height=1
        )
        self.machine_mode_label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    
    def _create_disc_status_section(self, parent, column):
        """Create disc status section."""
        frame = self._create_section_frame(parent, "Disc Status", column)
        
        self.status_vars['disc_status'] = tk.StringVar(value="Not Available")
        
        self.disc_label = tk.Label(
            frame,
            textvariable=self.status_vars['disc_status'],
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",  # Yellow (default Not Available)
            bg=Colors.PRIMARY_BG,
            height=1
        )
        self.disc_label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    
    def _create_confidence_section(self, parent, column):
        """Create confidence thresholds section."""
        frame = self._create_section_frame(parent, "Confidence Thresholds", column)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=8, pady=5, fill=tk.BOTH, expand=True)
        
        # BF confidence
        bf_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        bf_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            bf_frame,
            text="BF:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_vars['bf_conf'] = tk.StringVar(
            value=f"{int(self.app.bf_conf_threshold * 100)}.0%"
        )
        tk.Label(
            bf_frame,
            textvariable=self.status_vars['bf_conf'],
            font=Fonts.TEXT_BOLD,
            fg="#00bfff",  # Sky blue
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT)
        
        # OD confidence
        od_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        od_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            od_frame,
            text="OD:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_vars['od_conf'] = tk.StringVar(
            value=f"{int(self.app.od_conf_threshold * 100)}.0%"
        )
        tk.Label(
            od_frame,
            textvariable=self.status_vars['od_conf'],
            font=Fonts.TEXT_BOLD,
            fg="#00bfff",  # Sky blue
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT)
    
    def _create_ai_models_section(self, parent, column):
        """Create AI models section."""
        frame = self._create_section_frame(parent, "AI Models", column)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=8, pady=5, fill=tk.BOTH, expand=True)
        
        # BigFace Model
        bf_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        bf_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            bf_frame,
            text="BF Model:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_vars['bf_model'] = tk.StringVar(value="BF_sr.pt")
        tk.Label(
            bf_frame,
            textvariable=self.status_vars['bf_model'],
            font=Fonts.TEXT_BOLD,
            fg="#ff6b6b",  # Red
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT)
        
        # OD Model
        od_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        od_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            od_frame,
            text="OD Model:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_vars['od_model'] = tk.StringVar(value="OD_sr.pt")
        tk.Label(
            od_frame,
            textvariable=self.status_vars['od_model'],
            font=Fonts.TEXT_BOLD,
            fg="#ff6b6b",  # Red
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT)
    
    def update_disc_status(self, status, color=None):
        """Update disc status display."""
        self.status_vars['disc_status'].set(status)
        if color:
            self.disc_label.config(fg=color)
    
    def update_machine_mode(self, mode, color=None):
        """Update machine mode display."""
        self.status_vars['machine_mode'].set(mode)
        if color:
            self.machine_mode_label.config(fg=color)
    
    def update_confidence_thresholds(self):
        """Update confidence threshold displays."""
        self.status_vars['bf_conf'].set(f"{int(self.app.bf_conf_threshold * 100)}.0%")
        self.status_vars['od_conf'].set(f"{int(self.app.od_conf_threshold * 100)}.0%")
