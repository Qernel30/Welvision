"""
User Details Panel
Shows and edits details of selected user
"""

import tkinter as tk
from tkinter import ttk
from ..utils.styles import Colors, Fonts


class UserDetailsPanel:
    """Panel for displaying and editing user details."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize user details panel.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to UserManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
        # Input variables
        self.employee_id_var = None
        self.email_var = None
        self.role_var = None
        self.status_var = None
        
        # Widget references
        self.employee_id_entry = None
        self.email_entry = None
        self.role_combo = None
        self.active_radio = None
        self.inactive_radio = None
        
        # Current user data
        self.current_user_id = None
    
    def create(self):
        """Create the user details panel UI."""
        # Main frame - compact
        details_frame = tk.LabelFrame(
            self.parent,
            text="👤 User Details",
            font=("Arial", 13, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Direct frame - no scrolling needed
        scrollable_frame = tk.Frame(details_frame, bg=Colors.PRIMARY_BG)
        scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Employee ID
        self._create_field(
            scrollable_frame,
            "👤 Employee ID:",
            "employee_id"
        )
        
        # Email Address
        self._create_field(
            scrollable_frame,
            "📧 Email Address:",
            "email"
        )
        
        # Role
        self._create_role_field(scrollable_frame)
        
        # Password Section
        self._create_password_section(scrollable_frame)
        
        # Account Status
        self._create_status_section(scrollable_frame)
    
    def _create_field(self, parent, label_text, field_name):
        """Create a standard input field."""
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        label.pack(anchor=tk.W, pady=(0, 2))
        
        var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=("Arial", 10),
            bg=Colors.WHITE,
            fg=Colors.BLACK,
            width=35
        )
        entry.pack(fill=tk.X)
        
        # Store references
        if field_name == "employee_id":
            self.employee_id_var = var
            self.employee_id_entry = entry
        elif field_name == "email":
            self.email_var = var
            self.email_entry = entry
    
    def _create_role_field(self, parent):
        """Create role selection dropdown."""
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text="🔑 Role:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        label.pack(anchor=tk.W, pady=(0, 2))
        
        self.role_var = tk.StringVar()
        
        style = ttk.Style()
        style.configure("UserRole.TCombobox", fieldbackground=Colors.WHITE)
        
        self.role_combo = ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=["Admin", "Super Admin", "Operator"],
            state="readonly",
            font=("Arial", 10),
            style="UserRole.TCombobox",
            width=32
        )
        self.role_combo.pack(fill=tk.X)
    
    def _create_password_section(self, parent):
        """Create password change section."""
        frame = tk.LabelFrame(
            parent,
            text="🔐 Password",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1,
            relief=tk.GROOVE
        )
        frame.pack(fill=tk.X, padx=10, pady=8)
        
        # New Password
        pwd_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        pwd_frame.pack(fill=tk.X, padx=10, pady=(5, 3))
        
        pwd_label = tk.Label(
            pwd_frame,
            text="New Password:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        pwd_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.new_password_var = tk.StringVar()
        self.new_password_entry = tk.Entry(
            pwd_frame,
            textvariable=self.new_password_var,
            font=("Arial", 10),
            bg=Colors.WHITE,
            fg=Colors.BLACK,
            show="*",
            width=30
        )
        self.new_password_entry.pack(fill=tk.X)
        
        # Confirm Password
        confirm_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        confirm_frame.pack(fill=tk.X, padx=10, pady=(3, 5))
        
        confirm_label = tk.Label(
            confirm_frame,
            text="Confirm Password:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        confirm_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(
            confirm_frame,
            textvariable=self.confirm_password_var,
            font=("Arial", 10),
            bg=Colors.WHITE,
            fg=Colors.BLACK,
            show="*",
            width=30
        )
        self.confirm_password_entry.pack(fill=tk.X)
    
    def _create_status_section(self, parent):
        """Create account status radio buttons."""
        frame = tk.LabelFrame(
            parent,
            text="🔘 Account Status",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1,
            relief=tk.GROOVE
        )
        frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.status_var = tk.IntVar(value=1)
        
        radio_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        radio_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.active_radio = tk.Radiobutton(
            radio_frame,
            text="Active",
            variable=self.status_var,
            value=1,
            font=("Arial", 10),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.SUCCESS,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE
        )
        self.active_radio.pack(side=tk.LEFT, padx=8)
        
        self.inactive_radio = tk.Radiobutton(
            radio_frame,
            text="Inactive",
            variable=self.status_var,
            value=0,
            font=("Arial", 10),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.DANGER,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE
        )
        self.inactive_radio.pack(side=tk.LEFT, padx=8)
    
    def populate(self, user_data):
        """
        Populate fields with user data.
        
        Args:
            user_data: Dictionary containing user information
        """
        if not user_data:
            self.clear()
            return
        
        self.current_user_id = user_data.get('id')
        self.employee_id_var.set(user_data.get('employee_id', ''))
        self.email_var.set(user_data.get('email', ''))
        self.role_var.set(user_data.get('role', ''))
        self.status_var.set(1 if user_data.get('is_active') else 0)
        
        # Clear password fields
        self.new_password_var.set('')
        self.confirm_password_var.set('')
    
    def clear(self):
        """Clear all fields."""
        self.current_user_id = None
        self.employee_id_var.set('')
        self.email_var.set('')
        self.role_var.set('')
        self.status_var.set(1)
        self.new_password_var.set('')
        self.confirm_password_var.set('')
    
    def get_data(self):
        """
        Get current form data.
        
        Returns:
            dict: Form data
        """
        return {
            'user_id': self.current_user_id,
            'employee_id': self.employee_id_var.get().strip(),
            'email': self.email_var.get().strip(),
            'role': self.role_var.get(),
            'is_active': bool(self.status_var.get()),
            'new_password': self.new_password_var.get(),
            'confirm_password': self.confirm_password_var.get()
        }
