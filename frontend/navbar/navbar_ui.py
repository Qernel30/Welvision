"""
Navbar UI Module - Navigation bar UI components
"""
import tkinter as tk
from config import UI_COLORS


def setup_navbar(app, parent):
    """
    Setup the navigation bar with all sections
    
    Args:
        app: Main application instance
        parent: Parent frame (main frame)
        
    Returns:
        content_frame: The frame where tab content will be displayed
    """
    # Create navbar frame - increased height for better visibility
    navbar_frame = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'], height=40)
    navbar_frame.pack(fill=tk.X, padx=0, pady=0)
    navbar_frame.pack_propagate(False)
    
    # Store navbar buttons in app for later color updates
    app.navbar_buttons = {}
    app.current_tab = "INFERENCE"
    
    # All sections in order
    all_sections = [
        {"name": "INFERENCE", "text": "INFERENCE"},
        {"name": "DATA", "text": "DATA"},
        {"name": "DIAGNOSIS", "text": "DIAGNOSIS"},
        {"name": "SETTINGS", "text": "SETTINGS"},
        {"name": "MODEL MANAGEMENT", "text": "MODEL MANAGEMENT"},
        {"name": "USER MANAGEMENT", "text": "USER MANAGEMENT"},
        {"name": "SYSTEM CHECK", "text": "SYSTEM CHECK"},
        {"name": "INFO", "text": "INFO"},
        {"name": "EXIT", "text": "EXIT"}
    ]
    
    # Create content frame below navbar
    content_frame = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Store content frame reference
    app.content_frame = content_frame
    
    # Create all buttons in sequence from left to right
    for section in all_sections:
        _create_navbar_button(app, navbar_frame, section)
    
    return content_frame


def _create_navbar_button(app, parent, section):
    """
    Create a single navbar button
    
    Args:
        app: Main application instance
        parent: Parent frame (navbar frame)
        section: Dictionary with section name and text
    """
    from .navbar_manager import switch_tab
    
    section_name = section["name"]
    section_text = section["text"]
    
    # Determine button color based on section type
    if section_name == "EXIT":
        bg_color = UI_COLORS['NAVBAR_EXIT']
        active_color = "#cc0000"  # Darker red on hover
    elif section_name == app.current_tab:
        bg_color = UI_COLORS['NAVBAR_ACTIVE']
        active_color = "#1ea84c"  # Darker green on hover
    else:
        bg_color = UI_COLORS['PRIMARY']
        active_color = UI_COLORS['SECONDARY_BG']
    
    # Create button with increased height and padding
    button = tk.Button(
        parent,
        text=section_text,
        font=("Arial", 10, "bold"),  # Increased font size
        bg=bg_color,
        fg=UI_COLORS['WHITE'],
        activebackground=active_color,
        activeforeground=UI_COLORS['WHITE'],
        relief=tk.FLAT,
        cursor="hand2",
        bd=0,
        padx=30,  # Internal horizontal padding for button width
        pady=8,   # Internal vertical padding for button height
        command=lambda: switch_tab(app, section_name)
    )
    
    # Pack all buttons from left to right with tiny gap
    button.pack(side=tk.LEFT, padx=3, pady=3)
    
    # Store button reference
    app.navbar_buttons[section_name] = button
