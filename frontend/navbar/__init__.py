"""
Navbar Module - Custom navigation bar with all sections
"""
from .navbar_ui import setup_navbar
from .navbar_manager import switch_tab, update_navbar_colors


__all__ = [
    'setup_navbar',
    'switch_tab',
    'update_navbar_colors'
]
