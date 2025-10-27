"""
User Management Tab - Main Controller
Handles user CRUD operations and UI coordination
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions
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
        This is called when a user is selected from the table.
        
        Args:
            user_data: Dictionary containing user information
        """
        # Don't auto-populate form when user is selected
        # User must click an action button (Read, Update, etc.)
        pass
    
    def clear_form(self):
        """Clear the user details form."""
        if self.user_details_panel:
            self.user_details_panel.hide_form()
    
    def add_user(self):
        """Add a new user (called from button or internally from panel)."""
        # Show the add form if not already shown
        if self.user_details_panel.form_mode != 'add':
            self.user_details_panel.show_add_form()
            return
        
        # Get form data
        data = self.user_details_panel.get_data()
        
        # Get current user role
        current_user_role = getattr(self.app, 'current_role', 'Operator')
        
        # Check if Admin is trying to add Super Admin
        if data['role'] == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
            self.user_actions.show_error(
                "Permission Denied\n\n"
                "Admin users cannot add Super Admin accounts.\n"
                "Only Super Admin can create other Super Admin users."
            )
            return
        
        # Check if trying to add another Super Admin
        if data['role'] == "Super Admin":
            # Count existing Super Admin users
            if self.db.connect():
                super_admin_count = self.db.count_super_admins()
                self.db.disconnect()
                
                if super_admin_count >= 1:
                    self.user_actions.show_error(
                        "Super Admin Limit Reached\n\n"
                        "Only one Super Admin account is allowed in the system.\n"
                        "A Super Admin account already exists."
                    )
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
                self.user_details_panel.hide_form()
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
        
        # Show the read form with user data
        self.user_details_panel.show_read_form(selected_user)
    
    def update_user(self):
        """Update selected user."""
        # If form is not in update mode, show the update form
        if self.user_details_panel.form_mode != 'update':
            selected_user = self.users_table.get_selected_user()
            if not selected_user:
                self.user_actions.show_warning("Please select a user from the table")
                return
            self.user_details_panel.show_update_form(selected_user)
            return
        
        # Get form data
        data = self.user_details_panel.get_data()
        
        if not data['user_id']:
            self.user_actions.show_warning("Please select a user to update")
            return
        
        # Get current user role
        current_user_role = getattr(self.app, 'current_role', 'Operator')
        
        # Get the selected user's original data to check if they're Super Admin
        selected_user = self.users_table.get_selected_user()
        if selected_user:
            original_role = selected_user.get('role', '')
            
            # Check if Admin is trying to modify a Super Admin
            if original_role == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
                self.user_actions.show_error(
                    "Permission Denied\n\n"
                    "Admin users cannot modify Super Admin accounts.\n"
                    "Only Super Admin can update other Super Admin users."
                )
                return
            
            # Check if Admin is trying to change someone to Super Admin
            if data['role'] == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
                self.user_actions.show_error(
                    "Permission Denied\n\n"
                    "Admin users cannot promote users to Super Admin.\n"
                    "Only Super Admin can assign Super Admin role."
                )
                return
            
            # Check if trying to change to Super Admin when one already exists
            if data['role'] == "Super Admin" and original_role != "Super Admin":
                if self.db.connect():
                    super_admin_count = self.db.count_super_admins()
                    self.db.disconnect()
                    
                    if super_admin_count >= 1:
                        self.user_actions.show_error(
                            "Super Admin Limit Reached\n\n"
                            "Only one Super Admin account is allowed in the system.\n"
                            "A Super Admin account already exists."
                        )
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
        
        # Get current user role
        current_user_role = getattr(self.app, 'current_role', 'Operator')
        
        # Get the selected user's data to check if they're Super Admin
        selected_user = self.users_table.get_selected_user()
        if selected_user and selected_user.get('role') == "Super Admin":
            # Check if Admin is trying to delete Super Admin
            if not Permissions.can_manage_super_admin(current_user_role):
                self.user_actions.show_error(
                    "Permission Denied\n\n"
                    "Admin users cannot delete Super Admin accounts.\n"
                    "Only Super Admin can delete other Super Admin users."
                )
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
                self.user_details_panel.hide_form()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
    
    def change_password(self):
        """Change password for selected user."""
        # If form is not in change_password mode, show the password form
        if self.user_details_panel.form_mode != 'change_password':
            selected_user = self.users_table.get_selected_user()
            if not selected_user:
                self.user_actions.show_warning("Please select a user to change password")
                return
            self.user_details_panel.show_password_form(selected_user)
            return
        
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
        
        # Check if new password is same as current password
        if hasattr(self.user_details_panel, 'current_password_hash') and hasattr(self.user_details_panel, 'current_salt'):
            import hashlib
            # Hash new password with the same salt
            new_password_salt = (data['new_password'] + self.user_details_panel.current_salt).encode('utf-8')
            new_password_hash = hashlib.sha256(new_password_salt).hexdigest()
            
            if new_password_hash == self.user_details_panel.current_password_hash:
                self.user_actions.show_error("New password cannot be the same as current password")
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
                self.user_details_panel.hide_form()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
