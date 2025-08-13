import tkinter as tk
from tkinter import ttk
import datetime

class StatusBar:
    def __init__(self, root):
        self.root = root
        self.create_statusbar()
        self.update_time()
    
    def create_statusbar(self):
        # Frame untuk status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Separator line
        separator = ttk.Separator(self.status_frame, orient='horizontal')
        separator.pack(side=tk.TOP, fill=tk.X, pady=1)
        
        # Left side - Main status
        self.status_left = ttk.Label(
            self.status_frame, 
            text="Ready", 
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Center - Progress info (optional)
        self.status_center = ttk.Label(
            self.status_frame,
            text="",
            relief=tk.SUNKEN,
            anchor=tk.CENTER,
            width=20
        )
        self.status_center.pack(side=tk.LEFT, padx=2)
        
        # Right side - Time
        self.status_right = ttk.Label(
            self.status_frame,
            text="",
            relief=tk.SUNKEN,
            anchor=tk.E,
            width=20
        )
        self.status_right.pack(side=tk.RIGHT, padx=(0, 2))
    
    def set_status(self, message):
        """Set main status message"""
        self.status_left.config(text=message)
        
    def set_progress(self, message):
        """Set progress/center message"""
        self.status_center.config(text=message)
        
    def clear_progress(self):
        """Clear progress message"""
        self.status_center.config(text="")
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_right.config(text=current_time)
        # Update setiap detik
        self.root.after(1000, self.update_time)
    
    def show_temporary_message(self, message, duration=3000):
        """Show temporary message for specified duration (in milliseconds)"""
        original_text = self.status_left.cget("text")
        self.set_status(message)
        # Restore original message after duration
        self.root.after(duration, lambda: self.set_status(original_text))