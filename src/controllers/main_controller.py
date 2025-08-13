import os
import json
from tkinter import messagebox, filedialog
from src.models.database import AppDatabase

class MainController:
    """
    Main Controller dengan user context dari login
    """
    
    def __init__(self):
        self.db = AppDatabase()
        self.current_user = None
        self.current_file = None
        self.current_data = None
        self.is_modified = False
        self.app_settings = self.load_global_settings()
        
    def set_current_user(self, user_data):
        """Set current logged-in user"""
        self.current_user = user_data
        print(f"🔐 User context set: {user_data.get('username')} ({user_data.get('role')})")
        
        # Load user-specific settings
        self.load_user_settings()
        
    def get_current_user(self):
        """Get current user data"""
        return self.current_user
    
    def get_user_id(self):
        """Get current user ID"""
        return self.current_user.get('id') if self.current_user else None
    
    def get_username(self):
        """Get current username"""
        return self.current_user.get('username') if self.current_user else 'Guest'
    
    def get_user_role(self):
        """Get current user role"""
        return self.current_user.get('role', 'user') if self.current_user else 'guest'
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.get_user_role() == 'admin'
    
    def load_global_settings(self):
        """Load global app settings"""
        default_settings = {
            'theme': 'light',
            'font_size': 12,
            'font_family': 'Arial',
            'window_size': '800x600',
            'auto_save': True,
            'backup_enabled': True
        }
        
        settings_file = 'config/app_settings.json'
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading global settings: {e}")
            
        return default_settings
    
    def load_user_settings(self):
        """Load user-specific settings from database"""
        if not self.current_user:
            return
        
        try:
            user_id = self.get_user_id()
            settings = self.db.execute('''
                SELECT setting_key, setting_value 
                FROM app_settings 
                WHERE user_id = ?
            ''', (user_id,))
            
            # Override global settings with user settings
            for setting in settings:
                key, value = setting
                # Try to parse JSON value, fallback to string
                try:
                    self.app_settings[key] = json.loads(value)
                except:
                    self.app_settings[key] = value
                    
            print(f"📋 Loaded {len(settings)} user settings")
            
        except Exception as e:
            print(f"Error loading user settings: {e}")
    
    def save_user_setting(self, key, value):
        """Save user-specific setting to database"""
        if not self.current_user:
            return False
        
        try:
            user_id = self.get_user_id()
            value_json = json.dumps(value) if not isinstance(value, str) else value
            
            # Use INSERT OR REPLACE for upsert functionality
            self.db.execute('''
                INSERT OR REPLACE INTO app_settings (user_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, key, value_json))
            
            # Update local settings
            self.app_settings[key] = value
            return True
            
        except Exception as e:
            print(f"Error saving user setting: {e}")
            return False
    
    def get_user_setting(self, key, default=None):
        """Get user setting with fallback to default"""
        return self.app_settings.get(key, default)
    
    # Document Management with User Context
    def save_file(self, content=None):
        """Save current file with user context"""
        if not self.current_file:
            return self.save_as_file(content)
        
        try:
            if content is not None:
                self.current_data = content
            
            # Save to filesystem
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.current_data)
            
            # Save to database if user is logged in
            if self.current_user:
                self.save_document_to_db()
            
            self.is_modified = False
            
            # Create backup if enabled
            if self.app_settings.get('backup_enabled', False):
                self.create_backup()
            
            return True
            
        except Exception as e:
            print(f"Save error: {e}")
            messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
            return False
    
    def save_document_to_db(self):
        """Save current document to database"""
        if not self.current_user or not self.current_file:
            return
        
        try:
            user_id = self.get_user_id()
            title = os.path.basename(self.current_file)
            
            # Check if document already exists in DB
            existing = self.db.execute_one('''
                SELECT id FROM documents 
                WHERE user_id = ? AND file_path = ?
            ''', (user_id, self.current_file))
            
            if existing:
                # Update existing document
                self.db.execute('''
                    UPDATE documents 
                    SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (title, self.current_data, existing['id']))
            else:
                # Create new document record
                self.db.execute('''
                    INSERT INTO documents (user_id, title, content, file_path)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, title, self.current_data, self.current_file))
                
        except Exception as e:
            print(f"Error saving document to DB: {e}")
    
    def get_user_documents(self):
        """Get all documents for current user"""
        if not self.current_user:
            return []
        
        try:
            user_id = self.get_user_id()
            docs = self.db.execute('''
                SELECT * FROM documents 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            ''', (user_id,))
            
            return [dict(doc) for doc in docs]
            
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    def get_user_stats(self):
        """Get statistics for current user"""
        if not self.current_user:
            return {}
        
        try:
            user_id = self.get_user_id()
            stats = self.db.get_user_stats(user_id)
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    def logout(self):
        """Logout current user"""
        # Save any pending changes
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Logout", 
                "You have unsaved changes. Save before logout?"
            )
            if result is True:  # Yes
                if not self.save_file():
                    return False
            elif result is None:  # Cancel
                return False
        
        # Clear user context
        self.current_user = None
        self.current_file = None
        self.current_data = None
        self.is_modified = False
        
        # Clear user-specific settings (keep global ones)
        self.app_settings = self.load_global_settings()
        
        return True
    
    def can_exit(self):
        """Check if app can exit safely with logout"""
        return self.logout()
    
    # Theme and Settings with User Context
    def change_theme(self, theme):
        """Change theme and save to user settings"""
        self.save_user_setting('theme', theme)
        return True
    
    def change_font_size(self, size):
        """Change font size and save to user settings"""
        self.save_user_setting('font_size', size)
    
    def change_font_family(self, family):
        """Change font family and save to user settings"""
        self.save_user_setting('font_family', family)
    
    def save_window_state(self, geometry, state='normal'):
        """Save window state to user settings"""
        self.save_user_setting('window_size', geometry)
        self.save_user_setting('window_state', state)