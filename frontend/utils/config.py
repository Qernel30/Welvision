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
    
    # PLC settings
    PLC_IP = "172.17.8.17"
    PLC_RACK = 0
    PLC_SLOT = 1
    PLC_DB_NUMBER = 86
    
    # Database settings
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "root"
    DB_DATABASE = "welvision_db"
    
    # Camera resolution
    CAMERA_FRAME_WIDTH = 1280
    CAMERA_FRAME_HEIGHT = 960
    
    # Warmup images
    WARMUP_BF = r"Warmup BF.jpg"
    WARMUP_OD = r"Warmup OD.jpg"
