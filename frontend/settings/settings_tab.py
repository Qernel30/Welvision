"""
Settings Tab UI Component
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from ..utils.styles import Colors, Fonts


class SettingsTab:
    """Settings tab for model configuration."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the settings tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
    def setup(self):
        """Setup the settings tab UI."""
        # Main container for settings
        settings_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings Title
        title_label = tk.Label(
            settings_container, 
            text="Model Confidence Settings",
            font=Fonts.SUBTITLE, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 20))
        
        # ===== MODEL CONFIDENCE SECTION =====
        conf_frame = tk.LabelFrame(
            settings_container, 
            text="Model Confidence Thresholds",
            font=Fonts.LABEL_BOLD, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=2
        )
        conf_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # OD Model Confidence Slider
        od_conf_frame = tk.Frame(conf_frame, bg=Colors.PRIMARY_BG, pady=10)
        od_conf_frame.pack(fill=tk.X, padx=10)
        
        od_conf_label = tk.Label(
            od_conf_frame, 
            text="OD Model Confidence", 
            font=Fonts.TEXT,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=20, 
            anchor="w"
        )
        od_conf_label.pack(side=tk.LEFT, padx=10)
        
        # Initialize with default value (25% = 0.25)
        if not hasattr(self.app, 'od_conf_threshold'):
            self.app.od_conf_threshold = 0.25
        self.app.od_conf_slider_value = tk.DoubleVar(value=self.app.od_conf_threshold * 100)
        
        od_conf_slider = ttk.Scale(
            od_conf_frame, 
            from_=1, 
            to=100, 
            orient=tk.HORIZONTAL,
            length=300, 
            variable=self.app.od_conf_slider_value
        )
        od_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.app.od_conf_value_label = tk.Label(
            od_conf_frame, 
            text=f"{int(self.app.od_conf_threshold * 100)}%",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=5
        )
        self.app.od_conf_value_label.pack(side=tk.LEFT, padx=10)
        
        # Update OD confidence value label when slider is moved
        def update_od_conf_label(val):
            self.app.od_conf_value_label.config(text=f"{int(float(val))}%")
            # Update the actual threshold value
            self.app.od_conf_threshold = float(val) / 100
            # If inspection is running, update the model in real-time
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
        
        od_conf_slider.config(command=update_od_conf_label)
        
        # BIG FACE Model Confidence Slider
        bf_conf_frame = tk.Frame(conf_frame, bg=Colors.PRIMARY_BG, pady=10)
        bf_conf_frame.pack(fill=tk.X, padx=10)
        
        bf_conf_label = tk.Label(
            bf_conf_frame, 
            text="Bigface Model Confidence", 
            font=Fonts.TEXT,
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=20, 
            anchor="w"
        )
        bf_conf_label.pack(side=tk.LEFT, padx=10)
        
        # Initialize with default value (25% = 0.25)
        if not hasattr(self.app, 'bf_conf_threshold'):
            self.app.bf_conf_threshold = 0.25
        self.app.bf_conf_slider_value = tk.DoubleVar(value=self.app.bf_conf_threshold * 100)
        
        bf_conf_slider = ttk.Scale(
            bf_conf_frame, 
            from_=1, 
            to=100, 
            orient=tk.HORIZONTAL,
            length=300, 
            variable=self.app.bf_conf_slider_value
        )
        bf_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.app.bf_conf_value_label = tk.Label(
            bf_conf_frame, 
            text=f"{int(self.app.bf_conf_threshold * 100)}%",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=5
        )
        self.app.bf_conf_value_label.pack(side=tk.LEFT, padx=10)
        
        # Update BF confidence value label when slider is moved
        def update_bf_conf_label(val):
            self.app.bf_conf_value_label.config(text=f"{int(float(val))}%")
            # Update the actual threshold value
            self.app.bf_conf_threshold = float(val) / 100
            # If inspection is running, update the model in real-time
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
        
        bf_conf_slider.config(command=update_bf_conf_label)
        
        # Save button for settings
        save_button = tk.Button(
            settings_container, 
            text="Save Settings", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS, 
            fg=Colors.WHITE, 
            command=self.save_settings
        )
        save_button.pack(pady=20)
    
    def save_settings(self):
        """Save the current settings."""
        # Save model confidence thresholds
        self.app.od_conf_threshold = float(self.app.od_conf_slider_value.get()) / 100
        self.app.bf_conf_threshold = float(self.app.bf_conf_slider_value.get()) / 100
        
        # Update the shared data dictionary with new confidence values
        if hasattr(self.app, 'shared_data'):
            self.app.shared_data['od_conf_threshold'] = self.app.od_conf_threshold
            self.app.shared_data['bf_conf_threshold'] = self.app.bf_conf_threshold
        
        # If inspection is running, update the model in real-time
        if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
            self.app.update_model_confidence()

        messagebox.showinfo("Settings Saved", "Model confidence settings have been saved successfully.")
        print(f"OD Confidence: {self.app.od_conf_threshold}, BF Confidence: {self.app.bf_conf_threshold}")
