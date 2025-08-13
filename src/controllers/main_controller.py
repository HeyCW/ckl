import os
import json
from tkinter import messagebox, filedialog

class MainController:
    """
    Main Controller untuk mengelola business logic aplikasi
    """
    
    def __init__(self):
        self.current_file = None
        self.current_data = None
        self.is_modified = False
        self.app_settings = self.load_settings()
        
    def load_settings(self):
        """Load aplikasi settings"""
        default_settings = {
            'theme': 'light',
            'font_size': 12,
            'font_family': 'Arial',
            'window_size': '800x600',
            'recent_files': [],
            'auto_save': True,
            'backup_enabled': True
        }
        
        settings_file = 'config/app_settings.json'
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge dengan default settings
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
    
    def save_settings(self):
        """Save aplikasi settings"""
        settings_file = 'config/app_settings.json'
        
        try:
            # Buat folder config jika belum ada
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            with open(settings_file, 'w') as f:
                json.dump(self.app_settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # File Operations
    def new_file(self):
        """Create new file"""
        if self.is_modified:
            if not self.ask_save_changes():
                return False
                
        self.current_file = None
        self.current_data = ""
        self.is_modified = False
        return True
    
    def open_file(self, filename=None):
        """Open file"""
        if self.is_modified:
            if not self.ask_save_changes():
                return False
        
        if not filename:
            filename = filedialog.askopenfilename(
                title="Open File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("Python files", "*.py"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
        
        if not filename:
            return False
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.current_file = filename
            self.current_data = content
            self.is_modified = False
            
            # Add to recent files
            self.add_to_recent_files(filename)
            
            return content
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
            return False
    
    def save_file(self, content=None):
        """Save current file"""
        if not self.current_file:
            return self.save_as_file(content)
            
        try:
            if content is not None:
                self.current_data = content
                
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.current_data)
                
            self.is_modified = False
            
            # Create backup if enabled
            if self.app_settings.get('backup_enabled', False):
                self.create_backup()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
            return False
    
    def save_as_file(self, content=None):
        """Save file with new name"""
        filename = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return False
            
        try:
            if content is not None:
                self.current_data = content
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.current_data)
                
            self.current_file = filename
            self.is_modified = False
            
            # Add to recent files
            self.add_to_recent_files(filename)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
            return False
    
    def create_backup(self):
        """Create backup of current file"""
        if not self.current_file:
            return
            
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(self.current_file)
            backup_filename = f"{backup_dir}/{timestamp}_{filename}"
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(self.current_data)
                
        except Exception as e:
            print(f"Backup creation failed: {e}")
    
    def add_to_recent_files(self, filename):
        """Add file to recent files list"""
        recent_files = self.app_settings.get('recent_files', [])
        
        # Remove if already exists
        if filename in recent_files:
            recent_files.remove(filename)
            
        # Add to beginning
        recent_files.insert(0, filename)
        
        # Keep only last 10 files
        recent_files = recent_files[:10]
        
        self.app_settings['recent_files'] = recent_files
        self.save_settings()
    
    def get_recent_files(self):
        """Get list of recent files"""
        return self.app_settings.get('recent_files', [])
    
    # Content Management
    def set_content_modified(self, modified=True):
        """Mark content as modified"""
        self.is_modified = modified
    
    def get_current_filename(self):
        """Get current filename"""
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Untitled"
    
    def get_current_filepath(self):
        """Get current file path"""
        return self.current_file
    
    def ask_save_changes(self):
        """Ask user to save changes"""
        result = messagebox.askyesnocancel(
            "Save Changes",
            "The document has been modified. Do you want to save changes?"
        )
        
        if result is True:  # Yes
            return self.save_file()
        elif result is False:  # No
            return True
        else:  # Cancel
            return False
    
    # Settings Management
    def get_setting(self, key, default=None):
        """Get setting value"""
        return self.app_settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set setting value"""
        self.app_settings[key] = value
        self.save_settings()
    
    def update_settings(self, settings_dict):
        """Update multiple settings"""
        self.app_settings.update(settings_dict)
        self.save_settings()
    
    # Theme Management
    def change_theme(self, theme):
        """Change application theme"""
        self.set_setting('theme', theme)
        # Theme change logic akan dihandle di view layer
        return True
    
    def get_current_theme(self):
        """Get current theme"""
        return self.get_setting('theme', 'light')
    
    # Font Management
    def change_font_size(self, size):
        """Change font size"""
        self.set_setting('font_size', size)
    
    def change_font_family(self, family):
        """Change font family"""
        self.set_setting('font_family', family)
    
    def get_font_config(self):
        """Get current font configuration"""
        return {
            'family': self.get_setting('font_family', 'Arial'),
            'size': self.get_setting('font_size', 12)
        }
    
    # Utility Methods
    def can_exit(self):
        """Check if app can exit safely"""
        if self.is_modified:
            return self.ask_save_changes()
        return True
    
    def get_app_info(self):
        """Get application information"""
        return {
            'name': 'My Tkinter App',
            'version': '1.0.0',
            'author': 'Your Name',
            'description': 'A modern Tkinter application'
        }
    
    def export_data(self, format_type='json'):
        """Export current data in specified format"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export")
            return False
            
        filename = filedialog.asksaveasfilename(
            title=f"Export as {format_type.upper()}",
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    if format_type == 'json':
                        # Jika data adalah JSON, format dengan indentasi
                        try:
                            data = json.loads(self.current_data)
                            json.dump(data, f, indent=4, ensure_ascii=False)
                        except json.JSONDecodeError:
                            # Jika bukan JSON valid, simpan sebagai text
                            f.write(self.current_data)
                    else:
                        f.write(self.current_data)
                        
                messagebox.showinfo("Success", f"Data exported to {filename}")
                return True
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
                return False
        
        return False