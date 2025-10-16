"""
Control Panel Component
Contains start/stop/reset buttons and allow images checkbox
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from database import save_to_database
from .state_manager import InspectionStateManager


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
        self.allow_images_var = None
        
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
            bg="#ff8c00",  # Orange
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,  # White text when disabled
            width=15,
            height=2,
            command=self._reset_results
        )
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Allow all images checkbox
        self.allow_images_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(
            control_frame,
            text="Allow all images",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.PRIMARY_BG,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE,
            variable=self.allow_images_var,
            command=self._toggle_allow_images
        )
        checkbox.pack(side=tk.LEFT, padx=30, pady=5)
        
        # Apply inspection state if inspection is running
        self._restore_inspection_state()
        
        return control_frame
    
    def _reset_results(self):
        """Reset all inspection results and save to database."""
        print("Resetting results...")
        
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
                        employee_id = self.app.current_user if self.app.current_user else "Unknown"
                        
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
        
        print("✅ All statistics reset successfully")
    
    def _toggle_allow_images(self):
        """Toggle allow all images setting."""
        status = "enabled" if self.allow_images_var.get() else "disabled"
        print(f"Allow all images: {status}")
    
    def _restore_inspection_state(self):
        """Restore button states if inspection is running."""
        # Check if inspection is currently running
        if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
            print("🔄 Restoring inspection state after tab switch...")
            # Apply inspection state to control panel buttons (without re-disabling tabs)
            self.state_manager.restore_control_panel_state(self)
    
    def _on_start_inspection(self):
        """Handle start button click and monitor system readiness."""
        # Apply all UI state changes for inspection start
        self.state_manager.on_inspection_start(self)
        
        # Start the inspection process
        self.app.start_inspection()
        
        # Start monitoring for system readiness
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
        # Stop the inspection process
        self.app.stop_inspection()
        
        # Apply all UI state changes for inspection stop
        self.state_manager.on_inspection_stop(self)
    
    def enable_start(self):
        """Enable the start button and disable stop button."""
        if self.start_button:
            self.start_button.config(state=tk.NORMAL, bg=Colors.SUCCESS)
        if self.stop_button:
            self.stop_button.config(state=tk.DISABLED, bg="#6c757d")
        if self.reset_button:
            self.reset_button.config(state=tk.NORMAL, bg="#ff8c00")
    
    def enable_stop(self):
        """Enable the stop button and disable start button."""
        if self.start_button:
            self.start_button.config(state=tk.DISABLED, bg="#6c757d")
        if self.stop_button:
            self.stop_button.config(state=tk.NORMAL, bg=Colors.DANGER)
