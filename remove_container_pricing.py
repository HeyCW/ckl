import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

print("Removing container pricing columns from barang table...")
print(f"Database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Clear the container pricing data first
    print("\n1. Clearing container pricing data...")
    cursor.execute("""
        UPDATE barang
        SET container_pp = NULL,
            container_pd = NULL,
            container_dd = NULL
    """)
    print(f"   Cleared container pricing data from {cursor.rowcount} rows")

    # Step 2: Create new table without container pricing columns
    print("\n2. Creating new barang table structure...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barang_new (
            barang_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pengirim TEXT NOT NULL,
            penerima TEXT NOT NULL,
            nama_barang TEXT NOT NULL,
            panjang_barang REAL,
            lebar_barang REAL,
            tinggi_barang REAL,
            m3_barang REAL,
            ton_barang REAL,
            container_barang REAL,
            m3_pp REAL,
            m3_pd REAL,
            m3_dd REAL,
            ton_pp REAL,
            ton_pd REAL,
            ton_dd REAL,
            col_pp INTEGER,
            col_pd INTEGER,
            col_dd INTEGER,
            pajak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Step 3: Copy data from old table to new table (excluding container pricing columns)
    print("\n3. Copying data to new table...")
    cursor.execute("""
        INSERT INTO barang_new (
            barang_id, pengirim, penerima, nama_barang,
            panjang_barang, lebar_barang, tinggi_barang, m3_barang, ton_barang, container_barang,
            m3_pp, m3_pd, m3_dd, ton_pp, ton_pd, ton_dd,
            col_pp, col_pd, col_dd, pajak, created_at, updated_at
        )
        SELECT
            barang_id, pengirim, penerima, nama_barang,
            panjang_barang, lebar_barang, tinggi_barang, m3_barang, ton_barang, container_barang,
            m3_pp, m3_pd, m3_dd, ton_pp, ton_pd, ton_dd,
            col_pp, col_pd, col_dd, pajak, created_at, updated_at
        FROM barang
    """)
    print(f"   Copied {cursor.rowcount} rows")

    # Step 4: Drop old table
    print("\n4. Dropping old table...")
    cursor.execute("DROP TABLE barang")

    # Step 5: Rename new table to barang
    print("\n5. Renaming new table...")
    cursor.execute("ALTER TABLE barang_new RENAME TO barang")

    # Commit changes
    conn.commit()
    print("\n✓ Successfully removed container pricing columns!")
    print("  - container_pp")
    print("  - container_pd")
    print("  - container_dd")

except Exception as e:
    print(f"\n✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nDone!")
