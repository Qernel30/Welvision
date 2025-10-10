"""
Inference Page Module - Camera feeds and inspection controls
No threshold adjustment in inference page - moved to settings
"""

from .top_panel import setup_top_panel, update_confidence_display, update_model_status, update_disc_status
from .camera_feed import setup_camera_frames
from .status_indicators import create_status_indicator, update_status_indicator
from .results_display import setup_results_panel, update_bf_results, update_od_results, update_overall_results
from .controls import setup_control_buttons
from .camera_manager import start_camera_feeds, stop_camera_feeds
from .inspection_control import start_inspection, stop_inspection, toggle_allow_all_images


def setup_inference_tab(app, parent):
    """
    Setup the inference tab with all components.
    No threshold adjustment here - that's in settings tab.
    
    Args:
        app: Main application instance
        parent: Parent frame (inference tab)
    """
    # Setup top panel (Roller type, Date/Time, Mode, Status, Confidence, AI Models)
    setup_top_panel(app, parent)
    
    # Setup camera feeds with status indicators and right panel (Roller Info only)
    setup_camera_frames(app, parent)
    
    # Setup results panel at bottom (BF Result, OD Result, Overall Result - 3 columns)
    setup_results_panel(app, parent)
    
    # Setup control buttons at bottom (Start, Stop, Reset, Allow all images)
    setup_control_buttons(app, parent)


__all__ = [
    'setup_top_panel',
    'update_confidence_display',
    'update_model_status',
    'update_disc_status',
    'setup_camera_frames',
    'create_status_indicator',
    'update_status_indicator',
    'setup_results_panel',
    'update_bf_results',
    'update_od_results',
    'update_overall_results',
    'setup_control_buttons',
    'setup_inference_tab',
    'start_camera_feeds',
    'stop_camera_feeds',
    'start_inspection',
    'stop_inspection',
    'toggle_allow_all_images'
]
