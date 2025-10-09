"""
Settings Page Module - Model confidence configuration
"""
import tkinter as tk

from .confidence_sliders import setup_confidence_sliders
from .settings_form import setup_save_button
from .settings_utils import save_thresholds, create_slider, update_threshold, update_model_confidence


def setup_settings_tab(app, parent):
    """
    Creates the UI for the settings tab, only adjusting the confidence thresholds
    of the OD and Bigface YOLO models in real-time.
    
    Args:
        app: The main application instance
        parent: The parent frame (settings tab)
    """
    # Main container for settings
    settings_container = tk.Frame(parent, bg="#0a2158")
    settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Settings Title
    title_label = tk.Label(
        settings_container, 
        text="Model Confidence Settings", 
        font=("Arial", 18, "bold"), 
        fg="white", 
        bg="#0a2158"
    )
    title_label.pack(pady=(0, 20))
    
    # Setup confidence sliders
    setup_confidence_sliders(app, settings_container)
    
    # Setup save button
    setup_save_button(app, settings_container)


__all__ = [
    'setup_confidence_sliders',
    'setup_save_button',
    'setup_settings_tab',
    'save_thresholds',
    'create_slider',
    'update_threshold',
    'update_model_confidence'
]
