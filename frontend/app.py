"""
Frontend Application - WelVisionApp Main GUI Class
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import numpy as np
import time
from multiprocessing import Process, Array, Queue, Lock, Value, Manager
from ultralytics import YOLO
import snap7
from snap7.util import set_bool
from snap7.type import Areas

# Import backend modules
from backend import *

# Import frontend modules
from .auth_page import setup_login_page, users
from .navbar import setup_navbar
from .inference_page import (
    setup_inference_tab, 
    start_camera_feeds, 
    start_inspection, 
    stop_inspection, 
    toggle_allow_all_images,
    update_bf_results,
    update_od_results,
    update_overall_results
)
from .statistics_page import setup_statistics_tab, update_statistics
from .settings_page import setup_settings_tab, save_thresholds, create_slider, update_threshold, update_model_confidence

# Import configuration
from config import PLC_CONFIG, PLC_SENSORS, CAMERA_CONFIG, DEFECT_THRESHOLDS, DEFAULT_CONFIDENCE, UI_COLORS, IMAGE_STORAGE_PATHS, IMAGE_LIMIT_PER_DIRECTORY, WARMUP_IMAGES


class WelVisionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WELVISION")
        
        # Maximize window
        self.state('zoomed')  # Windows maximized
        
        self.configure(bg=UI_COLORS['PRIMARY_BG'])
        self.iconbitmap(default="")  # Add your icon path if available
        
        # Focus on window
        self.focus_force()
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        
        # Initialize variables
        self.current_user = None
        self.current_role = None
        
        # Statistics variables
        self.od_inspected = 0
        self.od_defective = 0
        self.od_good = 0
        
        self.bf_inspected = 0
        self.bf_defective = 0
        self.bf_good = 0
        
        # Camera variables
        self.od_camera = None
        self.bf_camera = None
        self.od_frame = None
        self.bf_frame = None
        
        # Inspection status
        self.inspection_running = False
        
        # Defect thresholds from config
        self.od_defect_thresholds = DEFECT_THRESHOLDS['OD'].copy()
        self.bf_defect_thresholds = DEFECT_THRESHOLDS['BIGFACE'].copy()
        
        # Show login page
        self.show_login_page()

    def center_window(self):
        """Center the application window on screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1280x800+{x}+{y}")
    
    def show_login_page(self):
        """Display the login page using modular auth component."""
        setup_login_page(self)

    def show_main_interface(self):
        """Display the main application interface."""
        # Clear any existing widgets
        self.initialize_system()
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self, bg=UI_COLORS['PRIMARY_BG'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = tk.Frame(main_frame, bg=UI_COLORS['PRIMARY_BG'], height=50)
        header_frame.pack(fill=tk.X)
        
        # Logo in header
        logo_label = tk.Label(header_frame, text="WELVISION", font=("Arial", 18, "bold"), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['PRIMARY_BG'])
        logo_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # User info
        user_label = tk.Label(header_frame, text=f"{self.current_role}: {self.current_user}", 
                             font=("Arial", 12), fg=UI_COLORS['WHITE'], bg=UI_COLORS['PRIMARY_BG'])
        user_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Logout button
        logout_button = tk.Button(header_frame, text="Logout", font=("Arial", 10), 
                                 command=self.show_login_page)
        logout_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Setup custom navbar
        content_frame = setup_navbar(self, main_frame)
        
        # Initialize with INFERENCE tab
        from .navbar.navbar_manager import _load_tab_content
        _load_tab_content(self, "INFERENCE")
    
    def initialize_system(self):
        """Initialize system components and shared memory."""
        self.RACK = PLC_CONFIG['RACK']
        self.PLC_IP = PLC_CONFIG['IP']
        self.SLOT = PLC_CONFIG['SLOT']
        self.DB_NUMBER = PLC_CONFIG['DB_NUMBER']

        self.model_bigface = YOLO(r"models/BF_sr.pt")
        self.model_od = YOLO(r"models/OD_sr.pt")

        self.model_bigface.to('cuda')
        self.model_od.to('cuda')

        self.frame_shape = CAMERA_CONFIG['FRAME_SHAPE']

        self.manager = Manager()
        self.shared_data = self.manager.dict()
        self.shared_data['bigface'] = False
        self.shared_data['od'] = False
        self.shared_data['bigface_presence'] = False
        self.shared_data['od_presence'] = False
        self.shared_data["head_classification_sensor"] = False
        self.shared_data['allow_all_images'] = False  # New flag for all images mode
        self.shared_data['bf_model_loaded'] = False  # Flag for Bigface model loaded
        self.shared_data['od_model_loaded'] = False  # Flag for OD model loaded
        self.shared_data['plc_ready'] = False  # Flag for PLC ready signal sent
        self.shared_data['image_storage_paths'] = IMAGE_STORAGE_PATHS
        self.shared_data['image_limit'] = IMAGE_LIMIT_PER_DIRECTORY
        self.shared_data['warmup_images'] = WARMUP_IMAGES
        self.shared_data['od_confidence'] = DEFAULT_CONFIDENCE['OD']
        self.shared_data['bigface_confidence'] = DEFAULT_CONFIDENCE['BIGFACE']

        self.command_queue = Queue()

        self.proximity_count_od = Value('i', 0)
        self.proximity_count_bigface = Value('i', 0)

        self.roller_data_od = self.manager.dict()
        self.roller_queue_od = Queue()
        self.roller_queue_bigface = Queue()
        self.roller_updation_dict = self.manager.dict()

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
        
        # Initialize storage directories
        from backend.image_manager import initialize_storage_directories
        initialize_storage_directories(IMAGE_STORAGE_PATHS)

    def on_closing(self):
        """Handle application closing."""
        self.camera_running = False
        time.sleep(0.5)
        self.destroy()
