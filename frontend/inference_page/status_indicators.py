"""
Status Indicators Module - Shows "Not Ready" indicators for camera feeds
"""
import tkinter as tk
from config import UI_COLORS


def create_status_indicator(parent, text="● Not Ready"):
    """
    Create a status indicator button (boxed style like reference image)
    
    Args:
        parent: Parent frame
        text: Text to display (default: "● Not Ready")
        
    Returns:
        Button widget for the status indicator
    """
    indicator = tk.Button(
        parent,
        text=text,
        font=("Arial", 10, "bold"),
        fg="white",
        bg="#FF0000",  # Red background
        relief=tk.RAISED,
        bd=2,
        state=tk.DISABLED,
        disabledforeground="white"
    )
    return indicator


def update_status_indicator(indicator, ready=False):
    """
    Update status indicator color and text
    
    Args:
        indicator: Button widget to update
        ready: Boolean indicating ready status
    """
    if ready:
        indicator.config(text="● Ready", bg="#00FF00")  # Green background
    else:
        indicator.config(text="● Not Ready", bg="#FF0000")  # Red background
