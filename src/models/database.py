import sqlite3
import os
from datetime import datetime
import hashlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_database.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom database exception"""
    pass

class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        try:
            self.ensure_data_dir()
            self.init_db()
            logger.info(f"Database initialized successfully: {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        try:
            data_dir = os.path.dirname(self.db_path)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"Created data directory: {data_dir}")
        except OSError as e:
            logger.error(f"Failed to create data directory: {e}")
            raise DatabaseError(f"Cannot create data directory: {e}")
    
    def get_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise DatabaseError(f"Cannot connect to database: {e}")
    
    def execute(self, query, params=()):
        """Execute query and return results with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                logger.debug(f"Query executed successfully: {query[:50]}...")
                return result
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity constraint violation: {e}")
            raise DatabaseError(f"Data integrity error: {e}")
        except sqlite3.OperationalError as e:
            logger.error(f"Operational error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    def execute_one(self, query, params=()):
        """Execute query and return single result with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                logger.debug(f"Single query executed successfully: {query[:50]}...")
                return result
        except sqlite3.Error as e:
            logger.error(f"Database error in execute_one: {e}")
            raise DatabaseError(f"Database query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in execute_one: {e}")
            raise DatabaseError(f"Unexpected error: {e}")
    
    def execute_insert(self, query, params=()):
        """Execute insert and return last row id with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                last_id = cursor.lastrowid
                logger.info(f"Insert successful, ID: {last_id}")
                return last_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Insert failed - integrity constraint: {e}")
            raise DatabaseError(f"Data already exists or constraint violation: {e}")
        except sqlite3.Error as e:
            logger.error(f"Insert failed: {e}")
            raise DatabaseError(f"Failed to insert data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during insert: {e}")
            raise DatabaseError(f"Unexpected insert error: {e}")
    
    def execute_many(self, query, params_list):
        """Execute query with multiple parameter sets with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                row_count = cursor.rowcount
                logger.info(f"Bulk operation completed, rows affected: {row_count}")
                return row_count
        except sqlite3.Error as e:
            logger.error(f"Bulk operation failed: {e}")
            raise DatabaseError(f"Bulk operation error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in bulk operation: {e}")
            raise DatabaseError(f"Unexpected bulk operation error: {e}")
    
    def init_db(self):
        """Initialize database with required tables"""
        try:
            self.create_users_table()
            self.create_customers_table()
            self.create_containers_table()
            self.create_barang_table()
            self.create_detail_container_table()
            self.insert_default_data()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise DatabaseError(f"Table initialization failed: {e}")
    
    def create_users_table(self):
        """Create users table with error handling"""
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
        try:
            self.execute(query)
            logger.info("Users table created successfully")
        except Exception as e:
            logger.error(f"Failed to create users table: {e}")
            raise
    
    def create_customers_table(self):
        """Create customers table with error handling"""
        query = '''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_customer TEXT NOT NULL,
            alamat_customer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        try:
            self.execute(query)
            logger.info("Customers table created successfully")
        except Exception as e:
            logger.error(f"Failed to create customers table: {e}")
            raise
    
    def create_containers_table(self):
        """Create containers table with error handling"""
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
        try:
            self.execute(query)
            logger.info("Containers table created successfully")
        except Exception as e:
            logger.error(f"Failed to create containers table: {e}")
            raise
    
    def create_barang_table(self):
        """Create barang table with error handling"""
        query = '''
        CREATE TABLE IF NOT EXISTS barang (
            barang_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pengirim TEXT NOT NULL,
            penerima TEXT NOT NULL,
            nama_barang TEXT NOT NULL,
            jenis_barang TEXT NOT NULL,
            panjang_barang  REAL,
            lebar_barang REAL,
            tinggi_barang REAL,
            m3_barang REAL,
            ton_barang REAL,
            col_barang  INTEGER,
            m3_pp REAL,
            m3_pd REAL,
            m3_dd REAL,
            ton_pp REAL,
            ton_pd REAL,
            ton_dd REAL,
            col_pp INTEGER,
            col_pd INTEGER,
            col_dd INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        try:
            self.execute(query)
            logger.info("Barang table created successfully")
        except Exception as e:
            logger.error(f"Failed to create barang table: {e}")
            raise
    
    def create_detail_container_table(self):
        """Create detail container table with pricing columns and sender/receiver info"""
        query = '''
        CREATE TABLE IF NOT EXISTS detail_container (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barang_id INTEGER NOT NULL,
            container_id INTEGER NOT NULL,
            colli_amount INTEGER NOT NULL DEFAULT 1,
            harga_per_unit DECIMAL(15,2) DEFAULT 0,
            total_harga DECIMAL(15,2) DEFAULT 0,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (barang_id) REFERENCES barang (barang_id),
            FOREIGN KEY (container_id) REFERENCES containers (container_id)
        )
        '''
        try:
            self.execute(query)
            print("✅ Detail container table created/updated successfully")
        except Exception as e:
            print(f"❌ Failed to create detail container table: {e}")
            raise
    
    def insert_default_data(self):
        """Insert default admin user if not exists with error handling"""
        try:
            admin_exists = self.execute_one(
                "SELECT id FROM users WHERE username = ?", 
                ("admin",)
            )
            
            if not admin_exists:
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                
                self.execute('''
                    INSERT INTO users (username, password, email, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', ("admin", password_hash, "admin@example.com", "admin", 1))
                
                logger.info("Default admin user created: admin/admin123")
        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")
            # Don't raise here as this is not critical

# User Management Methods
class UserDatabase(SQLiteDatabase):
    """Extended database class with user-specific methods"""
    
    def create_user(self, username, password, email, role='user'):
        """Create new user with error handling"""
        if not username or not password:
            raise ValueError("Username and password are required")
        
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user_id = self.execute_insert('''
                INSERT INTO users (username, password, email, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, role, 1))
            
            logger.info(f"User created successfully: {username}")
            return user_id
            
        except DatabaseError as e:
            if "constraint" in str(e).lower():
                logger.warning(f"Username already exists: {username}")
                raise ValueError(f"Username '{username}' already exists")
            raise e
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
    
    def authenticate_user(self, username, password):
        """Authenticate user login with error handling"""
        if not username or not password:
            raise ValueError("Username and password are required")
        
        try:
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
                
                logger.info(f"User authenticated successfully: {username}")
                return dict(user)
            else:
                logger.warning(f"Failed authentication attempt for: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            raise DatabaseError(f"Authentication failed: {e}")
    
    def get_user_by_username(self, username):
        """Get user by username with error handling"""
        if not username:
            raise ValueError("Username is required")
        
        try:
            user = self.execute_one(
                "SELECT * FROM users WHERE username = ?", 
                (username,)
            )
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {e}")
    
    def get_user_by_id(self, user_id):
        """Get user by ID with error handling"""
        if not user_id:
            raise ValueError("User ID is required")
        
        try:
            user = self.execute_one(
                "SELECT * FROM users WHERE id = ?", 
                (user_id,)
            )
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Failed to get user ID {user_id}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {e}")
    
    def update_user_password(self, username, new_password):
        """Update user password with error handling"""
        if not username or not new_password:
            raise ValueError("Username and new password are required")
        
        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        try:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            self.execute('''
                UPDATE users 
                SET password = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            ''', (password_hash, username))
            
            logger.info(f"Password updated for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update password for {username}: {e}")
            raise DatabaseError(f"Failed to update password: {e}")
    
    def deactivate_user(self, username):
        """Deactivate user account with error handling"""
        if not username:
            raise ValueError("Username is required")
        
        try:
            self.execute('''
                UPDATE users 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            ''', (username,))
            
            logger.info(f"User deactivated: {username}")
            
        except Exception as e:
            logger.error(f"Failed to deactivate user {username}: {e}")
            raise DatabaseError(f"Failed to deactivate user: {e}")
    
    def get_all_users(self):
        """Get all users with error handling"""
        try:
            users = self.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            raise DatabaseError(f"Failed to retrieve users: {e}")

# Customer Management Methods
class CustomerDatabase(SQLiteDatabase):
    """Extended database class with customer-specific methods"""
    
    def create_customer(self, nama_customer, alamat_customer):
        """Create new customer with error handling"""
        if not nama_customer:
            raise ValueError("Customer name is required")
        
        try:
            customer_id = self.execute_insert('''
                INSERT INTO customers (nama_customer, alamat_customer)
                VALUES (?, ?)
            ''', (nama_customer, alamat_customer))
            
            logger.info(f"Customer created successfully: {nama_customer}")
            return customer_id
            
        except Exception as e:
            logger.error(f"Failed to create customer {nama_customer}: {e}")
            raise DatabaseError(f"Failed to create customer: {e}")
    
    def get_all_customers(self):
        """Get all customers with error handling"""
        try:
            customers = self.execute("SELECT * FROM customers ORDER BY customer_id")
            return [dict(customer) for customer in customers]
        except Exception as e:
            logger.error(f"Failed to get all customers: {e}")
            raise DatabaseError(f"Failed to retrieve customers: {e}")
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID with error handling"""
        if not customer_id:
            raise ValueError("Customer ID is required")
        
        try:
            customer = self.execute_one(
                "SELECT * FROM customers WHERE customer_id = ?", 
                (customer_id,)
            )
            return dict(customer) if customer else None
        except Exception as e:
            logger.error(f"Failed to get customer ID {customer_id}: {e}")
            raise DatabaseError(f"Failed to retrieve customer: {e}")
        
    def get_customer_id_by_name(self, nama_customer):
        """Get customer ID by name with error handling - returns int, not sqlite3.Row"""
        if not nama_customer:
            raise ValueError("Customer name is required")
        try:
            customer = self.execute_one(
                "SELECT customer_id FROM customers WHERE nama_customer = ?",
                (nama_customer,)
            )
            
            if customer:
                # Extract the actual integer value from sqlite3.Row
                if hasattr(customer, '__getitem__'):  # Check if it's a Row object
                    customer_id = customer['customer_id']  # or customer[0]
                else:
                    customer_id = customer
                
                return int(customer_id) if customer_id is not None else None
            else:
                return None  # Customer not found
                
        except Exception as e:
            logger.error(f"Failed to get customer ID by name {nama_customer}: {e}")
            raise DatabaseError(f"Failed to retrieve customer ID: {e}")

    def update_customer(self, customer_id, nama_customer=None, alamat_customer=None):
        """Update customer with error handling"""
        if not customer_id:
            raise ValueError("Customer ID is required")
        
        if not nama_customer and not alamat_customer:
            raise ValueError("At least one field must be provided for update")
        
        try:
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
            
            logger.info(f"Customer updated successfully: ID {customer_id}")
            
        except Exception as e:
            logger.error(f"Failed to update customer ID {customer_id}: {e}")
            raise DatabaseError(f"Failed to update customer: {e}")

# Container Management Methods
class ContainerDatabase(SQLiteDatabase):
    """Extended database class with container-specific methods"""
    
    def create_container(self, feeder=None, etd_sub=None, party=None, cls=None, 
                        open_date=None, full=None, destination=None, container=None, 
                        seal=None, ref_joa=None):
        """Create new container with error handling"""
        try:
            container_id = self.execute_insert('''
                INSERT INTO containers (feeder, etd_sub, party, cls, open, full, 
                                      destination, container, seal, ref_joa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (feeder, etd_sub, party, cls, open_date, full, destination, 
                  container, seal, ref_joa))
            
            logger.info(f"Container created successfully: ID {container_id}")
            return container_id
            
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise DatabaseError(f"Failed to create container: {e}")
    
    def get_all_containers(self):
        """Get all containers with error handling"""
        try:
            containers = self.execute("SELECT * FROM containers ORDER BY created_at DESC")
            return [dict(container) for container in containers]
        except Exception as e:
            logger.error(f"Failed to get all containers: {e}")
            raise DatabaseError(f"Failed to retrieve containers: {e}")
    
    def get_container_by_id(self, container_id):
        """Get container by ID with error handling"""
        if not container_id:
            raise ValueError("Container ID is required")
        
        try:
            container = self.execute_one(
                "SELECT * FROM containers WHERE container_id = ?", 
                (container_id,)
            )
            return dict(container) if container else None
        except Exception as e:
            logger.error(f"Failed to get container ID {container_id}: {e}")
            raise DatabaseError(f"Failed to retrieve container: {e}")

# Barang Management Methods
class BarangDatabase(SQLiteDatabase):
    """Extended database class with barang-specific methods"""
    
    def create_barang(self, pengirim, penerima, jenis_barang, nama_barang,
                 panjang_barang=None, lebar_barang=None, tinggi_barang=None, m3_barang=None, ton_barang=None, col_barang=None,
                 m3_pp=None, m3_pd=None, m3_dd=None,
                 ton_pp=None, ton_pd=None, ton_dd=None,
                 col_pp=None, col_pd=None, col_dd=None):
        """Create new barang with error handling"""
        if not pengirim or not penerima or not nama_barang:
            raise ValueError("Pengirim, Penerima, and Nama Barang are required")
    
        try:
            barang_id = self.execute_insert('''
                INSERT INTO barang (pengirim, penerima, jenis_barang, nama_barang, 
                                panjang_barang, lebar_barang, tinggi_barang, m3_barang, ton_barang, col_barang,
                                m3_pp, m3_pd, m3_dd, ton_pp, ton_pd, ton_dd,
                                col_pp, col_pd, col_dd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pengirim, penerima, jenis_barang, nama_barang, panjang_barang, lebar_barang, tinggi_barang, m3_barang, ton_barang, col_barang,
                m3_pp, m3_pd, m3_dd, ton_pp, ton_pd, ton_dd, col_pp, col_pd, col_dd))
        
            logger.info(f"Barang created successfully: {nama_barang}")
            return barang_id
        
        except Exception as e:
            logger.error(f"Failed to create barang {nama_barang}: {e}")
            raise DatabaseError(f"Failed to create barang: {e}")

    def update_barang(self, barang_data):
        """Update existing barang with error handling"""
        if not barang_data or not barang_data.get('barang_id'):
            raise ValueError("Barang data and ID are required")

        required_fields = ['nama_barang', 'barang_id', 'pengirim', 'penerima']
        for field in required_fields:
            if field not in barang_data:
                raise ValueError(f"Required field missing: {field}")

        try:
            # Cek apakah barang_id ada sebelum update
            existing_barang = self.execute_one(
                "SELECT barang_id FROM barang WHERE barang_id = ?",
                (barang_data['barang_id'],)
            )
        
            if not existing_barang:
                raise ValueError(f"Barang dengan ID {barang_data['barang_id']} tidak ditemukan")
        
            # Lakukan update
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE barang
                    SET pengirim = ?, penerima = ?, jenis_barang = ?, nama_barang = ?,
                        panjang_barang = ?, lebar_barang = ?, tinggi_barang = ?, m3_barang = ?, ton_barang = ?, col_barang = ?,
                        m3_pp = ?, m3_pd = ?, m3_dd = ?, ton_pp = ?, ton_pd = ?, ton_dd = ?,
                        col_pp = ?, col_pd = ?, col_dd = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE barang_id = ?
                ''', (
                    barang_data.get('pengirim'), barang_data.get('penerima'),
                    barang_data.get('jenis_barang'), barang_data.get('nama_barang'),
                    barang_data.get('panjang_barang'), barang_data.get('lebar_barang'), barang_data.get('tinggi_barang'),
                    barang_data.get('m3_barang'), barang_data.get('ton_barang'), barang_data.get('col_barang'),
                    barang_data.get('m3_pp'), barang_data.get('m3_pd'), barang_data.get('m3_dd'),
                    barang_data.get('ton_pp'), barang_data.get('ton_pd'), barang_data.get('ton_dd'),
                    barang_data.get('col_pp'), barang_data.get('col_pd'), barang_data.get('col_dd'),
                    barang_data['barang_id']
                ))
            
                # Cek berapa row yang terpengaruh
                rows_affected = cursor.rowcount
            
                if rows_affected == 0:
                    raise ValueError(f"Gagal mengupdate barang ID {barang_data['barang_id']} - data tidak ditemukan")

            logger.info(f"Barang updated successfully: ID {barang_data['barang_id']}")

        except ValueError:
            # Re-raise ValueError tanpa wrap ke DatabaseError
            raise
        except Exception as e:
            logger.error(f"Failed to update barang ID {barang_data.get('barang_id')}: {e}")
            raise DatabaseError(f"Failed to update barang: {e}")
    
    def delete_barang(self, barang_id):
        """Delete barang with error handling"""
        if not barang_id:
            raise ValueError("Barang ID is required")
    
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM barang WHERE barang_id = ?
                ''', (barang_id,))
                
                # Cek apakah ada row yang terhapus
                if cursor.rowcount == 0:
                    raise ValueError(f"Barang dengan ID {barang_id} tidak ditemukan")
        
            logger.info(f"Barang deleted successfully: ID {barang_id}")
        
        except ValueError:
            # Re-raise ValueError agar bisa ditangani di GUI
            raise
        except Exception as e:
            logger.error(f"Failed to delete barang ID {barang_id}: {e}")
            raise DatabaseError(f"Failed to delete barang: {e}")

    def get_barang_by_customer(self, customer_id):
        """Get all barang for a customer with error handling"""
        if not customer_id:
            raise ValueError("Customer ID is required")
        
        try:
            barang_list = self.execute('''
                SELECT b.*, c.nama_customer 
                FROM barang b
                JOIN customers c ON b.customer_id = c.customer_id
                WHERE b.customer_id = ?
                ORDER BY b.created_at DESC
            ''', (customer_id,))
            
            return [dict(barang) for barang in barang_list]
            
        except Exception as e:
            logger.error(f"Failed to get barang for customer ID {customer_id}: {e}")
            raise DatabaseError(f"Failed to retrieve barang: {e}")
    
    def get_all_barang(self):
        """Get all barang with customer info and error handling"""
        
        try:
            barang_list = self.execute('''
                SELECT 
                    b.*,
                    s.nama_customer AS sender_name,
                    s.alamat_customer AS sender_address,
                    r.nama_customer AS receiver_name,
                    r.alamat_customer AS receiver_address
                FROM barang b
                LEFT JOIN customers r ON b.penerima = r.customer_id
                LEFT JOIN customers s ON b.pengirim = s.customer_id
                ORDER BY b.barang_id ASC;

            ''')
            
            
            return [dict(barang) for barang in barang_list]
            
        except Exception as e:
            logger.error(f"Failed to get all barang: {e}")
            raise DatabaseError(f"Failed to retrieve barang: {e}")
    
    def assign_barang_to_container(self, barang_id, container_id):
        """Assign barang to container with error handling"""
        if not barang_id or not container_id:
            raise ValueError("Barang ID and Container ID are required")
        
        try:
            self.execute_insert('''
                INSERT INTO detail_container (barang_id, container_id)
                VALUES (?, ?)
            ''', (barang_id, container_id))
            
            logger.info(f"Barang {barang_id} assigned to container {container_id}")
            return True
            
        except DatabaseError as e:
            if "constraint" in str(e).lower():
                logger.warning(f"Barang {barang_id} already assigned to container {container_id}")
                raise ValueError("Barang already assigned to this container")
            raise e
        except Exception as e:
            logger.error(f"Failed to assign barang {barang_id} to container {container_id}: {e}")
            raise DatabaseError(f"Failed to assign barang to container: {e}")
    
    def get_barang_in_container(self, container_id):
        """Get all barang in a container with error handling"""
        if not container_id:
            raise ValueError("Container ID is required")
        
        try:
            barang_list = self.execute('''
                SELECT b.*, dc.created_at as assigned_at
                FROM barang b
                JOIN customers r ON b.penerima = r.customer_id
                JOIN customers s ON b.pengirim = s.customer_id
                JOIN detail_container dc ON b.barang_id = dc.barang_id
                WHERE dc.container_id = ?
                ORDER BY dc.created_at DESC
            ''', (container_id,))
            
            return [dict(barang) for barang in barang_list]
            
        except Exception as e:
            logger.error(f"Failed to get barang in container {container_id}: {e}")
            raise DatabaseError(f"Failed to retrieve barang in container: {e}")

