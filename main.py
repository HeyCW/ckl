import tkinter as tk
from src.views.main_window import MainWindow
from src.controllers.main_controller import MainController
from config.settings import APP_CONFIG

def main():
    root = tk.Tk()
    controller = MainController()
    app = MainWindow(root, controller)
    
    # Load config
    root.title(APP_CONFIG['app_name'])
    root.geometry(APP_CONFIG['default_size'])
    
    root.mainloop()

if __name__ == "__main__":
    main()