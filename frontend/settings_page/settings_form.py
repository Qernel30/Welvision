"""
Settings Form Components
"""
import tkinter as tk
from .settings_utils import save_thresholds


def setup_save_button(app, parent):
    """
    Setup save settings button
    
    Args:
        app: Main application instance
        parent: Parent container frame
    """
    # Save button for settings
    save_button = tk.Button(
        parent, 
        text="Save Settings", 
        font=("Arial", 12, "bold"),
        bg="#28a745", 
        fg="white", 
        command=lambda: save_thresholds(app)
    )
    save_button.pack(pady=20)
