"""
Main Application Class for WelVision System
"""

import tkinter as tk
import numpy as np
import time
from multiprocessing import Process, Array, Queue, Lock, Value, Manager
from ultralytics import YOLO
import snap7
from snap7.util import set_bool
from snap7.type import Areas

from .utils.styles import Colors, Fonts
from .utils.config import AppConfig
from .utils.helpers import center_window, create_header
from .login import LoginPage
from .navbar import NavBarManager
from .inference import InferenceTab
from .statistics import StatisticsTab
from .settings import SettingsTab
from .model_management import ModelManagementTab
from .diagnosis import DiagnosisTab
from backend import (
    plc_communication,
    capture_frames_bigface,
    process_rollers_bigface,
    handle_slot_control_bigface,
    capture_frames_od,
    process_frames_od,
    handle_slot_control_od,
)

import shutil
import gc
import torch
import os

def delete_all_pycache(start_path="."):
    count = 0
    for root, dirs, files in os.walk(start_path):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                count += 1

def clear_gpu_memory():
    """Clears GPU memory if applicable."""
    try:
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    except ImportError:
        print("⚠️ PyTorch not installed; skipping GPU memory clearance.")

class WelVisionApp(tk.Tk):
    """Main WelVision Application."""
    
    def __init__(self):
        """Initialize the WelVision application."""
        super().__init__()
        
        # Window configuration
        self.title(AppConfig.WINDOW_TITLE)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.configure(bg=Colors.PRIMARY_BG)
        self.iconbitmap(default="")  # Add your icon path if available
        
        # Center window on screen
        center_window(self, AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        
        # User session
        self.current_user = None
        self.current_role = None
        
        # Statistics variables
        self.od_inspected = 0
        self.od_defective = 0
        self.od_good = 0
        self.bf_inspected = 0
        self.bf_defective = 0
        self.bf_good = 0
        
        # Inspection status
        self.inspection_running = False
        self.camera_running = False
        
        # Defect thresholds
        self.od_defect_thresholds = AppConfig.OD_DEFECT_THRESHOLDS.copy()
        self.bf_defect_thresholds = AppConfig.BF_DEFECT_THRESHOLDS.copy()
        
        # Model confidence thresholds
        self.od_conf_threshold = AppConfig.DEFAULT_OD_CONFIDENCE
        self.bf_conf_threshold = AppConfig.DEFAULT_BF_CONFIDENCE
        
        # Selected model paths from Settings (will be loaded from database)
        self.selected_bf_model_path = None
        self.selected_bf_model_name = None
        self.selected_od_model_path = None
        self.selected_od_model_name = None
        
        # Load latest models from database on startup
        self._load_latest_models_from_db()
        
        # Page references
        self.login_page = None
        self.navbar_manager = None
        self.inference_tab = None
        self.statistics_tab = None
        self.settings_tab = None
        self.model_management_tab = None
        self.diagnosis_tab = None
        
        # Content frame reference
        self.content_frame = None
        self.current_tab_frame = None
        
        # Backend system variables (will be initialized later)
        self.plc_process = None
        self.processes = []
        self.shared_data = None
        self.manager = None
        
        # Footer
        self.footer_frame = None
        
        # Logout button reference
        self.logout_button = None
        
        # Show login page
        self.show_login_page()
    
    def _load_latest_models_from_db(self):
        """Load the latest BF and OD models and their thresholds from database on app startup."""
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='welvision_db'
            )
            
            cursor = connection.cursor()
            
            # Load latest BF model
            cursor.execute("SELECT model_name, model_path FROM bf_models ORDER BY upload_date DESC LIMIT 1")
            bf_result = cursor.fetchone()
            if bf_result:
                self.selected_bf_model_name = bf_result[0]
                self.selected_bf_model_path = bf_result[1]
                
                # Load latest BF threshold for this model
                cursor.execute("""
                    SELECT model_threshold 
                    FROM bf_threshold_history 
                    WHERE model_name = %s 
                    ORDER BY change_timestamp DESC 
                    LIMIT 1
                """, (self.selected_bf_model_name,))
                bf_threshold_result = cursor.fetchone()
                if bf_threshold_result:
                    self.bf_conf_threshold = float(bf_threshold_result[0])
                else:
                    print(f"⚠️ No threshold history for BF model '{self.selected_bf_model_name}', using default")
            else:
                # Fallback to default if no models in database
                self.selected_bf_model_path = AppConfig.MODEL_BF_SR
                self.selected_bf_model_name = "Default BF Model (No DB models)"
                print(f"⚠️ No BF models in database, using default")
            
            # Load latest OD model
            cursor.execute("SELECT model_name, model_path FROM od_models ORDER BY upload_date DESC LIMIT 1")
            od_result = cursor.fetchone()
            if od_result:
                self.selected_od_model_name = od_result[0]
                self.selected_od_model_path = od_result[1]
                
                # Load latest OD threshold for this model
                cursor.execute("""
                    SELECT model_threshold 
                    FROM od_threshold_history 
                    WHERE model_name = %s 
                    ORDER BY change_timestamp DESC 
                    LIMIT 1
                """, (self.selected_od_model_name,))
                od_threshold_result = cursor.fetchone()
                if od_threshold_result:
                    self.od_conf_threshold = float(od_threshold_result[0])
                else:
                    print(f"⚠️ No threshold history for OD model '{self.selected_od_model_name}', using default")
            else:
                # Fallback to default if no models in database
                self.selected_od_model_path = AppConfig.MODEL_OD_SR
                self.selected_od_model_name = "Default OD Model (No DB models)"
                print(f"⚠️ No OD models in database, using default")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"❌ Error loading latest models from database: {e}")
            # Fallback to default models on error
            self.selected_bf_model_path = AppConfig.MODEL_BF_SR
            self.selected_bf_model_name = "Default BF Model (DB Error)"
            self.selected_od_model_path = AppConfig.MODEL_OD_SR
            self.selected_od_model_name = "Default OD Model (DB Error)"
    
    def show_login_page(self):
        """Display the login page."""
        # Stop camera threads and inspection if running
        if hasattr(self, 'camera_running') and self.camera_running:
            self.camera_running = False
            time.sleep(0.2)  # Give threads time to stop
        
        if hasattr(self, 'inspection_running') and self.inspection_running:
            self.stop_inspection()
        
        # Show login page
        self.login_page = LoginPage(self, self.on_login_success)
        self.login_page.show()
        
        # Add global footer
        self._create_global_footer()
    
    def _create_global_footer(self):
        """Create footer with company name that appears on all pages."""
        # Remove existing footer if present
        if hasattr(self, 'footer_frame') and self.footer_frame:
            self.footer_frame.destroy()
        
        # Create footer frame
        self.footer_frame = tk.Frame(self, bg=Colors.PRIMARY_BG)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 5))
        
        # Create company label with larger font
        company_label = tk.Label(
            self.footer_frame,
            text="Developed and Maintained by \n© Welvision Pvt Limited",
            font=Fonts.TEXT_BOLD,  # Using TEXT_BOLD font for larger size
            fg="#FFFFFF",
            bg=Colors.PRIMARY_BG
        )
        company_label.pack(side=tk.RIGHT, padx=20)
    
    def on_login_success(self, email, role):
        """
        Handle successful login.
        
        Args:
            email: User email
            role: User role
        """
        self.current_user = email
        self.current_role = role
        self.show_main_interface()
    
    def show_main_interface(self):
        """Display the main application interface."""
        # Initialize backend system
        self.initialize_system()
        
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self, bg=Colors.PRIMARY_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header and store logout button reference
        header_frame, self.logout_button = create_header(
            main_frame, 
            AppConfig.WINDOW_TITLE,
            self.current_user, 
            self.current_role, 
            self.show_login_page
        )
        
        # Create navigation bar
        self.navbar_manager = NavBarManager(main_frame, self.on_nav_change)
        self.navbar_manager.create()
        
        # Create content frame for tabs
        self.content_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add global footer
        self._create_global_footer()
        
        # Set window close protocol handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show initial tab (Inference)
        self.show_tab("inference")
        
        # Start camera feeds
        self.start_camera_feeds()
        
        # Start updating statistics
        self.update_statistics()
    
    def initialize_system(self):
        """Initialize the backend inspection system."""
        
        
        # Frame shape
        self.frame_shape = (
            AppConfig.CAMERA_FRAME_HEIGHT, 
            AppConfig.CAMERA_FRAME_WIDTH, 
            3
        )
        
        # Shared memory and process communication
        self.manager = Manager()
        self.shared_data = self.manager.dict()
        self.shared_data['bigface'] = False
        self.shared_data['od'] = False
        self.shared_data['bigface_presence'] = False
        self.shared_data['od_presence'] = False
        self.shared_data['head_classification'] = False
        self.shared_data['od_conf_threshold'] = self.od_conf_threshold
        self.shared_data['bf_conf_threshold'] = self.bf_conf_threshold
        self.shared_data["bf_ready"] = False
        self.shared_data["od_ready"] = False
        self.shared_data["overall_system_ready"] = False
        self.shared_data["system_mode"] = False 
        self.shared_data["system_ready"] = False 
        self.shared_data["disc_status"] = False 
        self.shared_data["allow_all"] = False 
        
        # BF Defect Statistics
        self.shared_data["bf_inspected"] = 0
        self.shared_data["bf_ok_rollers"] = 0
        self.shared_data["bf_not_ok_rollers"] = 0
        self.shared_data["rust"] = 0
        self.shared_data["dent"] = 0
        self.shared_data["damage"] = 0
        self.shared_data["high_head"] = 0
        self.shared_data["down_head"] = 0
        self.shared_data["others"] = 0
        
        # OD Defect Statistics
        self.shared_data["od_inspected"] = 0
        self.shared_data["od_ok_rollers"] = 0
        self.shared_data["od_not_ok_rollers"] = 0
        self.shared_data["od_rust"] = 0
        self.shared_data["od_dent"] = 0
        self.shared_data["od_damage"] = 0
        self.shared_data["od_damage_on_end"] = 0
        self.shared_data["od_spherical_mark"] = 0
        self.shared_data["od_others"] = 0
        
        # Track inspection session start time
        self.inspection_start_time = None
        
        self.command_queue = Queue()
        
        self.proximity_count_od = Value('i', 0)
        self.proximity_count_bigface = Value('i', 0)
        
        self.roller_data_od = self.manager.dict()
        self.roller_queue_od = Queue()
        self.roller_queue_bigface = Queue()
        self.roller_updation_dict = self.manager.dict()
        
        # Shared frames
        self.shared_frame_bigface = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        self.shared_frame_od = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        
        self.frame_lock_bigface = Lock()
        self.frame_lock_od = Lock()
        self.queue_lock = Lock()
        
        # Shared memory for storing annotated frames
        self.shared_annotated_bigface = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        self.shared_annotated_od = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        
        self.annotated_frame_lock_bigface = Lock()
        self.annotated_frame_lock_od = Lock()
        
        # PLC configuration
        self.PLC_IP = AppConfig.PLC_IP
        self.RACK = AppConfig.PLC_RACK
        self.SLOT = AppConfig.PLC_SLOT
        self.DB_NUMBER = AppConfig.PLC_DB_NUMBER
        
    
    def create_processes(self):
        """Create process instances for backend operations."""
        self.plc_process = Process(
            target=plc_communication,
            args=(self.PLC_IP, self.RACK, self.SLOT, self.DB_NUMBER, self.shared_data, self.command_queue),
            daemon=True
        )
        
        self.processes = [
            Process(
                target=capture_frames_bigface, 
                args=(self.shared_frame_bigface, self.frame_lock_bigface, self.frame_shape), 
                daemon=True
            ),
            Process(
                target=handle_slot_control_bigface, 
                args=(self.roller_queue_bigface, self.shared_data, self.command_queue), 
                daemon=True
            ),
            Process(
                target=process_rollers_bigface, 
                args=(
                    self.shared_frame_bigface, 
                    self.frame_lock_bigface, 
                    self.roller_queue_bigface, 
                    self.selected_bf_model_path, 
                    self.proximity_count_bigface, 
                    self.roller_updation_dict, 
                    self.queue_lock, 
                    self.shared_data, 
                    self.frame_shape, 
                    self.shared_annotated_bigface, 
                    self.annotated_frame_lock_bigface
                ), 
                daemon=True
            ),
            Process(
                target=process_frames_od, 
                args=(
                    self.shared_frame_od, 
                    self.frame_lock_od, 
                    self.roller_queue_od,
                    self.selected_od_model_path, 
                    self.queue_lock, 
                    self.shared_data, 
                    self.frame_shape, 
                    self.roller_updation_dict, 
                    self.shared_annotated_od, 
                    self.annotated_frame_lock_od
                ), 
                daemon=True
            ),
            Process(
                target=capture_frames_od, 
                args=(self.shared_frame_od, self.frame_lock_od, self.frame_shape), 
                daemon=True
            ),
            Process(
                target=handle_slot_control_od, 
                args=(self.roller_queue_od, self.shared_data, self.command_queue), 
                daemon=True
            )
        ]
    
    def start_inspection(self):
        """Start the inspection process."""
        if self.inspection_running:
            print("Inspection is already running!")
            return
        
        self.inspection_running = True
        if self.inference_tab and self.inference_tab.control_panel:
            self.inference_tab.control_panel.enable_stop()
        
        # Record start time
        from datetime import datetime
        self.inspection_start_time = datetime.now().time()
        
        # Recreate processes before starting
        self.create_processes()
        
        # Start PLC process
        if self.plc_process is not None:
            self.plc_process.start()
        
        # Start subprocesses
        for process in self.processes:
            process.start()
        
    
    def stop_inspection(self):
        """Stop the inspection process."""
        if not self.inspection_running:
            print("Inspection is not running.")
            return
        
        plc_client = snap7.client.Client() 
        try:
            plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
            
            data = plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            set_bool(data, byte_index=1, bool_index=6, value=False)
            set_bool(data, byte_index=1, bool_index=7, value=False)
            plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
            plc_client.disconnect()
        except Exception as e:
            print(f"❌ PLC Communication: Failed to connect to PLC. Error: {e}")
        
        self.inspection_running = False
        if self.inference_tab and self.inference_tab.control_panel:
            self.inference_tab.control_panel.enable_start()
        
        # Stop the PLC process if it's running
        if self.plc_process and self.plc_process.is_alive():
            self.plc_process.terminate()
            self.plc_process.join()
            self.plc_process = None
        
        # Stop and clear all subprocesses
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        
        self.processes = []
    
    def on_nav_change(self, button_id):
        """
        Handle navigation button click.
        
        Args:
            button_id: ID of the clicked navigation button
        """
        self.show_tab(button_id)
    
    def show_tab(self, tab_id):
        """
        Show the specified tab.
        
        Args:
            tab_id: ID of the tab to show
        """
        # Store reference to previous settings tab if it exists and has active preview
        previous_settings_tab = None
        if hasattr(self, 'settings_tab') and self.settings_tab is not None:
            if hasattr(self.settings_tab, 'preview_active') and self.settings_tab.preview_active:
                # Keep reference to preserve state
                previous_settings_tab = self.settings_tab
                print("📌 Settings tab has active preview - preserving state")
            elif tab_id != "settings":
                # Cleanup settings tab when navigating away (no active preview)
                try:
                    if hasattr(self.settings_tab, 'cleanup'):
                        self.settings_tab.cleanup()
                except:
                    pass
        
        # Clear current tab content
        if self.current_tab_frame:
            self.current_tab_frame.destroy()
        
        # Create new tab frame
        self.current_tab_frame = tk.Frame(self.content_frame, bg=Colors.PRIMARY_BG)
        self.current_tab_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup the appropriate tab
        if tab_id == "inference":
            self.inference_tab = InferenceTab(self.current_tab_frame, self)
            self.inference_tab.setup()
            # Restart camera feeds if they were running
            if self.camera_running:
                self.start_camera_feeds()
        
        elif tab_id == "data":
            self._show_placeholder_tab("Data Tab", "Data management and viewing functionality")
        
        elif tab_id == "diagnosis":
            self.diagnosis_tab = DiagnosisTab(self.current_tab_frame, self)
            self.diagnosis_tab.setup()
        
        elif tab_id == "settings":
            # If we have a previous settings tab with active preview, restore it
            if previous_settings_tab is not None:
                self.settings_tab = previous_settings_tab
                self.settings_tab.parent = self.current_tab_frame
                self.settings_tab.setup()
            else:
                # Create fresh settings tab instance
                self.settings_tab = SettingsTab(self.current_tab_frame, self)
                self.settings_tab.setup()
        
        elif tab_id == "model_management":
            self.model_management_tab = ModelManagementTab(self.current_tab_frame, self)
            self.model_management_tab.setup()
        
        elif tab_id == "user_management":
            self._show_placeholder_tab("User Management Tab", "User accounts and permissions")
        
        elif tab_id == "system_check":
            self._show_placeholder_tab("System Check Tab", "Hardware and connection diagnostics")
        
        elif tab_id == "info":
            self.statistics_tab = StatisticsTab(self.current_tab_frame, self)
            self.statistics_tab.setup()
        
        elif tab_id == "config":
            self._show_placeholder_tab("Config Tab", "System configuration and parameters")
        
        # Update navbar active state
        if self.navbar_manager:
            self.navbar_manager.set_active_button(tab_id)
    
    def _show_placeholder_tab(self, title, description):
        """
        Show a placeholder tab for unimplemented features.
        
        Args:
            title: Tab title
            description: Tab description
        """
        container = tk.Frame(self.current_tab_frame, bg=Colors.PRIMARY_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            container,
            text=title,
            font=Fonts.LARGE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(50, 20))
        
        desc_label = tk.Label(
            container,
            text=description,
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        desc_label.pack(pady=10)
        
        info_label = tk.Label(
            container,
            text="This feature is under development",
            font=Fonts.SMALL,
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        info_label.pack(pady=10)
    
    def start_camera_feeds(self):
        """Start camera feed update threads."""
        self.camera_running = True
        if self.inference_tab:
            self.inference_tab.start_camera_threads()
    
    def update_statistics(self):
        """Update statistics display (mock data for now)."""
        if hasattr(self, 'od_inspected_var') and self.inspection_running:
            # Increment counters randomly for demonstration
            if np.random.random() < 0.2:  # 20% chance to update
                self.od_inspected += 1
                defect = np.random.random() < 0.3  # 30% chance of defect
                if defect:
                    self.od_defective += 1
                else:
                    self.od_good += 1
                
                # Update display variables
                self.od_inspected_var.set(str(self.od_inspected))
                self.od_defective_var.set(str(self.od_defective))
                self.od_good_var.set(str(self.od_good))
                
                if self.od_inspected > 0:
                    proportion = (self.od_defective / self.od_inspected) * 100
                    self.od_proportion_var.set(f"{proportion:.1f}%")
            
            # BIG FACE statistics
            if np.random.random() < 0.2:  # 20% chance to update
                self.bf_inspected += 1
                defect = np.random.random() < 0.2  # 20% chance of defect
                if defect:
                    self.bf_defective += 1
                else:
                    self.bf_good += 1
                
                # Update display variables
                self.bf_inspected_var.set(str(self.bf_inspected))
                self.bf_defective_var.set(str(self.bf_defective))
                self.bf_good_var.set(str(self.bf_good))
                
                if self.bf_inspected > 0:
                    proportion = (self.bf_defective / self.bf_inspected) * 100
                    self.bf_proportion_var.set(f"{proportion:.1f}%")
            
            # Update total statistics
            total_inspected = self.od_inspected + self.bf_inspected
            total_defective = self.od_defective + self.bf_defective
            total_good = self.od_good + self.bf_good
            
            self.total_inspected_var.set(str(total_inspected))
            self.total_defective_var.set(str(total_defective))
            self.total_good_var.set(str(total_good))
            
            if total_inspected > 0:
                total_proportion = (total_defective / total_inspected) * 100
                self.total_proportion_var.set(f"{total_proportion:.1f}%")
        
        # Schedule next update
        self.after(100, self.update_statistics)
    
    def update_threshold(self, val, label, defect, is_od):
        """
        Update threshold value label.
        
        Args:
            val: New threshold value
            label: Label widget to update
            defect: Defect type name
            is_od: Whether this is an OD threshold
        """
        label.config(text=f"{int(float(val))}%")
        
        # Update the threshold in the appropriate dictionary
        if is_od:
            self.od_defect_thresholds[defect] = int(float(val))
        else:
            self.bf_defect_thresholds[defect] = int(float(val))
    
    def update_model_confidence(self):
        """Update model confidence thresholds in real-time."""
        if not hasattr(self, 'inspection_running') or not self.inspection_running:
            return
        
        # Get current confidence values
        od_conf = self.od_conf_threshold
        bf_conf = self.bf_conf_threshold
        
        print(f"Updating model confidence: OD={od_conf:.2f}, Bigface={bf_conf:.2f}")
        
        # Update the shared data dictionary with new confidence values
        if hasattr(self, 'shared_data'):
            self.shared_data['od_conf_threshold'] = od_conf
            self.shared_data['bf_conf_threshold'] = bf_conf
    
    def on_closing(self):
        """Handle application closing."""
        # Check if settings preview is active
        if hasattr(self, 'settings_tab') and self.settings_tab:
            if hasattr(self.settings_tab, 'preview_active') and self.settings_tab.preview_active:
                from tkinter import messagebox
                response = messagebox.askyesno(
                    "Preview Active",
                    "Settings preview is currently running.\n\n"
                    "Closing the application will stop the preview.\n\n"
                    "Do you want to close anyway?"
                )
                if not response:
                    return  
        
        print("Closing application...")
        self.camera_running = False
        
        if self.inspection_running:
            self.stop_inspection()
        
        delete_all_pycache(".")
        clear_gpu_memory()

        time.sleep(0.5)
        self.destroy()
