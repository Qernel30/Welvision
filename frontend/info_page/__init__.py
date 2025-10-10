"""
Info Page Module - Application information and help
"""
import tkinter as tk
from config import UI_COLORS


def setup_info_tab(app, parent):
    """
    Setup the info tab with application information
    
    Args:
        app: Main application instance
        parent: Parent frame (info tab)
    """
    # Main container
    container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        container,
        text="WELVISION - INFORMATION",
        font=("Arial", 24, "bold"),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG']
    )
    title_label.pack(pady=(0, 30))
    
    # Application info
    info_text = """
    WELVISION - Roller Inspection System
    Version 2.1
    
    © 2025 Welvision Technologies
    
    This application uses AI-powered computer vision to detect 
    defects on roller surfaces in real-time.
    
    Features:
    • Real-time camera inspection
    • YOLO-based defect detection
    • PLC integration
    • Statistics tracking
    • Configurable thresholds
    
    For support, contact: support@welvision.com
    Documentation: www.welvision.com/docs
    """
    
    info_label = tk.Label(
        container,
        text=info_text,
        font=("Arial", 12),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG'],
        justify=tk.LEFT
    )
    info_label.pack(pady=20)


__all__ = ['setup_info_tab']
