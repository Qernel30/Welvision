"""
Configuration constants and utility functions for Welvision
"""
import os

# PLC Configuration
PLC_CONFIG = {
    'IP': "172.17.8.17",
    'RACK': 0,
    'SLOT': 1,
    'DB_NUMBER': 86
}

# PLC Sensors and Actions Mapping
# All byte and bool indices for reading sensors and triggering actions
PLC_SENSORS = {
    # Input Sensors (Reading from PLC)
    'SENSORS': {
        'bigface_presence': {'byte': 0, 'bit': 1},
        'bigface': {'byte': 0, 'bit': 2},
        'od': {'byte': 0, 'bit': 0},
        'od_presence': {'byte': 1, 'bit': 4},
        'head_classification_sensor': {'byte': 2, 'bit': 2}
    },
    # Output Actions (Writing to PLC)
    'ACTIONS': {
        'lights': {'byte': 1, 'bit': 6},
        'app_ready': {'byte': 1, 'bit': 7},
        'accept_bigface': {'byte': 1, 'bit': 0},
        'reject_bigface': {'byte': 1, 'bit': 1},
        'accept_od': {'byte': 1, 'bit': 2},
        'reject_od': {'byte': 1, 'bit': 3}
    }
}

# Camera Configuration
CAMERA_CONFIG = {
    'BIGFACE_NAME': "DFK 33GP1300e [BF]",
    'OD_NAME': "DFK 33GP1300e [OD]",
    'FRAME_WIDTH': 1280,
    'FRAME_HEIGHT': 960,
    'FRAME_SHAPE': (960, 1280, 3)
}

# Warmup Images
WARMUP_IMAGES = {
    'BIGFACE': r"assets\images\Warmup BF.jpg",
    'OD': r"assets\images\Warmup OD.jpg"
}

# Image Storage Paths - Dynamic Desktop paths
def get_desktop_path():
    """Get the Desktop path for the current user"""
    return os.path.join(os.path.expanduser('~'), 'Desktop')

DESKTOP_PATH = get_desktop_path()

# Image Storage Configuration
IMAGE_STORAGE_PATHS = {
    'INFERENCE': {
        'BF': {
            'DEFECT': os.path.join(DESKTOP_PATH, 'Inference', 'BF', 'Defect'),
            'HEAD_DEFECT': os.path.join(DESKTOP_PATH, 'Inference', 'BF', 'Head_Defect')
        },
        'OD': {
            'DEFECT': os.path.join(DESKTOP_PATH, 'Inference', 'OD', 'Defect')
        }
    },
    'ALL_FRAMES': {
        'BF': {
            'ALL_BF': os.path.join(DESKTOP_PATH, 'All Frames', 'BF', 'All_BF'),
            'ALL_HEAD': os.path.join(DESKTOP_PATH, 'All Frames', 'BF', 'All_Head')
        },
        'OD': {
            'ALL_OD': os.path.join(DESKTOP_PATH, 'All Frames', 'OD', 'All_OD')
        }
    }
}

# Image Management Configuration
IMAGE_LIMIT_PER_DIRECTORY = 10000

# Default Model Confidence Thresholds
DEFAULT_CONFIDENCE = {
    'OD': 0.2,
    'BIGFACE': 0.2
}

# Defect Thresholds (placeholder - can be customized)
DEFECT_THRESHOLDS = {
    'OD': {},
    'BIGFACE': {}
}

# UI Colors
UI_COLORS = {
    'PRIMARY_BG': "#0a2158",
    'SECONDARY_BG': "#1a3168",
    'SUCCESS': "#28a745",
    'DANGER': "#dc3545",
    'PRIMARY': "#007bff",
    'WHITE': "white",
    'BLACK': "black",
    'NAVBAR_ACTIVE': "#28a745",  # Green for active tab
    'NAVBAR_EXIT': "#dc3545"     # Red for EXIT button
}
