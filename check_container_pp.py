import sqlite3

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

# Check barang with container_pp values
cursor.execute("""
    SELECT barang_id, nama_barang, container_pp, container_pd, container_dd, container_barang
    FROM barang
    WHERE container_pp IS NOT NULL AND container_pp > 0
    LIMIT 5
""")

print("Barang with container_pp:")
print("-" * 100)
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Nama: {row[1]}, Container_PP: {row[2]:,.0f}, Container_PD: {row[3] or 0:,.0f}, Container_DD: {row[4] or 0:,.0f}, Container_Barang: {row[5]}")

conn.close()
