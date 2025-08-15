import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from src.models.database import AppDatabase

class LoginWindow:
    def __init__(self, root, on_login_success=None):
        self.root = root
        self.on_login_success = on_login_success
        self.login_window = None
        
        # Use SQLite database
        self.db = AppDatabase()
        
        # Variables untuk form
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar()
        self.failed_attempts = 0
        
        self.create_login_window()
    
    def create_login_window(self):
        """Create login window with forced visibility"""
        print("🔑 Creating login window...")
        
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login - My Tkinter App")
        self.login_window.geometry("400x450")
        self.login_window.resizable(False, False)
        
        print(f"   📍 Initial geometry: {self.login_window.geometry()}")
        
        # FORCE WINDOW TO SHOW - Multiple methods
        self.login_window.lift()
        self.login_window.focus_force()
        self.login_window.attributes('-topmost', True)
        
        # Center window BEFORE making it modal
        self.center_window()
        
        # Make it modal AFTER positioning
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        
        # Hide main window AFTER login window is set up
        self.root.withdraw()
        
        # Handle window close
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup UI
        self.setup_ui()
        
        # Force visibility again after UI setup
        self.login_window.deiconify()  # Ensure window is shown
        self.login_window.update()     # Force update
        
        # Remove topmost after window is established
        self.login_window.after(1000, lambda: self.login_window.attributes('-topmost', False))
        
        # Final focus
        self.login_window.focus_set()
        self.login_window.focus_force()
        
        print(f"   ✅ Login window created")
        print(f"   📊 Final geometry: {self.login_window.geometry()}")
        print(f"   👁️ Window visible: {self.login_window.winfo_viewable()}")
        print(f"   🎯 Window mapped: {self.login_window.winfo_ismapped()}")
    
    def center_window(self):
        """Center login window on screen with debug info"""
        # Force update to get real dimensions
        self.login_window.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width // 2) - (400 // 2)
        y = (screen_height // 2) - (450 // 2)
        
        # Ensure window is not off-screen
        x = max(0, min(x, screen_width - 400))
        y = max(0, min(y, screen_height - 450))
        
        # Set geometry
        self.login_window.geometry(f"400x450+{x}+{y}")
        
        print(f"   📏 Screen: {screen_width}x{screen_height}")
        print(f"   📍 Position: {x}, {y}")
    
    def setup_ui(self):
        """Setup login UI"""
        print("   🎨 Setting up UI...")
        
        # Main container
        main_frame = ttk.Frame(self.login_window, padding="30")
        main_frame.pack(fill='both', expand=True)
        
        # Title Section
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="Welcome Back!",
            font=('Arial', 24, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Please sign in to your account",
            font=('Arial', 11),
            foreground='gray'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Login Form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            form_frame,
            textvariable=self.username_var,
            font=('Arial', 11),
            width=30
        )
        self.username_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        password_container = ttk.Frame(form_frame)
        password_container.pack(fill='x', pady=(0, 25))
        
        self.password_entry = ttk.Entry(
            password_container,
            textvariable=self.password_var,
            font=('Arial', 11),
            show="*"
        )
        self.password_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        # Show/Hide password button
        self.show_pwd_btn = ttk.Button(
            password_container,
            text="👁",
            width=3,
            command=self.toggle_password_visibility
        )
        self.show_pwd_btn.pack(side='right', padx=(5, 0))
        
        # Login button - STORE REFERENCE
        self.login_btn = ttk.Button(
            form_frame,
            text="Sign In",
            command=self.login
        )
        self.login_btn.pack(fill='x', ipady=10, pady=(0, 15))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            foreground='red'
        )
        self.status_label.pack(pady=(10, 0))
        
        # Info section
        info_label = ttk.Label(
            main_frame,
            text="Default login: admin / admin123",
            font=('Arial', 9),
            foreground='gray'
        )
        info_label.pack(side='bottom', pady=(20, 0))
        
        # Test button untuk debug
        test_btn = ttk.Button(
            main_frame,
            text="Test Window Visibility",
            command=self.test_window_visibility
        )
        test_btn.pack(pady=5)
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda e: self.login())
        
        # Focus on username field
        self.username_entry.focus()
        
        print("   ✅ UI setup complete")
    
    def test_window_visibility(self):
        """Test method to check window visibility"""
        print("=" * 50)
        print("🔍 WINDOW VISIBILITY TEST")
        print("=" * 50)
        
        if self.login_window:
            print(f"Window exists: ✅")
            print(f"Window state: {self.login_window.state()}")
            print(f"Window geometry: {self.login_window.geometry()}")
            print(f"Window visible: {self.login_window.winfo_viewable()}")
            print(f"Window mapped: {self.login_window.winfo_ismapped()}")
            print(f"Window width: {self.login_window.winfo_width()}")
            print(f"Window height: {self.login_window.winfo_height()}")
            print(f"Window x: {self.login_window.winfo_x()}")
            print(f"Window y: {self.login_window.winfo_y()}")
            
            # Force window to front
            self.login_window.lift()
            self.login_window.focus_force()
            self.login_window.attributes('-topmost', True)
            self.login_window.after(2000, lambda: self.login_window.attributes('-topmost', False))
            
            messagebox.showinfo("Test", "If you see this, the window is working!")
        else:
            print("❌ Login window does not exist!")
        
        print("=" * 50)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
            self.show_pwd_btn.config(text="🙈")
            self.show_password_var.set(False)
        else:
            self.password_entry.config(show="*")
            self.show_pwd_btn.config(text="👁")
            self.show_password_var.set(True)
    
    def validate_login_input(self, username, password):
        """Validate login form input"""
        if not username:
            self.show_status("Please enter username", "error")
            self.username_entry.focus()
            return False
        
        if not password:
            self.show_status("Please enter password", "error")
            self.password_entry.focus()
            return False
        
        if len(username) < 3:
            self.show_status("Username must be at least 3 characters", "error")
            self.username_entry.focus()
            return False
        
        if len(password) < 6:
            self.show_status("Password must be at least 6 characters", "error")
            self.password_entry.focus()
            return False
        
        return True
    
    def login(self):
        """Handle login process"""
        print("🔐 Login attempt started...")
        
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        print(f"   👤 Username: '{username}'")
        print(f"   🔑 Password length: {len(password)}")
        
        # Input validation
        if not self.validate_login_input(username, password):
            print("   ❌ Validation failed")
            return
        
        try:
            # Authenticate user through database
            print("   🔍 Authenticating user...")
            user_data = self.db.authenticate_user(username, password)
            
            if user_data:
                print(f"   ✅ Authentication successful: {user_data}")
                
                # Check if account is active
                if not user_data.get('is_active', True):
                    self.show_status("Account is deactivated. Contact administrator.", "error")
                    return
                
                # Show success message
                self.show_status("Login successful!", "success")
                
                # Reset failed attempts
                self.failed_attempts = 0
                
                print("   🚪 Closing login window...")
                # Close login window first
                self.close_login()
                
                print("   📞 Calling success callback...")
                # Call success callback immediately
                if self.on_login_success:
                    self.on_login_success(username, user_data)
                else:
                    print("   ❌ No callback function provided!")
                
            else:
                print("   ❌ Authentication failed")
                # Authentication failed
                self.handle_login_failure()
                
        except Exception as e:
            # Handle database errors gracefully
            print(f"   💥 Login error: {e}")
            self.show_status("Login error. Please try again.", "error")
            import traceback
            traceback.print_exc()
    
    def handle_login_failure(self):
        """Handle failed login attempts"""
        self.show_status("Invalid username or password", "error")
        
        # Clear password for security
        self.password_var.set("")
        
        # Focus back to password field
        self.password_entry.focus()
        
        # Track failed attempts
        self.failed_attempts += 1
        
        # Lock login after 5 failed attempts
        if self.failed_attempts >= 5:
            self.lock_login_temporarily()
    
    def lock_login_temporarily(self):
        """Temporarily lock login after too many failed attempts"""
        # Disable login button and form
        self.login_btn.config(state='disabled')
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        
        # Show lockout message
        self.show_status("Too many failed attempts. Please wait 30 seconds.", "error")
        
        # Re-enable after 30 seconds
        self.login_window.after(30000, self.unlock_login)
    
    def unlock_login(self):
        """Unlock login form after lockout period"""
        # Reset failed attempts
        self.failed_attempts = 0
        
        # Re-enable form
        self.login_btn.config(state='normal')
        self.username_entry.config(state='normal')
        self.password_entry.config(state='normal')
        
        # Clear status
        self.show_status("You can try logging in again.", "info")
        
        # Focus on username
        self.username_entry.focus()
    
    def show_status(self, message, status_type="info"):
        """Show status message"""
        colors = {
            "error": "#dc3545",
            "success": "#28a745",
            "info": "#17a2b8"
        }
        
        self.status_label.config(
            text=message,
            foreground=colors.get(status_type, "#333333")
        )
        
        # Clear message after delay
        delay = 4000 if status_type == "error" else 2000
        self.login_window.after(delay, lambda: self.status_label.config(text=""))
    
    def close_login(self):
        """Close login window"""
        try:
            print("   🚪 Closing login window...")
            if self.login_window:
                self.login_window.grab_release()
                self.login_window.destroy()
                self.login_window = None
                print("   ✅ Login window closed")
        except Exception as e:
            print(f"Error closing login window: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        print("🚪 Login window closing - exiting application")
        self.root.quit()