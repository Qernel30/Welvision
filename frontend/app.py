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
from .auth import users
from .inference_tab import setup_inference_tab
from .statistics_tab import setup_statistics_tab
from .settings_tab import setup_settings_tab
from .camera_manager import start_camera_feeds

# Import configuration
from config import PLC_CONFIG, CAMERA_CONFIG, DEFECT_THRESHOLDS, DEFAULT_CONFIDENCE, UI_COLORS


class WelVisionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WELVISION")
        self.geometry("1366x768")
        self.configure(bg=UI_COLORS['PRIMARY_BG'])
        self.iconbitmap(default="")  # Add your icon path if available
        
        # Center window on screen
        self.center_window()
        
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
        """Display the login page."""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create login frame with black background
        login_frame = tk.Frame(self, bg=UI_COLORS['BLACK'], width=500, height=600)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Logo
        logo_label = tk.Label(login_frame, text="WELVISION", font=("Arial", 32, "bold"), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
        logo_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(login_frame, text="Please sign in to continue", font=("Arial", 14), 
                                 fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
        subtitle_label.pack(pady=(0, 30))
        
        # Role selection
        role_frame = tk.Frame(login_frame, bg=UI_COLORS['BLACK'])
        role_frame.pack(pady=(0, 20))
        
        self.role_var = tk.StringVar(value="User")
        
        user_rb = tk.Radiobutton(role_frame, text="User", variable=self.role_var, value="User", 
                                font=("Arial", 12), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                                selectcolor=UI_COLORS['BLACK'])
        admin_rb = tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="Admin", 
                                 font=("Arial", 12), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                                 selectcolor=UI_COLORS['BLACK'])
        super_admin_rb = tk.Radiobutton(role_frame, text="Super Admin", variable=self.role_var, 
                                       value="Super Admin", font=("Arial", 12), fg=UI_COLORS['WHITE'], 
                                       bg=UI_COLORS['BLACK'], selectcolor=UI_COLORS['BLACK'])
        
        user_rb.pack(side=tk.LEFT, padx=10)
        admin_rb.pack(side=tk.LEFT, padx=10)
        super_admin_rb.pack(side=tk.LEFT, padx=10)
        
        # Email
        email_label = tk.Label(login_frame, text="Email", font=("Arial", 12), 
                              fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
        email_label.pack(fill="x", pady=(0, 5))
        
        self.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=40)
        self.email_entry.pack(pady=(0, 15), ipady=8)
        
        # Password
        password_label = tk.Label(login_frame, text="Password", font=("Arial", 12), 
                                 fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=40, show="*")
        self.password_entry.pack(pady=(0, 30), ipady=8)
        
        # Sign in button
        sign_in_button = tk.Button(login_frame, text="Sign In", font=("Arial", 12, "bold"), 
                                  bg=UI_COLORS['PRIMARY'], fg=UI_COLORS['WHITE'], width=20, height=2, 
                                  command=self.authenticate)
        sign_in_button.pack(pady=10)
        
        # Bind Enter key to authenticate
        self.bind("<Return>", lambda event: self.authenticate())
    
    def authenticate(self):
        """Authenticate user credentials."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if email in users and users[email]["password"] == password and users[email]["role"] == role:
            self.current_user = email
            self.current_role = role
            self.show_main_interface()
        else:
            messagebox.showerror("Login Failed", "Invalid email, password, or role.")

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
        
        # Create tabs with custom style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background=UI_COLORS['PRIMARY_BG'], foreground=UI_COLORS['WHITE'], 
                       font=('Arial', 12, 'bold'), padding=[20, 10], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', UI_COLORS['SECONDARY_BG'])], 
                 foreground=[('selected', UI_COLORS['WHITE'])])
        style.configure('TNotebook', background=UI_COLORS['PRIMARY_BG'], borderwidth=0)
        
        tab_control = ttk.Notebook(main_frame)
        
        inference_tab = tk.Frame(tab_control, bg=UI_COLORS['PRIMARY_BG'])
        statistics_tab = tk.Frame(tab_control, bg=UI_COLORS['PRIMARY_BG'])
        settings_tab = tk.Frame(tab_control, bg=UI_COLORS['PRIMARY_BG'])
        
        tab_control.add(inference_tab, text="Inference")
        tab_control.add(statistics_tab, text="Statistics")
        tab_control.add(settings_tab, text="Settings")
        
        tab_control.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configure tabs using modular functions
        setup_inference_tab(self, inference_tab)
        setup_statistics_tab(self, statistics_tab)
        setup_settings_tab(self, settings_tab)
        
        # Start camera feeds
        start_camera_feeds(self)
        
        # Start updating statistics
        self.update_statistics()
    
    def update_model_confidence(self):
        """Updates the confidence thresholds of the YOLO models in real-time."""
        if not hasattr(self, 'inspection_running') or not self.inspection_running:
            return
        
        # Get current confidence values from sliders
        od_conf = self.od_conf_threshold
        bf_conf = self.bf_conf_threshold
        
        print(f"Updating model confidence: OD={od_conf:.2f}, Bigface={bf_conf:.2f}")
        
        # Update the shared data dictionary with new confidence values
        if hasattr(self, 'shared_data'):
            self.shared_data['od_conf_threshold'] = od_conf
            self.shared_data['bf_conf_threshold'] = bf_conf
        
        # If you need to update the models directly (if they're in the main process)
        if hasattr(self, 'model_od'):
            self.model_od.conf = od_conf
        
        if hasattr(self, 'model_bigface'):
            self.model_bigface.conf = bf_conf

    def create_processes(self):
        """Recreates process instances before starting them."""
        self.plc_process = Process(
            target=plc_communication,
            args=(self.PLC_IP, self.RACK, self.SLOT, self.DB_NUMBER, self.shared_data, self.command_queue),
            daemon=True
        )

        self.processes = [
            Process(target=capture_frames_bigface, args=(self.shared_frame_bigface, self.frame_lock_bigface, self.frame_shape), daemon=True),
            Process(target=handle_slot_control_bigface, args=(self.roller_queue_bigface, self.shared_data, self.command_queue), daemon=True),
            Process(target=process_rollers_bigface, args=(self.shared_frame_bigface, self.frame_lock_bigface, self.roller_queue_bigface, self.model_bigface, self.proximity_count_bigface, self.roller_updation_dict, self.queue_lock, self.shared_data, self.frame_shape, self.shared_annotated_bigface, self.annotated_frame_lock_bigface), daemon=True),
            Process(target=process_frames_od, args=(self.shared_frame_od, self.frame_lock_od, self.roller_queue_od, self.queue_lock, self.shared_data, self.frame_shape, self.roller_updation_dict, self.shared_annotated_od, self.annotated_frame_lock_od), daemon=True),
            Process(target=capture_frames_od, args=(self.shared_frame_od, self.frame_lock_od, self.frame_shape), daemon=True),
            Process(target=handle_slot_control_od, args=(self.roller_queue_od, self.shared_data, self.command_queue), daemon=True)
        ]

    def start_inspection(self):
        """Start the inspection process."""
        if self.inspection_running:
            print("Inspection is already running!")
            return

        self.inspection_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Recreate processes before starting
        self.create_processes()

        # Start PLC process
        if self.plc_process is not None:
            self.plc_process.start()

        # Start subprocesses
        for process in self.processes:
            process.start()

    def stop_inspection(self):
        """Stops all running processes."""
        if not self.inspection_running:
            print("Inspection is not running.")
            return

        # Create PLC client
        plc_client = snap7.client.Client()

        try:
            plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
            print("✅ PLC Communication: Connected to PLC.")
        except Exception as e:
            print(f"❌ PLC Communication: Failed to connect to PLC. Error: {e}")
            return

        data = plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)  # Read 2 bytes

        set_bool(data, byte_index=1, bool_index=6, value=False)  # Turn OFF specific bit
        set_bool(data, byte_index=1, bool_index=7, value=False)  # Turn OFF another bit

        # Write back the modified data to DB
        plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
        print("✅ PLC Communication: Lights OFF signal sent.")
        # Close PLC connection
        plc_client.disconnect()
                
        self.inspection_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Stop the PLC process if it's running
        if self.plc_process.is_alive():
            self.plc_process.terminate()
            self.plc_process.join()
            self.plc_process = None  # Mark it for recreation

        # Stop and clear all subprocesses
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()

        self.processes = []  # Clear the list of processes

        print("Inspection stopped.")

    def save_thresholds(self):
        """Saves the current threshold settings."""
        # Save model confidence thresholds
        self.od_conf_threshold = float(self.od_conf_slider_value.get()) / 100
        self.bf_conf_threshold = float(self.bf_conf_slider_value.get()) / 100
        
        # Update the shared data dictionary with new confidence values
        if hasattr(self, 'shared_data'):
            self.shared_data['od_conf_threshold'] = self.od_conf_threshold
            self.shared_data['bf_conf_threshold'] = self.bf_conf_threshold
        
        # If inspection is running, update the model in real-time
        if hasattr(self, 'inspection_running') and self.inspection_running:
            self.update_model_confidence()

        messagebox.showinfo("Settings Saved", "Model confidence settings have been saved successfully.")
        print(f"OD Confidence: {self.od_conf_threshold}, BF Confidence: {self.bf_conf_threshold}")

    def create_slider(self, parent, label_text, min_val, max_val, default_val, row, is_od=True):
        """Create a slider widget for threshold adjustment."""
        if not hasattr(self, "slider_values"):  
            self.slider_values = {}

        frame = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

        label = tk.Label(frame, text=label_text, font=("Arial", 10), fg=UI_COLORS['WHITE'], 
                        bg=UI_COLORS['PRIMARY_BG'], width=20, anchor="w")
        label.pack(side=tk.LEFT, padx=5)

        slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200)
        slider.set(default_val)  
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        value_label = tk.Label(frame, text=f"{default_val}%", font=("Arial", 10), 
                              fg=UI_COLORS['WHITE'], bg=UI_COLORS['PRIMARY_BG'], width=5)
        value_label.pack(side=tk.RIGHT, padx=5)

        slider.configure(command=lambda val, lbl=value_label, defect=label_text, is_od=is_od: 
                        self.update_threshold(val, lbl, defect, is_od))

        self.slider_values[label_text] = slider

    def update_threshold(self, val, label, defect, is_od):
        """Update threshold value when slider is moved."""
        label.config(text=f"{int(float(val))}%")

    def update_statistics(self):
        """Update statistics display."""
        # Simulate updating statistics
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

    def initialize_system(self):
        """Initialize system components and shared memory."""
        self.RACK = PLC_CONFIG['RACK']
        self.PLC_IP = PLC_CONFIG['IP']
        self.SLOT = PLC_CONFIG['SLOT']
        self.DB_NUMBER = PLC_CONFIG['DB_NUMBER']
        
        initialize_bigface_csv()
        initialize_od_csv()

        print("Loading YOLO model...")
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

    def on_closing(self):
        """Handle application closing."""
        self.camera_running = False
        time.sleep(0.5)
        self.destroy()
