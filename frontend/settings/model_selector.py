"""
Model Selector Component for Settings Tab
Allows selection of BF and OD models from database
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig


class ModelSelector:
    """Component for selecting AI models from database."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the model selector.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.selector_frame = None
        
        # Model dropdowns
        self.bf_model_var = tk.StringVar()
        self.od_model_var = tk.StringVar()
        self.bf_model_dropdown = None
        self.od_model_dropdown = None
        
        # Model data
        self.bf_models = []
        self.od_models = []
        self.bf_model_paths = {}  # {model_name: model_path}
        self.od_model_paths = {}  # {model_name: model_path}
        
    def create(self):
        """Create the model selector UI."""
        self.selector_frame = tk.LabelFrame(
            self.parent,
            text="🤖 Model Selection for Inspection",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        self.selector_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Main content frame with reduced padding
        content_frame = tk.Frame(self.selector_frame, bg=Colors.PRIMARY_BG)
        content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # BF Model Selection (more compact)
        bf_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
        bf_frame.pack(fill=tk.X, pady=3)
        
        bf_label = tk.Label(
            bf_frame,
            text="BF Model:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=12,
            anchor="w"
        )
        bf_label.pack(side=tk.LEFT, padx=5)
        
        self.bf_model_dropdown = ttk.Combobox(
            bf_frame,
            textvariable=self.bf_model_var,
            font=Fonts.SMALL,
            state="readonly",
            width=35
        )
        self.bf_model_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.bf_model_dropdown.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        # OD Model Selection (more compact)
        od_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
        od_frame.pack(fill=tk.X, pady=3)
        
        od_label = tk.Label(
            od_frame,
            text="OD Model:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=12,
            anchor="w"
        )
        od_label.pack(side=tk.LEFT, padx=5)
        
        self.od_model_dropdown = ttk.Combobox(
            od_frame,
            textvariable=self.od_model_var,
            font=Fonts.SMALL,
            state="readonly",
            width=35
        )
        self.od_model_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.od_model_dropdown.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        # Refresh button (smaller)
        button_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
        button_frame.pack(fill=tk.X, pady=3)
        
        # Refresh button (smaller)
        button_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
        button_frame.pack(fill=tk.X, pady=3)
        
        refresh_button = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=Fonts.SMALL,
            bg="#17a2b8",
            fg=Colors.WHITE,
            width=12,
            command=self.load_models_from_db
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Load models on creation
        self.load_models_from_db()
        
        return self.selector_frame
    
    def load_models_from_db(self):
        """Load available models from database and preserve current selection."""
        try:
            # Save current selections
            current_bf_selection = self.bf_model_var.get()
            current_od_selection = self.od_model_var.get()
            
            # Connect to database
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                port=AppConfig.DB_PORT,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            
            # Load BF models (ordered by upload_date DESC, so latest is first)
            cursor.execute("SELECT model_name, model_path FROM bf_models ORDER BY upload_date DESC")
            bf_results = cursor.fetchall()
            self.bf_models = [row[0] for row in bf_results]
            self.bf_model_paths = {row[0]: row[1] for row in bf_results}
            
            # Load OD models (ordered by upload_date DESC, so latest is first)
            cursor.execute("SELECT model_name, model_path FROM od_models ORDER BY upload_date DESC")
            od_results = cursor.fetchall()
            self.od_models = [row[0] for row in od_results]
            self.od_model_paths = {row[0]: row[1] for row in od_results}
            
            cursor.close()
            connection.close()
            
            # Update dropdowns
            if self.bf_model_dropdown:
                self.bf_model_dropdown['values'] = self.bf_models
                # Restore previous selection if it still exists, otherwise use app's selected model or first
                if current_bf_selection and current_bf_selection in self.bf_models:
                    self.bf_model_var.set(current_bf_selection)
                elif hasattr(self.app, 'selected_bf_model_name') and self.app.selected_bf_model_name in self.bf_models:
                    self.bf_model_var.set(self.app.selected_bf_model_name)
                elif self.bf_models:
                    self.bf_model_var.set(self.bf_models[0])
            
            if self.od_model_dropdown:
                self.od_model_dropdown['values'] = self.od_models
                # Restore previous selection if it still exists, otherwise use app's selected model or first
                if current_od_selection and current_od_selection in self.od_models:
                    self.od_model_var.set(current_od_selection)
                elif hasattr(self.app, 'selected_od_model_name') and self.app.selected_od_model_name in self.od_models:
                    self.od_model_var.set(self.app.selected_od_model_name)
                elif self.od_models:
                    self.od_model_var.set(self.od_models[0])
            
            # Auto-save selected models to app on load
            self._save_selected_models_to_app()
                        
        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")
            messagebox.showerror("Database Error", f"Failed to load models from database:\n{str(e)}")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            messagebox.showerror("Error", f"Failed to load models:\n{str(e)}")
    
    def get_selected_bf_model_path(self):
        """Get the file path of the selected BF model."""
        model_name = self.bf_model_var.get()
        return self.bf_model_paths.get(model_name)
    
    def get_selected_od_model_path(self):
        """Get the file path of the selected OD model."""
        model_name = self.od_model_var.get()
        return self.od_model_paths.get(model_name)
    
    def get_selected_models(self):
        """Get both selected model paths."""
        return {
            'bf_model_path': self.get_selected_bf_model_path(),
            'od_model_path': self.get_selected_od_model_path(),
            'bf_model_name': self.bf_model_var.get(),
            'od_model_name': self.od_model_var.get()
        }
    
    def _on_model_selected(self, event=None):
        """Handle model selection change and reload defect thresholds."""
        # Save selected models to app
        self._save_selected_models_to_app()
        
        # Get selected model names
        bf_model_name = self.bf_model_var.get()
        od_model_name = self.od_model_var.get()
        
        # Reload defect thresholds immediately for the newly selected models
        if hasattr(self.app, 'settings_tab') and self.app.settings_tab:
            # Use the reload method to recreate threshold sliders with new model classes
            self.app.settings_tab.reload_defect_thresholds_for_selected_models()
                
    def _save_selected_models_to_app(self):
        """Save selected models to app instance for use in inspection."""
        if hasattr(self.app, 'selected_bf_model_path'):
            self.app.selected_bf_model_path = self.get_selected_bf_model_path()
            self.app.selected_bf_model_name = self.bf_model_var.get()
            self.app.selected_od_model_path = self.get_selected_od_model_path()
            self.app.selected_od_model_name = self.od_model_var.get()
        else:
            # Initialize if not exists
            self.app.selected_bf_model_path = self.get_selected_bf_model_path()
            self.app.selected_bf_model_name = self.bf_model_var.get()
            self.app.selected_od_model_path = self.get_selected_od_model_path()
            self.app.selected_od_model_name = self.od_model_var.get()
