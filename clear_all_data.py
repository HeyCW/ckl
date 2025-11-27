import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

print("Clearing all data from database...")
print(f"Database: {db_path}\n")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()

    print(f"Found {len(tables)} tables")

    # Disable foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")

    # Delete data from all tables
    for table in tables:
        table_name = table[0]

        # Count rows before delete
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_before = cursor.fetchone()[0]

        if count_before > 0:
            # Delete all rows
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"  {table_name:30} - Deleted {count_before} rows")
        else:
            print(f"  {table_name:30} - Already empty")

    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")

    # Reset autoincrement counters
    cursor.execute("DELETE FROM sqlite_sequence")
    print(f"\n  Reset all autoincrement counters")

    conn.commit()
    print("\n" + "="*60)
    print("All data cleared successfully!")
    print("="*60)

except Exception as e:
    print(f"\nError: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nDatabase is now empty and ready for fresh data.")
