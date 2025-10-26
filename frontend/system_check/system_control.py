"""
System Control Component
Control buttons for system operations
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts


class SystemControl:
    """System control buttons component."""
    
    def __init__(self, parent, app_instance, system_check_tab):
        """
        Initialize system control.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
            system_check_tab: Reference to SystemCheckTab instance
        """
        self.parent = parent
        self.app = app_instance
        self.system_check_tab = system_check_tab
        
        # Button references
        self.start_button = None
        self.stop_button = None
        self.reset_button = None
        self.emergency_button = None
    
    def create(self):
        """Create the system control UI."""
        # Main frame
        control_frame = tk.LabelFrame(
            self.parent,
            text="System Control",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Inner container
        inner_frame = tk.Frame(control_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Buttons container (centered)
        buttons_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(anchor="center")
        
        # Start System button - Green with White text
        self.start_button = tk.Button(
            buttons_frame,
            text="START SYSTEM",
            font=("Arial", 10, "bold"),
            bg="#28A745",  # Green
            fg="#FFFFFF",  # White
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=2,
            command=self._start_system
        )
        self.start_button.pack(side=tk.LEFT, padx=8)
        
        # Stop System button - Grey with White text
        self.stop_button = tk.Button(
            buttons_frame,
            text="STOP SYSTEM",
            font=("Arial", 10, "bold"),
            bg="#6C757D",  # Grey
            fg="#FFFFFF",  # White
            disabledforeground="#FFFFFF",  # White text even when disabled
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=2,
            state=tk.DISABLED,
            command=self._stop_system
        )
        self.stop_button.pack(side=tk.LEFT, padx=8)
        
        # Reset Counters button - Red when enabled (system stopped), Grey when disabled (system running)
        self.reset_button = tk.Button(
            buttons_frame,
            text="RESET COUNTERS",
            font=("Arial", 10, "bold"),
            bg="#DC3545",  # Red when enabled
            fg=Colors.WHITE,
            disabledforeground="#FFFFFF",  # White text even when disabled
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=2,
            state=tk.NORMAL,  # Enabled by default
            command=self._reset_counters
        )
        self.reset_button.pack(side=tk.LEFT, padx=8)
        
        # Emergency Stop button - Grey when disabled (system stopped), Red when enabled (system running)
        self.emergency_button = tk.Button(
            buttons_frame,
            text="EMERGENCY STOP",
            font=("Arial", 10, "bold"),
            bg="#6C757D",  # Grey when disabled
            fg=Colors.WHITE,
            disabledforeground="#FFFFFF",  # White text even when disabled
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=2,
            state=tk.DISABLED,  # Disabled by default
            command=self._emergency_stop
        )
        self.emergency_button.pack(side=tk.LEFT, padx=8)
    
    def _start_system(self):
        """Start the system check control."""
        if self.system_check_tab.start_system():
            # Update button states and colors
            self.start_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            self.stop_button.config(state=tk.NORMAL, bg="#DC3545")  # Red when enabled
            self.reset_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            self.emergency_button.config(state=tk.NORMAL, bg="#FF0000")  # Red when enabled
            
            # Block app closing
            if hasattr(self.app, 'protocol'):
                self.app.protocol("WM_DELETE_WINDOW", self._block_closing)
            
            messagebox.showinfo("System Started", "System Check control started successfully")
        else:
            messagebox.showerror("Error", "Failed to start System Check.\nCould not connect to PLC.")
    
    def _stop_system(self):
        """Stop the system check control."""
        response = messagebox.askyesno(
            "Confirm Stop",
            "Are you sure you want to stop the System Check control?"
        )
        if response:
            self.system_check_tab.stop_system()
            # Update button states and colors
            self.start_button.config(state=tk.NORMAL, bg="#28A745")  # Green when enabled
            self.stop_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            self.reset_button.config(state=tk.NORMAL, bg="#DC3545")  # Red when enabled
            self.emergency_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            
            # Restore app closing
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            messagebox.showinfo("System Stopped", "System Check control stopped")
    
    def _reset_counters(self):
        """Reset processing counters."""
        response = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all counters to zero?"
        )
        if response:
            self.system_check_tab.reset_counters()
            messagebox.showinfo("Success", "All counters have been reset to zero")
    
    def _emergency_stop(self):
        """Emergency stop - immediate system halt."""
        response = messagebox.askokcancel(
            "⚠ EMERGENCY STOP",
            "This will immediately halt all System Check operations!\n\n"
            "Are you sure you want to perform an emergency stop?",
            icon='warning'
        )
        if response:
            self.system_check_tab.stop_system()
            # Update button states and colors
            self.start_button.config(state=tk.NORMAL, bg="#28A745")  # Green when enabled
            self.stop_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            self.reset_button.config(state=tk.NORMAL, bg="#DC3545")  # Red when enabled
            self.emergency_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
            
            # Restore app closing
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            print("🚨 EMERGENCY STOP - System halted")
            messagebox.showwarning(
                "Emergency Stop", 
                "System Check has been halted immediately"
            )
    
    def enable_start(self):
        """Enable start button, disable stop button."""
        self.start_button.config(state=tk.NORMAL, bg="#28A745")  # Green
        self.stop_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey
        self.reset_button.config(state=tk.NORMAL, bg="#DC3545")  # Red when enabled
        self.emergency_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
    
    def enable_stop(self):
        """Enable stop button, disable start button."""
        self.start_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey
        self.stop_button.config(state=tk.NORMAL, bg="#DC3545")  # Red
        self.reset_button.config(state=tk.DISABLED, bg="#6C757D")  # Grey when disabled
        self.emergency_button.config(state=tk.NORMAL, bg="#FF0000")  # Red when enabled
    
    def _block_closing(self):
        """Block app closing when system is running."""
        messagebox.showwarning(
            "System Running",
            "System Check is currently running!\n\n"
            "Please stop the system before closing the application."
        )
