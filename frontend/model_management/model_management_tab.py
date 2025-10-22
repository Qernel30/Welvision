"""
Model Management Tab - Main Controller
Handles AI model upload, viewing, and deletion
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from .upload_section import UploadSection
from .models_table import ModelsTable
from .model_actions import ModelActions


class ModelManagementTab:
    """Model Management tab for uploading and managing AI models."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the model management tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.upload_section = None
        self.models_table = None
        self.model_actions = None
        
    def setup(self):
        """Setup the model management tab UI."""
        # Main container
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="AI Model Management",
            font=Fonts.TITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 20))
        
        # Company footer in top right (below logout button area)
        company_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        company_frame.place(relx=1.0, y=10, anchor=tk.NE)
        
        company_label = tk.Label(
            company_frame,
            text="Developed and Maintained by\n© Welvision Pvt Limited",
            font=Fonts.TEXT_BOLD,
            fg="#FFFFFF",
            bg=Colors.PRIMARY_BG,
            justify=tk.RIGHT
        )
        company_label.pack(padx=20)
        
        # Upload section
        self.upload_section = UploadSection(main_container, self)
        self.upload_section.create()
        
        # Loaded models section
        models_frame = tk.LabelFrame(
            main_container,
            text="📦 Loaded Models",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        models_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 10))
        
        # Models table
        self.models_table = ModelsTable(models_frame, self)
        self.models_table.create()
        
        # Model actions
        self.model_actions = ModelActions(main_container, self)
        self.model_actions.create()
        
        # Load initial data
        self.refresh_models()
    
    def refresh_models(self):
        """Refresh the models table with latest data from database."""
        if self.models_table:
            self.models_table.load_models()
    
    def get_selected_model(self):
        """Get the currently selected model from the table."""
        if self.models_table:
            return self.models_table.get_selected_model()
        return None
