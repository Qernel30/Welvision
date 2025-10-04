"""
Welvision Roller Inspection System - Main Entry Point
Main application launcher for the Welvision GUI
"""

from frontend import WelVisionApp


if __name__ == "__main__":
    app = WelVisionApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
