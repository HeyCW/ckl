import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

print("Restoring container pricing columns to barang table...")
print(f"Database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check current columns
    cursor.execute("PRAGMA table_info(barang)")
    current_cols = [col[1] for col in cursor.fetchall()]
    print(f"\nCurrent columns: {', '.join(current_cols)}")

    # Add container_pp, container_pd, container_dd if not exists
    if 'container_pp' not in current_cols:
        print("\nAdding container_pp column...")
        cursor.execute("ALTER TABLE barang ADD COLUMN container_pp REAL")
        print("  Added container_pp")

    if 'container_pd' not in current_cols:
        print("Adding container_pd column...")
        cursor.execute("ALTER TABLE barang ADD COLUMN container_pd REAL")
        print("  Added container_pd")

    if 'container_dd' not in current_cols:
        print("Adding container_dd column...")
        cursor.execute("ALTER TABLE barang ADD COLUMN container_dd REAL")
        print("  Added container_dd")

    conn.commit()

    # Verify
    cursor.execute("PRAGMA table_info(barang)")
    new_cols = [col[1] for col in cursor.fetchall()]
    print(f"\nNew columns: {', '.join(new_cols)}")
    print("\nSuccessfully restored container pricing columns!")

except Exception as e:
    print(f"\nError: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nDone!")
