"""
Frontend package for Welvision Roller Inspection System
"""

from .app import WelVisionApp
from .auth import users
from .inference_tab import setup_inference_tab
from .statistics_tab import setup_statistics_tab, create_stat_label
from .settings_tab import setup_settings_tab
from .camera_manager import start_camera_feeds, update_od_camera, update_bf_camera

__all__ = [
    'WelVisionApp',
    'users',
    'setup_inference_tab',
    'setup_statistics_tab',
    'create_stat_label',
    'setup_settings_tab',
    'start_camera_feeds',
    'update_od_camera',
    'update_bf_camera'
]
