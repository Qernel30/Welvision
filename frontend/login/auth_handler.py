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
            tuple: (success: bool, error_message: str or None)
        """
        return authenticate_user(email, password, role)
    
    @staticmethod
    def show_error(error_message=None):
        """
        Display error message for failed login.
        
        Args:
            error_message: Specific error message to display (optional)
        """
        if error_message is None:
            error_message = "Invalid email, password, or role."
        
        messagebox.showerror("Login Failed", error_message)
