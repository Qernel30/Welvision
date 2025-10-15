"""
Window Configuration Module
Handles window startup configuration
"""


class WindowConfig:
    """Window configuration for maximized and focused startup."""
    
    @staticmethod
    def configure(window):
        """
        Configure the window for optimal display.
        
        Args:
            window: Tk window instance to configure
        """
        # Make window come to front and get focus
        window.lift()
        window.focus_force()
        
        # Start maximized
        window.state('zoomed')  # For Windows
