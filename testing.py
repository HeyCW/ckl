import sqlite3
import os

def check_database_schema(db_path="data/app.db"):
    """Check and display database schema"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"📊 DATABASE SCHEMA: {db_path}")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found in database")
            return
        
        print(f"📋 Found {len(tables)} table(s):")
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Get schema for each table
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️  TABLE: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("COLUMNS:")
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                null_str = "NOT NULL" if not_null else "NULL"
                pk_str = "PRIMARY KEY" if pk else ""
                default_str = f"DEFAULT {default}" if default else ""
                
                extras = " ".join(filter(None, [null_str, default_str, pk_str]))
                print(f"   {name:<20} {data_type:<15} {extras}")
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print("\nFOREIGN KEYS:")
                for fk in foreign_keys:
                    id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                    print(f"   {from_col} -> {table}.{to_col}")
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()
            
            if indexes:
                print("\nINDEXES:")
                for idx in indexes:
                    seq, name, unique, origin, partial = idx
                    unique_str = "UNIQUE" if unique else ""
                    print(f"   {name} {unique_str}")
            
            # Show sample data (first 3 rows)
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"\nROW COUNT: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                
                if sample_data:
                    print("\nSAMPLE DATA (first 5 rows):")
                    col_names = [desc[0] for desc in cursor.description]
                    
                    # Print headers
                    header = " | ".join(f"{name:<15}" for name in col_names)
                    print(f"   {header}")
                    print(f"   {'-' * len(header)}")
                    
                    # Print data
                    for row in sample_data:
                        row_str = " | ".join(f"{str(val):<15}" for val in row)
                        print(f"   {row_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def show_table_details(db_path="data/app.db", table_name=None):
    """Show detailed info for specific table"""
    
    if not table_name:
        print("❌ Please specify table name")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"🔍 DETAILED VIEW: {table_name}")
        print("=" * 60)
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"❌ Table '{table_name}' not found")
            return
        
        # Get CREATE statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_sql = cursor.fetchone()[0]
        
        print("CREATE STATEMENT:")
        print(create_sql)
        print()
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        all_data = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        print(f"ALL DATA ({len(all_data)} rows):")
        
        if all_data:
            # Print headers
            header = " | ".join(f"{name:<15}" for name in col_names)
            print(header)
            print("-" * len(header))
            
            # Print all rows
            for row in all_data:
                row_str = " | ".join(f"{str(val):<15}" for val in row)
                print(row_str)
        else:
            print("No data found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_sample_queries(db_path="data/app.db"):
    """Generate sample SQL queries for your database"""
    
    print("=" * 60)
    print("📝 SAMPLE SQL QUERIES")
    print("=" * 60)
    
    queries = [
        ("Show all users", "SELECT * FROM users;"),
        ("Show active users only", "SELECT username, email, role FROM users WHERE is_active = 1;"),
        ("Count users by role", "SELECT role, COUNT(*) as count FROM users GROUP BY role;"),
        ("Show recent login activity", "SELECT username, last_login, login_count FROM users ORDER BY last_login DESC;"),
        ("Show user documents", """
            SELECT u.username, d.title, d.created_at 
            FROM users u 
            JOIN documents d ON u.id = d.user_id 
            ORDER BY d.created_at DESC;
        """),
        ("Show active sessions", "SELECT * FROM sessions WHERE expires_at > datetime('now');"),
        ("Show user settings", """
            SELECT u.username, s.setting_key, s.setting_value 
            FROM users u 
            JOIN app_settings s ON u.id = s.user_id;
        """),
    ]
    
    for description, query in queries:
        print(f"\n-- {description}")
        print(query)

def interactive_db_explorer(db_path="data/app.db"):
    """Interactive database explorer"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print("=" * 60)
    print("🔍 INTERACTIVE DATABASE EXPLORER")
    print("=" * 60)
    print("Commands:")
    print("  tables    - Show all tables")
    print("  schema    - Show full schema")
    print("  table <name> - Show table details")
    print("  query <sql>  - Execute custom SQL")
    print("  samples   - Show sample queries")
    print("  quit      - Exit")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    while True:
        try:
            command = input("\ndb> ").strip()
            
            if command.lower() == 'quit':
                break
            elif command.lower() == 'tables':
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print("\nTables:")
                for table in tables:
                    print(f"  • {table[0]}")
            
            elif command.lower() == 'schema':
                check_database_schema(db_path)
            
            elif command.lower().startswith('table '):
                table_name = command[6:].strip()
                show_table_details(db_path, table_name)
            
            elif command.lower().startswith('query '):
                sql = command[6:].strip()
                cursor = conn.cursor()
                cursor.execute(sql)
                results = cursor.fetchall()
                
                if results:
                    # Print column names
                    col_names = [desc[0] for desc in cursor.description]
                    header = " | ".join(f"{name:<15}" for name in col_names)
                    print(header)
                    print("-" * len(header))
                    
                    # Print results
                    for row in results:
                        row_str = " | ".join(f"{str(val):<15}" for val in row)
                        print(row_str)
                else:
                    print("No results")
            
            elif command.lower() == 'samples':
                create_sample_queries(db_path)
            
            else:
                print("❌ Unknown command. Type 'quit' to exit.")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    conn.close()
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    # Quick schema check
    check_database_schema()
    
    print("\n" + "=" * 60)
    
    # Sample queries
    create_sample_queries()
    
    print("\n" + "=" * 60)
    print("💡 Want to explore interactively? Run:")
    print("   interactive_db_explorer()")
    
    # Uncomment to start interactive mode
    # interactive_db_explorer()