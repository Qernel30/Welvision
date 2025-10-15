"""
Login Form Container Module
Handles the main form layout and structure
"""

import tkinter as tk
from ..utils.styles import Colors


class LoginForm:
    """Main login form container."""
    
    def __init__(self, parent):
        """
        Initialize the login form container.
        
        Args:
            parent: Parent Tk window
        """
        self.parent = parent
        self.frame = None
        self.container = None
        
    def create(self):
        """
        Create the main login form container.
        
        Returns:
            container: The inner container frame for form components
        """
        # Create login frame with increased size
        self.frame = tk.Frame(
            self.parent, 
            bg=Colors.BLACK, 
            width=500,  # Increased from 500
            height=800  # Increased from 600
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add padding container
        self.container = tk.Frame(self.frame, bg=Colors.BLACK)
        self.container.pack(fill=tk.BOTH, expand=True, padx=50, pady=40)
        
        return self.container
    
    def destroy(self):
        """Destroy the login form."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
            self.container = None
