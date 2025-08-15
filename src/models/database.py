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
        self.create_customers_table()
        self.create_containers_table()
        self.create_barang_table()
        self.create_detail_container_table()
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
    
    def create_customers_table(self):
        """Create customers table"""
        query = '''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_customer TEXT NOT NULL,
            alamat_customer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute(query)
    
    def create_containers_table(self):
        """Create containers table"""
        query = '''
        CREATE TABLE IF NOT EXISTS containers (
            container_id INTEGER PRIMARY KEY AUTOINCREMENT,
            feeder TEXT,
            etd_sub DATE,
            party TEXT,
            cls DATE,
            open DATE,
            full DATE,
            destination TEXT,
            container TEXT,
            seal TEXT,
            ref_joa TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.execute(query)
    
    def create_barang_table(self):
        """Create barang table"""
        query = '''
        CREATE TABLE IF NOT EXISTS barang (
            barang_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            nama_barang TEXT NOT NULL,
            panjang_barang REAL,
            lebar_barang REAL,
            tinggi_barang REAL,
            m3_barang REAL,
            ton_barang REAL,
            col_barang INTEGER,
            harga_satuan REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
        '''
        self.execute(query)
    
    def create_detail_container_table(self):
        """Create detail container table (junction table)"""
        query = '''
        CREATE TABLE IF NOT EXISTS detail_container (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barang_id INTEGER,
            container_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (barang_id) REFERENCES barang (barang_id),
            FOREIGN KEY (container_id) REFERENCES containers (container_id),
            UNIQUE(barang_id, container_id)
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

# Customer Management Methods
class CustomerDatabase(SQLiteDatabase):
    """Extended database class with customer-specific methods"""
    
    def create_customer(self, nama_customer, alamat_customer):
        """Create new customer"""
        customer_id = self.execute_insert('''
            INSERT INTO customers (nama_customer, alamat_customer)
            VALUES (?, ?)
        ''', (nama_customer, alamat_customer))
        
        return customer_id
    
    def get_all_customers(self):
        """Get all customers"""
        customers = self.execute("SELECT * FROM customers ORDER BY nama_customer")
        return [dict(customer) for customer in customers]
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        customer = self.execute_one(
            "SELECT * FROM customers WHERE customer_id = ?", 
            (customer_id,)
        )
        return dict(customer) if customer else None
    
    def update_customer(self, customer_id, nama_customer=None, alamat_customer=None):
        """Update customer"""
        if nama_customer and alamat_customer:
            self.execute('''
                UPDATE customers 
                SET nama_customer = ?, alamat_customer = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE customer_id = ?
            ''', (nama_customer, alamat_customer, customer_id))
        elif nama_customer:
            self.execute('''
                UPDATE customers 
                SET nama_customer = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE customer_id = ?
            ''', (nama_customer, customer_id))
        elif alamat_customer:
            self.execute('''
                UPDATE customers 
                SET alamat_customer = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE customer_id = ?
            ''', (alamat_customer, customer_id))

# Container Management Methods
class ContainerDatabase(SQLiteDatabase):
    """Extended database class with container-specific methods"""
    
    def create_container(self, feeder=None, etd_sub=None, party=None, cls=None, 
                        open_date=None, full=None, destination=None, container=None, 
                        seal=None, ref_joa=None):
        """Create new container"""
        container_id = self.execute_insert('''
            INSERT INTO containers (feeder, etd_sub, party, cls, open, full, 
                                  destination, container, seal, ref_joa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (feeder, etd_sub, party, cls, open_date, full, destination, 
              container, seal, ref_joa))
        
        return container_id
    
    def get_all_containers(self):
        """Get all containers"""
        containers = self.execute("SELECT * FROM containers ORDER BY created_at DESC")
        return [dict(container) for container in containers]
    
    def get_container_by_id(self, container_id):
        """Get container by ID"""
        container = self.execute_one(
            "SELECT * FROM containers WHERE container_id = ?", 
            (container_id,)
        )
        return dict(container) if container else None

# Barang Management Methods
class BarangDatabase(SQLiteDatabase):
    """Extended database class with barang-specific methods"""
    
    def create_barang(self, customer_id, nama_barang, panjang_barang=None, 
                     lebar_barang=None, tinggi_barang=None, m3_barang=None, 
                     ton_barang=None, col_barang=None, harga_satuan=None):
        """Create new barang"""
        barang_id = self.execute_insert('''
            INSERT INTO barang (customer_id, nama_barang, panjang_barang, lebar_barang,
                               tinggi_barang, m3_barang, ton_barang, col_barang, harga_satuan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, nama_barang, panjang_barang, lebar_barang, tinggi_barang,
              m3_barang, ton_barang, col_barang, harga_satuan))
        
        return barang_id
    
    def get_barang_by_customer(self, customer_id):
        """Get all barang for a customer"""
        barang_list = self.execute('''
            SELECT b.*, c.nama_customer 
            FROM barang b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.customer_id = ?
            ORDER BY b.created_at DESC
        ''', (customer_id,))
        
        return [dict(barang) for barang in barang_list]
    
    def get_all_barang(self):
        """Get all barang with customer info"""
        barang_list = self.execute('''
            SELECT b.*, c.nama_customer 
            FROM barang b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.created_at DESC
        ''')
        
        return [dict(barang) for barang in barang_list]
    
    def assign_barang_to_container(self, barang_id, container_id):
        """Assign barang to container"""
        try:
            self.execute_insert('''
                INSERT INTO detail_container (barang_id, container_id)
                VALUES (?, ?)
            ''', (barang_id, container_id))
            return True
        except sqlite3.IntegrityError:
            return False  # Already assigned
    
    def get_barang_in_container(self, container_id):
        """Get all barang in a container"""
        barang_list = self.execute('''
            SELECT b.*, c.nama_customer, dc.created_at as assigned_at
            FROM barang b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN detail_container dc ON b.barang_id = dc.barang_id
            WHERE dc.container_id = ?
            ORDER BY dc.created_at DESC
        ''', (container_id,))
        
        return [dict(barang) for barang in barang_list]

# Combined Database Class
class AppDatabase(UserDatabase, CustomerDatabase, ContainerDatabase, BarangDatabase):
    """Complete app database with all methods"""
    
    def __init__(self, db_path="data/app.db"):
        super().__init__(db_path)
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        user_info = self.get_user_by_id(user_id)
        
        return {
            'login_count': user_info.get('login_count', 0) if user_info else 0,
            'last_login': user_info.get('last_login') if user_info else None
        }
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        total_customers = self.execute_one("SELECT COUNT(*) as count FROM customers")
        total_barang = self.execute_one("SELECT COUNT(*) as count FROM barang")
        total_containers = self.execute_one("SELECT COUNT(*) as count FROM containers")
        
        return {
            'total_customers': total_customers['count'] if total_customers else 0,
            'total_barang': total_barang['count'] if total_barang else 0,
            'total_containers': total_containers['count'] if total_containers else 0
        }

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
    
    # Test customer creation
    customer_id = db.create_customer("PT. Test Company", "Jl. Test No. 123")
    print(f"Created customer with ID: {customer_id}")
    
    # Test container creation
    container_id = db.create_container(
        feeder="EVER GIVEN",
        destination="JAKARTA",
        container="TCLU1234567"
    )
    print(f"Created container with ID: {container_id}")
    
    # Test barang creation
    if customer_id:
        barang_id = db.create_barang(
            customer_id=customer_id,
            nama_barang="Elektronik",
            panjang_barang=100,
            lebar_barang=50,
            tinggi_barang=30,
            m3_barang=0.15,
            ton_barang=0.5,
            col_barang=10,
            harga_satuan=1000000
        )
        print(f"Created barang with ID: {barang_id}")
        
        # Test assign barang to container
        if container_id and barang_id:
            assigned = db.assign_barang_to_container(barang_id, container_id)
            print(f"Barang assigned to container: {assigned}")
    
    # Get dashboard stats
    stats = db.get_dashboard_stats()
    print(f"Dashboard stats: {stats}")