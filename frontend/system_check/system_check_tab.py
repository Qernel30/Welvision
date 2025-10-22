"""
System Check Tab - Main Controller
Professional interface for BigFace and OD roller inspection control
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from .control_settings import ControlSettings
from .system_status import SystemStatus
from .processing_counters import ProcessingCounters
from .system_control import SystemControl
from .plc_controller import PLCController


class SystemCheckTab:
    """System Check tab for PLC control interface."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the system check tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.control_settings = None
        self.system_status = None
        self.processing_counters = None
        self.system_control = None
        self.plc_controller = None
        
        # Initialize state from app if it exists (for persistence across tab switches)
        if hasattr(self.app, 'system_check_running'):
            self.system_running = self.app.system_check_running
        else:
            self.system_running = False
            self.app.system_check_running = False
        
        if hasattr(self.app, 'system_check_controls_disabled'):
            self.controls_are_disabled = self.app.system_check_controls_disabled
        else:
            self.controls_are_disabled = False
            self.app.system_check_controls_disabled = False
        
    def setup(self):
        """Setup the system check tab UI."""
        # Save the current running state before rebuilding UI
        was_running = self.system_running
        
        # Main container with dark blue background
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Title Section
        title_label = tk.Label(
            main_container,
            text="System Check - PLC Control Interface",
            font=("Arial", 20, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 2))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_container,
            text="Professional interface for BigFace and OD roller inspection control",
            font=("Arial", 9),
            fg="#CCCCCC",
            bg=Colors.PRIMARY_BG
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Control Settings Section - preserve disabled state if system was running
        # Use the SystemCheckTab's own flag, not the old ControlSettings instance
        controls_disabled = self.controls_are_disabled
        
        self.control_settings = ControlSettings(main_container, self.app)
        self.control_settings.controls_disabled = controls_disabled  # Set before create()
        self.control_settings.create()
        
        # Initialize PLC Controller only if not already initialized
        if self.plc_controller is None:
            self.plc_controller = PLCController(self.app, self.control_settings)
        else:
            # Update the control_settings reference in existing PLC controller
            self.plc_controller.control_settings = self.control_settings
        
        # System Status Section
        self.system_status = SystemStatus(main_container, self.app, self)
        self.system_status.create()
        
        # Processing Counters Section
        self.processing_counters = ProcessingCounters(main_container, self.app)
        self.processing_counters.create()
        
        # System Control Section
        self.system_control = SystemControl(main_container, self.app, self)
        self.system_control.create()
        
        # Restore button states if system is running
        if was_running:
            # Button states are already handled in create(), just update colors
            self.system_control.enable_stop()
            # Control settings are already disabled via controls_disabled flag
            self._block_navigation_buttons()
            # Also restore app closing block
            if hasattr(self.app, 'protocol'):
                self.app.protocol("WM_DELETE_WINDOW", self.system_control._block_closing)
        
        # Start monitoring updates
        self._monitor_updates()
    
    def _monitor_updates(self):
        """Monitor shared_data for real-time updates."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # Update system status
            if self.system_status:
                self.system_status.update_status(self.app.shared_data, self.system_running)
            
            # Update processing counters
            if self.processing_counters:
                self.processing_counters.update_counters(self.app.shared_data)
        
        # Continue monitoring every 500ms
        self.parent.after(500, self._monitor_updates)
    
    def start_system(self):
        """Start the system check control."""
        if self.system_running:
            print("⚠ System Check: Already running")
            return False
        
        # Start PLC monitoring
        if self.plc_controller.start_monitoring():
            self.system_running = True
            self.app.system_check_running = True  # Store in app for persistence
            
            # Block Inference and Settings navigation buttons
            self._block_navigation_buttons()
            
            # Block Control Settings pattern selection
            if self.control_settings:
                self.control_settings.disable_controls()
                self.controls_are_disabled = True
                self.app.system_check_controls_disabled = True  # Store in app for persistence
            
            # Update button states
            if self.system_control:
                self.system_control.enable_stop()
            
            return True
        else:
            print("❌ System Check: Failed to start system")
            return False
    
    def stop_system(self):
        """Stop the system check control."""
        if not self.system_running:
            print("⚠ System Check: Not running")
            return
        
        # Stop PLC monitoring
        self.plc_controller.stop_monitoring()
        self.system_running = False
        self.app.system_check_running = False  # Store in app for persistence
        
        # Unblock Inference and Settings navigation buttons
        self._unblock_navigation_buttons()
        
        # Unblock Control Settings pattern selection
        if self.control_settings:
            self.control_settings.enable_controls()
            self.controls_are_disabled = False
            self.app.system_check_controls_disabled = False  # Store in app for persistence
        
        # Update button states
        if self.system_control:
            self.system_control.enable_start()
        
    
    def reset_counters(self):
        """Reset all processing counters."""
        if self.plc_controller:
            self.plc_controller.reset_counters()
    
    def _block_navigation_buttons(self):
        """Block Inference and Settings navigation buttons with red color."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Block Inference button
            if 'inference' in navbar.buttons:
                navbar.buttons['inference'].button.config(
                    state=tk.DISABLED,
                    bg="#DC3545",  # Red color
                    disabledforeground="#FFFFFF"
                )
            
            # Block Settings button
            if 'settings' in navbar.buttons:
                navbar.buttons['settings'].button.config(
                    state=tk.DISABLED,
                    bg="#DC3545",  # Red color
                    disabledforeground="#FFFFFF"
                )
    
    def _unblock_navigation_buttons(self):
        """Unblock Inference and Settings navigation buttons."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Unblock Inference button
            if 'inference' in navbar.buttons:
                nav_button = navbar.buttons['inference']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
            
            # Unblock Settings button
            if 'settings' in navbar.buttons:
                nav_button = navbar.buttons['settings']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
