import sqlite3
import os
from datetime import datetime
import hashlib

class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.ensure_data_dir()
        self.init_db()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def execute(self, query, params=()):
        """Execute query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_one(self, query, params=()):
        """Execute query and return single result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def execute_insert(self, query, params=()):
        """Execute insert and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_many(self, query, params_list):
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def init_db(self):
        """Initialize database with required tables"""
        self.create_users_table()
        self.create_documents_table()
        self.create_sessions_table()
        self.create_app_settings_table()
        self.insert_default_data()
    
    def create_users_table(self):
        """Create users table"""
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0
        )
        '''
        self.execute(query)
    
    def create_documents_table(self):
        """Create documents table"""
        query = '''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
        self.execute(query)
    
    def create_sessions_table(self):
        """Create sessions table for remember me functionality"""
        query = '''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
        self.execute(query)
    
    def create_app_settings_table(self):
        """Create app settings table"""
        query = '''
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, setting_key)
        )
        '''
        self.execute(query)
    
    def insert_default_data(self):
        """Insert default admin user if not exists"""
        admin_exists = self.execute_one(
            "SELECT id FROM users WHERE username = ?", 
            ("admin",)
        )
        
        if not admin_exists:
            # Hash default password
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            self.execute('''
                INSERT INTO users (username, password, email, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', ("admin", password_hash, "admin@example.com", "admin", 1))
            
            print("Default admin user created: admin/admin123")

# User Management Methods
class UserDatabase(SQLiteDatabase):
    """Extended database class with user-specific methods"""
    
    def create_user(self, username, password, email, role='user'):
        """Create new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            user_id = self.execute_insert('''
                INSERT INTO users (username, password, email, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, role, 1))
            
            return user_id
        except sqlite3.IntegrityError:
            return None  # Username already exists
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = self.execute_one('''
            SELECT * FROM users 
            WHERE username = ? AND password = ? AND is_active = 1
        ''', (username, password_hash))
        
        if user:
            # Update login info
            self.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, 
                    login_count = login_count + 1
                WHERE id = ?
            ''', (user['id'],))
            
            return dict(user)
        
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        user = self.execute_one(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        user = self.execute_one(
            "SELECT * FROM users WHERE id = ?", 
            (user_id,)
        )
        return dict(user) if user else None
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        result = self.execute('''
            UPDATE users 
            SET password = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ?
        ''', (password_hash, username))
        
        return True
    
    def deactivate_user(self, username):
        """Deactivate user account"""
        self.execute('''
            UPDATE users 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ?
        ''', (username,))
    
    def get_all_users(self):
        """Get all users"""
        users = self.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(user) for user in users]

# Document Management Methods  
class DocumentDatabase(SQLiteDatabase):
    """Extended database class with document-specific methods"""
    
    def create_document(self, user_id, title, content, file_path=None):
        """Create new document"""
        doc_id = self.execute_insert('''
            INSERT INTO documents (user_id, title, content, file_path)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, content, file_path))
        
        return doc_id
    
    def get_user_documents(self, user_id):
        """Get all documents for a user"""
        docs = self.execute('''
            SELECT * FROM documents 
            WHERE user_id = ? 
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        return [dict(doc) for doc in docs]
    
    def update_document(self, doc_id, title=None, content=None):
        """Update document"""
        if title and content:
            self.execute('''
                UPDATE documents 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (title, content, doc_id))
        elif title:
            self.execute('''
                UPDATE documents 
                SET title = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (title, doc_id))
        elif content:
            self.execute('''
                UPDATE documents 
                SET content = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (content, doc_id))
    
    def delete_document(self, doc_id, user_id):
        """Delete document (only if owned by user)"""
        self.execute('''
            DELETE FROM documents 
            WHERE id = ? AND user_id = ?
        ''', (doc_id, user_id))

# Combined Database Class
class AppDatabase(UserDatabase, DocumentDatabase):
    """Complete app database with all methods"""
    
    def __init__(self, db_path="data/app.db"):
        super().__init__(db_path)
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        doc_count = self.execute_one(
            "SELECT COUNT(*) as count FROM documents WHERE user_id = ?",
            (user_id,)
        )
        
        user_info = self.get_user_by_id(user_id)
        
        return {
            'document_count': doc_count['count'] if doc_count else 0,
            'login_count': user_info.get('login_count', 0) if user_info else 0,
            'last_login': user_info.get('last_login') if user_info else None
        }
    
    def search_documents(self, user_id, search_term):
        """Search documents by title or content"""
        docs = self.execute('''
            SELECT * FROM documents 
            WHERE user_id = ? AND (
                title LIKE ? OR content LIKE ?
            )
            ORDER BY updated_at DESC
        ''', (user_id, f'%{search_term}%', f'%{search_term}%'))
        
        return [dict(doc) for doc in docs]

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = AppDatabase()
    
    # Test user creation
    user_id = db.create_user("testuser", "password123", "test@example.com")
    print(f"Created user with ID: {user_id}")
    
    # Test authentication
    user = db.authenticate_user("admin", "admin123")
    print(f"Authenticated user: {user['username'] if user else 'Failed'}")
    
    # Test document creation
    if user:
        doc_id = db.create_document(user['id'], "Test Document", "This is test content")
        print(f"Created document with ID: {doc_id}")
        
        # Get user documents
        docs = db.get_user_documents(user['id'])
        print(f"User has {len(docs)} documents")