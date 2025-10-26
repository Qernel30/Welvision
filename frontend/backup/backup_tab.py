"""
Backup Tab - Main Controller
Image Backup Management
Admin and Super Admin only
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from .image_backup import ImageBackupManager


class BackupTab:
    """Backup tab for image backup operations."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the backup tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Component manager
        self.image_manager = None
        
    def setup(self):
        """Setup the backup tab UI."""
        # Main container - Full width and height, no scrolling
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Image Backup Management",
            font=Fonts.TITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_container,
            text="Copy Inference Images to External Device",
            font=Fonts.TEXT,
            fg="#AAAAAA",
            bg=Colors.PRIMARY_BG
        )
        subtitle_label.pack(pady=(0, 15))
        
        # ============= IMAGE BACKUP SECTION =============
        image_section_frame = tk.LabelFrame(
            main_container,
            text="🖼️ Inference Images Backup",
            font=Fonts.SUBTITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=3,
            relief=tk.RIDGE,
            padx=20,
            pady=15
        )
        image_section_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create image backup manager and UI
        self.image_manager = ImageBackupManager(self.parent)
        self.image_manager.create_ui(image_section_frame)
