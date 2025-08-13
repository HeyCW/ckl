import tkinter as tk
from tkinter import ttk
from src.views.components.menu_bar import MenuBar
from src.views.components.status_bar import StatusBar

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Menu bar
        self.menu_bar = MenuBar(self.root)
        
        # Main content
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)
        