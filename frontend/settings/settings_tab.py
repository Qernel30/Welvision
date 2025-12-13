"""
Settings Tab UI Component
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import snap7
from snap7.type import Areas
from snap7.util import set_bool
import threading
import numpy as np
import time
import torch
import cv2
from ultralytics import YOLO
from multiprocessing import Process
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig
from ..utils.process_manager import ThreadStopFlag
from ..utils.debug_logger import log_error, log_warning, log_info
from .preview_camera_feed import PreviewCameraManager
from .preview_control_panel import PreviewControlPanel
from .model_selector import ModelSelector
from .threshold_manager import ThresholdManager
from .threshold_database import ThresholdDatabase

# Import camera capture functions from backend
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend import capture_frames_bigface, capture_frames_od


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
        
        # Preview components
        self.preview_camera_manager = None
        self.preview_control_panel = None
        self.model_selector = None
        self.threshold_manager = None
        self.preview_active = False
        self.preview_od_thread = None
        self.preview_bf_thread = None
        self.preview_stop_flag = None  # Thread stop flag
        
        # Preview models (loaded when preview starts)
        self.preview_bf_model = None
        self.preview_od_model = None
        
        # Camera capture processes for preview
        self.preview_bf_camera_process = None
        self.preview_od_camera_process = None
        
        # Threshold snapshot (taken when preview starts)
        self.threshold_snapshot = None
        
        # Database handler
        self.threshold_db = ThresholdDatabase()
        
        # Scrollable canvas and frame
        self.canvas = None
        self.scrollable_frame = None
        self._mousewheel_bound = False
        
    def setup(self):
        """Setup the settings tab UI with scrolling support."""
        # Check if we're restoring with active preview
        restoring_active_preview = self.preview_active
        
        # Unbind previous mousewheel if it was bound
        if self._mousewheel_bound:
            try:
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        # Create main container
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(main_container, bg=Colors.PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.PRIMARY_BG)
        
        # Debounced scroll region update with longer delay for better performance
        self._scroll_update_id = None
        self._last_scroll_update = 0
        
        def _update_scroll_region(event=None):
            # Cancel pending update
            if self._scroll_update_id:
                self.canvas.after_cancel(self._scroll_update_id)
            
            # Throttle updates to max once per 200ms
            import time
            current_time = time.time()
            if current_time - self._last_scroll_update < 0.2:
                return
            
            # Schedule new update after 200ms
            def _do_update():
                try:
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    self._last_scroll_update = time.time()
                except:
                    pass
            
            self._scroll_update_id = self.canvas.after(200, _do_update)
        
        self.scrollable_frame.bind("<Configure>", _update_scroll_region)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize to update window width
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
        
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        # Enable mouse wheel scrolling - HEAVILY OPTIMIZED VERSION
        self._scroll_throttle_id = None
        
        def _on_mousewheel(event):
            # Check if canvas still exists before scrolling
            if not self.canvas or not self.canvas.winfo_exists():
                return
            
            # Throttle scroll events to prevent lag
            if self._scroll_throttle_id:
                return  # Ignore if already processing
            
            try:
                # Scroll with acceleration based on delta
                delta = -1 if event.delta > 0 else 1
                self.canvas.yview_scroll(delta * 2, "units")  # 2x speed for smoother feel
                
                # Reset throttle after 16ms (~60fps)
                self._scroll_throttle_id = self.canvas.after(16, lambda: setattr(self, '_scroll_throttle_id', None))
            except tk.TclError:
                # Canvas was destroyed, ignore
                pass
        
        def _bind_mousewheel(event=None):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self._mousewheel_bound = True
        
        def _unbind_mousewheel(event=None):
            if self._mousewheel_bound:
                try:
                    self.canvas.unbind_all("<MouseWheel>")
                    self._mousewheel_bound = False
                except:
                    pass
        
        # Bind only when mouse enters the canvas area
        self.canvas.bind("<Enter>", _bind_mousewheel)
        self.canvas.bind("<Leave>", _unbind_mousewheel)
        
        # Initial bind
        _bind_mousewheel()
        
        # Settings Title
        title_label = tk.Label(
            self.scrollable_frame, 
            text="Model Confidence Settings",
            font=Fonts.SUBTITLE, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 20), fill=tk.X)
        
        # ===== MODEL SELECTION SECTION =====
        self.model_selector = ModelSelector(self.scrollable_frame, self.app)
        self.model_selector.create()
        
        # ===== CAMERA PREVIEW SECTION =====
        preview_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Live Camera Preview",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Preview control panel
        self.preview_control_panel = PreviewControlPanel(preview_frame, self)
        self.preview_control_panel.setup()
        
        # If restoring active preview, update button states
        if restoring_active_preview:
            self.preview_control_panel.enable_stop()
        
        # Container for camera feeds
        self.preview_container = tk.Frame(preview_frame, bg=Colors.PRIMARY_BG)
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create fresh camera feed manager
        self.preview_camera_manager = PreviewCameraManager(self.preview_container)
        self.preview_camera_manager.setup()
        
        # If restoring with active preview, restart threads
        if restoring_active_preview:
            self._start_preview_threads()
        
        # ===== THRESHOLD MANAGER SECTION =====
        self.threshold_manager = ThresholdManager(self.scrollable_frame, self.app)
        
        # Create model confidence sliders
        self.threshold_manager.create_model_confidence_section(self.scrollable_frame)
        
        # Load selected models and create defect thresholds immediately
        self._load_models_and_create_thresholds()
        
        # Save button
        self.save_button = tk.Button(
            self.scrollable_frame, 
            text="Save Settings", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS, 
            fg=Colors.WHITE, 
            command=self.save_settings
        )
        self.save_button.pack(pady=20, padx=10)
    
    def _load_models_and_create_thresholds(self):
        """Load selected models and create defect threshold sliders."""
        try:
            # Get selected model paths from app (persistent selection)
            bf_model_path = self.app.selected_bf_model_path
            od_model_path = self.app.selected_od_model_path
            
            if bf_model_path and od_model_path:
                # Load models temporarily to get classes
                temp_bf_model = YOLO(bf_model_path)
                temp_od_model = YOLO(od_model_path)
                
                # Create defect threshold sliders
                self.threshold_manager.create_defect_thresholds_section(
                    self.scrollable_frame,
                    temp_bf_model,
                    temp_od_model
                )
                
                # Clean up temporary models
                del temp_bf_model
                del temp_od_model
                
                # Update canvas scroll region - deferred to avoid blocking
                def _update_scroll():
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    except:
                        pass
                self.canvas.after(100, _update_scroll)
                
                # Load latest thresholds from database for these models
                bf_model_name = self.app.selected_bf_model_name
                od_model_name = self.app.selected_od_model_name
                
                # Only load thresholds if models are actually selected (not "No Model Available")
                if bf_model_name and bf_model_name != "No Model Available" and od_model_name and od_model_name != "No Model Available":
                    self._load_latest_thresholds_from_db(bf_model_name, od_model_name)
                
            else:
                # Show message when no models available
                self._show_no_models_message()
                
        except Exception as e:
            print(f"⚠️ Could not load defect thresholds: {e}")
    
    def _show_no_models_message(self):
        """Show message when no models are available."""
        no_model_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Defect Thresholds",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        no_model_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        no_model_label = tk.Label(
            no_model_frame,
            text="⚠️ No models available\n\nPlease upload BF and OD models in Model Management tab\nto configure defect thresholds.",
            font=Fonts.TEXT,
            fg="#ffff00",  # Yellow
            bg=Colors.PRIMARY_BG,
            justify=tk.CENTER,
            pady=30
        )
        no_model_label.pack(fill=tk.BOTH, expand=True)
    
    def reload_defect_thresholds_for_selected_models(self):
        """Reload defect threshold sliders when models are changed."""
        try:
            # Clear existing slider references (the frames will be destroyed by threshold_manager)
            self.threshold_manager.bf_threshold_sliders = {}
            self.threshold_manager.od_threshold_sliders = {}
            self.threshold_manager.bf_size_threshold_sliders = {}
            self.threshold_manager.od_size_threshold_sliders = {}
            self.threshold_manager.bf_threshold_values = {}
            self.threshold_manager.od_threshold_values = {}
            self.threshold_manager.bf_size_threshold_values = {}
            self.threshold_manager.od_size_threshold_values = {}
            
            # Get selected model paths from app
            bf_model_path = self.app.selected_bf_model_path
            od_model_path = self.app.selected_od_model_path
            
            if bf_model_path and od_model_path:
                # Load models temporarily to get classes
                temp_bf_model = YOLO(bf_model_path)
                temp_od_model = YOLO(od_model_path)
                
                # Create defect threshold sliders (this will destroy old container automatically)
                self.threshold_manager.create_defect_thresholds_section(
                    self.scrollable_frame,
                    temp_bf_model,
                    temp_od_model
                )
                
                # Clean up temporary models
                del temp_bf_model
                del temp_od_model
                
                # Update canvas scroll region
                def _update_scroll():
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    except:
                        pass
                self.canvas.after(100, _update_scroll)
                
                # Load latest thresholds from database for these models
                bf_model_name = self.app.selected_bf_model_name
                od_model_name = self.app.selected_od_model_name
                
                # Only load thresholds if models are actually selected
                if bf_model_name and bf_model_name != "No Model Available" and od_model_name and od_model_name != "No Model Available":
                    self._load_latest_thresholds_from_db(bf_model_name, od_model_name)
                
            else:
                # Show "no models" message
                self._show_no_models_message()
                
        except Exception as e:
            print(f"⚠️ Error reloading defect thresholds: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_latest_thresholds_from_db(self, bf_model_name, od_model_name):
        """Load latest threshold values from database for the selected models. Use defaults if not found."""
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                port=AppConfig.DB_PORT,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            
            # Load latest BF thresholds for this model
            cursor.execute("""
                SELECT defect_threshold, size_threshold, model_threshold 
                FROM bf_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (bf_model_name,))
            bf_result = cursor.fetchone()
            
            if bf_result:
                defect_str, size_str, model_conf = bf_result
                # Parse defect thresholds: "rust:80%, dent:60%"
                bf_defects = self._parse_defect_string(defect_str)
                bf_sizes = self._parse_size_string(size_str) if size_str else {}
                
                # Apply BF thresholds
                for defect_name, value in bf_defects.items():
                    if defect_name in self.threshold_manager.bf_threshold_sliders:
                        slider, entry, var = self.threshold_manager.bf_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.bf_threshold_values[defect_name] = value
                
                # Apply BF size thresholds
                for defect_name, value in bf_sizes.items():
                    if defect_name in self.threshold_manager.bf_size_threshold_sliders:
                        slider, entry, var = self.threshold_manager.bf_size_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.bf_size_threshold_values[defect_name] = value
                
                # Apply BF model confidence
                self.app.bf_conf_threshold = float(model_conf)
                self.app.bf_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.bf_conf_entry.delete(0, tk.END)
                self.threshold_manager.bf_conf_entry.insert(0, str(int(float(model_conf) * 100)))
            # Load latest OD thresholds for this model
            cursor.execute("""
                SELECT defect_threshold, size_threshold, model_threshold 
                FROM od_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (od_model_name,))
            od_result = cursor.fetchone()
            
            if od_result:
                defect_str, size_str, model_conf = od_result
                # Parse defect thresholds
                od_defects = self._parse_defect_string(defect_str)
                od_sizes = self._parse_size_string(size_str) if size_str else {}
                
                # Apply OD thresholds
                for defect_name, value in od_defects.items():
                    if defect_name in self.threshold_manager.od_threshold_sliders:
                        slider, entry, var = self.threshold_manager.od_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.od_threshold_values[defect_name] = value
                
                # Apply OD size thresholds
                for defect_name, value in od_sizes.items():
                    if defect_name in self.threshold_manager.od_size_threshold_sliders:
                        slider, entry, var = self.threshold_manager.od_size_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.od_size_threshold_values[defect_name] = value
                
                # Apply OD model confidence
                self.app.od_conf_threshold = float(model_conf)
                self.app.od_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.od_conf_entry.delete(0, tk.END)
                self.threshold_manager.od_conf_entry.insert(0, str(int(float(model_conf) * 100)))
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"⚠️ Could not load thresholds from database: {e}")
    
    def _parse_defect_string(self, defect_str):
        """Parse defect threshold string format: 'rust:80%, dent:60%' to dict."""
        defects = {}
        try:
            pairs = defect_str.split(', ')
            for pair in pairs:
                if ':' in pair:
                    name, value = pair.split(':')
                    # Remove '%' and convert to int
                    value = int(value.replace('%', '').strip())
                    defects[name.strip()] = value
        except Exception as e:
            print(f"⚠️ Error parsing defect string: {e}")
        return defects
    
    def _parse_size_string(self, size_str):
        """Parse size threshold string format: 'rust:1000, dent:5000' to dict (area in pixels)."""
        sizes = {}
        try:
            pairs = size_str.split(', ')
            for pair in pairs:
                if ':' in pair:
                    name, value = pair.split(':')
                    # Convert to int (no % sign for sizes)
                    value = int(value.strip())
                    sizes[name.strip()] = value
        except Exception as e:
            print(f"⚠️ Error parsing size string: {e}")
        return sizes
    
    def save_settings(self):
        """Save the current settings to database and apply to inference."""
        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Save Settings",
            "Are you sure you want to save the current threshold settings?\n\n"
            "This will update the database and apply settings to the system.",
            icon='question'
        )
        
        if not confirm:
            log_info("settings", "User cancelled save settings")
            return
        
        try:
            log_info("settings", "Saving threshold settings")
            
            # Get current user
            employee_id = self.app.current_user if hasattr(self.app, 'current_user') else "unknown"
            
            # Get selected models
            bf_model_name = self.app.selected_bf_model_name if hasattr(self.app, 'selected_bf_model_name') else "Unknown"
            od_model_name = self.app.selected_od_model_name if hasattr(self.app, 'selected_od_model_name') else "Unknown"
            
            # Get threshold values
            bf_thresholds = self.threshold_manager.get_bf_thresholds()
            od_thresholds = self.threshold_manager.get_od_thresholds()
            bf_size_thresholds = self.threshold_manager.get_bf_size_thresholds()
            od_size_thresholds = self.threshold_manager.get_od_size_thresholds()
            bf_conf = self.threshold_manager.get_bf_model_confidence()
            od_conf = self.threshold_manager.get_od_model_confidence()
            
            # Apply model confidence to app (this is the only place where it updates)
            self.app.bf_conf_threshold = bf_conf
            self.app.od_conf_threshold = od_conf
            
            # Save to database
            bf_success = self.threshold_db.save_bf_thresholds(
                employee_id, 
                bf_thresholds,
                bf_size_thresholds,
                bf_conf, 
                bf_model_name
            )
            
            od_success = self.threshold_db.save_od_thresholds(
                employee_id, 
                od_thresholds,
                od_size_thresholds,
                od_conf, 
                od_model_name
            )
            
            # Update shared data if inspection is running
            if hasattr(self.app, 'shared_data'):
                self.app.shared_data['od_conf_threshold'] = od_conf
                self.app.shared_data['bf_conf_threshold'] = bf_conf
            
            # Update model confidence in inference page if running
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
            
            if bf_success and od_success:
                log_info("settings", f"Settings saved successfully by {employee_id}")
                messagebox.showinfo("Settings Saved", 
                                  "Threshold settings have been saved to database successfully.")
            else:
                log_warning("settings", "Partial save - some settings could not be saved")
                messagebox.showwarning("Partial Save", 
                                     "Some settings could not be saved to database.")
        
        except Exception as e:
            log_error("settings", "Failed to save settings", e, {
                "user": getattr(self.app, 'current_user', 'unknown'),
                "bf_model": getattr(self.app, 'selected_bf_model_name', 'Unknown'),
                "od_model": getattr(self.app, 'selected_od_model_name', 'Unknown')
            })
            print(f"❌ Error saving settings: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings:\n{str(e)}")
    
    def start_preview(self):
        """Start the camera preview with model inference."""
        if self.preview_active:
            log_warning("settings", "Attempted to start preview while already running")
            print("Preview already running!")
            return False
        
        log_info("settings", "Starting camera preview")
        
        # ===== VALIDATION CHECKS BEFORE PREVIEW =====
        # 1. Check if models are available
        models_ok, models_error = self._check_models_available()
        if not models_ok:
            log_warning("settings", f"Models check failed: {models_error}")
            messagebox.showerror("Models Check Failed", models_error)
            return False
        
        # 2. Check PLC connection
        plc_ok, plc_error = self._check_plc_connection()
        if not plc_ok:
            log_warning("settings", f"PLC check failed: {plc_error}")
            messagebox.showerror("PLC Check Failed", plc_error)
            return False
        
        # 3. Check cameras
        cameras_ok, cameras_error = self._check_cameras_connected()
        if not cameras_ok:
            log_warning("settings", f"Camera check failed: {cameras_error}")
            messagebox.showerror("Camera Check Failed", cameras_error)
            return False
        
        # All checks passed - proceed with preview
        # Get selected models
        selected_models = self.model_selector.get_selected_models()
        bf_model_path = selected_models['bf_model_path']
        od_model_path = selected_models['od_model_path']
        
        # Check if models are available
        if not bf_model_path or not od_model_path:
            log_warning("settings", "Models not available for preview")
            messagebox.showerror(
                "Models Not Available", 
                "⚠️ Cannot start preview\n\n"
                "Both BF and OD models are required.\n\n"
                "Please upload models in the Model Management tab first."
            )
            return False
        
        # Initialize stop flag
        self.preview_stop_flag = ThreadStopFlag()
        
        # Start camera capture processes if not already running
        if not hasattr(self.app, 'inspection_running') or not self.app.inspection_running:
            self._start_camera_capture_processes()
        
        # Load models
        try:
            log_info("settings", f"Loading models - BF: {bf_model_path}, OD: {od_model_path}")
            self.preview_bf_model = YOLO(bf_model_path)
            if torch.cuda.is_available():
                self.preview_bf_model.to("cuda")
            
            self.preview_od_model = YOLO(od_model_path)
            if torch.cuda.is_available():
                self.preview_od_model.to("cuda")
            
            log_info("settings", "Models loaded successfully")
                
        except Exception as e:
            log_error("settings", "Failed to load models for preview", e, {
                "bf_model_path": bf_model_path,
                "od_model_path": od_model_path
            })
            messagebox.showerror("Model Load Error", f"Failed to load models:\n{str(e)}")
            print(f"❌ Error loading models: {e}")
            return False
        
        # Take snapshot of current threshold values
        self._save_threshold_snapshot()
        
        # Turn on PLC lights
        plc_client = snap7.client.Client()
        plc_client.connect("172.17.8.17", 0, 1)        
        data = plc_client.read_area(Areas.DB, 86, 0, 2)
        set_bool(data, byte_index=1, bool_index=6, value=True)
        set_bool(data, byte_index=1, bool_index=7, value=True)
        plc_client.write_area(Areas.DB, 86, 0, data)
        plc_client.disconnect()

        self.preview_active = True
        
        # Block navigation to Inference and System Check pages
        self._block_navigation_buttons()
        
        # Block logout button
        self._block_logout_button()
        
        # Block model dropdowns and save button
        self._block_model_dropdowns()
        self._block_save_button()
        
        # Block app closing when preview is running
        if hasattr(self.app, 'protocol'):
            self.app.protocol("WM_DELETE_WINDOW", self._block_closing)
        
        # Start camera update threads
        self._start_preview_threads()
        
        # Start monitoring for system errors during preview
        self._monitor_preview_errors()
        
        return True  # Preview started successfully    
    
    def stop_preview(self):
        """Stop the camera preview with save/discard option and proper cleanup."""
        try:
            log_info("settings", "Attempting to stop camera preview")
            
            if not self.preview_active:
                log_warning("settings", "Stop preview called but preview is not running")
                print("Preview is not running.")
                return
            
            # Check if thresholds were changed
            if self._thresholds_changed():
                log_info("settings", "Thresholds were modified - prompting user to save changes")
                # Ask user: Save or Don't Save
                response = messagebox.askyesnocancel(
                    "Save Threshold Changes?",
                    "Threshold values have been modified.\n\n"
                    "Do you want to save these changes to the database?\n\n"
                    "Yes: Save changes\n"
                    "No: Discard changes (restore previous values)\n"
                    "Cancel: Continue preview"
                )
                
                if response is None:  # Cancel - continue preview
                    log_info("settings", "User cancelled stop preview - continuing preview")
                    return
                elif response:  # Yes - save changes
                    log_info("settings", "User chose to save threshold changes")
                    self.save_settings()
                else:  # No - restore previous values
                    log_info("settings", "User chose to discard threshold changes")
                    self._restore_threshold_snapshot()
            
            # Turn off PLC lights
            log_info("settings", "Turning off PLC lights")
            plc_client = snap7.client.Client()
            plc_client.connect("172.17.8.17", 0, 1)        
            data = plc_client.read_area(Areas.DB, 86, 0, 2)
            set_bool(data, byte_index=1, bool_index=6, value=False)
            set_bool(data, byte_index=1, bool_index=7, value=False)
            plc_client.write_area(Areas.DB, 86, 0, data)
            plc_client.disconnect()
            
            self.preview_active = False
            
            # Signal threads to stop
            if self.preview_stop_flag:
                self.preview_stop_flag.set()
            
            # Unblock navigation buttons
            self._unblock_navigation_buttons()
            
            # Unblock logout button
            self._unblock_logout_button()
            
            # Unblock model dropdowns and Save Settings button
            self._unblock_model_dropdowns()
            self._unblock_save_button()
            
            # Restore app closing
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            # Display black screens on both feeds
            self._display_black_screens()

            # Wait for threads to finish properly
            if hasattr(self, 'preview_od_thread') and self.preview_od_thread and self.preview_od_thread.is_alive():
                self.preview_od_thread.join(timeout=2.0)
            
            if hasattr(self, 'preview_bf_thread') and self.preview_bf_thread and self.preview_bf_thread.is_alive():
                self.preview_bf_thread.join(timeout=2.0)
            
            # Unload models to free memory
            if self.preview_bf_model is not None:
                del self.preview_bf_model
                self.preview_bf_model = None
            
            if self.preview_od_model is not None:
                del self.preview_od_model
                self.preview_od_model = None
            
            # Stop camera capture processes using process manager
            if self.preview_bf_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            if self.preview_od_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            self.app.process_manager.stop_all_preview()
            
            log_info("settings", "Camera preview stopped successfully")
            
        except Exception as e:
            log_error("settings", "Error stopping camera preview", e)
            messagebox.showerror("Error", f"Failed to stop preview:\n{str(e)}")
        
        # Clear process references
        self.preview_bf_camera_process = None
        self.preview_od_camera_process = None
        
        # Clean up camera feeds to release image memory
        if self.preview_camera_manager:
            for feed_id in ['bf', 'od']:
                feed = self.preview_camera_manager.get_feed(feed_id)
                if feed and hasattr(feed, 'cleanup'):
                    feed.cleanup()
        
        # Clean up GPU memory
        self.app.process_manager.cleanup_gpu_memory()
        
        # Force garbage collection to free memory
        import gc
        gc.collect()
        
        # Small delay to ensure cleanup is complete
        time.sleep(0.3)
        
    
    def _start_camera_capture_processes(self):
        """Start camera capture processes for preview mode."""
        try:
            # Start BF camera capture
            self.preview_bf_camera_process = Process(
                target=capture_frames_bigface,
                args=(self.app.shared_frame_bigface, self.app.frame_lock_bigface, self.app.frame_shape, self.app.shared_data),
                daemon=True
            )
            self.preview_bf_camera_process.start()
            
            # Register with process manager
            self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            # Start OD camera capture
            self.preview_od_camera_process = Process(
                target=capture_frames_od,
                args=(self.app.shared_frame_od, self.app.frame_lock_od, self.app.frame_shape, self.app.shared_data),
                daemon=True
            )
            self.preview_od_camera_process.start()
            
            # Register with process manager
            self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            # Give cameras time to start capturing
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error starting camera capture: {e}")
            messagebox.showerror("Camera Error", f"Failed to start camera capture:\n{str(e)}")
    
    def _start_preview_threads(self):
        """Start camera feed update threads for preview."""
        # Clear stop flag
        self.preview_stop_flag.clear()
        
        # Start OD camera thread
        self.preview_od_thread = threading.Thread(target=self._update_od_preview, name="Preview_OD_Thread")
        self.preview_od_thread.daemon = True
        self.preview_od_thread.start()
        
        # Register with process manager
        self.app.process_manager.register_preview_thread(self.preview_od_thread)
        
        # Start BF camera thread
        self.preview_bf_thread = threading.Thread(target=self._update_bf_preview, name="Preview_BF_Thread")
        self.preview_bf_thread.daemon = True
        self.preview_bf_thread.start()
        
        # Register with process manager
        self.app.process_manager.register_preview_thread(self.preview_bf_thread)
    
    def _filter_and_draw_detections(self, frame, results, model_conf_threshold, defect_thresholds, size_thresholds, model_type='od'):
        """
        Filter detections based on confidence and size thresholds, then draw annotations.
        Uses different colors for different classes and bold text for class names.
        
        Args:
            frame: Original frame
            results: YOLO prediction results
            model_conf_threshold: Model confidence threshold (0-1)
            defect_thresholds: Dictionary of defect-specific confidence thresholds (0-100)
            size_thresholds: Dictionary of defect-specific size thresholds (area in px²)
            model_type: 'od' or 'bf' to identify which defect thresholds to use
            
        Returns:
            Annotated frame with filtered detections
        """
        # Define a color palette for different classes (BGR format for OpenCV)
        color_palette = [
            (0, 255, 0),      # Green
            (255, 0, 0),      # Blue
            (0, 0, 255),      # Red
            (255, 255, 0),    # Cyan
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Yellow
            (128, 0, 128),    # Purple
            (0, 128, 255),    # Orange
            (128, 128, 0),    # Teal
            (255, 128, 0),    # Light Blue
            (0, 128, 128),    # Olive
            (128, 0, 255),    # Pink
        ]
        
        # Create a copy of the frame for drawing
        annotated_frame = frame.copy()
        
        # Get detection results
        boxes = results[0].boxes
        
        if boxes is None or len(boxes) == 0:
            return annotated_frame
        
        # Get class names from the model
        class_names = results[0].names
        
        # Process each detection
        for box in boxes:
            # Get detection info
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = class_names[cls_id]
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Calculate bounding box area (width * height)
            width = x2 - x1
            height = y2 - y1
            bbox_area = width * height
            
            # Get defect-specific confidence threshold (default to 0 if not found)
            defect_threshold = defect_thresholds.get(class_name, 0) / 100.0
            
            # Get defect-specific size threshold (default to 0 if not found)
            size_threshold = size_thresholds.get(class_name, 0)
            
            # Apply filters: Model Confidence + Defect Confidence + Size Threshold
            if conf >= model_conf_threshold and conf >= defect_threshold and bbox_area >= size_threshold:
                # Select color based on class ID
                color = color_palette[cls_id % len(color_palette)]
                
                # Draw bounding box with thicker line
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
                
                # Prepare label with class name and confidence
                label = f"{class_name} {conf:.2f}"
                
                # Get label size for background rectangle (using bold font thickness)
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                
                # Ensure label stays within frame bounds
                label_y1 = max(y1 - label_height - baseline - 10, 0)
                label_y2 = max(y1, label_height + baseline + 10)
                
                # Draw label background with same color as box
                cv2.rectangle(
                    annotated_frame,
                    (x1, label_y1),
                    (x1 + label_width + 10, label_y2),
                    color,
                    -1
                )
                
                # Draw label text in bold (thickness=2)
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1 + 5, label_y2 - baseline - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),  # White text
                    2,  # Bold thickness
                    cv2.LINE_AA  # Anti-aliased for smoother text
                )
        
        return annotated_frame
    
    def _update_od_preview(self):
        """Update OD camera preview feed with model inference."""
        od_feed = self.preview_camera_manager.get_feed('od') if self.preview_camera_manager else None
        
        # Keep thread running until stop flag is set or canvas is destroyed
        while od_feed and od_feed.canvas and od_feed.canvas.winfo_exists() and not self.preview_stop_flag.is_set():
            try:
                # Check if preview is active
                if self.preview_active:
                    # Preview is running - get frame and run inference
                    with self.app.frame_lock_od:
                        np_frame = np.frombuffer(
                            self.app.shared_frame_od.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
        
                    # Get real-time threshold values from sliders
                    current_od_conf = self.app.od_conf_slider_value.get() / 100.0
                    current_od_defect_thresholds = self.threshold_manager.get_od_thresholds()
                    current_od_size_thresholds = self.threshold_manager.get_od_size_thresholds()
                    
                    # Double-check model is still loaded before prediction
                    if self.preview_od_model is None:
                        # Model unloaded - show black screen
                        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                        od_feed.update_frame(black_frame)
                        time.sleep(0.03)
                        continue
                    
                    # Run inference with a low confidence to get all detections
                    results = self.preview_od_model.predict(
                        frame, 
                        device=0 if torch.cuda.is_available() else 'cpu',
                        conf=0.01,  # Low threshold to get all detections
                        verbose=False,
                        half=True if torch.cuda.is_available() else False
                    )
                    
                    # Filter and draw detections based on current slider values
                    # Applies: Model Confidence Filter + Defect Confidence Filter + Size Threshold Filter
                    annotated_frame = self._filter_and_draw_detections(
                        frame, 
                        results, 
                        current_od_conf, 
                        current_od_defect_thresholds,
                        current_od_size_thresholds,
                        model_type='od'
                    )
                    od_feed.update_frame(annotated_frame)
                else:
                    # Preview is stopped - show black screen
                    black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                    od_feed.update_frame(black_frame)
                
                    time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ OD preview thread error: {e}")
                import traceback
                traceback.print_exc()
                # Set system error flag
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break
        
    def _update_bf_preview(self):
        """Update Bigface camera preview feed with model inference."""
        bf_feed = self.preview_camera_manager.get_feed('bf') if self.preview_camera_manager else None
        
        # Keep thread running until stop flag is set or canvas is destroyed
        while bf_feed and bf_feed.canvas and bf_feed.canvas.winfo_exists() and not self.preview_stop_flag.is_set():
            try:
                # Check if preview is active
                if self.preview_active:
                    # Preview is running - get frame and run inference
                    with self.app.frame_lock_bigface:
                        np_frame = np.frombuffer(
                            self.app.shared_frame_bigface.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
                    
                    # Get real-time threshold values from sliders
                    current_bf_conf = self.app.bf_conf_slider_value.get() / 100.0
                    current_bf_defect_thresholds = self.threshold_manager.get_bf_thresholds()
                    current_bf_size_thresholds = self.threshold_manager.get_bf_size_thresholds()
                    
                    # Double-check model is still loaded before prediction
                    if self.preview_bf_model is None:
                        # Model unloaded - show black screen
                        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                        bf_feed.update_frame(black_frame)
                        time.sleep(0.03)
                        continue
                    
                    # Run inference with a low confidence to get all detections
                    results = self.preview_bf_model.predict(
                        frame, 
                        device=0 if torch.cuda.is_available() else 'cpu',
                        conf=0.01,  # Low threshold to get all detections
                        verbose=False,
                        half=True if torch.cuda.is_available() else False
                    )
                    
                    # Filter and draw detections based on current slider values
                    # Applies: Model Confidence Filter + Defect Confidence Filter + Size Threshold Filter
                    annotated_frame = self._filter_and_draw_detections(
                        frame, 
                        results, 
                        current_bf_conf, 
                        current_bf_defect_thresholds,
                        current_bf_size_thresholds,
                        model_type='bf'
                    )
                    
                    # Update the camera feed with annotated frame
                    bf_feed.update_frame(annotated_frame)
                else:
                    # Preview is stopped - show black screen
                    black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                    bf_feed.update_frame(black_frame)
                
                    time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ BF preview thread error: {e}")
                import traceback
                traceback.print_exc()
                # Set system error flag
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break

    def _display_black_screens(self):
        """Display black screens on both camera feeds when preview is stopped."""
        # Create a black frame
        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
        
        # Update both feeds with black screen
        od_feed = self.preview_camera_manager.get_feed('od')
        od_feed.update_frame(black_frame)
        
        bf_feed = self.preview_camera_manager.get_feed('bf')
        bf_feed.update_frame(black_frame)
    
    def _block_navigation_buttons(self):
        """Block Inference and System Check navigation buttons with red color."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Block Inference button
            if 'inference' in navbar.buttons:
                navbar.buttons['inference'].button.config(
                    state=tk.DISABLED,
                    bg=Colors.DANGER,  # Red color
                    disabledforeground=Colors.WHITE
                )
            
            # Block System Check button
            if 'system_check' in navbar.buttons:
                navbar.buttons['system_check'].button.config(
                    state=tk.DISABLED,
                    bg=Colors.DANGER,  # Red color
                    disabledforeground=Colors.WHITE
                )
            
    
    def _unblock_navigation_buttons(self):
        """Unblock Inference and System Check navigation buttons."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Unblock Inference button
            if 'inference' in navbar.buttons:
                nav_button = navbar.buttons['inference']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
            
            # Unblock System Check button
            if 'system_check' in navbar.buttons:
                nav_button = navbar.buttons['system_check']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
    
    def _block_logout_button(self):
        """Block the logout button during preview with grey color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.DISABLED,
                bg="#6c757d",  # Grey
                fg=Colors.WHITE  # White text
            )
    
    def _unblock_logout_button(self):
        """Unblock the logout button after preview with red color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,  # Red
                fg=Colors.WHITE  # White text
            )
    
    def _block_save_button(self):
        """Block the Save Settings button during preview with red color."""
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.config(
                state=tk.DISABLED,
                bg=Colors.DANGER,  # Red color when disabled during preview
                disabledforeground=Colors.WHITE
            )
    
    def _unblock_save_button(self):
        """Unblock the Save Settings button after preview."""
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.config(
                state=tk.NORMAL,
                bg=Colors.SUCCESS  # Green color when enabled
            )
    
    def _block_model_dropdowns(self):
        """Block model dropdown selection during preview."""
        if self.model_selector:
            if self.model_selector.bf_model_dropdown:
                self.model_selector.bf_model_dropdown.config(state=tk.DISABLED)
            if self.model_selector.od_model_dropdown:
                self.model_selector.od_model_dropdown.config(state=tk.DISABLED)
    
    def _unblock_model_dropdowns(self):
        """Unblock model dropdown selection after preview."""
        if self.model_selector:
            if self.model_selector.bf_model_dropdown:
                self.model_selector.bf_model_dropdown.config(state="readonly")
            if self.model_selector.od_model_dropdown:
                self.model_selector.od_model_dropdown.config(state="readonly")
    def _save_threshold_snapshot(self):
        """Save current threshold values to memory for potential restore."""
        if self.threshold_manager:
            self.threshold_snapshot = {
                'bf_thresholds': self.threshold_manager.get_bf_thresholds(),
                'od_thresholds': self.threshold_manager.get_od_thresholds(),
                'bf_size_thresholds': self.threshold_manager.get_bf_size_thresholds(),
                'od_size_thresholds': self.threshold_manager.get_od_size_thresholds(),
                'bf_conf': self.threshold_manager.get_bf_model_confidence(),
                'od_conf': self.threshold_manager.get_od_model_confidence()
            }
    
    def _restore_threshold_snapshot(self):
        """Restore threshold values from snapshot."""
        if self.threshold_snapshot and self.threshold_manager:
            self.threshold_manager.restore_thresholds(
                self.threshold_snapshot['bf_thresholds'],
                self.threshold_snapshot['od_thresholds'],
                self.threshold_snapshot['bf_conf'],
                self.threshold_snapshot['od_conf'],
                self.threshold_snapshot.get('bf_size_thresholds'),
                self.threshold_snapshot.get('od_size_thresholds')
            )
    
    def _thresholds_changed(self):
        """Check if threshold values have changed since snapshot."""
        if not self.threshold_snapshot or not self.threshold_manager:
            return False
        
        current_bf = self.threshold_manager.get_bf_thresholds()
        current_od = self.threshold_manager.get_od_thresholds()
        current_bf_size = self.threshold_manager.get_bf_size_thresholds()
        current_od_size = self.threshold_manager.get_od_size_thresholds()
        current_bf_conf = self.threshold_manager.get_bf_model_confidence()
        current_od_conf = self.threshold_manager.get_od_model_confidence()
        
        # Check if any values changed
        bf_changed = current_bf != self.threshold_snapshot['bf_thresholds']
        od_changed = current_od != self.threshold_snapshot['od_thresholds']
        bf_size_changed = current_bf_size != self.threshold_snapshot.get('bf_size_thresholds', {})
        od_size_changed = current_od_size != self.threshold_snapshot.get('od_size_thresholds', {})
        bf_conf_changed = abs(current_bf_conf - self.threshold_snapshot['bf_conf']) > 0.001
        od_conf_changed = abs(current_od_conf - self.threshold_snapshot['od_conf']) > 0.001
        
        return bf_changed or od_changed or bf_size_changed or od_size_changed or bf_conf_changed or od_conf_changed
    
    def _block_closing(self):
        """Block app closing when preview is running."""
        messagebox.showwarning(
            "Preview Running",
            "Camera preview is currently running!\n\n"
            "Please stop the preview before closing the application."
        )
    
    def _monitor_preview_errors(self):
        """Monitor for system errors during preview mode."""
        if not self.preview_active:
            return
        
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # Check if system error occurred
            if self.app.shared_data.get('system_error', False):
                # Reset the flag
                self.app.shared_data['system_error'] = False
                
                # Show error popup and force stop preview
                self._show_preview_error_popup()
                return  # Don't continue monitoring
        
        # Continue monitoring every 500ms if preview is still active
        if self.preview_active:
            try:
                self.parent.after(500, self._monitor_preview_errors)
            except:
                pass  # Tab might be destroyed
    
    def _show_preview_error_popup(self):
        """Show error popup and force stop preview."""
        from tkinter import messagebox
        
        # Force stop preview without save/discard dialog
        try:
            # Turn off PLC lights
            try:
                plc_client = snap7.client.Client()
                plc_client.connect("172.17.8.17", 0, 1)
                data = plc_client.read_area(Areas.DB, 86, 0, 2)
                set_bool(data, byte_index=1, bool_index=6, value=False)
                set_bool(data, byte_index=1, bool_index=7, value=False)
                plc_client.write_area(Areas.DB, 86, 0, data)
                plc_client.disconnect()
            except:
                pass
            
            self.preview_active = False
            
            # Signal threads to stop
            if self.preview_stop_flag:
                self.preview_stop_flag.set()
            
            # Unload models
            if self.preview_bf_model is not None:
                del self.preview_bf_model
                self.preview_bf_model = None
            
            if self.preview_od_model is not None:
                del self.preview_od_model
                self.preview_od_model = None
            
            # Stop camera processes
            if self.preview_bf_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            if self.preview_od_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            self.app.process_manager.stop_all_preview()
            
            # Clear references
            self.preview_bf_camera_process = None
            self.preview_od_camera_process = None
            
            # Unblock navigation and controls
            self._unblock_navigation_buttons()
            self._unblock_logout_button()
            self._unblock_model_dropdowns()
            self._unblock_save_button()
            
            # Update preview control panel
            if self.preview_control_panel:
                self.preview_control_panel.enable_start()
            
            # Restore normal app closing
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            # Display black screens
            self._display_black_screens()
            
            # Clean up GPU memory
            self.app.process_manager.cleanup_gpu_memory()
            
        except Exception as e:
            print(f"❌ Error during preview emergency stop: {e}")
        
        # Show error message
        messagebox.showerror(
            "Preview Error Detected",
            "⚠️ A critical error occurred during preview!\n\n"
            "The preview has been stopped automatically.\n\n"
            "Possible causes:\n"
            "• Camera disconnection\n"
            "• PLC communication error\n"
            "• GPU memory overflow\n"
            "• Model inference failure\n\n"
            "Recommended action:\n"
            "Please check camera and PLC connections.\n"
            "Restart the application if the issue persists.\n\n"
            "Click OK to continue using other features."
        )
    
    def _check_models_available(self):
        """
        Check if both BF and OD models are available.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        bf_model_path = getattr(self.app, 'selected_bf_model_path', None)
        od_model_path = getattr(self.app, 'selected_od_model_path', None)
        
        if not bf_model_path or not od_model_path:
            return False, "⚠️ Models Not Available\n\nBoth BF and OD models are required.\n\nPlease upload models in Model Management tab first."
        
        # Check if model files actually exist
        import os
        if not os.path.exists(bf_model_path):
            return False, f"⚠️ BF Model File Not Found\n\nPath: {bf_model_path}\n\nPlease upload the model again."
        
        if not os.path.exists(od_model_path):
            return False, f"⚠️ OD Model File Not Found\n\nPath: {od_model_path}\n\nPlease upload the model again."
        
        return True, ""
    
    def _check_plc_connection(self):
        """
        Check PLC connection.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            import snap7
            from snap7.type import Areas
            
            plc = snap7.client.Client()
            plc.connect(AppConfig.PLC_IP, AppConfig.PLC_RACK, AppConfig.PLC_SLOT)
            
            if plc.get_connected():
                plc.disconnect()
                return True, ""
            else:
                return False, f"⚠️ PLC Not Connected\n\nCannot connect to PLC at {AppConfig.PLC_IP}\n\nPlease check:\n• PLC is powered on\n• Network cable is connected\n• IP address is correct"
        
        except Exception as e:
            return False, f"⚠️ PLC Connection Failed\n\nError: {str(e)}\n\nPlease check PLC connection and network settings."
    
    def _check_cameras_connected(self):
        """
        Check if cameras are connected.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        import cv2
        cameras_connected = []
        
        # Check camera indices 0 and 1
        for idx in [0, 1]:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                cameras_connected.append(idx)
                cap.release()
        
        if len(cameras_connected) < 2:
            return False, f"⚠️ Cameras Not Connected\n\nRequired: 2 cameras\nDetected: {len(cameras_connected)} camera(s)\n\nPlease connect all cameras and try again."
        
        return True, ""
    
    def capture_bf_frame(self):
        """Capture current BF frame and save to disk."""
        if not self.preview_active:
            messagebox.showwarning("Preview Not Active", "Please start the preview first before capturing frames.")
            return
        
        try:
            from datetime import datetime
            import os
            
            # Get current frame from shared memory
            with self.app.frame_lock_bigface:
                np_frame = np.frombuffer(
                    self.app.shared_frame_bigface.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()
            
            # Create directory path
            username = os.getlogin()
            save_path = f"C:\\Users\\{username}\\Desktop\\Settings Frame\\BF"
            os.makedirs(save_path, exist_ok=True)
            
            # Create filename with current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove last 3 digits of microseconds
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(save_path, filename)
            
            # Save the frame
            cv2.imwrite(filepath, frame)
            
            # Show success message
            messagebox.showinfo(
                "Frame Captured",
                f"✅ BF frame captured successfully!\n\n"
                f"Saved to:\n{filepath}"
            )
            
        except Exception as e:
            print(f"❌ Error capturing BF frame: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Capture Error", f"Failed to capture BF frame:\n{str(e)}")
    
    def capture_od_frame(self):
        """Capture current OD frame and save to disk."""
        if not self.preview_active:
            messagebox.showwarning("Preview Not Active", "Please start the preview first before capturing frames.")
            return
        
        try:
            from datetime import datetime
            import os
            
            # Get current frame from shared memory
            with self.app.frame_lock_od:
                np_frame = np.frombuffer(
                    self.app.shared_frame_od.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()
            
            # Create directory path
            username = os.getlogin()
            save_path = f"C:\\Users\\{username}\\Desktop\\Settings Frame\\OD"
            os.makedirs(save_path, exist_ok=True)
            
            # Create filename with current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove last 3 digits of microseconds
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(save_path, filename)
            
            # Save the frame
            cv2.imwrite(filepath, frame)
            
            # Show success message
            messagebox.showinfo(
                "Frame Captured",
                f"✅ OD frame captured successfully!\n\n"
                f"Saved to:\n{filepath}"
            )
            
        except Exception as e:
            print(f"❌ Error capturing OD frame: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Capture Error", f"Failed to capture OD frame:\n{str(e)}")
    
    def cleanup(self):
        """Cleanup method called when settings tab is destroyed."""
        # Unbind mousewheel event immediately
        if self._mousewheel_bound:
            try:
                self.canvas.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        # Stop preview if active
        if self.preview_active:
            try:
                # Set stop flag
                if self.preview_stop_flag:
                    self.preview_stop_flag.set()
                
                # Turn off preview flag
                self.preview_active = False
                
                # Turn off PLC lights
                try:
                    plc_client = snap7.client.Client()
                    plc_client.connect("172.17.8.17", 0, 1)        
                    data = plc_client.read_area(Areas.DB, 86, 0, 2)
                    set_bool(data, byte_index=1, bool_index=6, value=False)
                    set_bool(data, byte_index=1, bool_index=7, value=False)
                    plc_client.write_area(Areas.DB, 86, 0, data)
                    plc_client.disconnect()
                except:
                    pass
                
                # Unload models
                if self.preview_bf_model is not None:
                    del self.preview_bf_model
                    self.preview_bf_model = None
                
                if self.preview_od_model is not None:
                    del self.preview_od_model
                    self.preview_od_model = None
                
                # Use process manager for cleanup
                if self.preview_bf_camera_process is not None:
                    self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
                
                if self.preview_od_camera_process is not None:
                    self.app.process_manager.register_preview_process(self.preview_od_camera_process)
                
                self.app.process_manager.stop_all_preview()
                
                # Clear references
                self.preview_bf_camera_process = None
                self.preview_od_camera_process = None
                
                # Clean GPU memory
                self.app.process_manager.cleanup_gpu_memory()
                
            except Exception as e:
                print(f"⚠️ Error during preview cleanup: {e}")            