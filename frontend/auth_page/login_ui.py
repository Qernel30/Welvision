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
    
    # Create login frame with black background - increased size
    login_frame = tk.Frame(app, bg=UI_COLORS['BLACK'], width=650, height=700)
    login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Logo - increased size
    logo_label = tk.Label(login_frame, text="WELVISION", font=("Arial", 40, "bold"), 
                         fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
    logo_label.pack(pady=(30, 20))
    
    # Subtitle - increased size
    subtitle_label = tk.Label(login_frame, text="Please sign in to continue", font=("Arial", 16), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'])
    subtitle_label.pack(pady=(0, 40))
    
    # Role selection - increased spacing and font
    role_frame = tk.Frame(login_frame, bg=UI_COLORS['BLACK'])
    role_frame.pack(pady=(0, 30))
    
    app.role_var = tk.StringVar(value="User")
    
    user_rb = tk.Radiobutton(role_frame, text="User", variable=app.role_var, value="User", 
                            font=("Arial", 13), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                            selectcolor=UI_COLORS['BLACK'])
    admin_rb = tk.Radiobutton(role_frame, text="Admin", variable=app.role_var, value="Admin", 
                             font=("Arial", 13), fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], 
                             selectcolor=UI_COLORS['BLACK'])
    super_admin_rb = tk.Radiobutton(role_frame, text="Super Admin", variable=app.role_var, 
                                   value="Super Admin", font=("Arial", 13), fg=UI_COLORS['WHITE'], 
                                   bg=UI_COLORS['BLACK'], selectcolor=UI_COLORS['BLACK'])
    
    user_rb.pack(side=tk.LEFT, padx=15)
    admin_rb.pack(side=tk.LEFT, padx=15)
    super_admin_rb.pack(side=tk.LEFT, padx=15)
    
    # Email - increased size
    email_label = tk.Label(login_frame, text="Email", font=("Arial", 13), 
                          fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
    email_label.pack(fill="x", pady=(0, 8))
    
    app.email_entry = tk.Entry(login_frame, font=("Arial", 13), width=45)
    app.email_entry.pack(pady=(0, 20), ipady=10)
    
    # Password - increased size
    password_label = tk.Label(login_frame, text="Password", font=("Arial", 13), 
                             fg=UI_COLORS['WHITE'], bg=UI_COLORS['BLACK'], anchor="w")
    password_label.pack(fill="x", pady=(0, 8))
    
    app.password_entry = tk.Entry(login_frame, font=("Arial", 13), width=45, show="*")
    app.password_entry.pack(pady=(0, 35), ipady=10)
    
    # Sign in button - increased size and stored reference
    app.sign_in_button = tk.Button(login_frame, text="Sign In", font=("Arial", 14, "bold"), 
                              bg=UI_COLORS['PRIMARY'], fg=UI_COLORS['WHITE'], width=22, height=2, 
                              command=lambda: authenticate_user(app))
    app.sign_in_button.pack(pady=15)
    
    # Bind Enter key to authenticate with visual feedback
    def on_enter_press(event):
        # Visual feedback - button press effect (both relief and color change)
        original_bg = app.sign_in_button.cget('bg')
        app.sign_in_button.config(relief=tk.SUNKEN, bg=UI_COLORS['WHITE'], fg=UI_COLORS['PRIMARY'])
        # Delay authentication to show visual effect, then restore button if it still exists
        def authenticate_delayed():
            authenticate_user(app)
            if app.sign_in_button.winfo_exists():
                app.sign_in_button.config(relief=tk.RAISED, bg=original_bg, fg=UI_COLORS['WHITE'])
        app.after(150, authenticate_delayed)
    
    app.bind("<Return>", on_enter_press)


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