# Combined Database Class with Pricing Features
class AppDatabase(UserDatabase, CustomerDatabase, ContainerDatabase, BarangDatabase):
    """Complete app database with all methods including pricing features"""
    
    def __init__(self, db_path="data/app.db"):
        try:
            super().__init__(db_path)
            logger.info("AppDatabase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AppDatabase: {e}")
            raise
    
    def get_user_stats(self, user_id):
        """Get user statistics with error handling"""
        if not user_id:
            raise ValueError("User ID is required")
        
        try:
            user_info = self.get_user_by_id(user_id)
            
            return {
                'login_count': user_info.get('login_count', 0) if user_info else 0,
                'last_login': user_info.get('last_login') if user_info else None
            }
        except Exception as e:
            logger.error(f"Failed to get user stats for ID {user_id}: {e}")
            raise DatabaseError(f"Failed to retrieve user statistics: {e}")
    
    def get_dashboard_stats(self):
        """Get dashboard statistics with error handling"""
        try:
            total_customers = self.execute_one("SELECT COUNT(*) as count FROM customers")
            total_barang = self.execute_one("SELECT COUNT(*) as count FROM barang")
            total_containers = self.execute_one("SELECT COUNT(*) as count FROM containers")
            
            return {
                'total_customers': total_customers['count'] if total_customers else 0,
                'total_barang': total_barang['count'] if total_barang else 0,
                'total_containers': total_containers['count'] if total_containers else 0
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            raise DatabaseError(f"Failed to retrieve dashboard statistics: {e}")

    # ================== PRICING FEATURES ==================

    def assign_barang_to_container_with_pricing(self, barang_id, container_id, colli_amount, harga_per_unit=0, total_harga=0):
        """Assign barang to container with pricing information"""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert with pricing
            self.execute("""
                INSERT INTO detail_container 
                (barang_id, container_id, colli_amount, harga_per_unit, total_harga, assigned_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (barang_id, container_id, colli_amount, harga_per_unit, total_harga, current_time))
            
            logger.info(f"Barang {barang_id} assigned to container {container_id} with pricing")
            return True
        except Exception as e:
            logger.error(f"Error assigning barang to container with pricing: {e}")
            return False

    def get_barang_in_container_with_colli_and_pricing(self, container_id):
        """Get all barang in a specific container with colli and pricing information"""
        try:
            result = self.execute("""
                SELECT 
                    b.barang_id,
                    b.nama_barang,
                    b.jenis_barang,
                    b.panjang_barang,
                    b.lebar_barang,
                    b.tinggi_barang,
                    b.m3_barang,
                    b.ton_barang,
                    r.nama_customer AS receiver_name,
                    s.nama_customer AS sender_name,
                    dc.colli_amount,
                    COALESCE(dc.harga_per_unit, 0) as harga_per_unit,
                    COALESCE(dc.total_harga, 0) as total_harga,
                    dc.assigned_at
                FROM detail_container dc
                JOIN barang b ON dc.barang_id = b.barang_id
                JOIN customers r ON b.penerima = r.customer_id
                JOIN customers s ON b.pengirim = s.customer_id
                WHERE dc.container_id = ?
                ORDER BY dc.assigned_at DESC
            """, (container_id,))
            
            logger.debug(f"Retrieved {len(result)} barang with pricing for container {container_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting barang in container with pricing: {e}")
            return []

    def update_barang_pricing_in_container(self, barang_id, container_id, harga_per_unit, total_harga):
        """Update pricing for specific barang in container"""
        try:
            self.execute("""
                UPDATE detail_container 
                SET harga_per_unit = ?, total_harga = ?
                WHERE barang_id = ? AND container_id = ?
            """, (harga_per_unit, total_harga, barang_id, container_id))
            
            logger.info(f"Updated pricing for barang {barang_id} in container {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating barang pricing: {e}")
            return False
        
    
    def get_barang_with_pricing_info(self, barang_id):
        """Get barang with pricing information from database"""
        try:
            result = self.execute_one("""
                SELECT b.*, s.nama_customer AS sender_name, r.nama_customer AS receiver_name
                FROM barang b 
                JOIN customers s ON b.pengirim = s.customer_id
                JOIN customers r ON b.penerima = r.customer_id
                WHERE b.barang_id = ?
            """, (barang_id,))
            
            return dict(result) if result else None
            
        except Exception as e:
            print(f"Error getting barang pricing info: {e}")
            return None

    def get_container_total_value(self, container_id):
        """Get total value of all barang in container"""
        try:
            result = self.execute_one("""
                SELECT SUM(COALESCE(total_harga, 0)) as total_value
                FROM detail_container 
                WHERE container_id = ?
            """, (container_id,))
            
            if result and result[0]:
                return float(result[0] or 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting container total value: {e}")
            return 0

    def get_customer_container_summary_with_pricing(self, container_id):
        """Get summary by customer for container including pricing"""
        try:
            result = self.execute("""
                SELECT 
                    c.nama_customer,
                    COUNT(dc.barang_id) as jumlah_barang,
                    SUM(dc.colli_amount) as total_colli,
                    SUM(COALESCE(dc.total_harga, 0)) as total_nilai,
                    SUM(b.m3_barang * dc.colli_amount) as total_volume,
                    SUM(b.ton_barang * dc.colli_amount) as total_berat
                FROM detail_container dc
                JOIN barang b ON dc.barang_id = b.barang_id
                JOIN customers c ON b.customer_id = c.customer_id
                WHERE dc.container_id = ?
                GROUP BY c.customer_id, c.nama_customer
                ORDER BY total_nilai DESC
            """, (container_id,))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting customer container summary with pricing: {e}")
            return []

    def get_all_containers_with_value(self):
        """Get all containers with total value"""
        try:
            result = self.execute("""
                SELECT 
                    cont.*,
                    COUNT(dc.barang_id) as jumlah_barang,
                    SUM(COALESCE(dc.total_harga, 0)) as total_nilai
                FROM containers cont
                LEFT JOIN detail_container dc ON cont.container_id = dc.container_id
                GROUP BY cont.container_id
                ORDER BY cont.container_id DESC
            """)
            
            return [dict(container) for container in result]
            
        except Exception as e:
            logger.error(f"Error getting containers with value: {e}")
            return self.get_all_containers()  # Fallback to original method

    def get_pricing_report_by_date_range(self, start_date, end_date):
        """Get pricing report for containers within date range"""
        try:
            result = self.execute("""
                SELECT 
                    cont.container_id,
                    cont.container,
                    cont.destination,
                    cont.etd_sub,
                    COUNT(dc.barang_id) as jumlah_barang,
                    SUM(dc.colli_amount) as total_colli,
                    SUM(COALESCE(dc.total_harga, 0)) as total_nilai
                FROM containers cont
                LEFT JOIN detail_container dc ON cont.container_id = dc.container_id
                WHERE cont.etd_sub BETWEEN ? AND ?
                GROUP BY cont.container_id
                HAVING total_nilai > 0
                ORDER BY cont.etd_sub DESC
            """, (start_date, end_date))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting pricing report: {e}")
            return []

    # BACKWARD COMPATIBILITY - Override existing methods
    def assign_barang_to_container_with_colli(self, barang_id, container_id, colli_amount):
        """Original method - now calls the pricing version with 0 prices for backward compatibility"""
        return self.assign_barang_to_container_with_pricing(
            barang_id, container_id, colli_amount, 0, 0
        )

    def get_barang_in_container_with_colli(self, container_id):
        """Override existing method to include pricing data for backward compatibility"""
        try:
            # Get with pricing data but return in original format
            result = self.get_barang_in_container_with_colli_and_pricing(container_id)
            return result
        except Exception as e:
            logger.error(f"Error in get_barang_in_container_with_colli: {e}")
            # Fallback to basic query without pricing if needed
            try:
                result = self.execute("""
                    SELECT 
                        b.barang_id,
                        b.nama_barang,
                        b.jenis_barang,
                        b.panjang_barang,
                        b.lebar_barang,
                        b.tinggi_barang,
                        b.m3_barang,
                        b.ton_barang,
                        c.nama_customer,
                        dc.colli_amount,
                        dc.assigned_at
                    FROM detail_container dc
                    JOIN barang b ON dc.barang_id = b.barang_id
                    JOIN customers c ON b.customer_id = c.customer_id
                    WHERE dc.container_id = ?
                    ORDER BY dc.assigned_at DESC
                """, (container_id,))
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback error: {fallback_error}")
                return []

    # HELPER METHODS UNTUK PRICING
    def bulk_update_container_pricing(self, container_id, pricing_data):
        """Update pricing for multiple barang in container
        pricing_data: dict {barang_id: {'harga_per_unit': x, 'total_harga': y}}
        """
        try:
            success_count = 0
            error_count = 0
            
            for barang_id, price_data in pricing_data.items():
                try:
                    self.update_barang_pricing_in_container(
                        barang_id, 
                        container_id, 
                        price_data['harga_per_unit'], 
                        price_data['total_harga']
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error updating pricing for barang {barang_id}: {e}")
                    error_count += 1
            
            logger.info(f"Bulk pricing update: {success_count} success, {error_count} errors")
            return {'success': success_count, 'error': error_count}
            
        except Exception as e:
            logger.error(f"Error in bulk_update_container_pricing: {e}")
            return {'success': 0, 'error': len(pricing_data)}

    def get_container_pricing_summary(self, container_id):
        """Get detailed pricing summary for a container"""
        try:
            # Get container info
            container = self.get_container_by_id(container_id)
            if not container:
                return None
            
            # Get total values
            total_value = self.get_container_total_value(container_id)
            
            # Get customer breakdown
            customer_summary = self.get_customer_container_summary_with_pricing(container_id)
            
            # Get item count
            item_count = self.execute_one("""
                SELECT COUNT(*) as count, SUM(colli_amount) as total_colli
                FROM detail_container WHERE container_id = ?
            """, (container_id,))
            
            return {
                'container': container,
                'total_value': total_value,
                'customer_summary': [dict(row) for row in customer_summary],
                'total_items': item_count['count'] if item_count else 0,
                'total_colli': item_count['total_colli'] if item_count else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting container pricing summary: {e}")
            return None

    def search_containers_by_value_range(self, min_value=0, max_value=None):
        """Search containers by value range"""
        try:
            if max_value is None:
                result = self.execute("""
                    SELECT 
                        cont.*,
                        SUM(COALESCE(dc.total_harga, 0)) as total_nilai
                    FROM containers cont
                    LEFT JOIN detail_container dc ON cont.container_id = dc.container_id
                    GROUP BY cont.container_id
                    HAVING total_nilai >= ?
                    ORDER BY total_nilai DESC
                """, (min_value,))
            else:
                result = self.execute("""
                    SELECT 
                        cont.*,
                        SUM(COALESCE(dc.total_harga, 0)) as total_nilai
                    FROM containers cont
                    LEFT JOIN detail_container dc ON cont.container_id = dc.container_id
                    GROUP BY cont.container_id
                    HAVING total_nilai BETWEEN ? AND ?
                    ORDER BY total_nilai DESC
                """, (min_value, max_value))
            
            return [dict(container) for container in result]
            
        except Exception as e:
            logger.error(f"Error searching containers by value range: {e}")
            return []

    def get_top_value_containers(self, limit=10):
        """Get top containers by value"""
        try:
            result = self.execute("""
                SELECT 
                    cont.*,
                    SUM(COALESCE(dc.total_harga, 0)) as total_nilai,
                    COUNT(dc.barang_id) as jumlah_barang
                FROM containers cont
                LEFT JOIN detail_container dc ON cont.container_id = dc.container_id
                GROUP BY cont.container_id
                HAVING total_nilai > 0
                ORDER BY total_nilai DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(container) for container in result]
            
        except Exception as e:
            logger.error(f"Error getting top value containers: {e}")
            return []

    def get_customer_total_value_by_period(self, customer_id, start_date, end_date):
        """Get total value for a customer within date range"""
        try:
            result = self.execute_one("""
                SELECT 
                    c.nama_customer,
                    SUM(COALESCE(dc.total_harga, 0)) as total_nilai,
                    COUNT(DISTINCT cont.container_id) as jumlah_container,
                    COUNT(dc.barang_id) as jumlah_barang
                FROM customers c
                JOIN barang b ON c.customer_id = b.customer_id
                JOIN detail_container dc ON b.barang_id = dc.barang_id
                JOIN containers cont ON dc.container_id = cont.container_id
                WHERE c.customer_id = ? AND cont.etd_sub BETWEEN ? AND ?
            """, (customer_id, start_date, end_date))
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error getting customer total value by period: {e}")
            return None

# Usage example with error handling and pricing features
if __name__ == "__main__":
    try:
        # Initialize database
        db = AppDatabase()
        
        # Test user creation
        try:
            user_id = db.create_user("testuser", "password123", "test@example.com")
            print(f"Created user with ID: {user_id}")
        except (ValueError, DatabaseError) as e:
            print(f"User creation failed: {e}")
        
        # Test authentication
        try:
            user = db.authenticate_user("admin", "admin123")
            print(f"Authenticated user: {user['username'] if user else 'Failed'}")
        except (ValueError, DatabaseError) as e:
            print(f"Authentication failed: {e}")
        
        # Test customer creation
        try:
            customer_id = db.create_customer("PT. Test Company", "Jl. Test No. 123")
            print(f"Created customer with ID: {customer_id}")
        except (ValueError, DatabaseError) as e:
            print(f"Customer creation failed: {e}")
        
        # Test container creation
        try:
            container_id = db.create_container(
                feeder="EVER GIVEN",
                destination="JAKARTA",
                container="TCLU1234567"
            )
            print(f"Created container with ID: {container_id}")
        except DatabaseError as e:
            print(f"Container creation failed: {e}")
        
        # Test barang creation
        if 'customer_id' in locals():
            try:
                barang_id = db.create_barang(
                    customer_id=customer_id,
                    nama_barang="Elektronik",
                    panjang_barang=100,
                    lebar_barang=50,
                    tinggi_barang=30,
                    m3_barang=0.15,
                    ton_barang=0.5,
                    col_barang=10,
                    harga_m3=1000000
                )
                print(f"Created barang with ID: {barang_id}")
                
                # Test assign barang to container WITH PRICING
                if 'container_id' in locals() and 'barang_id' in locals():
                    try:
                        assigned = db.assign_barang_to_container_with_pricing(
                            barang_id, container_id, 5, 150000, 750000
                        )
                        print(f"Barang assigned to container with pricing: {assigned}")
                        
                        # Test get container total value
                        total_value = db.get_container_total_value(container_id)
                        print(f"Container total value: Rp {total_value:,.0f}")
                        
                    except (ValueError, DatabaseError) as e:
                        print(f"Assignment with pricing failed: {e}")
                        
            except (ValueError, DatabaseError) as e:
                print(f"Barang creation failed: {e}")
        
        # Get dashboard stats
        try:
            stats = db.get_dashboard_stats()
            print(f"Dashboard stats: {stats}")
        except DatabaseError as e:
            print(f"Failed to get dashboard stats: {e}")
            
        # Test pricing features
        try:
            containers_with_value = db.get_all_containers_with_value()
            print(f"Containers with value: {len(containers_with_value)}")
            
            top_containers = db.get_top_value_containers(5)
            print(f"Top 5 value containers: {len(top_containers)}")
            
        except DatabaseError as e:
            print(f"Failed to test pricing features: {e}")
            
    except DatabaseError as e:
        print(f"Database initialization failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}")