"""
Info Tab - Main Controller
Manages application settings, system information, and user manual
"""

import tkinter as tk
import tkinter.ttk as ttk
from ..utils.styles import Colors, Fonts
from .title_management import TitleManagement
from .settings_history import SettingsHistory
from .system_information import SystemInformation
from .database_config import DatabaseConfig
from .user_manual import UserManual


class InfoTab:
    """Info tab for application settings and system information."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the info tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.title_management = None
        self.settings_history = None
        self.system_information = None
        self.database_config = None
        self.user_manual = None
        
        # Scrollable canvas and frame
        self.canvas = None
        self.scrollable_frame = None
        self._mousewheel_bound = False
    
    def setup(self):
        """Setup the info tab UI with scrolling support."""
        # Unbind previous mousewheel if it was bound
        if self._mousewheel_bound:
            try:
                self.parent.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        # Create main container
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Application Settings",
            font=Fonts.TITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_container,
            text="Configure application preferences and system settings",
            font=Fonts.TEXT,
            fg="#CCCCCC",
            bg=Colors.PRIMARY_BG
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(main_container, bg=Colors.PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.PRIMARY_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize to update window width
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
        
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        # Enable mouse wheel scrolling with safety check
        def _on_mousewheel(event):
            try:
                if self.canvas and self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas was destroyed, unbind the event
                try:
                    self.parent.unbind_all("<MouseWheel>")
                    self._mousewheel_bound = False
                except:
                    pass
        
        self.parent.bind_all("<MouseWheel>", _on_mousewheel)
        self._mousewheel_bound = True
        
        # ===== PAGE 1: TITLE MANAGEMENT =====
        self.title_management = TitleManagement(self.scrollable_frame, self.app)
        self.title_management.create()
        
        # ===== PAGE 2 SECTIONS =====
        
        # Settings History
        self.settings_history = SettingsHistory(self.scrollable_frame, self.app)
        self.settings_history.create()
        
        # System Information
        self.system_information = SystemInformation(self.scrollable_frame, self.app)
        self.system_information.create()
        
        # Database Configuration
        self.database_config = DatabaseConfig(self.scrollable_frame, self.app)
        self.database_config.create()
        
        # User Manual
        self.user_manual = UserManual(self.scrollable_frame, self.app)
        self.user_manual.create()
        
        # Update canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def cleanup(self):
        """Cleanup method called when tab is destroyed."""
        # Unbind mousewheel event
        if self._mousewheel_bound:
            try:
                self.parent.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
