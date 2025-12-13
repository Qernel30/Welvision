"""
Login Page UI Component - Main Controller
Orchestrates all login page components
"""

import tkinter as tk
from .window_config import WindowConfig
from .login_form import LoginForm
from .login_header import LoginHeader
from .role_selector import RoleSelector
from .input_fields import InputFields
from .signin_button import SignInButton
from .auth_handler import AuthHandler


class LoginPage:
    """Main login page controller that orchestrates all components."""
    
    def __init__(self, parent, on_login_success):
        """
        Initialize the login page.
        
        Args:
            parent: Parent Tk window
            on_login_success: Callback function when login is successful
                             Should accept (email, role) as parameters
        """
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Components
        self.login_form = None
        self.role_selector = None
        self.input_fields = None
        self.signin_button = None
        
        # Configure window to open maximized and focused
        WindowConfig.configure(self.parent)
        
    def show(self):
        """Display the login page."""
        # Clear any existing widgets
        self._clear_widgets()
        
        # Create login form structure
        self._build_login_form()
        
        # Bind Enter key to authenticate with visual feedback
        self.parent.bind("<Return>", lambda event: self._on_enter_key_press())
        
    def _clear_widgets(self):
        """Clear any existing widgets from parent."""
        for widget in self.parent.winfo_children():
            widget.destroy()
    
    def _build_login_form(self):
        """Build the complete login form with all components."""
        # Create main form container
        self.login_form = LoginForm(self.parent)
        container = self.login_form.create()
        
        # Create header (logo and subtitle)
        LoginHeader.create(container)
        
        # Create role selector
        self.role_selector = RoleSelector(container)
        self.role_selector.create()
        
        # Create input fields
        self.input_fields = InputFields(container)
        self.input_fields.create()
        
        # Create sign-in button
        self.signin_button = SignInButton(container, self._authenticate)
        self.signin_button.create()
        
    def _on_enter_key_press(self):
        """Handle Enter key press with visual button feedback."""
        # Trigger button press animation with authentication callback
        if self.signin_button and self.signin_button.button:
            try:
                # Check if button widget still exists
                if self.signin_button.button.winfo_exists():
                    self.signin_button.trigger_press_animation(callback=self._authenticate)
                else:
                    # Button destroyed, just authenticate
                    self._authenticate()
            except tk.TclError:
                # Widget no longer exists, just authenticate
                self._authenticate()
        else:
            # Fallback if button not available
            self._authenticate()
    
    def _authenticate(self):
        """Handle authentication logic."""
        # Check if input fields still exist before trying to get credentials
        if not self.input_fields or not hasattr(self.input_fields, 'email_entry'):
            return
        
        try:
            # Check if widgets still exist
            if not self.input_fields.email_entry.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            # Widgets destroyed, abort authentication
            return
        
        # Get credentials and role
        email, password = self.input_fields.get_credentials()
        role = self.role_selector.role_var.get()
        
        # Attempt authentication (returns tuple: success, error_message)
        success, error_message = AuthHandler.authenticate(email, password, role)
        
        if success:
            # Unbind Enter key before cleanup to prevent double execution
            try:
                self.parent.unbind("<Return>")
            except:
                pass
            
            # Clear the login page
            self._cleanup()
            # Call the success callback
            self.on_login_success(email, role)
        else:
            # Reset button state immediately for failed authentication
            if self.signin_button:
                self.signin_button.reset_to_normal()
            # Show specific error message
            AuthHandler.show_error(error_message)
    
    def _cleanup(self):
        """Clean up login form resources."""
        if self.login_form:
            self.login_form.destroy()
            self.login_form = None
    
    def hide(self):
        """Hide the login page."""
        self._cleanup()
