"""
Configuration constants and utility functions for Welvision
"""

# PLC Configuration
PLC_CONFIG = {
    'IP': "172.17.8.17",
    'RACK': 0,
    'SLOT': 1,
    'DB_NUMBER': 86
}

# Camera Configuration
CAMERA_CONFIG = {
    'BIGFACE_INDEX': 0,
    'OD_INDEX': 1,
    'FRAME_WIDTH': 1280,
    'FRAME_HEIGHT': 960,
    'FRAME_SHAPE': (960, 1280, 3)
}

# Model Paths
MODEL_PATHS = {
    'BIGFACE': r"C:\Users\NBC\Desktop\WELVISION-Project\Feb models\model_22_feb.pt",
    'HEAD': r"C:\Users\NBC\Downloads\18 Sep 25 Head Train.pt",
    'OD': r"C:\Users\NBC\Desktop\WELVISION-Project\FEBRUARY-13-ENDGAME\mainsrc\NewModels\march_20.pt"
}

# Warmup Images
WARMUP_IMAGES = {
    'BIGFACE': r"assets\images\Warmup BF.jpg",
    'OD': r"assets\images\Warmup OD.jpg"
}

# Default Confidence Thresholds
DEFAULT_CONFIDENCE = {
    'OD': 0.25,
    'BIGFACE': 0.25
}

# Defect Thresholds
DEFECT_THRESHOLDS = {
    'OD': {
        "Rust": 50,
        "Dent": 50,
        "Spherical Mark": 50,
        "Damage": 50,
        "Flat Line": 50,
        "Damage on End": 50,
        "Roller": 50
    },
    'BIGFACE': {
        "Damage": 50,
        "Rust": 50,
        "Dent": 50,
        "Roller": 50
    }
}

# UI Colors
UI_COLORS = {
    'PRIMARY_BG': "#0a2158",
    'SECONDARY_BG': "#1a3168",
    'SUCCESS': "#28a745",
    'DANGER': "#dc3545",
    'PRIMARY': "#007bff",
    'WHITE': "white",
    'BLACK': "black"
}
