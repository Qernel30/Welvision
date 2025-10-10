"""
User Management Page Module - User account management
"""
import tkinter as tk
from config import UI_COLORS


def setup_user_management_tab(app, parent):
    """
    Setup the user management tab
    
    Args:
        app: Main application instance
        parent: Parent frame (user management tab)
    """
    # Main container
    container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        container,
        text="USER MANAGEMENT",
        font=("Arial", 24, "bold"),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG']
    )
    title_label.pack(pady=(0, 30))
    
    # Placeholder content
    info_label = tk.Label(
        container,
        text="User management features will be implemented here.\n\n"
             "This section will include:\n"
             "• Add/Remove users\n"
             "• Edit user credentials\n"
             "• Role management (User/Admin/Super Admin)\n"
             "• User activity logs\n"
             "• Password reset options",
        font=("Arial", 14),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG'],
        justify=tk.LEFT
    )
    info_label.pack(pady=20)


__all__ = ['setup_user_management_tab']
