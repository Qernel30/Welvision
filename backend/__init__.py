"""
Backend package for Welvision Roller Inspection System
"""

from .plc_communication import plc_communication, trigger_plc_action
from .frame_capture import capture_frames_bigface, capture_frames_od
from .yolo_processing import process_rollers_bigface, process_frames_od
from .slot_control import handle_slot_control_bigface, handle_slot_control_od
from .camera_detector import get_camera_index_by_name, list_available_cameras, get_camera_indices_from_config
from .image_manager import (
    save_defect_image,
    save_all_frames_image,
    initialize_storage_directories,
    ensure_directory_exists,
    cleanup_old_images
)

__all__ = [
    'plc_communication',
    'trigger_plc_action',
    'capture_frames_bigface',
    'capture_frames_od',
    'process_rollers_bigface',
    'process_frames_od',
    'handle_slot_control_bigface',
    'handle_slot_control_od',
    'get_camera_index_by_name',
    'list_available_cameras',
    'get_camera_indices_from_config',
    'save_defect_image',
    'save_all_frames_image',
    'initialize_storage_directories',
    'ensure_directory_exists',
    'cleanup_old_images'
]
