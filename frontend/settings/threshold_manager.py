"""
Threshold Manager Component for Settings Tab
Handles dynamic defect threshold sliders based on model classes
"""

import tkinter as tk
import tkinter.ttk as ttk
from ..utils.styles import Colors, Fonts


class ThresholdManager:
    """Manages defect threshold sliders dynamically based on model classes."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the threshold manager.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Storage for threshold widgets
        self.bf_threshold_sliders = {}  # {defect_name: (slider, label)}
        self.od_threshold_sliders = {}  # {defect_name: (slider, label)}
        self.bf_size_threshold_sliders = {}  # {defect_name: (slider, label)}
        self.od_size_threshold_sliders = {}  # {defect_name: (slider, label)}
        
        # Storage for threshold values
        self.bf_threshold_values = {}  # {defect_name: value}
        self.od_threshold_values = {}  # {defect_name: value}
        self.bf_size_threshold_values = {}  # {defect_name: value}
        self.od_size_threshold_values = {}  # {defect_name: value}
        
        # Model confidence sliders
        self.bf_conf_slider = None
        self.od_conf_slider = None
        self.bf_conf_label = None
        self.od_conf_label = None
        
        # Container frames
        self.conf_frame = None
        self.bf_defect_frame = None
        self.od_defect_frame = None
        self.defect_container = None  # Track the main defect container
    
    def create_model_confidence_section(self, parent_frame):
        """
        Create model confidence threshold sliders.
        
        Args:
            parent_frame: Parent frame to attach to
        """
        self.conf_frame = tk.LabelFrame(
            parent_frame, 
            text="Model Confidence",
            font=Fonts.LABEL_BOLD, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            bd=2
        )
        self.conf_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # BF Model Confidence
        bf_conf_frame = tk.Frame(self.conf_frame, bg=Colors.PRIMARY_BG, pady=10)
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
        
        # Set default if None or not exists
        if not hasattr(self.app, 'bf_conf_threshold') or self.app.bf_conf_threshold is None:
            self.app.bf_conf_threshold = 0.25
        self.app.bf_conf_slider_value = tk.DoubleVar(value=self.app.bf_conf_threshold * 100)
        
        self.bf_conf_slider = ttk.Scale(
            bf_conf_frame, 
            from_=1, 
            to=100, 
            orient=tk.HORIZONTAL,
            length=250, 
            variable=self.app.bf_conf_slider_value
        )
        self.bf_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Bind click event for direct positioning
        self.bf_conf_slider.bind("<Button-1>", lambda e: self._slider_click_handler(e, self.bf_conf_slider, self.app.bf_conf_slider_value))
        
        # Entry field for BF confidence
        self.bf_conf_entry = tk.Entry(
            bf_conf_frame,
            font=Fonts.TEXT,
            width=6,
            justify=tk.CENTER,
            bg=Colors.SECONDARY_BG,
            fg=Colors.WHITE,
            insertbackground=Colors.WHITE
        )
        self.bf_conf_entry.pack(side=tk.LEFT, padx=5)
        self.bf_conf_entry.insert(0, str(int(self.app.bf_conf_threshold * 100)))
        
        self.bf_conf_label = tk.Label(
            bf_conf_frame, 
            text="%",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=2
        )
        self.bf_conf_label.pack(side=tk.LEFT, padx=2)
        
        # Bind slider and entry updates for BF
        def update_bf_conf_from_slider(val):
            self.bf_conf_entry.delete(0, tk.END)
            self.bf_conf_entry.insert(0, str(int(float(val))))
        
        def update_bf_conf_from_entry(event=None):
            try:
                value = float(self.bf_conf_entry.get())
                # Clamp value between 1 and 100
                value = max(1, min(100, value))
                self.app.bf_conf_slider_value.set(value)
                self.bf_conf_entry.delete(0, tk.END)
                self.bf_conf_entry.insert(0, str(int(value)))
            except ValueError:
                # Invalid input - restore from slider
                self.bf_conf_entry.delete(0, tk.END)
                self.bf_conf_entry.insert(0, str(int(self.app.bf_conf_slider_value.get())))
        
        self.bf_conf_slider.config(command=update_bf_conf_from_slider)
        self.bf_conf_entry.bind("<Return>", update_bf_conf_from_entry)
        self.bf_conf_entry.bind("<FocusOut>", update_bf_conf_from_entry)
        
        # OD Model Confidence
        od_conf_frame = tk.Frame(self.conf_frame, bg=Colors.PRIMARY_BG, pady=10)
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
        
        # Set default if None or not exists
        if not hasattr(self.app, 'od_conf_threshold') or self.app.od_conf_threshold is None:
            self.app.od_conf_threshold = 0.25
        self.app.od_conf_slider_value = tk.DoubleVar(value=self.app.od_conf_threshold * 100)
        
        self.od_conf_slider = ttk.Scale(
            od_conf_frame, 
            from_=1, 
            to=100, 
            orient=tk.HORIZONTAL,
            length=250, 
            variable=self.app.od_conf_slider_value
        )
        self.od_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Bind click event for direct positioning
        self.od_conf_slider.bind("<Button-1>", lambda e: self._slider_click_handler(e, self.od_conf_slider, self.app.od_conf_slider_value))
        
        # Entry field for OD confidence
        self.od_conf_entry = tk.Entry(
            od_conf_frame,
            font=Fonts.TEXT,
            width=6,
            justify=tk.CENTER,
            bg=Colors.SECONDARY_BG,
            fg=Colors.WHITE,
            insertbackground=Colors.WHITE
        )
        self.od_conf_entry.pack(side=tk.LEFT, padx=5)
        self.od_conf_entry.insert(0, str(int(self.app.od_conf_threshold * 100)))
        
        self.od_conf_label = tk.Label(
            od_conf_frame, 
            text="%",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG, 
            width=2
        )
        self.od_conf_label.pack(side=tk.LEFT, padx=2)
        
        # Bind slider and entry updates for OD
        def update_od_conf_from_slider(val):
            self.od_conf_entry.delete(0, tk.END)
            self.od_conf_entry.insert(0, str(int(float(val))))
        
        def update_od_conf_from_entry(event=None):
            try:
                value = float(self.od_conf_entry.get())
                # Clamp value between 1 and 100
                value = max(1, min(100, value))
                self.app.od_conf_slider_value.set(value)
                self.od_conf_entry.delete(0, tk.END)
                self.od_conf_entry.insert(0, str(int(value)))
            except ValueError:
                # Invalid input - restore from slider
                self.od_conf_entry.delete(0, tk.END)
                self.od_conf_entry.insert(0, str(int(self.app.od_conf_slider_value.get())))
        
        self.od_conf_slider.config(command=update_od_conf_from_slider)
        self.od_conf_entry.bind("<Return>", update_od_conf_from_entry)
        self.od_conf_entry.bind("<FocusOut>", update_od_conf_from_entry)
    
    def create_defect_thresholds_section(self, parent_frame, bf_model, od_model):
        """
        Create dynamic defect threshold sliders based on model classes.
        Displays BF and OD thresholds side by side in 4 columns.
        
        Args:
            parent_frame: Parent frame to attach to
            bf_model: YOLO BF model instance
            od_model: YOLO OD model instance
        """
        # Destroy existing defect container if it exists
        if self.defect_container and self.defect_container.winfo_exists():
            self.defect_container.destroy()
        
        # Main container for defect thresholds
        self.defect_container = tk.LabelFrame(
            parent_frame,
            text="Thresholds",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.defect_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create 4-column layout
        columns_frame = tk.Frame(self.defect_container, bg=Colors.PRIMARY_BG)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights for equal column width
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_columnconfigure(2, weight=1)
        columns_frame.grid_columnconfigure(3, weight=1)
        
        # Column 1 - BF Defect Confidence
        self.bf_defect_frame = tk.LabelFrame(
            columns_frame,
            text="BF Defect Confidence",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.bf_defect_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Get BF model classes
        if bf_model and hasattr(bf_model, 'names'):
            bf_classes = bf_model.names
            for class_id, class_name in bf_classes.items():
                self._create_threshold_slider(
                    self.bf_defect_frame,
                    class_name,
                    'bf',
                    default_value=100
                )
        
        # Column 2 - OD Defect Confidence
        self.od_defect_frame = tk.LabelFrame(
            columns_frame,
            text="OD Defect Confidence",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.od_defect_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Get OD model classes
        if od_model and hasattr(od_model, 'names'):
            od_classes = od_model.names
            for class_id, class_name in od_classes.items():
                self._create_threshold_slider(
                    self.od_defect_frame,
                    class_name,
                    'od',
                    default_value=100
                )
        
        # Column 3 - BF Defect Size Threshold
        self.bf_size_frame = tk.LabelFrame(
            columns_frame,
            text="BF Defect Size Threshold",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.bf_size_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Get BF model classes for size thresholds
        if bf_model and hasattr(bf_model, 'names'):
            bf_classes = bf_model.names
            for class_id, class_name in bf_classes.items():
                self._create_size_threshold_slider(
                    self.bf_size_frame,
                    class_name,
                    'bf',
                    default_value=0
                )
        
        # Column 4 - OD Defect Size Threshold
        self.od_size_frame = tk.LabelFrame(
            columns_frame,
            text="OD Defect Size Threshold",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.od_size_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        
        # Get OD model classes for size thresholds
        if od_model and hasattr(od_model, 'names'):
            od_classes = od_model.names
            for class_id, class_name in od_classes.items():
                self._create_size_threshold_slider(
                    self.od_size_frame,
                    class_name,
                    'od',
                    default_value=0
                )
    
    def _create_threshold_slider(self, parent, defect_name, model_type, default_value=100):
        """
        Create a single threshold slider with entry field.
        
        Args:
            parent: Parent frame
            defect_name: Name of the defect
            model_type: 'bf' or 'od'
            default_value: Default threshold value (0-100)
        """
        slider_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG, pady=5)
        slider_frame.pack(fill=tk.X, padx=5)
        
        label = tk.Label(
            slider_frame,
            text=f"{defect_name}:",
            font=Fonts.SMALL,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=2)
        
        var = tk.DoubleVar(value=default_value)
        
        slider = ttk.Scale(
            slider_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            length=100,
            variable=var
        )
        slider.pack(side=tk.LEFT, padx=2)
        
        # Bind click event for direct positioning
        slider.bind("<Button-1>", lambda e: self._slider_click_handler(e, slider, var))
        
        # Entry field
        entry = tk.Entry(
            slider_frame,
            font=Fonts.SMALL,
            width=5,
            justify=tk.CENTER,
            bg=Colors.SECONDARY_BG,
            fg=Colors.WHITE,
            insertbackground=Colors.WHITE
        )
        entry.pack(side=tk.LEFT, padx=2)
        entry.insert(0, str(int(default_value)))
        
        value_label = tk.Label(
            slider_frame,
            text="%",
            font=Fonts.SMALL_BOLD,
            fg=Colors.INFO,
            bg=Colors.PRIMARY_BG,
            width=2,
            anchor="w"
        )
        value_label.pack(side=tk.LEFT, padx=1)
        
        # Update functions
        def update_from_slider(val):
            entry.delete(0, tk.END)
            entry.insert(0, str(int(float(val))))
            if model_type == 'bf':
                self.bf_threshold_values[defect_name] = int(float(val))
            else:
                self.od_threshold_values[defect_name] = int(float(val))
        
        def update_from_entry(event=None):
            try:
                value = float(entry.get())
                # Clamp value between 1 and 100
                value = max(1, min(100, value))
                var.set(value)
                entry.delete(0, tk.END)
                entry.insert(0, str(int(value)))
                if model_type == 'bf':
                    self.bf_threshold_values[defect_name] = int(value)
                else:
                    self.od_threshold_values[defect_name] = int(value)
            except ValueError:
                # Invalid input - restore from slider
                entry.delete(0, tk.END)
                entry.insert(0, str(int(var.get())))
        
        slider.config(command=update_from_slider)
        entry.bind("<Return>", update_from_entry)
        entry.bind("<FocusOut>", update_from_entry)
        
        # Trigger initial update to display the value
        update_from_slider(default_value)
        
        # Store references
        if model_type == 'bf':
            self.bf_threshold_sliders[defect_name] = (slider, entry, var)
            self.bf_threshold_values[defect_name] = default_value
        else:
            self.od_threshold_sliders[defect_name] = (slider, entry, var)
            self.od_threshold_values[defect_name] = default_value
    
    def _create_size_threshold_slider(self, parent, defect_name, model_type, default_value=0):
        """
        Create a single size threshold slider with entry field (measured in bounding box area in pixels).
        
        Args:
            parent: Parent frame
            defect_name: Name of the defect
            model_type: 'bf' or 'od'
            default_value: Default threshold value 
        """
        slider_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG, pady=5)
        slider_frame.pack(fill=tk.X, padx=5)
        
        label = tk.Label(
            slider_frame,
            text=f"{defect_name}:",
            font=Fonts.SMALL,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=2)
        
        var = tk.DoubleVar(value=default_value)
        
        slider = ttk.Scale(
            slider_frame,
            from_=0,
            to=30000,  # Maximum area in pixels
            orient=tk.HORIZONTAL,
            length=100,
            variable=var
        )
        slider.pack(side=tk.LEFT, padx=2)
        
        # Bind click event for direct positioning
        slider.bind("<Button-1>", lambda e: self._slider_click_handler(e, slider, var))
        
        # Entry field
        entry = tk.Entry(
            slider_frame,
            font=Fonts.SMALL,
            width=7,
            justify=tk.CENTER,
            bg=Colors.SECONDARY_BG,
            fg=Colors.WHITE,
            insertbackground=Colors.WHITE
        )
        entry.pack(side=tk.LEFT, padx=2)
        entry.insert(0, str(int(default_value)))
        
        value_label = tk.Label(
            slider_frame,
            text="px²",
            font=Fonts.SMALL_BOLD,
            fg=Colors.INFO,
            bg=Colors.PRIMARY_BG,
            width=3,
            anchor="w"
        )
        value_label.pack(side=tk.LEFT, padx=1)
        
        # Update functions
        def update_from_slider(val):
            entry.delete(0, tk.END)
            entry.insert(0, str(int(float(val))))
            if model_type == 'bf':
                self.bf_size_threshold_values[defect_name] = int(float(val))
            else:
                self.od_size_threshold_values[defect_name] = int(float(val))
        
        def update_from_entry(event=None):
            try:
                value = float(entry.get())
                # Clamp value between 0 and 30000
                value = max(0, min(30000, value))
                var.set(value)
                entry.delete(0, tk.END)
                entry.insert(0, str(int(value)))
                if model_type == 'bf':
                    self.bf_size_threshold_values[defect_name] = int(value)
                else:
                    self.od_size_threshold_values[defect_name] = int(value)
            except ValueError:
                # Invalid input - restore from slider
                entry.delete(0, tk.END)
                entry.insert(0, str(int(var.get())))
        
        slider.config(command=update_from_slider)
        entry.bind("<Return>", update_from_entry)
        entry.bind("<FocusOut>", update_from_entry)
        
        # Trigger initial update to display the value
        update_from_slider(default_value)
        
        # Store references
        if model_type == 'bf':
            self.bf_size_threshold_sliders[defect_name] = (slider, entry, var)
            self.bf_size_threshold_values[defect_name] = default_value
        else:
            self.od_size_threshold_sliders[defect_name] = (slider, entry, var)
            self.od_size_threshold_values[defect_name] = default_value
    
    def get_bf_thresholds(self):
        """Get current BF defect threshold values."""
        return self.bf_threshold_values.copy()
    
    def get_od_thresholds(self):
        """Get current OD defect threshold values."""
        return self.od_threshold_values.copy()
    
    def get_bf_size_thresholds(self):
        """Get current BF defect size threshold values."""
        return self.bf_size_threshold_values.copy()
    
    def get_od_size_thresholds(self):
        """Get current OD defect size threshold values."""
        return self.od_size_threshold_values.copy()
    
    def get_bf_model_confidence(self):
        """Get current BF model confidence from slider value."""
        return self.app.bf_conf_slider_value.get() / 100
    
    def get_od_model_confidence(self):
        """Get current OD model confidence from slider value."""
        return self.app.od_conf_slider_value.get() / 100
    
    def restore_thresholds(self, bf_thresholds, od_thresholds, bf_conf, od_conf, bf_size_thresholds=None, od_size_thresholds=None):
        """
        Restore threshold values.
        
        Args:
            bf_thresholds: Dictionary of BF defect thresholds
            od_thresholds: Dictionary of OD defect thresholds
            bf_conf: BF model confidence
            od_conf: OD model confidence
            bf_size_thresholds: Dictionary of BF size thresholds (optional)
            od_size_thresholds: Dictionary of OD size thresholds (optional)
        """
        # Restore BF defect thresholds
        for defect_name, value in bf_thresholds.items():
            if defect_name in self.bf_threshold_sliders:
                slider, entry, var = self.bf_threshold_sliders[defect_name]
                var.set(value)
                entry.delete(0, tk.END)
                entry.insert(0, str(int(value)))
                self.bf_threshold_values[defect_name] = value
        
        # Restore OD defect thresholds
        for defect_name, value in od_thresholds.items():
            if defect_name in self.od_threshold_sliders:
                slider, entry, var = self.od_threshold_sliders[defect_name]
                var.set(value)
                entry.delete(0, tk.END)
                entry.insert(0, str(int(value)))
                self.od_threshold_values[defect_name] = value
        
        # Restore BF size thresholds
        if bf_size_thresholds:
            for defect_name, value in bf_size_thresholds.items():
                if defect_name in self.bf_size_threshold_sliders:
                    slider, entry, var = self.bf_size_threshold_sliders[defect_name]
                    var.set(value)
                    entry.delete(0, tk.END)
                    entry.insert(0, str(int(value)))
                    self.bf_size_threshold_values[defect_name] = value
        
        # Restore OD size thresholds
        if od_size_thresholds:
            for defect_name, value in od_size_thresholds.items():
                if defect_name in self.od_size_threshold_sliders:
                    slider, entry, var = self.od_size_threshold_sliders[defect_name]
                    var.set(value)
                    entry.delete(0, tk.END)
                    entry.insert(0, str(int(value)))
                    self.od_size_threshold_values[defect_name] = value
        
        # Restore model confidence
        self.app.bf_conf_slider_value.set(bf_conf * 100)
        self.bf_conf_entry.delete(0, tk.END)
        self.bf_conf_entry.insert(0, str(int(bf_conf * 100)))
        self.app.bf_conf_threshold = bf_conf
        
        self.app.od_conf_slider_value.set(od_conf * 100)
        self.od_conf_entry.delete(0, tk.END)
        self.od_conf_entry.insert(0, str(int(od_conf * 100)))
        self.app.od_conf_threshold = od_conf
    
    def _slider_click_handler(self, event, slider, var):
        """
        Handle direct click on slider to jump to position.
        Makes sliders more user-friendly by allowing direct positioning.
        
        Args:
            event: Click event
            slider: The Scale widget
            var: The variable associated with the slider
        """
        try:
            # Get slider geometry
            slider_width = slider.winfo_width()
            click_x = event.x
            
            # Get slider range
            from_val = slider.cget('from')
            to_val = slider.cget('to')
            
            # Calculate value based on click position
            # Account for slider padding/border (approximately 10 pixels on each side)
            padding = 10
            effective_width = slider_width - (2 * padding)
            effective_x = max(0, min(click_x - padding, effective_width))
            
            # Calculate percentage and value
            percentage = effective_x / effective_width
            new_value = from_val + (percentage * (to_val - from_val))
            
            # Set the new value
            var.set(new_value)
            
            # Trigger the slider's command callback
            slider.event_generate("<<TrackbarChanged>>")
            
        except Exception as e:
            print(f"⚠️ Slider click handler error: {e}")
