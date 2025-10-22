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
                self.parent.unbind_all("<MouseWheel>")
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
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize to update window width
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
        
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        # Enable mouse wheel scrolling with safety check
        def _on_mousewheel(event):
            try:
                if self.canvas and self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas was destroyed, unbind the event
                try:
                    self.parent.unbind_all("<MouseWheel>")
                    self._mousewheel_bound = False
                except:
                    pass
        
        self.parent.bind_all("<MouseWheel>", _on_mousewheel)
        self._mousewheel_bound = True
        
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
            # Get selected model paths
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
                
                # Update canvas scroll region
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                # Load latest thresholds from database for these models
                bf_model_name = self.app.selected_bf_model_name
                od_model_name = self.app.selected_od_model_name
                self._load_latest_thresholds_from_db(bf_model_name, od_model_name)
                
            else:
                print("⚠️ No models selected yet, defect thresholds will load after model selection")
        except Exception as e:
            print(f"⚠️ Could not load defect thresholds: {e}")
    
    def _load_latest_thresholds_from_db(self, bf_model_name, od_model_name):
        """Load latest threshold values from database for the selected models."""
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='welvision_db'
            )
            
            cursor = connection.cursor()
            
            # Load latest BF thresholds for this model
            cursor.execute("""
                SELECT defect_threshold, model_threshold 
                FROM bf_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (bf_model_name,))
            bf_result = cursor.fetchone()
            
            if bf_result:
                defect_str, model_conf = bf_result
                # Parse defect thresholds: "rust:80%, dent:60%"
                bf_defects = self._parse_defect_string(defect_str)
                # Apply BF thresholds
                for defect_name, value in bf_defects.items():
                    if defect_name in self.threshold_manager.bf_threshold_sliders:
                        slider, label, var = self.threshold_manager.bf_threshold_sliders[defect_name]
                        var.set(value)
                        label.config(text=f"{int(value)}%")
                        self.threshold_manager.bf_threshold_values[defect_name] = value
                
                # Apply BF model confidence
                self.app.bf_conf_threshold = float(model_conf)
                self.app.bf_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.bf_conf_label.config(text=f"{int(float(model_conf) * 100)}%")
                
            
            # Load latest OD thresholds for this model
            cursor.execute("""
                SELECT defect_threshold, model_threshold 
                FROM od_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (od_model_name,))
            od_result = cursor.fetchone()
            
            if od_result:
                defect_str, model_conf = od_result
                # Parse defect thresholds
                od_defects = self._parse_defect_string(defect_str)
                # Apply OD thresholds
                for defect_name, value in od_defects.items():
                    if defect_name in self.threshold_manager.od_threshold_sliders:
                        slider, label, var = self.threshold_manager.od_threshold_sliders[defect_name]
                        var.set(value)
                        label.config(text=f"{int(value)}%")
                        self.threshold_manager.od_threshold_values[defect_name] = value
                
                # Apply OD model confidence
                self.app.od_conf_threshold = float(model_conf)
                self.app.od_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.od_conf_label.config(text=f"{int(float(model_conf) * 100)}%")
                
            
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
    
    def save_settings(self):
        """Save the current settings to database and apply to inference."""
        try:
            # Get current user
            employee_id = self.app.current_user if hasattr(self.app, 'current_user') else "unknown"
            
            # Get selected models
            bf_model_name = self.app.selected_bf_model_name if hasattr(self.app, 'selected_bf_model_name') else "Unknown"
            od_model_name = self.app.selected_od_model_name if hasattr(self.app, 'selected_od_model_name') else "Unknown"
            
            # Get threshold values
            bf_thresholds = self.threshold_manager.get_bf_thresholds()
            od_thresholds = self.threshold_manager.get_od_thresholds()
            bf_conf = self.threshold_manager.get_bf_model_confidence()
            od_conf = self.threshold_manager.get_od_model_confidence()
            
            # Apply model confidence to app (this is the only place where it updates)
            self.app.bf_conf_threshold = bf_conf
            self.app.od_conf_threshold = od_conf
            
            # Save to database
            bf_success = self.threshold_db.save_bf_thresholds(
                employee_id, 
                bf_thresholds, 
                bf_conf, 
                bf_model_name
            )
            
            od_success = self.threshold_db.save_od_thresholds(
                employee_id, 
                od_thresholds, 
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
                messagebox.showinfo("Settings Saved", 
                                  "Threshold settings have been saved to database successfully.")
            else:
                messagebox.showwarning("Partial Save", 
                                     "Some settings could not be saved to database.")
        
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings:\n{str(e)}")
    
    def start_preview(self):
        """Start the camera preview with model inference."""
        if self.preview_active:
            print("Preview already running!")
            return
        
        # Get selected models
        selected_models = self.model_selector.get_selected_models()
        bf_model_path = selected_models['bf_model_path']
        od_model_path = selected_models['od_model_path']
        
        if not bf_model_path or not od_model_path:
            messagebox.showerror("Error", "Please select both BF and OD models!")
            return
        
        # Start camera capture processes if not already running
        if not hasattr(self.app, 'inspection_running') or not self.app.inspection_running:
            self._start_camera_capture_processes()
        
        # Load models
        try:
            self.preview_bf_model = YOLO(bf_model_path)
            if torch.cuda.is_available():
                self.preview_bf_model.to("cuda")
            else:
                print("✅ BF model loaded on CPU")
            
            self.preview_od_model = YOLO(od_model_path)
            if torch.cuda.is_available():
                self.preview_od_model.to("cuda")
            else:
                print("✅ OD model loaded on CPU")
                
        except Exception as e:
            messagebox.showerror("Model Load Error", f"Failed to load models:\n{str(e)}")
            print(f"❌ Error loading models: {e}")
            return
        
        # Take snapshot of current threshold values
        self._save_threshold_snapshot()
        
        # Turn on PLC lights
        plc_client = snap7.client.Client()
        plc_client.connect("172.17.8.17", 0, 1)        
        data = plc_client.read_area(Areas.DB, 86, 0, 2)
        set_bool(data, byte_index=1, bool_index=7, value=True)
        plc_client.write_area(Areas.DB, 86, 0, data)
        plc_client.disconnect()

        self.preview_active = True
        
        # Block navigation to Inference and System Check pages
        self._block_navigation_buttons()
        
        # Block model dropdowns and save button
        self._block_model_dropdowns()
        self._block_save_button()
        
        # Block app closing when preview is running
        if hasattr(self.app, 'protocol'):
            self.app.protocol("WM_DELETE_WINDOW", self._block_closing)
        
        # Start camera update threads
        self._start_preview_threads()    
    
    def stop_preview(self):
        """Stop the camera preview with save/discard option."""
        if not self.preview_active:
            print("Preview is not running.")
            return
        
        # Check if thresholds were changed
        if self._thresholds_changed():
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
                return
            elif response:  # Yes - save changes
                self.save_settings()
                print("✅ Threshold changes saved")
            else:  # No - restore previous values
                self._restore_threshold_snapshot()
        
        # Turn off PLC lights
        plc_client = snap7.client.Client()
        plc_client.connect("172.17.8.17", 0, 1)        
        data = plc_client.read_area(Areas.DB, 86, 0, 2)
        set_bool(data, byte_index=1, bool_index=7, value=False)
        plc_client.write_area(Areas.DB, 86, 0, data)
        plc_client.disconnect()
        
        self.preview_active = False
        
        # Unblock navigation buttons
        self._unblock_navigation_buttons()
        
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
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Stop camera capture processes if we started them
        if self.preview_bf_camera_process is not None and self.preview_bf_camera_process.is_alive():
            self.preview_bf_camera_process.terminate()
            self.preview_bf_camera_process.join(timeout=1)
            self.preview_bf_camera_process = None
        
        if self.preview_od_camera_process is not None and self.preview_od_camera_process.is_alive():
            self.preview_od_camera_process.terminate()
            self.preview_od_camera_process.join(timeout=1)
            self.preview_od_camera_process = None
    
    def _start_camera_capture_processes(self):
        """Start camera capture processes for preview mode."""
        try:
            # Start BF camera capture
            self.preview_bf_camera_process = Process(
                target=capture_frames_bigface,
                args=(self.app.shared_frame_bigface, self.app.frame_lock_bigface, self.app.frame_shape),
                daemon=True
            )
            self.preview_bf_camera_process.start()
            
            # Start OD camera capture
            self.preview_od_camera_process = Process(
                target=capture_frames_od,
                args=(self.app.shared_frame_od, self.app.frame_lock_od, self.app.frame_shape),
                daemon=True
            )
            self.preview_od_camera_process.start()
            
            # Give cameras time to start capturing
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error starting camera capture: {e}")
            messagebox.showerror("Camera Error", f"Failed to start camera capture:\n{str(e)}")
    
    def _start_preview_threads(self):
        """Start camera feed update threads for preview."""
        # Start OD camera thread
        self.preview_od_thread = threading.Thread(target=self._update_od_preview)
        self.preview_od_thread.daemon = True
        self.preview_od_thread.start()
        
        # Start BF camera thread
        self.preview_bf_thread = threading.Thread(target=self._update_bf_preview)
        self.preview_bf_thread.daemon = True
        self.preview_bf_thread.start()
    
    def _filter_and_draw_detections(self, frame, results, model_conf_threshold, defect_thresholds, model_type='od'):
        """
        Filter detections based on thresholds and draw only those that pass.
        Uses different colors for different classes and bold text for class names.
        
        Args:
            frame: Original frame
            results: YOLO prediction results
            model_conf_threshold: Model confidence threshold (0-1)
            defect_thresholds: Dictionary of defect-specific thresholds (0-100)
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
            
            # Get defect-specific threshold (default to 0 if not found)
            defect_threshold = defect_thresholds.get(class_name, 0) / 100.0
            
            # Apply both model confidence and defect-specific thresholds
            if conf >= model_conf_threshold and conf >= defect_threshold:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
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
                
        while self.preview_active:
            try:
                # Check if feed still exists
                if od_feed is None or od_feed.canvas is None:
                    print("❌ OD feed or canvas is None")
                    break
                
                # Check if model is loaded
                if self.preview_od_model is None:
                    print("❌ OD model is None")
                    break
                
                # Get frame from shared memory
                with self.app.frame_lock_od:
                    np_frame = np.frombuffer(
                        self.app.shared_frame_od.get_obj(), 
                        dtype=np.uint8
                    ).reshape(self.app.frame_shape)
                    frame = np_frame.copy()
        
                # Get real-time threshold values from sliders
                current_od_conf = self.app.od_conf_slider_value.get() / 100.0
                current_od_defect_thresholds = self.threshold_manager.get_od_thresholds()
                
                # Double-check model is still loaded before prediction
                if self.preview_od_model is None:
                    break
                
                # Run inference with a low confidence to get all detections
                # We'll filter them manually based on our thresholds
                results = self.preview_od_model.predict(
                    frame, 
                    device=0 if torch.cuda.is_available() else 'cpu',
                    conf=0.01,  # Low threshold to get all detections
                    verbose=False,
                    half=True if torch.cuda.is_available() else False
                )
                
                # Filter and draw detections based on current slider values
                annotated_frame = self._filter_and_draw_detections(
                    frame, 
                    results, 
                    current_od_conf, 
                    current_od_defect_thresholds,
                    model_type='od'
                )
                
                # Update the camera feed with annotated frame
                od_feed.update_frame(annotated_frame)
                time.sleep(AppConfig.FRAME_UPDATE_RATE)
            except Exception as e:
                # Handle exceptions and exit gracefully
                print(f"❌ OD preview thread error: {e}")
                import traceback
                traceback.print_exc()
                break
        
    
    def _update_bf_preview(self):
        """Update Bigface camera preview feed with model inference."""
        bf_feed = self.preview_camera_manager.get_feed('bf') if self.preview_camera_manager else None
        
        
        while self.preview_active:
            try:
                # Check if feed still exists
                if bf_feed is None or bf_feed.canvas is None:
                    print("❌ BF feed or canvas is None")
                    break
                
                # Check if model is loaded
                if self.preview_bf_model is None:
                    print("❌ BF model is None")
                    break
                
                # Get frame from shared memory
                with self.app.frame_lock_bigface:
                    np_frame = np.frombuffer(
                        self.app.shared_frame_bigface.get_obj(), 
                        dtype=np.uint8
                    ).reshape(self.app.frame_shape)
                    frame = np_frame.copy()
                
                # Get real-time threshold values from sliders
                current_bf_conf = self.app.bf_conf_slider_value.get() / 100.0
                current_bf_defect_thresholds = self.threshold_manager.get_bf_thresholds()
                
                # Double-check model is still loaded before prediction
                if self.preview_bf_model is None:
                    break
                
                # Run inference with a low confidence to get all detections
                # We'll filter them manually based on our thresholds
                results = self.preview_bf_model.predict(
                    frame, 
                    device=0 if torch.cuda.is_available() else 'cpu',
                    conf=0.01,  # Low threshold to get all detections
                    verbose=False,
                    half=True if torch.cuda.is_available() else False
                )
                
                # Filter and draw detections based on current slider values
                annotated_frame = self._filter_and_draw_detections(
                    frame, 
                    results, 
                    current_bf_conf, 
                    current_bf_defect_thresholds,
                    model_type='bf'
                )
                
                # Update the camera feed with annotated frame
                bf_feed.update_frame(annotated_frame)
                time.sleep(AppConfig.FRAME_UPDATE_RATE)
            except Exception as e:
                # Handle exceptions and exit gracefully
                print(f"❌ BF preview thread error: {e}")
                import traceback
                traceback.print_exc()
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
                self.threshold_snapshot['od_conf']
            )
    
    def _thresholds_changed(self):
        """Check if threshold values have changed since snapshot."""
        if not self.threshold_snapshot or not self.threshold_manager:
            return False
        
        current_bf = self.threshold_manager.get_bf_thresholds()
        current_od = self.threshold_manager.get_od_thresholds()
        current_bf_conf = self.threshold_manager.get_bf_model_confidence()
        current_od_conf = self.threshold_manager.get_od_model_confidence()
        
        # Check if any values changed
        bf_changed = current_bf != self.threshold_snapshot['bf_thresholds']
        od_changed = current_od != self.threshold_snapshot['od_thresholds']
        bf_conf_changed = abs(current_bf_conf - self.threshold_snapshot['bf_conf']) > 0.001
        od_conf_changed = abs(current_od_conf - self.threshold_snapshot['od_conf']) > 0.001
        
        return bf_changed or od_changed or bf_conf_changed or od_conf_changed
    
    def _block_closing(self):
        """Block app closing when preview is running."""
        messagebox.showwarning(
            "Preview Running",
            "Camera preview is currently running!\n\n"
            "Please stop the preview before closing the application."
        )
    
    def cleanup(self):
        """Cleanup method called when settings tab is destroyed."""
        # Unbind mousewheel event
        if self._mousewheel_bound:
            try:
                self.parent.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        # Stop preview if active
        if self.preview_active:
            try:
                self.stop_preview()
            except:
                pass
            