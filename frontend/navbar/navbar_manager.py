"""
Navbar Manager Module - Navigation bar logic and tab switching
"""
import tkinter as tk
import tkinter.messagebox as messagebox
from config import UI_COLORS


def switch_tab(app, tab_name):
    """
    Switch to a different tab
    
    Args:
        app: Main application instance
        tab_name: Name of the tab to switch to
    """
    # Handle EXIT button
    if tab_name == "EXIT":
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            app.on_closing()
        return
    
    # Stop camera feeds if leaving inference tab
    if hasattr(app, 'current_tab') and app.current_tab == "INFERENCE" and tab_name != "INFERENCE":
        from ..inference_page import stop_camera_feeds
        stop_camera_feeds(app)
    
    # Update current tab
    app.current_tab = tab_name
    
    # Update navbar button colors
    update_navbar_colors(app)
    
    # Clear content frame
    for widget in app.content_frame.winfo_children():
        widget.destroy()
    
    # Load the appropriate tab content
    _load_tab_content(app, tab_name)


def update_navbar_colors(app):
    """
    Update navbar button colors based on active tab
    
    Args:
        app: Main application instance
    """
    for section_name, button in app.navbar_buttons.items():
        if section_name == "EXIT":
            # EXIT button stays red
            button.config(bg=UI_COLORS['NAVBAR_EXIT'])
        elif section_name == app.current_tab:
            # Active tab is green
            button.config(bg=UI_COLORS['NAVBAR_ACTIVE'])
        else:
            # Inactive tabs are blue
            button.config(bg=UI_COLORS['PRIMARY'])


def _load_tab_content(app, tab_name):
    """
    Load content for the specified tab
    
    Args:
        app: Main application instance
        tab_name: Name of the tab to load
    """
    # Import tab setup functions
    from ..inference_page import setup_inference_tab, start_camera_feeds
    from ..statistics_page import setup_statistics_tab, update_statistics
    from ..settings_page import setup_settings_tab
    from ..data_page import setup_data_tab
    from ..diagnosis_page import setup_diagnosis_tab
    from ..model_management_page import setup_model_management_tab
    from ..user_management_page import setup_user_management_tab
    from ..system_check_page import setup_system_check_tab
    from ..info_page import setup_info_tab
    
    # Create tab frame
    tab_frame = tk.Frame(app.content_frame, bg=UI_COLORS['PRIMARY_BG'])
    tab_frame.pack(fill=tk.BOTH, expand=True)
    
    # Load appropriate tab content
    if tab_name == "INFERENCE":
        setup_inference_tab(app, tab_frame)
        start_camera_feeds(app)
        update_statistics(app)
    elif tab_name == "DATA":
        setup_data_tab(app, tab_frame)
    elif tab_name == "DIAGNOSIS":
        setup_diagnosis_tab(app, tab_frame)
    elif tab_name == "SETTINGS":
        setup_settings_tab(app, tab_frame)
    elif tab_name == "MODEL MANAGEMENT":
        setup_model_management_tab(app, tab_frame)
    elif tab_name == "USER MANAGEMENT":
        setup_user_management_tab(app, tab_frame)
    elif tab_name == "SYSTEM CHECK":
        setup_system_check_tab(app, tab_frame)
    elif tab_name == "INFO":
        setup_info_tab(app, tab_frame)
