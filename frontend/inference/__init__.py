"""
Inference tab module.
"""

from .inference_tab import InferenceTab
from .camera_feed import CameraFeed, CameraFeedManager
from .control_panel import ControlPanel
from .threshold_panel import ThresholdPanel

__all__ = [
    'InferenceTab',
    'CameraFeed',
    'CameraFeedManager',
    'ControlPanel',
    'ThresholdPanel'
]
