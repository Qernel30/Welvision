"""
Sign In Button Module
Button component with hover effects and press animations
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class SignInButton:
    """Sign-in button with proper styling, hover effects, and press animations."""
    
    def __init__(self, parent, command):
        """
        Initialize the sign-in button.
        
        Args:
            parent: Parent frame to contain the button
            command: Callback function when button is clicked
        """
        self.parent = parent
        self.command = command
        self.button = None
        self._is_animating = False
        
    def create(self):
        """
        Create the sign-in button with proper styling.
        
        Returns:
            button: The created button widget
        """
        # Sign in button with fixed colors
        self.button = tk.Button(
            self.parent, 
            text="Sign In", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.PRIMARY_BLUE, 
            fg=Colors.WHITE, 
            width=25, 
            height=2,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self._on_button_click,
            activebackground=Colors.PRIMARY_BLUE,  # Keep blue when clicked
            activeforeground=Colors.WHITE  # Keep white text when clicked
        )
        self.button.pack(pady=20)
        
        # Bind hover effects
        self._bind_hover_effects()
        
        return self.button
    
    def _bind_hover_effects(self):
        """Bind hover effects to the sign-in button."""
        def on_enter(event):
            """Handle mouse enter event."""
            if not self._is_animating:
                self.button.config(bg="#0056b3")  # Darker blue on hover
            
        def on_leave(event):
            """Handle mouse leave event."""
            if not self._is_animating:
                self.button.config(bg=Colors.PRIMARY_BLUE)  # Original blue
            
        self.button.bind("<Enter>", on_enter)
        self.button.bind("<Leave>", on_leave)
    
    def _on_button_click(self):
        """Handle button click with visual feedback animation."""
        if self._is_animating:
            return
        
        # Animate press and then execute command
        self._animate_press(callback=self.command)
    
    def _animate_press(self, callback=None):
        """
        Animate button press with color change.
        
        Args:
            callback: Optional callback to execute after animation
        """
        self._is_animating = True
        
        # Change to pressed state (darker)
        self.button.config(bg="#FFFFFF", relief=tk.SUNKEN)

        self.button.config(text="Signing In...", fg="#000000")
        
        # Schedule return to normal state
        self.button.after(150, lambda: self._reset_button_state(callback))
    
    def _reset_button_state(self, callback=None):
        """
        Reset button to normal state after animation.
        
        Args:
            callback: Optional callback to execute after reset
        """
        self.button.config(bg=Colors.PRIMARY_BLUE, relief=tk.FLAT)
        self._is_animating = False
        
        # Execute callback if provided
        if callback:
            callback()
    
    def trigger_press_animation(self, callback=None):
        """
        Trigger the press animation programmatically (for Enter key).
        
        Args:
            callback: Optional callback to execute after animation
        """
        if self._is_animating:
            return
        
        self._animate_press(callback=callback)
