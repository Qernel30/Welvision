"""
Diagnosis Page Module - System diagnostics and troubleshooting
"""
import tkinter as tk
from config import UI_COLORS


def setup_diagnosis_tab(app, parent):
    """
    Setup the diagnosis tab with system diagnostics
    
    Args:
        app: Main application instance
        parent: Parent frame (diagnosis tab)
    """
    # Main container
    container = tk.Frame(parent, bg=UI_COLORS['PRIMARY_BG'])
    container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        container,
        text="SYSTEM DIAGNOSIS",
        font=("Arial", 24, "bold"),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG']
    )
    title_label.pack(pady=(0, 30))
    
    # Placeholder content
    info_label = tk.Label(
        container,
        text="System diagnostics features will be implemented here.\n\n"
             "This section will include:\n"
             "• Camera connection status\n"
             "• PLC connection status\n"
             "• Model loading status\n"
             "• System logs and errors\n"
             "• Performance metrics",
        font=("Arial", 14),
        fg=UI_COLORS['WHITE'],
        bg=UI_COLORS['PRIMARY_BG'],
        justify=tk.LEFT
    )
    info_label.pack(pady=20)


__all__ = ['setup_diagnosis_tab']
