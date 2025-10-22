"""
System Status Component
Displays system and sensor status information
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class SystemStatus:
    """System status display component."""
    
    def __init__(self, parent, app_instance, system_check_tab):
        """
        Initialize system status.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
            system_check_tab: Reference to SystemCheckTab instance
        """
        self.parent = parent
        self.app = app_instance
        self.system_check_tab = system_check_tab
        
        # Status labels
        self.system_status_label = None
        self.system_message_label = None
        self.bf_sensor_label = None
        self.od_sensor_label = None
        
    def create(self):
        """Create the system status UI."""
        # Main frame
        status_frame = tk.LabelFrame(
            self.parent,
            text="System Status",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Inner container
        inner_frame = tk.Frame(status_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # Create two columns
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        
        # System Status (Left)
        self._create_system_status_section(inner_frame)
        
        # Sensor Status (Right)
        self._create_sensor_status_section(inner_frame)
    
    def _create_system_status_section(self, parent):
        """Create system status section."""
        # Container
        status_container = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        status_container.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Title
        title_label = tk.Label(
            status_container,
            text="System Status:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # Status value
        self.system_status_label = tk.Label(
            status_container,
            text="STOPPED",
            font=("Arial", 14, "bold"),
            fg="#FF0000",  # Red
            bg=Colors.PRIMARY_BG
        )
        self.system_status_label.pack(anchor="w", pady=(0, 5))
        
        # Warning icon and message
        warning_frame = tk.Frame(status_container, bg=Colors.PRIMARY_BG)
        warning_frame.pack(anchor="w")
        
        warning_icon = tk.Label(
            warning_frame,
            text="⚠",
            font=("Arial", 12),
            fg="#FFD700",  # Gold
            bg=Colors.PRIMARY_BG
        )
        warning_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.system_message_label = tk.Label(
            warning_frame,
            text="System stopped - No rollers will be processed",
            font=("Arial", 9),
            fg="#FFD700",  # Gold
            bg=Colors.PRIMARY_BG
        )
        self.system_message_label.pack(side=tk.LEFT)
    
    def _create_sensor_status_section(self, parent):
        """Create sensor status section."""
        # Container
        sensor_container = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        sensor_container.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Title
        title_label = tk.Label(
            sensor_container,
            text="Sensor Status:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # BigFace sensor
        bf_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        bf_frame.pack(anchor="w", pady=5)
        
        bf_label = tk.Label(
            bf_frame,
            text="BigFace:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=10,
            anchor="w"
        )
        bf_label.pack(side=tk.LEFT)
        
        self.bf_sensor_label = tk.Label(
            bf_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.bf_sensor_label.pack(side=tk.LEFT)
        
        # OD sensor
        od_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        od_frame.pack(anchor="w", pady=5)
        
        od_label = tk.Label(
            od_frame,
            text="OD:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=10,
            anchor="w"
        )
        od_label.pack(side=tk.LEFT)
        
        self.od_sensor_label = tk.Label(
            od_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.od_sensor_label.pack(side=tk.LEFT)
    
    def update_status(self, shared_data, system_running):
        """
        Update status displays from shared data.
        
        Args:
            shared_data: Dictionary containing system status data
            system_running: Boolean indicating if system check is running
        """
        # Update system status based on System Check state
        if system_running:
            self.system_status_label.config(text="RUNNING", fg="#00FF00")
            self.system_message_label.config(
                text="✓ System active - Processing rollers",
                fg="#00FF00"
            )
        else:
            self.system_status_label.config(text="STOPPED", fg="#FF0000")
            self.system_message_label.config(
                text="System stopped - No rollers will be processed",
                fg="#FFD700"
            )
        
        # Update sensor status
        bf_presence = shared_data.get('bigface_presence', False)
        od_presence = shared_data.get('od_presence', False)
        
        if bf_presence:
            self.bf_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.bf_sensor_label.config(text="OFF", fg="#888888")
        
        if od_presence:
            self.od_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.od_sensor_label.config(text="OFF", fg="#888888")
