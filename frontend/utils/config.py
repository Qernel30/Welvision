"""
Application Configuration
"""


class AppConfig:
    """Application configuration constants."""
    
    # Window settings
    WINDOW_WIDTH = 1366
    WINDOW_HEIGHT = 768
    WINDOW_TITLE = "WELVISION"
    
    # Camera settings
    CAMERA_WIDTH = 580
    CAMERA_HEIGHT = 380
    FRAME_UPDATE_RATE = 0.03  # 30ms = ~33 FPS
    
    # PLC settings
    PLC_IP = "172.17.8.17"
    PLC_RACK = 0
    PLC_SLOT = 1
    PLC_DB_NUMBER = 86
    
    # Camera resolution
    CAMERA_FRAME_WIDTH = 1280
    CAMERA_FRAME_HEIGHT = 960
    
    # Model paths
    MODEL_BF_SR = r".\models\BF_sr.pt"
    MODEL_BF_HEAD = r".\models\BF_head.pt"
    MODEL_OD_SR = r".\models\OD_sr.pt"
    
    # Warmup images
    WARMUP_BF = r"Warmup BF.jpg"
    WARMUP_OD = r"Warmup OD.jpg"
    
    
    # Captured frames directories
    DIR_BIGFACE_FRAMES = "captured_bigface_frames"
    DIR_HEAD_FRAMES = "captured_head_frames"
    DIR_OD_FRAMES = "captured_od_frames"
    
    # Default confidence thresholds
    DEFAULT_OD_CONFIDENCE = 0.25
    DEFAULT_BF_CONFIDENCE = 0.25
    
    # Defect thresholds
    OD_DEFECT_THRESHOLDS = {
        "Rust": 50,
        "Dent": 50,
        "Spherical Mark": 50,
        "Damage": 50,
        "Flat Line": 50,
        "Damage on End": 50,
        "Roller": 50
    }
    
    BF_DEFECT_THRESHOLDS = {
        "Damage": 50,
        "Rust": 50,
        "Dent": 50,
        "Roller": 50
    }
