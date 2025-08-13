import tkinter as tk
from src.views.login_window import LoginWindow
from src.controllers.main_controller import MainController
from config.settings import APP_CONFIG

def main():
    root = tk.Tk()
    controller = MainController()
    app = LoginWindow(root)
    
    # Load config
    root.title(APP_CONFIG['app_name'])
    root.geometry(APP_CONFIG['default_size'])
    
    root.mainloop()

if __name__ == "__main__":
    main()