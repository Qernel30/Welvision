"""
Login Page UI Component
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.auth import authenticate_user


class LoginPage:
    """Login page for user authentication."""
    
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
        self.frame = None
        
    def show(self):
        """Display the login page."""
        # Clear any existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create login frame with black background
        self.frame = tk.Frame(self.parent, bg=Colors.BLACK, width=500, height=600)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Logo
        logo_label = tk.Label(
            self.frame, 
            text="WELVISION", 
            font=Fonts.TITLE, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK
        )
        logo_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            self.frame, 
            text="Please sign in to continue", 
            font=Fonts.LABEL, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Role selection
        role_frame = tk.Frame(self.frame, bg=Colors.BLACK)
        role_frame.pack(pady=(0, 20))
        
        self.role_var = tk.StringVar(value="User")
        
        user_rb = tk.Radiobutton(
            role_frame, 
            text="User", 
            variable=self.role_var, 
            value="User",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            selectcolor=Colors.BLACK
        )
        admin_rb = tk.Radiobutton(
            role_frame, 
            text="Admin", 
            variable=self.role_var, 
            value="Admin",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            selectcolor=Colors.BLACK
        )
        super_admin_rb = tk.Radiobutton(
            role_frame, 
            text="Super Admin", 
            variable=self.role_var, 
            value="Super Admin",
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            selectcolor=Colors.BLACK
        )
        
        user_rb.pack(side=tk.LEFT, padx=10)
        admin_rb.pack(side=tk.LEFT, padx=10)
        super_admin_rb.pack(side=tk.LEFT, padx=10)
        
        # Email
        email_label = tk.Label(
            self.frame, 
            text="Email", 
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            anchor="w"
        )
        email_label.pack(fill="x", pady=(0, 5))
        
        self.email_entry = tk.Entry(self.frame, font=Fonts.TEXT, width=40)
        self.email_entry.pack(pady=(0, 15), ipady=8)
        
        # Password
        password_label = tk.Label(
            self.frame, 
            text="Password", 
            font=Fonts.TEXT, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = tk.Entry(self.frame, font=Fonts.TEXT, width=40, show="*")
        self.password_entry.pack(pady=(0, 30), ipady=8)
        
        # Sign in button
        sign_in_button = tk.Button(
            self.frame, 
            text="Sign In", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.PRIMARY_BLUE, 
            fg=Colors.WHITE, 
            width=20, 
            height=2,
            command=self._authenticate
        )
        sign_in_button.pack(pady=10)
        
        # Bind Enter key to authenticate
        self.parent.bind("<Return>", lambda event: self._authenticate())
        
    def _authenticate(self):
        """Handle authentication logic."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if authenticate_user(email, password, role):
            # Clear the login page
            if self.frame:
                self.frame.destroy()
            # Call the success callback
            self.on_login_success(email, role)
        else:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Login Failed", "Invalid email, password, or role.")
    
    def hide(self):
        """Hide the login page."""
        if self.frame:
            self.frame.destroy()
