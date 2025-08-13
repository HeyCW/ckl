import tkinter as tk
import traceback
import sys
import os

def main():
    try:
        print("🚀 Starting application...")
        
        # Import modules
        from src.views.login_window import LoginWindow
        from src.views.main_window import MainWindow
        from src.controllers.main_controller import MainController
        from config.settings import APP_CONFIG
        
        # Create root window
        print("🪟 Creating root window...")
        root = tk.Tk()
        
        # IMPORTANT: Don't hide root window initially on Windows
        # root.withdraw()  # Comment this out for debugging
        
        # Configure root window (temporary, will be hidden when login shows)
        root.title("Initializing...")
        root.geometry("1x1")  # Minimal size
        root.attributes('-topmost', True)  # Force on top
        
        print("   ✅ Root window created")
        
        def on_login_success(username, user_data):
            """Callback after successful login"""
            print(f"🔐 Login success callback triggered for: {username}")
            try:
                # Create controller with user context
                print("🎮 Creating controller...")
                controller = MainController()
                controller.set_current_user(user_data)
                print(f"   ✅ Controller created and user set: {username}")
                
                # IMPORTANT: Show root window first before creating MainWindow
                print("🪟 Showing root window...")
                root.deiconify()  # Show the hidden root window
                root.lift()       # Bring to front
                root.focus_force()  # Give it focus
                
                # Configure root window
                root.title(f"{APP_CONFIG['app_name']} - Welcome {username}")
                root.geometry(APP_CONFIG['default_size'])
                root.attributes('-topmost', False)  # Remove topmost
                
                print(f"   ✅ Root window configured: {root.geometry()}")
                
                # Center window
                center_window(root)
                print(f"   ✅ Window centered")
                
                # THEN create main window content
                print("🏠 Creating main window...")
                app = MainWindow(root, controller)
                print(f"   ✅ Main window created")
                
                # Ensure window is visible and on top
                root.after(100, lambda: root.lift())
                root.after(200, lambda: root.focus_force())
                
                # Optional: Apply user settings
                try:
                    window_state = controller.get_user_setting('window_state', 'normal')
                    if window_state == 'maximized':
                        root.state('zoomed')  # Windows
                        print("   ✅ Window maximized")
                except Exception as e:
                    print(f"   ⚠️ Window state error: {e}")
                
                # Apply theme
                try:
                    theme = controller.get_user_setting('theme', 'light')
                    if hasattr(app, 'apply_theme'):
                        app.apply_theme(theme)
                        print(f"   ✅ Theme applied: {theme}")
                except Exception as e:
                    print(f"   ⚠️ Theme error: {e}")
                
                print(f"✅ Login successful: {username} ({user_data.get('role', 'user')})")
                print(f"📊 Final window state: {root.state()}")
                print(f"📊 Final window geometry: {root.geometry()}")
                
            except Exception as e:
                print(f"❌ Error in login success callback: {e}")
                traceback.print_exc()
                # Show error to user
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"Failed to initialize main window:\n{str(e)}")
                except:
                    pass
                root.quit()
        
        # Show login window
        print("🔑 Creating login window...")
        login = LoginWindow(root, on_login_success)
        
        # Force login window to show and focus
        if hasattr(login, 'login_window') and login.login_window:
            print("🔍 Forcing login window to show...")
            
            # Multiple methods to ensure window shows
            login.login_window.lift()
            login.login_window.attributes('-topmost', True)
            login.login_window.focus_force()
            login.login_window.grab_set()
            
            # Remove topmost after a delay
            login.login_window.after(100, lambda: login.login_window.attributes('-topmost', False))
            
            print(f"   ✅ Login window forced to show")
            print(f"   📍 Login window geometry: {login.login_window.geometry()}")
            
            # Hide root window now
            root.after(200, lambda: root.withdraw())
        else:
            print("   ❌ Login window object not found!")
            return
        
        # Handle application exit
        def on_app_exit():
            print("🚪 Application exit triggered")
            try:
                if hasattr(login, 'db') and login.db:
                    login.db.close()
                root.quit()
            except:
                root.quit()
        
        root.protocol("WM_DELETE_WINDOW", on_app_exit)
        
        # Additional debug info
        print(f"📊 Root window state: {root.state()}")
        print(f"📊 Root window geometry: {root.geometry()}")
        
        print("🎬 Starting mainloop...")
        root.mainloop()
        print("🏁 Application finished")
        
    except Exception as e:
        print(f"💥 FATAL ERROR in main(): {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

def center_window(window):
    """Center window on screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    main()