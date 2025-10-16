"""
Inference tab module.
Contains modularized components for real-time inspection display.
"""

from .inference_tab import InferenceTab
from .status_panel import StatusPanel
from .camera_feed import CameraFeed, CameraFeedManager
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .roller_info_panel import RollerInfoPanel
from .threshold_panel import ThresholdPanel
from .state_manager import InspectionStateManager

__all__ = [
    'InferenceTab',
    'StatusPanel',
    'CameraFeed',
    'CameraFeedManager',
    'ControlPanel',
    'ResultsPanel',
    'RollerInfoPanel',
    'ThresholdPanel',
    'InspectionStateManager'
]
