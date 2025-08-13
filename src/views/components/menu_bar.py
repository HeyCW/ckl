import tkinter as tk
from tkinter import messagebox, filedialog

class MenuBar:
    def __init__(self, root):
        self.root = root
        self.create_menubar()
    
    def create_menubar(self):
        # Buat menubar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Alt+F4")
        
        # Edit Menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # View Menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        
        # Submenu untuk themes
        self.theme_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="Theme", menu=self.theme_menu)
        self.theme_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        self.theme_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))
        
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        
        # Tools Menu
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Options", command=self.show_options)
        self.tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help Menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Help", command=self.show_help, accelerator="F1")
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        self.root.bind('<F1>', lambda e: self.show_help())
    
    # File Menu Methods
    def new_file(self):
        print("New file created")
        # Implement new file logic here
        
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        if filename:
            print(f"Opening file: {filename}")
            # Implement file opening logic here
    
    def save_file(self):
        print("File saved")
        # Implement save logic here
        
    def save_as_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        if filename:
            print(f"Saving file as: {filename}")
            # Implement save as logic here
    
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    # Edit Menu Methods
    def undo(self):
        print("Undo action")
        # Implement undo logic here
        
    def redo(self):
        print("Redo action")
        # Implement redo logic here
        
    def cut(self):
        try:
            self.root.clipboard_clear()
            selection = self.root.selection_get()
            self.root.clipboard_append(selection)
            print("Cut to clipboard")
        except tk.TclError:
            print("No text selected")
    
    def copy(self):
        try:
            self.root.clipboard_clear()
            selection = self.root.selection_get()
            self.root.clipboard_append(selection)
            print("Copied to clipboard")
        except tk.TclError:
            print("No text selected")
    
    def paste(self):
        try:
            clipboard_content = self.root.clipboard_get()
            print(f"Pasting: {clipboard_content}")
            # Insert clipboard content to focused widget
        except tk.TclError:
            print("Clipboard is empty")
    
    def select_all(self):
        print("Select all")
        # Implement select all logic here
    
    # View Menu Methods
    def change_theme(self, theme):
        print(f"Changing theme to: {theme}")
        # Implement theme change logic here
        
    def zoom_in(self):
        print("Zoom in")
        # Implement zoom in logic here
        
    def zoom_out(self):
        print("Zoom out")
        # Implement zoom out logic here
        
    def reset_zoom(self):
        print("Reset zoom")
        # Implement reset zoom logic here
    
    # Tools Menu Methods
    def show_options(self):
        messagebox.showinfo("Options", "Options dialog would open here")
        
    def show_settings(self):
        messagebox.showinfo("Settings", "Settings dialog would open here")
    
    # Help Menu Methods
    def show_help(self):
        help_text = """
        Help Information:
        
        File Menu:
        - New: Create a new file
        - Open: Open an existing file
        - Save: Save current file
        - Save As: Save file with new name
        - Exit: Close the application
        
        Edit Menu:
        - Standard editing operations
        
        View Menu:
        - Theme options
        - Zoom controls
        
        Use keyboard shortcuts for faster access!
        """
        messagebox.showinfo("Help", help_text)
        
    def show_about(self):
        about_text = """
        My Tkinter Application
        Version 1.0.0
        
        Created with Python and Tkinter
        
        © 2025 Your Name
        """
        messagebox.showinfo("About", about_text)