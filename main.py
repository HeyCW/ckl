import tkinter as tk
import traceback
import sys
import os
from src.utils.helpers import setup_window_restore_behavior
from src.utils.icon_cache import icon_cache

def main():
    try:
        print("🚀 Starting application...")

        # Create root window
        print("🪟 Creating root window...")
        root = tk.Tk()
        
        
        # Configure root winprint("")dow (initially hidden)
        root.title("Aplikasi Data Shipping")
        root.geometry("1x1")  # Minimal size initially
        root.withdraw()  # Hide initially
        
        # Set icon menggunakan cache system
        icon_photo = icon_cache.get_icon("assets/logo.jpg", (32, 32))
        if icon_photo:
            root.iconphoto(False, icon_photo)
        
        print("   ✅ Root window created")
        
        def on_login_success(username, user_data):
            """Callback after successful login"""
            print(f"🔐 Login success callback triggered for: {username}")
            try:
                # Record who's logged in so every create/edit from here
                # on gets stamped with it (see src/models/db/audit.py)
                from src.models.db.audit import set_current_user
                set_current_user(username)

                # Lazy import MainWindow (hanya saat login berhasil)
                from src.views.main_window import MainWindow

                # Show and configure root window
                print("🪟 Showing main window...")
                root.deiconify()  # Show the hidden root window
                root.geometry("1000x700")  # Set proper size
                root.lift()       # Bring to front
                root.focus_force()  # Give it focus

                print(f"   ✅ Root window configured: {root.geometry()}")

                # Center window
                center_window(root)
                print(f"   ✅ Window centered")

                # Create main window content
                print("🏠 Creating main window...")
                app = MainWindow(root, current_user=user_data)
                print(f"   ✅ Main window created")
                
                # Ensure window is visible
                root.after(100, lambda: root.lift())
                root.after(200, lambda: root.focus_force())
                
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
        
        # Show login window (lazy import)
        print("🔑 Creating login window...")
        from src.views.login_window import LoginWindow
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
            login.login_window.after(1000, lambda: login.login_window.attributes('-topmost', False))
            
            print(f"   ✅ Login window forced to show")
            print(f"   📍 Login window geometry: {login.login_window.geometry()}")
        else:
            print("   ❌ Login window object not found!")
            return
        
        # Setup window restore behavior (fix minimize/restore issue)
        setup_window_restore_behavior(root)

        # Handle application exit
        def on_app_exit():
            print("🚪 Application exit triggered")
            try:
                if hasattr(login, 'db') and login.db:
                    print("🗃️ Closing database connection...")
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