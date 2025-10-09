"""
Inference Page Module - Camera feeds and inspection controls
"""

from .camera_feed import setup_camera_frames
from .controls import setup_control_buttons
from .threshold_panel import setup_threshold_panel
from .camera_manager import start_camera_feeds
from .inspection_control import start_inspection, stop_inspection, toggle_allow_all_images


def setup_inference_tab(app, parent):
    """
    Setup the inference tab with camera feeds and controls.
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Setup camera feeds
    setup_camera_frames(app, parent)
    
    # Setup control buttons
    setup_control_buttons(app, parent)
    
    # Setup threshold panel
    setup_threshold_panel(app, parent)


__all__ = [
    'setup_camera_frames',
    'setup_control_buttons',
    'setup_threshold_panel',
    'setup_inference_tab',
    'start_camera_feeds',
    'start_inspection',
    'stop_inspection',
    'toggle_allow_all_images'
]
