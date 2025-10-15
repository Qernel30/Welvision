"""
Authentication Handler Module
Handles login authentication and error display
"""

import tkinter.messagebox as messagebox
from ..utils.auth import authenticate_user


class AuthHandler:
    """Authentication handler for login operations."""
    
    @staticmethod
    def authenticate(email, password, role):
        """
        Authenticate user credentials.
        
        Args:
            email: User email
            password: User password
            role: Selected role
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        return authenticate_user(email, password, role)
    
    @staticmethod
    def show_error():
        """Display error message for failed login."""
        messagebox.showerror("Login Failed", "Invalid email, password, or role.")
