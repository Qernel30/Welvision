"""
Control Panel Component
Contains start/stop/reset buttons and allow images checkbox
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig
from database import save_to_database
from .state_manager import InspectionStateManager
import snap7
import cv2


class ControlPanel:
    """Control panel for inspection operations."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the control panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.start_button = None
        self.stop_button = None
        self.reset_button = None
        
        # State manager for UI state changes
        self.state_manager = InspectionStateManager(app_instance)
        
    def setup(self):
        """Setup the control panel UI."""
        # Control buttons frame with better spacing
        control_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Start button
        self.start_button = tk.Button(
            control_frame,
            text="Start",
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,  # White text when disabled
            width=15,
            height=2,
            command=self._on_start_inspection
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Stop button
        self.stop_button = tk.Button(
            control_frame,
            text="Stop",
            font=Fonts.TEXT_BOLD,
            bg="#6c757d",  # Gray
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,  # White text when disabled
            width=15,
            height=2,
            command=self._on_stop_inspection,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Reset button
        self.reset_button = tk.Button(
            control_frame,
            text="Reset",
            font=Fonts.TEXT_BOLD,
            bg="#6c757d",  # Grey (initially disabled color)
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,  # White text when disabled
            width=15,
            height=2,
            command=self._reset_results,
            state=tk.DISABLED  # Initially disabled
        )
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Apply inspection state if inspection is running
        self._restore_inspection_state()
        
        return control_frame
    
    def _reset_results(self):
        """Reset all inspection results and save to database."""
        # Show confirmation dialog first
        confirm_reset = messagebox.askyesno(
            "Reset Counters",
            "Are you sure you want to reset all inspection counters?\n\n"
            "This will clear all current statistics."
        )
        
        if not confirm_reset:
            return  # User cancelled - keep Reset button enabled
        
        # User confirmed - proceed with reset and then disable the button
        
        # Check if there's data to save
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            bf_inspected = self.app.shared_data.get("bf_inspected", 0)
            od_inspected = self.app.shared_data.get("od_inspected", 0)
            
            # Only save if there's actual data
            if bf_inspected > 0 or od_inspected > 0:
                # Ask for confirmation
                response = messagebox.askyesno(
                    "Save Data",
                    f"Do you want to save the current inspection data to database?\n\n"
                    f"BF Inspected: {bf_inspected}\n"
                    f"OD Inspected: {od_inspected}\n\n"
                    f"This will also reset all counters."
                )
                
                if response:
                    try:
                        # Get employee ID (use current user email or ID)
                        employee_id = self.app.current_user if self.app.current_user is not None else "Unknown"
                        
                        # Get start time (or use current time if not set)
                        start_time = self.app.inspection_start_time if hasattr(self.app, 'inspection_start_time') and self.app.inspection_start_time else None
                        if start_time is None:
                            from datetime import datetime
                            start_time = datetime.now().time()
                        
                        # Save to database
                        success = save_to_database(
                            employee_id=employee_id,
                            start_time=start_time,
                            shared_data=dict(self.app.shared_data)
                        )
                        
                        if success:
                            messagebox.showinfo("Success", "✅ Data saved successfully to database!")
                        else:
                            messagebox.showerror("Error", "❌ Failed to save data to database. Check console for details.")
                    
                    except Exception as e:
                        messagebox.showerror("Error", f"❌ Error saving data: {str(e)}")
                        print(f"Error details: {e}")
                        import traceback
                        traceback.print_exc()
        
        # Reset all statistics in shared_data
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # BF Statistics
            self.app.shared_data["bf_inspected"] = 0
            self.app.shared_data["bf_ok_rollers"] = 0
            self.app.shared_data["bf_not_ok_rollers"] = 0
            self.app.shared_data["rust"] = 0
            self.app.shared_data["dent"] = 0
            self.app.shared_data["damage"] = 0
            self.app.shared_data["high_head"] = 0
            self.app.shared_data["down_head"] = 0
            self.app.shared_data["others"] = 0
            
            # OD Statistics
            self.app.shared_data["od_inspected"] = 0
            self.app.shared_data["od_ok_rollers"] = 0
            self.app.shared_data["od_not_ok_rollers"] = 0
            self.app.shared_data["od_rust"] = 0
            self.app.shared_data["od_dent"] = 0
            self.app.shared_data["od_damage"] = 0
            self.app.shared_data["od_damage_on_end"] = 0
            self.app.shared_data["od_spherical_mark"] = 0
            self.app.shared_data["od_others"] = 0
        
        # Reset old statistics (for backward compatibility)
        self.app.od_inspected = 0
        self.app.od_defective = 0
        self.app.od_good = 0
        self.app.bf_inspected = 0
        self.app.bf_defective = 0
        self.app.bf_good = 0
        
        # Disable reset button after successful reset
        if self.reset_button:
            self.reset_button.config(state=tk.DISABLED, bg="#6c757d")
    
    def _restore_inspection_state(self):
        """Restore button states if inspection is running."""
        if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
            self.state_manager.restore_control_panel_state(self)
    
    def _check_models_available(self):
        """
        Check if both BF and OD models are available.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        bf_model_path = getattr(self.app, 'selected_bf_model_path', None)
        od_model_path = getattr(self.app, 'selected_od_model_path', None)
        
        if not bf_model_path or not od_model_path:
            return False, "⚠️ Models Not Available\n\nBoth BF and OD models are required to start inference.\n\nPlease configure models in the Settings tab."
        
        return True, ""
    
    def _check_plc_connection(self):
        """
        Check PLC connection.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            plc = snap7.client.Client()
            plc.connect(AppConfig.PLC_IP, AppConfig.PLC_RACK, AppConfig.PLC_SLOT)
            
            if plc.get_connected():
                plc.disconnect()
                return True, ""
            else:
                return False, f"⚠️ PLC Not Connected\n\nCannot connect to PLC at {AppConfig.PLC_IP}\n\nPlease check PLC connection and try again."
        
        except Exception as e:
            return False, f"⚠️ PLC Connection Failed\n\nError: {str(e)}\n\nPlease check PLC connection and try again."
    
    def _check_cameras_connected(self):
        """
        Check if cameras are connected.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
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
    
    def _check_database_connection(self):
        """
        Check database connection.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                port=AppConfig.DB_PORT,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE,
                connection_timeout=5
            )
            
            if connection.is_connected():
                connection.close()
                return True, ""
            else:
                return False, f"⚠️ Database Not Connected\n\nCannot connect to database at {AppConfig.DB_HOST}:{AppConfig.DB_PORT}\n\nPlease check database connection and try again."
        
        except Exception as e:
            return False, f"⚠️ Database Connection Failed\n\nError: {str(e)}\n\nPlease check database connection and try again."
    
    def _validate_system_ready(self):
        """
        Validate that all prerequisites are met before starting inference.
        
        Returns:
            bool: True if system is ready, False otherwise
        """
        # Check 1: Models available
        models_ok, models_error = self._check_models_available()
        if not models_ok:
            messagebox.showerror("System Not Ready", models_error)
            return False
        
        # Check 2: PLC connection
        plc_ok, plc_error = self._check_plc_connection()
        if not plc_ok:
            messagebox.showerror("System Not Ready", plc_error)
            return False
        
        # Check 3: Cameras connected
        cameras_ok, cameras_error = self._check_cameras_connected()
        if not cameras_ok:
            messagebox.showerror("System Not Ready", cameras_error)
            return False
        
        # Check 4: Database connection
        db_ok, db_error = self._check_database_connection()
        if not db_ok:
            messagebox.showerror("System Not Ready", db_error)
            return False
        
        return True
    
    def _on_start_inspection(self):
        """Handle start button click and monitor system readiness."""
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Start Inspection",
            "Are you sure you want to start the inspection process?\n"
        )
        
        if not response:
            return  # User cancelled
        
        # Validate system prerequisites before starting
        if not self._validate_system_ready():
            return  # Exit if validation fails
        
        # Mark that inspection has been run at least once
        self.app.inspection_has_run = True
        
        if hasattr(self.app, 'shared_data') and self.app.shared_data is not None:
            # Get allow_all value from header checkbox if it exists
            if hasattr(self.app, 'allow_images_var'):
                self.app.shared_data['allow_all'] = self.app.allow_images_var.get()
            else:
                self.app.shared_data['allow_all'] = False
            
            # Store selected roller type in shared_data
            if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
                if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                    selected_roller = self.app.inference_tab.status_panel.status_vars.get('roller_type')
                    if selected_roller:
                        roller_type = selected_roller.get()
                        if roller_type and roller_type != "No Rollers":
                            self.app.shared_data['selected_roller_type'] = roller_type
                        else:
                            self.app.shared_data['selected_roller_type'] = None
        
        # Disable allow_images checkbox in header during inspection
        if (hasattr(self.app, 'allow_images_checkbutton') and 
            self.app.allow_images_checkbutton and 
            self.app.allow_images_checkbutton.winfo_exists()):
            self.app.allow_images_checkbutton.config(state=tk.DISABLED, fg="#808080")  # Grey when disabled
        
        # Disable debug checkbox in header during inspection (change color)
        if (hasattr(self.app, 'debug_checkbutton') and 
            self.app.debug_checkbutton and 
            self.app.debug_checkbutton.winfo_exists()):
            # Store original color before changing
            if not hasattr(self.app, '_debug_original_fg'):
                self.app._debug_original_fg = self.app.debug_checkbutton.cget('fg')
            self.app.debug_checkbutton.config(state=tk.DISABLED, fg="#808080")  # Grey when disabled
        
        self.state_manager.on_inspection_start(self)
        
        self.app.start_inspection()
        
        self._check_system_ready()
    
    def _check_system_ready(self):
        """Check if both BF and OD models are ready and show popup."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # Check if overall system is ready
            if self.app.shared_data.get('overall_system_ready', False):
                # Show success popup
                messagebox.showinfo(
                    "System Ready",
                    "✅ System is Ready!\n\nBoth BF and OD models have been loaded and warmed up successfully.\nLights are ON and the system is ready for inspection."
                )
                return
            
            # If not ready yet, check again after 500ms
            if self.app.inspection_running:
                self.parent.after(500, self._check_system_ready)
    
    def _on_stop_inspection(self):
        """Handle stop button click and re-enable all buttons."""
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Stop Inspection",
            "Are you sure you want to stop the inspection process?\n"
        )
        
        if not response:
            return  # User cancelled - inspection continues, Reset stays disabled
        
        # User confirmed - stop the inspection process
        self.app.stop_inspection()
        
        # Re-enable the allow_images checkbox in header after inspection stops
        if (hasattr(self.app, 'allow_images_checkbutton') and 
            self.app.allow_images_checkbutton and 
            self.app.allow_images_checkbutton.winfo_exists()):
            self.app.allow_images_checkbutton.config(state=tk.NORMAL, fg=Colors.WHITE)  # White when enabled
        
        # Re-enable debug checkbox in header after inspection stops (restore color)
        if (hasattr(self.app, 'debug_checkbutton') and 
            self.app.debug_checkbutton and 
            self.app.debug_checkbutton.winfo_exists()):
            # Restore original color or white
            original_fg = getattr(self.app, '_debug_original_fg', Colors.WHITE)
            self.app.debug_checkbutton.config(state=tk.NORMAL, fg=original_fg)
        
        # Apply all UI state changes for inspection stop
        self.state_manager.on_inspection_stop(self)
        
        # Enable Reset button ONLY if there's data to reset (after stop is confirmed)
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            bf_inspected = self.app.shared_data.get("bf_inspected", 0)
            od_inspected = self.app.shared_data.get("od_inspected", 0)
            
            if bf_inspected > 0 or od_inspected > 0:
                # There's data - enable Reset button with orange color
                if self.reset_button:
                    self.reset_button.config(state=tk.NORMAL, bg="#ff8c00")
            else:
                # No data - keep Reset button disabled
                if self.reset_button:
                    self.reset_button.config(state=tk.DISABLED, bg="#6c757d")
    
    def enable_start(self):
        """Enable the start button and disable stop button."""
        if self.start_button:
            self.start_button.config(state=tk.NORMAL, bg=Colors.SUCCESS)
        if self.stop_button:
            self.stop_button.config(state=tk.DISABLED, bg="#6c757d")
        
        # Note: Reset button state is controlled by _on_stop_inspection
        # Don't modify it here - it should remain in its current state
        
        # Re-enable allow_images checkbox in header when inspection is not running
        if (hasattr(self.app, 'allow_images_checkbutton') and 
            self.app.allow_images_checkbutton and 
            self.app.allow_images_checkbutton.winfo_exists()):
            self.app.allow_images_checkbutton.config(state=tk.NORMAL, fg=Colors.WHITE)  # White when enabled
        
        # Re-enable debug checkbox in header when inspection is not running (restore color)
        if (hasattr(self.app, 'debug_checkbutton') and 
            self.app.debug_checkbutton and 
            self.app.debug_checkbutton.winfo_exists()):
            # Restore original color or white
            original_fg = getattr(self.app, '_debug_original_fg', Colors.WHITE)
            self.app.debug_checkbutton.config(state=tk.NORMAL, fg=original_fg)
    
    def enable_stop(self):
        """Enable the stop button and disable start and reset buttons."""
        if self.start_button:
            self.start_button.config(state=tk.DISABLED, bg="#6c757d")
        if self.stop_button:
            self.stop_button.config(state=tk.NORMAL, bg=Colors.DANGER)
        # Disable Reset button during inspection
        if self.reset_button:
            self.reset_button.config(state=tk.DISABLED, bg="#6c757d")
        # Keep allow_images checkbox in header disabled during inspection
        if (hasattr(self.app, 'allow_images_checkbutton') and 
            self.app.allow_images_checkbutton and 
            self.app.allow_images_checkbutton.winfo_exists()):
            self.app.allow_images_checkbutton.config(state=tk.DISABLED, fg="#808080")  # Grey when disabled
        
        # Keep debug checkbox in header disabled during inspection (change color)
        if (hasattr(self.app, 'debug_checkbutton') and 
            self.app.debug_checkbutton and 
            self.app.debug_checkbutton.winfo_exists()):
            # Store original color before changing
            if not hasattr(self.app, '_debug_original_fg'):
                self.app._debug_original_fg = self.app.debug_checkbutton.cget('fg')
            self.app.debug_checkbutton.config(state=tk.DISABLED, fg="#808080")  # Grey when disabled
