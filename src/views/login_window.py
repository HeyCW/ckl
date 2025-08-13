import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import json
import os
from datetime import datetime, timedelta

from src.models.database import AppDatabase

class LoginWindow:
    def __init__(self, root, on_login_success=None):
        self.root = root
        self.on_login_success = on_login_success
        self.login_window = None
        
        # Use SQLite database instead of JSON
        self.db = AppDatabase()
        
        # Variables untuk form
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_me_var = tk.BooleanVar()
        self.show_password_var = tk.BooleanVar()
        
        self.create_login_window()
    
    def hash_password(self, password):
        """Hash password dengan SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_login_window(self):
        """Create login window"""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login - My Tkinter App")
        self.login_window.geometry("400x550")
        self.login_window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Make it modal
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        
        # Hide main window
        self.root.withdraw()
        
        # Handle window close
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
        # Focus on window
        self.login_window.focus_set()
    
    def center_window(self):
        """Center login window on screen"""
        self.login_window.update_idletasks()
        x = (self.login_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (550 // 2)
        self.login_window.geometry(f"400x550+{x}+{y}")
    
    def setup_ui(self):
        """Setup login UI"""
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
        
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill='x', pady=(0, 15))
        
        self.username_entry = ttk.Entry(
            username_frame, 
            textvariable=self.username_var,
            font=('Arial', 11),
            width=30
        )
        self.username_entry.pack(fill='x', ipady=8)
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill='x', pady=(0, 15))
        
        password_container = ttk.Frame(password_frame)
        password_container.pack(fill='x')
        
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
        
        # Options frame
        options_frame = ttk.Frame(form_frame)
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Remember me checkbox
        remember_cb = ttk.Checkbutton(
            options_frame,
            text="Remember me",
            variable=self.remember_me_var
        )
        remember_cb.pack(side='left')
        
        # Forgot password link
        forgot_btn = ttk.Button(
            options_frame,
            text="Forgot Password?",
            command=self.forgot_password,
            style='Link.TButton'
        )
        forgot_btn.pack(side='right')
        
        # Login button
        login_btn = ttk.Button(
            form_frame,
            text="Sign In",
            command=self.login,
            style='Accent.TButton'
        )
        login_btn.pack(fill='x', ipady=10, pady=(0, 15))
        
        # Divider
        divider_frame = ttk.Frame(form_frame)
        divider_frame.pack(fill='x', pady=(10, 15))
        
        ttk.Separator(divider_frame).pack(fill='x')
        
        or_label = ttk.Label(divider_frame, text="OR", background='white')
        or_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Register button
        register_btn = ttk.Button(
            form_frame,
            text="Create New Account",
            command=self.show_register,
            style='Outline.TButton'
        )
        register_btn.pack(fill='x', ipady=8)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            foreground='red'
        )
        self.status_label.pack(pady=(10, 0))
        
        # Info section
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        info_label = ttk.Label(
            info_frame,
            text="Default login: admin / admin123",
            font=('Arial', 9),
            foreground='gray'
        )
        info_label.pack()
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda e: self.login())
        
        # Focus on username field
        self.username_entry.focus()
    
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
    
    def login(self):
        """Handle login process with improved error handling and SQLite"""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        try:
            # Authenticate user through database
            user_data = self.db.authenticate_user(username, password)
            
            if user_data:
                # Check if account is active
                if not user_data.get('is_active', True):
                    self.show_status("Account is deactivated. Contact administrator.", "error")
                    return
                
                
                # Show success message
                self.show_status("Login successful!", "success")
                
                # Add small delay for better UX
                self.login_window.after(500, lambda: self.complete_login(username, user_data))
                
            else:
                # Authentication failed
                self.handle_login_failure()
                
        except Exception as e:
            # Handle database errors gracefully
            self.show_status("Login error. Please try again.", "error")
            print(f"Login error: {e}")  # Log for debugging
    
    def handle_login_failure(self):
        """Handle failed login attempts"""
        self.show_status("Invalid username or password", "error")
        
        # Clear password for security
        self.password_var.set("")
        
        # Focus back to password field
        self.password_entry.focus()
    
    def show_register(self):
        """Show registration dialog"""
        self.register_window = tk.Toplevel(self.login_window)
        self.register_window.title("Create Account")
        self.register_window.geometry("350x400")
        self.register_window.resizable(False, False)
        self.register_window.transient(self.login_window)
        self.register_window.grab_set()
        
        # Center register window
        x = self.login_window.winfo_x() + 25
        y = self.login_window.winfo_y() + 25
        self.register_window.geometry(f"350x400+{x}+{y}")
        
        # Registration form
        reg_frame = ttk.Frame(self.register_window, padding="20")
        reg_frame.pack(fill='both', expand=True)
        
        ttk.Label(reg_frame, text="Create New Account", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Username:", "reg_username"),
            ("Email:", "reg_email"),
            ("Password:", "reg_password"),
            ("Confirm Password:", "reg_confirm_password")
        ]
        
        self.reg_vars = {}
        self.reg_entries = {}
        
        for label_text, var_name in fields:
            ttk.Label(reg_frame, text=label_text).pack(anchor='w', pady=(10, 2))
            
            self.reg_vars[var_name] = tk.StringVar()
            
            entry = ttk.Entry(
                reg_frame, 
                textvariable=self.reg_vars[var_name],
                font=('Arial', 10)
            )
            
            if "password" in var_name:
                entry.config(show="*")
            
            entry.pack(fill='x', ipady=5)
            self.reg_entries[var_name] = entry
        
        # Register button
        ttk.Button(
            reg_frame,
            text="Create Account",
            command=self.register_user
        ).pack(fill='x', pady=(20, 10), ipady=8)
        
        # Cancel button
        ttk.Button(
            reg_frame,
            text="Cancel",
            command=self.register_window.destroy
        ).pack(fill='x', ipady=8)
        
        # Focus on username
        self.reg_entries['reg_username'].focus()
    
    def register_user(self):
        """Handle user registration"""
        username = self.reg_vars['reg_username'].get().strip()
        email = self.reg_vars['reg_email'].get().strip()
        password = self.reg_vars['reg_password'].get()
        confirm_password = self.reg_vars['reg_confirm_password'].get()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if username in self.users:
            messagebox.showerror("Error", "Username already exists")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Create new user
        self.users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "role": "user",
            "created": datetime.now().isoformat(),
            "last_login": None,
            "login_count": 0,
            "is_active": True
        }
        
        self.save_users()
        messagebox.showinfo("Success", "Account created successfully!")
        self.register_window.destroy()
        
        # Auto fill login form
        self.username_var.set(username)
        self.username_entry.focus()
    
    def forgot_password(self):
        """Handle forgot password"""
        # Simple forgot password dialog
        dialog = tk.Toplevel(self.login_window)
        dialog.title("Reset Password")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.login_window)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Reset Password", font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        ttk.Label(frame, text="Enter your username:").pack(anchor='w')
        
        username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=username_var).pack(fill='x', pady=(5, 15))
        
        def reset_password():
            username = username_var.get().strip()
            if username in self.users:
                # Reset to default password
                self.users[username]['password'] = self.hash_password("newpass123")
                self.save_users()
                messagebox.showinfo("Success", f"Password reset to: newpass123")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Username not found")
        
        ttk.Button(frame, text="Reset Password", command=reset_password).pack(fill='x', pady=(0, 5))
        ttk.Button(frame, text="Cancel", command=dialog.destroy).pack(fill='x')
    
    
    def show_status(self, message, status_type="info"):
        """Show status message"""
        colors = {
            "error": "red",
            "success": "green",
            "info": "blue"
        }
        
        self.status_label.config(
            text=message,
            foreground=colors.get(status_type, "black")
        )
        
        # Clear message after 3 seconds
        self.login_window.after(3000, lambda: self.status_label.config(text=""))
    
    def close_login(self):
        """Close login window and show main window"""
        self.root.deiconify()  # Show main window
        self.login_window.destroy()
    
    def on_closing(self):
        """Handle window closing"""
        self.root.quit()  # Exit application if login is closed

# Example usage function
def on_login_success(username, user_data):
    """Callback function called after successful login"""
    print(f"Login successful for {username}")
    print(f"User role: {user_data.get('role', 'user')}")
    print(f"Last login: {user_data.get('last_login', 'Never')}")
    print(f"Login count: {user_data.get('login_count', 0)}")

# Test function
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Application")
    root.geometry("800x600")
    
    # Create login window
    login = LoginWindow(root, on_login_success)
    
    root.mainloop()