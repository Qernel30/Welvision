"""
Navigation Bar Manager
Main controller for the navigation bar system
"""

import tkinter as tk
from ..utils.styles import Colors
from .nav_button import NavButton
from .nav_config import NavConfig


class NavBarManager:
    """Manages the navigation bar and its buttons."""
    
    def __init__(self, parent, on_nav_change):
        """
        Initialize the navigation bar manager.
        
        Args:
            parent: Parent frame
            on_nav_change: Callback function when navigation changes
                          Should accept button_id as parameter
        """
        self.parent = parent
        self.on_nav_change = on_nav_change
        self.navbar_frame = None
        self.buttons = {}
        self.active_button_id = None
        
    def create(self):
        """Create the navigation bar."""
        # Create navbar container frame
        self.navbar_frame = tk.Frame(
            self.parent,
            bg=Colors.PRIMARY_BG,
            height=NavConfig.NAVBAR_HEIGHT
        )
        self.navbar_frame.pack(
            fill=tk.X,
            padx=NavConfig.NAVBAR_PADDING_X,
            pady=NavConfig.NAVBAR_PADDING_Y
        )
        
        # Create buttons container (left-aligned, not centered)
        buttons_container = tk.Frame(
            self.navbar_frame,
            bg=Colors.PRIMARY_BG
        )
        buttons_container.pack(anchor=tk.W, padx=5)
        
        # Create all navigation buttons
        for button_id, button_text, _ in NavConfig.get_button_configs():
            nav_button = NavButton(
                buttons_container,
                button_text,
                self._handle_nav_click,
                button_id
            )
            nav_button.create()
            nav_button.pack(side=tk.LEFT, padx=NavConfig.BUTTON_GAP)
            
            self.buttons[button_id] = nav_button
        
        return self.navbar_frame
    
    def _handle_nav_click(self, button_id):
        """
        Handle navigation button click.
        
        Args:
            button_id: ID of the clicked button
        """
        # Update active state for all buttons
        self.set_active_button(button_id)
        
        # Call the callback function
        if self.on_nav_change:
            self.on_nav_change(button_id)
    
    def set_active_button(self, button_id):
        """
        Set the active button and update visual states.
        
        Args:
            button_id: ID of the button to set as active
        """
        # Deactivate previously active button
        if self.active_button_id and self.active_button_id in self.buttons:
            self.buttons[self.active_button_id].set_active(False)
        
        # Activate new button
        if button_id in self.buttons:
            self.buttons[button_id].set_active(True)
            self.active_button_id = button_id
    
    def get_active_button_id(self):
        """Get the currently active button ID."""
        return self.active_button_id
    
    def enable_button(self, button_id):
        """Enable a specific button."""
        if button_id in self.buttons:
            self.buttons[button_id].button.config(state=tk.NORMAL)
    
    def disable_button(self, button_id):
        """Disable a specific button."""
        if button_id in self.buttons:
            self.buttons[button_id].button.config(state=tk.DISABLED)
