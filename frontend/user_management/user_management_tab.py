"""
User Management Tab - Main Controller
Handles user CRUD operations and UI coordination
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from .users_table import UsersTable
from .user_details_panel import UserDetailsPanel
from .user_actions import UserActions
from .user_database import UserDatabase


class UserManagementTab:
    """User Management tab for managing user accounts."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the user management tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.users_table = None
        self.user_details_panel = None
        self.user_actions = None
        
        # Database
        self.db = UserDatabase()
    
    def setup(self):
        """Setup the user management tab UI."""
        # Main container - no scrolling, fit to page
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header frame - compact
        header_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        header_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        # Title - smaller font
        title_label = tk.Label(
            header_frame,
            text="👥 User Management System",
            font=("Arial", 24, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle - more compact
        subtitle_label = tk.Label(
            main_container,
            text="Manage user accounts, roles, and passwords",
            font=("Arial", 11),
            fg="#FFD700",  # Gold color
            bg=Colors.PRIMARY_BG
        )
        subtitle_label.pack(padx=20, pady=(2, 5))
        
        # Content frame - maximize space
        content_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 5))
        
        # Left side - User Accounts (Current Users Table)
        left_frame = tk.LabelFrame(
            content_frame,
            text="📋 User Accounts",
            font=("Arial", 13, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Users table
        self.users_table = UsersTable(left_frame, self)
        self.users_table.create()
        
        # Right side - User Details
        right_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(8, 0))
        right_frame.config(width=400)
        right_frame.pack_propagate(False)
        
        # User details panel
        self.user_details_panel = UserDetailsPanel(right_frame, self)
        self.user_details_panel.create()
        
        # Action buttons at bottom - compact
        self.user_actions = UserActions(main_container, self)
        self.user_actions.create()
        
        # Load initial data
        self.refresh_users()
    
    def refresh_users(self):
        """Refresh the users table with latest data from database."""
        if self.users_table:
            self.users_table.load_users()
    
    def populate_user_details(self, user_data):
        """
        Populate user details panel with selected user data.
        
        Args:
            user_data: Dictionary containing user information
        """
        if self.user_details_panel:
            self.user_details_panel.populate(user_data)
    
    def clear_form(self):
        """Clear the user details form."""
        if self.user_details_panel:
            self.user_details_panel.clear()
    
    def add_user(self):
        """Add a new user."""
        # Get form data
        data = self.user_details_panel.get_data()
        
        # Validate inputs
        if not data['employee_id']:
            self.user_actions.show_error("Employee ID is required")
            return
        
        if not data['email']:
            self.user_actions.show_error("Email is required")
            return
        
        if not self.user_actions.validate_email(data['email']):
            self.user_actions.show_error("Invalid email format")
            return
        
        if not data['role']:
            self.user_actions.show_error("Role is required")
            return
        
        if not data['new_password']:
            self.user_actions.show_error("Password is required for new user")
            return
        
        if data['new_password'] != data['confirm_password']:
            self.user_actions.show_error("Passwords do not match")
            return
        
        # Validate password strength
        is_valid, msg = self.user_actions.validate_password(data['new_password'])
        if not is_valid:
            self.user_actions.show_error(msg)
            return
        
        # Confirm action
        if not self.user_actions.confirm_action(
            "Add User",
            f"Add new user with Employee ID: {data['employee_id']}?"
        ):
            return
        
        # Add user to database
        if self.db.connect():
            success, message = self.db.add_user(
                data['employee_id'],
                data['email'],
                data['new_password'],
                data['role'],
                data['is_active']
            )
            self.db.disconnect()
            
            if success:
                self.user_actions.show_success(message)
                self.refresh_users()
                self.clear_form()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
    
    def read_user(self):
        """Read/view selected user details."""
        selected_user = self.users_table.get_selected_user()
        
        if not selected_user:
            self.user_actions.show_warning("Please select a user from the table")
            return
        
        # Populate details panel (already done via selection event)
        # Show info message
        from tkinter import messagebox
        messagebox.showinfo(
            "User Information",
            f"Employee ID: {selected_user['employee_id']}\n"
            f"Email: {selected_user['email']}\n"
            f"Role: {selected_user['role']}\n"
            f"Status: {selected_user['status']}\n"
            f"Failed Attempts: {selected_user.get('failed_attempts', 0)}\n"
            f"Created: {selected_user.get('created_at', 'N/A')}"
        )
    
    def update_user(self):
        """Update selected user."""
        # Get form data
        data = self.user_details_panel.get_data()
        
        if not data['user_id']:
            self.user_actions.show_warning("Please select a user to update")
            return
        
        # Validate inputs
        if not data['employee_id']:
            self.user_actions.show_error("Employee ID is required")
            return
        
        if not data['email']:
            self.user_actions.show_error("Email is required")
            return
        
        if not self.user_actions.validate_email(data['email']):
            self.user_actions.show_error("Invalid email format")
            return
        
        if not data['role']:
            self.user_actions.show_error("Role is required")
            return
        
        # Confirm action
        if not self.user_actions.confirm_action(
            "Update User",
            f"Update user: {data['employee_id']}?"
        ):
            return
        
        # Update user in database
        if self.db.connect():
            success, message = self.db.update_user(
                data['user_id'],
                data['employee_id'],
                data['email'],
                data['role'],
                data['is_active']
            )
            self.db.disconnect()
            
            if success:
                self.user_actions.show_success(message)
                self.refresh_users()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
    
    def delete_user(self):
        """Delete selected user."""
        # Get current user
        data = self.user_details_panel.get_data()
        
        if not data['user_id']:
            self.user_actions.show_warning("Please select a user to delete")
            return
        
        # Prevent deleting current logged-in user
        if data['email'] == self.app.current_user:
            self.user_actions.show_error("Cannot delete currently logged-in user")
            return
        
        # Confirm action
        if not self.user_actions.confirm_action(
            "Delete User",
            f"Are you sure you want to delete user: {data['employee_id']}?\n\n"
            "This action cannot be undone!"
        ):
            return
        
        # Delete user from database
        if self.db.connect():
            success, message = self.db.delete_user(data['user_id'])
            self.db.disconnect()
            
            if success:
                self.user_actions.show_success(message)
                self.refresh_users()
                self.clear_form()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
    
    def change_password(self):
        """Change password for selected user."""
        # Get form data
        data = self.user_details_panel.get_data()
        
        if not data['user_id']:
            self.user_actions.show_warning("Please select a user to change password")
            return
        
        if not data['new_password']:
            self.user_actions.show_error("New password is required")
            return
        
        if data['new_password'] != data['confirm_password']:
            self.user_actions.show_error("Passwords do not match")
            return
        
        # Validate password strength
        is_valid, msg = self.user_actions.validate_password(data['new_password'])
        if not is_valid:
            self.user_actions.show_error(msg)
            return
        
        # Confirm action
        if not self.user_actions.confirm_action(
            "Change Password",
            f"Change password for user: {data['employee_id']}?"
        ):
            return
        
        # Change password in database
        if self.db.connect():
            success, message = self.db.change_password(
                data['user_id'],
                data['new_password']
            )
            self.db.disconnect()
            
            if success:
                self.user_actions.show_success(message)
                # Clear password fields
                self.user_details_panel.new_password_var.set('')
                self.user_details_panel.confirm_password_var.set('')
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
