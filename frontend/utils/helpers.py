"""
Helper functions and utilities for the frontend.
"""

import tkinter as tk
from .styles import Colors, Fonts


def center_window(window, width=1280, height=800):
    """
    Center a window on the screen.
    
    Args:
        window: Tk window instance
        width: Window width
        height: Window height
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_header(parent, title, user_email, user_role, logout_callback):
    """
    Create a header frame with logo and user info.
    
    Args:
        parent: Parent frame
        title: Application title
        user_email: Current user email
        user_role: Current user role
        logout_callback: Function to call on logout
        
    Returns:
        Header frame
    """
    header_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG, height=50)
    header_frame.pack(fill=tk.X)
    
    # Logo in header
    logo_label = tk.Label(
        header_frame, 
        text=title, 
        font=Fonts.SUBTITLE,
        fg=Colors.WHITE, 
        bg=Colors.PRIMARY_BG
    )
    logo_label.pack(side=tk.LEFT, padx=20, pady=5)
    
    # User info and logout on the right
    right_frame = tk.Frame(header_frame, bg=Colors.PRIMARY_BG)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # User info label
    user_label = tk.Label(
        right_frame, 
        text=f"{user_role}: {user_email}",
        font=Fonts.TEXT_BOLD, 
        fg=Colors.WHITE, 
        bg=Colors.PRIMARY_BG
    )
    user_label.pack(side=tk.LEFT, padx=(0, 10))
    
    # Logout button with styling
    logout_button = tk.Button(
        right_frame, 
        text="Logout", 
        font=Fonts.SMALL_BOLD,
        bg=Colors.DANGER,
        fg=Colors.WHITE,
        relief=tk.RAISED,
        bd=2,
        padx=15,
        pady=5,
        cursor="hand2",
        command=logout_callback
    )
    logout_button.pack(side=tk.LEFT)
    
    return header_frame


def configure_notebook_style():
    """Configure ttk Notebook style for tabs."""
    import tkinter.ttk as ttk
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        'TNotebook.Tab', 
        background=Colors.PRIMARY_BG, 
        foreground=Colors.WHITE,
        font=('Arial', 12, 'bold'), 
        padding=[20, 10], 
        borderwidth=0
    )
    style.map(
        'TNotebook.Tab', 
        background=[('selected', Colors.SECONDARY_BG)],
        foreground=[('selected', Colors.WHITE)]
    )
    style.configure('TNotebook', background=Colors.PRIMARY_BG, borderwidth=0)
