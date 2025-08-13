import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from src.views.components.menu_bar import MenuBar
from src.views.components.status_bar import StatusBar

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.setup_ui()
        
    
    
    def load_user_dashboard(self):
        """Load user dashboard data"""
        try:
            # Get user stats
            stats = self.controller.get_user_stats()
            doc_count = stats.get('document_count', 0)
            login_count = stats.get('login_count', 0)
            
            # Show in status bar
            self.status_bar.set_progress(f"Documents: {doc_count} | Logins: {login_count}")
            
            # Load recent documents
            recent_docs = self.controller.get_user_documents()
            if recent_docs:
                self.update_recent_files_menu(recent_docs[:5])  # Show last 5
                
        except Exception as e:
            print(f"Error loading user dashboard: {e}")
    
    def setup_ui(self):
        # Menu bar with user context
        self.menu_bar = MenuBar(self.root)
        self.add_user_menus()
        
        # Main content area
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create main content widgets
        self.create_main_content()
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        
        # Update title with user info
        self.update_title()
    
    def add_user_menus(self):
        """Add user-specific menu items"""
        # Add User menu
        user_menu = tk.Menu(self.menu_bar.menubar, tearoff=0)
        self.menu_bar.menubar.add_cascade(label="User", menu=user_menu)
        
        username = self.controller.get_username()
        role = self.controller.get_user_role()
        
        user_menu.add_command(label=f"Logged in as: {username}", state="disabled")
        user_menu.add_command(label=f"Role: {role.title()}", state="disabled")
        user_menu.add_separator()
        
        user_menu.add_command(label="My Documents", command=self.show_my_documents)
        user_menu.add_command(label="User Settings", command=self.show_user_settings)
        
        if self.controller.is_admin():
            user_menu.add_separator()
            user_menu.add_command(label="Admin Panel", command=self.show_admin_panel)
        
        user_menu.add_separator()
        user_menu.add_command(label="Logout", command=self.logout)
    
    def show_my_documents(self):
        """Show user's documents in a dialog"""
        docs = self.controller.get_user_documents()
        
        # Create documents dialog
        docs_window = tk.Toplevel(self.root)
        docs_window.title("My Documents")
        docs_window.geometry("600x400")
        docs_window.transient(self.root)
        
        # Create treeview for documents
        frame = ttk.Frame(docs_window, padding="10")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="My Documents", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=('title', 'created', 'updated'), show='headings')
        tree.heading('title', text='Title')
        tree.heading('created', text='Created')
        tree.heading('updated', text='Last Updated')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate tree
        for doc in docs:
            tree.insert('', 'end', values=(
                doc['title'],
                doc['created_at'][:16],  # Format datetime
                doc['updated_at'][:16]
            ))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Close", command=docs_window.destroy).pack(side='right')
        
        if docs:
            def open_selected():
                selection = tree.selection()
                if selection:
                    item = tree.item(selection[0])
                    title = item['values'][0]
                    # Find document by title
                    for doc in docs:
                        if doc['title'] == title:
                            self.load_document_from_db(doc)
                            docs_window.destroy()
                            break
            
            ttk.Button(btn_frame, text="Open Selected", command=open_selected).pack(side='right', padx=(0, 5))
    
    def load_document_from_db(self, doc):
        """Load document from database to editor"""
        try:
            # Load content to editor
            if hasattr(self, 'text_editor'):
                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert('1.0', doc.get('content', ''))
            
            # Update controller state
            self.controller.current_file = doc.get('file_path')
            self.controller.current_data = doc.get('content', '')
            self.controller.is_modified = False
            
            # Update UI
            self.update_title()
            self.status_bar.set_status(f"Loaded: {doc['title']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load document:\n{str(e)}")
    
    def show_user_settings(self):
        """Show user settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("User Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="User Settings", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Theme setting
        theme_frame = ttk.LabelFrame(frame, text="Appearance", padding=10)
        theme_frame.pack(fill='x', pady=5)
        
        current_theme = self.controller.get_user_setting('theme', 'light')
        theme_var = tk.StringVar(value=current_theme)
        
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=theme_var, value="light").pack(anchor='w')
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=theme_var, value="dark").pack(anchor='w')
        
        # Font settings
        font_frame = ttk.LabelFrame(frame, text="Font", padding=10)
        font_frame.pack(fill='x', pady=5)
        
        current_size = self.controller.get_user_setting('font_size', 12)
        
        ttk.Label(font_frame, text=f"Font Size: {current_size}").pack(anchor='w')
        size_var = tk.IntVar(value=current_size)
        size_scale = ttk.Scale(font_frame, from_=8, to=20, orient='horizontal', variable=size_var)
        size_scale.pack(fill='x', pady=2)
        
        # Save button
        def save_settings():
            self.controller.change_theme(theme_var.get())
            self.controller.change_font_size(int(size_var.get()))
            
            # Apply changes immediately
            self.apply_theme(theme_var.get())
            font_config = self.controller.get_font_config()
            self.update_font(font_config['family'], font_config['size'])
            
            messagebox.showinfo("Success", "Settings saved!")
            settings_window.destroy()
        
        ttk.Button(frame, text="Save Settings", command=save_settings).pack(pady=20)
        ttk.Button(frame, text="Cancel", command=settings_window.destroy).pack()
    
    def show_admin_panel(self):
        """Show admin panel (only for admin users)"""
        if not self.controller.is_admin():
            messagebox.showerror("Access Denied", "Admin privileges required")
            return
        
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        admin_window.geometry("500x400")
        admin_window.transient(self.root)
        
        frame = ttk.Frame(admin_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Admin Panel", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Get all users
        try:
            all_users = self.controller.db.get_all_users()
            
            # Users list
            users_frame = ttk.LabelFrame(frame, text="All Users", padding=10)
            users_frame.pack(fill='both', expand=True)
            
            # Create treeview for users
            user_tree = ttk.Treeview(users_frame, columns=('username', 'email', 'role', 'active'), show='headings')
            user_tree.heading('username', text='Username')
            user_tree.heading('email', text='Email')
            user_tree.heading('role', text='Role')
            user_tree.heading('active', text='Active')
            
            for user in all_users:
                user_tree.insert('', 'end', values=(
                    user['username'],
                    user.get('email', 'N/A'),
                    user['role'],
                    'Yes' if user['is_active'] else 'No'
                ))
            
            user_tree.pack(fill='both', expand=True)
            
        except Exception as e:
            ttk.Label(frame, text=f"Error loading users: {e}").pack()
        
        ttk.Button(frame, text="Close", command=admin_window.destroy).pack(pady=10)
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if self.controller.logout():
                # Hide main window
                self.root.withdraw()
                
                # Show login window again
                from src.views.login_window import LoginWindow
                
                def on_new_login(username, user_data):
                    # Update controller with new user
                    self.controller.set_current_user(user_data)
                    
                    # Update UI
                    self.update_ui_from_controller()
                    
                    # Show main window
                    self.root.deiconify()
                
                # Create new login window
                LoginWindow(self.root, on_new_login)
    
    def create_main_content(self):
        """Create main content area with user context"""
        
        # Text editor with user context
        editor_frame = ttk.Frame(self.main_frame)
        editor_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            undo=True,
            maxundo=50
        )
        self.text_editor.pack(fill='both', expand=True)
        # Load user's last document if any
        self.load_last_document()
    
    def load_last_document(self):
        """Load user's last opened document"""
        try:
            recent_docs = self.controller.get_user_documents()
            if recent_docs:
                last_doc = recent_docs[0]  # Most recent
                self.load_document_from_db(last_doc)
        except Exception as e:
            print(f"Error loading last document: {e}")
    
    def update_title(self):
        """Update window title with user context"""
        username = self.controller.get_username()
        filename = self.controller.get_current_filename() if self.controller.current_file else "Untitled"
        modified = " *" if self.controller.is_modified else ""
        
        title = f"{filename}{modified} - My Tkinter App ({username})"
        self.root.title(title)
    
    def on_window_closing(self):
        """Handle window closing with logout"""
        # Save window state
        geometry = self.root.geometry()
        state = self.root.state()
        self.controller.save_window_state(geometry, state)
        
        # Logout and exit
        if self.controller.can_exit():
            self.root.destroy()