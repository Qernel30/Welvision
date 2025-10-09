"""
Login UI Module - Authentication interface components
"""
import tkinter as tk
import tkinter.messagebox as messagebox
from config import UI_COLORS
from .credentials import users


def setup_login_page(app):
    """
    Display the login page.
    
    Args:
        app: Main application instance (WelVisionApp)
    """
    # Clear any existing widgets
    for widget in app.winfo_children():
        widget.destroy()
    
    # Create login frame with black background
    login_frame = tk.Frame(app, bg=UI_COLORS['BLACK'], width=500, height=600)
    login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Logo
    logo_label = tk.Label(login_frame, text="WELVISION", font=("Arial", 32, "bold"), 
                         fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
    logo_label.pack(pady=(0, 20))
    
    # Subtitle
    subtitle_label = tk.Label(login_frame, text="Please sign in to continue", font=("Arial", 14), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
    subtitle_label.pack(pady=(0, 30))
    
    # Role selection
    role_frame = tk.Frame(login_frame, bg=UI_COLORS['BLACK'])
    role_frame.pack(pady=(0, 20))
    
    app.role_var = tk.StringVar(value="User")
    
    user_rb = tk.Radiobutton(role_frame, text="User", variable=app.role_var, value="User", 
                            font=("Arial", 12), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                            selectcolor=UI_COLORS['BLACK'])
    admin_rb = tk.Radiobutton(role_frame, text="Admin", variable=app.role_var, value="Admin", 
                             font=("Arial", 12), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                             selectcolor=UI_COLORS['BLACK'])
    super_admin_rb = tk.Radiobutton(role_frame, text="Super Admin", variable=app.role_var, 
                                   value="Super Admin", font=("Arial", 12), fg=UI_COLORS['WHITE'], 
                                   bg=UI_COLORS['BLACK'], selectcolor=UI_COLORS['BLACK'])
    
    user_rb.pack(side=tk.LEFT, padx=10)
    admin_rb.pack(side=tk.LEFT, padx=10)
    super_admin_rb.pack(side=tk.LEFT, padx=10)
    
    # Email
    email_label = tk.Label(login_frame, text="Email", font=("Arial", 12), 
                          fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
    email_label.pack(fill="x", pady=(0, 5))
    
    app.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=40)
    app.email_entry.pack(pady=(0, 15), ipady=8)
    
    # Password
    password_label = tk.Label(login_frame, text="Password", font=("Arial", 12), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
    password_label.pack(fill="x", pady=(0, 5))
    
    app.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=40, show="*")
    app.password_entry.pack(pady=(0, 30), ipady=8)
    
    # Sign in button
    sign_in_button = tk.Button(login_frame, text="Sign In", font=("Arial", 12, "bold"), 
                              bg=UI_COLORS['PRIMARY'], fg=UI_COLORS['WHITE'], width=20, height=2, 
                              command=lambda: authenticate_user(app))
    sign_in_button.pack(pady=10)
    
    # Bind Enter key to authenticate
    app.bind("<Return>", lambda event: authenticate_user(app))


def authenticate_user(app):
    """
    Authenticate user credentials and proceed to main interface.
    
    Args:
        app: Main application instance (WelVisionApp)
    """
    email = app.email_entry.get().strip()
    password = app.password_entry.get().strip()
    role = app.role_var.get()
    
    if email in users and users[email]["password"] == password and users[email]["role"] == role:
        app.current_user = email
        app.current_role = role
        app.show_main_interface()
    else:
        messagebox.showerror("Login Failed", "Invalid email, password, or role.")
