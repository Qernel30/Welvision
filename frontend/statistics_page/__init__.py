"""
Statistics Page Module - Inspection metrics and defect analysis
"""
import tkinter as tk

from .stat_card import create_stat_label, setup_total_stats
from .defect_breakdown import setup_camera_stats
from .statistics_updater import update_statistics


def setup_statistics_tab(app, parent):
    """
    Setup the statistics tab with inspection metrics.
    
    Args:
        app: Main application instance
        parent: Parent frame (statistics tab)
    """
    # Main statistics container
    stats_container = tk.Frame(parent, bg="#0a2158")
    stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        stats_container, 
        text="Inspection Statistics", 
        font=("Arial", 24, "bold"), 
        fg="white", 
        bg="#0a2158"
    )
    title_label.pack(pady=(0, 30))
    
    # Setup total statistics
    setup_total_stats(app, stats_container)
    
    # Setup camera-specific statistics
    setup_camera_stats(app, stats_container)


__all__ = [
    'create_stat_label',
    'setup_total_stats',
    'setup_camera_stats',
    'setup_statistics_tab',
    'update_statistics'
]
