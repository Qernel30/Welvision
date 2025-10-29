"""
State Manager for Inspection UI
Manages button and tab states during inspection start/stop
"""

import tkinter as tk
from ..utils.styles import Colors


class InspectionStateManager:
    """Manages UI state changes during inspection."""
    
    def __init__(self, app_instance):
        """
        Initialize the state manager.
        
        Args:
            app_instance: Reference to main WelVisionApp instance
        """
        self.app = app_instance
        self.original_close_handler = None
        
    def on_inspection_start(self, control_panel):
        """
        Handle UI state changes when inspection starts.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        # Apply control panel button states
        self._apply_control_panel_inspection_state(control_panel)
        
        # Lock roller type selection
        self._lock_roller_selection()
        
        # 4. Disable Logout button with grey color and white text
        self._disable_logout_button()
        
        # 5. Disable the Close button (top right X)
        self._disable_window_close()
        
        # 6. Disable all tabs except Inference (Diagnosis) tab with red color and white text
        self._disable_other_tabs()
    
    def restore_control_panel_state(self, control_panel):
        """
        Restore control panel button states when returning to inference tab during inspection.
        Does not modify tabs, logout button, or window close state.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        # Only apply control panel button states
        self._apply_control_panel_inspection_state(control_panel)
    
    def _apply_control_panel_inspection_state(self, control_panel):
        """
        Apply inspection state to control panel buttons.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        # 1. Disable Start button with grey color and white text
        if control_panel.start_button:
            control_panel.start_button.config(
                state=tk.DISABLED,
                bg="#6c757d",  # Grey
                fg=Colors.WHITE  # White text
            )
        
        # 2. Enable Stop button with red color and white text
        if control_panel.stop_button:
            control_panel.stop_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,  # Red
                fg=Colors.WHITE  # White text
            )
        
        # 3. Disable Reset button with grey color and white text during inspection
        if control_panel.reset_button:
            control_panel.reset_button.config(
                state=tk.DISABLED,
                bg="#6c757d",  # Grey
                fg=Colors.WHITE  # White text
            )
    
        # 4. Disable Allow All Images checkbox during inspection
        if hasattr(control_panel, 'allow_images_checkbox') and control_panel.allow_images_checkbox:
            control_panel.allow_images_checkbox.config(state=tk.DISABLED)
    
    def on_inspection_stop(self, control_panel):
        """
        Handle UI state changes when inspection stops.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        # 1. Enable Start button with green color and white text
        if control_panel.start_button:
            control_panel.start_button.config(
                state=tk.NORMAL,
                bg=Colors.SUCCESS,  # Green
                fg=Colors.WHITE  # White text
            )
        
        # 2. Disable Stop button with grey color and white text
        if control_panel.stop_button:
            control_panel.stop_button.config(
                state=tk.DISABLED,
                bg="#6c757d",  # Grey
                fg=Colors.WHITE  # White text
            )
        
        # 3. Reset button state will be handled by _on_stop_inspection
        #    It will check if there's data and enable accordingly
        #    We don't set it here to avoid race conditions
        
        # 4. Re-enable Allow All Images checkbox
        if hasattr(control_panel, 'allow_images_checkbox') and control_panel.allow_images_checkbox:
            control_panel.allow_images_checkbox.config(state=tk.NORMAL)
        
        # Unlock roller type selection
        self._unlock_roller_selection()
        
        # 5. Enable Logout button with red color and white text
        self._enable_logout_button()
        
        # 6. Enable the Close button (top right X)
        self._enable_window_close()
        
        # 7. Enable all tabs with normal colors
        self._enable_all_tabs()
    
    def _disable_logout_button(self):
        """Disable the logout button with grey color and white text."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.DISABLED,
                bg="#6c757d",  # Grey
                fg=Colors.WHITE  # White text
            )
    
    def _enable_logout_button(self):
        """Enable the logout button with red color and white text."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,  # Red
                fg=Colors.WHITE  # White text
            )
    
    def _disable_window_close(self):
        """Disable the window close button (top right X)."""
        # Store original handler
        self.original_close_handler = self.app.protocol("WM_DELETE_WINDOW")
        
        # Set new handler that shows warning
        self.app.protocol("WM_DELETE_WINDOW", self._on_disabled_close)
    
    def _enable_window_close(self):
        """Enable the window close button (top right X)."""
        # Restore original handler or set default
        if self.original_close_handler:
            self.app.protocol("WM_DELETE_WINDOW", self.original_close_handler)
        elif hasattr(self.app, 'on_closing'):
            self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
        else:
            self.app.protocol("WM_DELETE_WINDOW", self.app.destroy)
    
    def _on_disabled_close(self):
        """Show warning when trying to close during inspection."""
        from tkinter import messagebox
        messagebox.showwarning(
            "Inspection Running",
            "⚠️ Please stop the inspection before closing the application."
        )
    
    def _disable_other_tabs(self):
        """Disable all navigation tabs except Inference and Diagnosis with red color and white text."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Disable all buttons except 'inference' and 'diagnosis'
            for button_id, nav_button in navbar.buttons.items():
                if button_id not in ["inference", "diagnosis"]:
                    # Disable the button
                    nav_button.button.config(
                        state=tk.DISABLED,
                        bg=Colors.DANGER,  # Red
                        fg=Colors.WHITE,  # White text
                        disabledforeground=Colors.WHITE  # White text when disabled
                    )
                    
                    # Unbind hover events to prevent color restoration
                    nav_button.button.unbind("<Enter>")
                    nav_button.button.unbind("<Leave>")
    
    def _enable_all_tabs(self):
        """Enable all navigation tabs with normal colors and restore hover events."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            # Enable all buttons and restore colors
            for button_id, nav_button in navbar.buttons.items():
                nav_button.button.config(state=tk.NORMAL)
                
                # Restore active/inactive colors
                if nav_button.is_active:
                    nav_button.button.config(bg=nav_button.active_bg)
                else:
                    nav_button.button.config(bg=nav_button.inactive_bg)
                
                # Re-bind hover events
                nav_button.button.bind("<Enter>", nav_button._on_hover)
                nav_button.button.bind("<Leave>", nav_button._on_leave)
    
    def _lock_roller_selection(self):
        """Lock roller type dropdown during inspection."""
        if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
            if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                self.app.inference_tab.status_panel.lock_roller_selection()
    
    def _unlock_roller_selection(self):
        """Unlock roller type dropdown after inspection stops."""
        if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
            if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                self.app.inference_tab.status_panel.unlock_roller_selection()
