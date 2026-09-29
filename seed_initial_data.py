import secrets

from src.models.database import AppDatabase
from src.utils.password_hash import hash_password

db = AppDatabase()

print("Seeding initial data to database...")
print(f"Backend: {db.backend_name}\n")

seeded_credentials = []

try:
    # Everything below runs as one transaction: if any insert fails
    # partway through (a bad row, a dropped connection), the whole
    # batch is rolled back instead of leaving the database with, say,
    # customers but no barang referencing them.
    with db.transaction() as tx:
        # 1. USERS - init_db() already creates the default 'admin' and
        # 'owner' accounts (fixed passwords, see DEFAULT_ACCOUNTS in
        # src/models/database.py), so this only adds a 'staff' account
        # on top of those. Its password is
        # randomly generated (not a fixed string) and printed once at
        # the end - a seed script that writes known credentials into a
        # real database is itself a security hole.
        print("1. Creating users...")
        existing = tx.execute_one("SELECT id FROM users WHERE username = ?", ("staff",))
        if existing:
            print("   Skipped: 'staff' user already exists")
        else:
            password = secrets.token_urlsafe(12)
            password_hash = hash_password(password)
            tx.execute_insert('''
                INSERT INTO users (username, password, email, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', ("staff", password_hash, "staff@example.com", "staff", 1))
            seeded_credentials.append(("staff", password, "staff"))
            print("   Created user: staff (staff)")

        # 2. PENGIRIM - Create sender companies
        print("\n2. Creating pengirim (senders)...")
        pengirim_list = [
            'PT Berkah Jaya',
            'PT Maju Bersama',
            'CV Sentosa Makmur',
            'PT Global Trading',
            'PT Indo Cargo',
        ]

        for pengirim in pengirim_list:
            tx.execute_insert('INSERT INTO pengirim (nama_pengirim) VALUES (?)', (pengirim,))
            print(f"   Created pengirim: {pengirim}")

        # 3. CUSTOMERS - Create customer companies
        print("\n3. Creating customers...")
        customers = [
            ('PT Sinar Harapan', 'Jakarta'),
            ('CV Mitra Abadi', 'Surabaya'),
            ('PT Cahaya Timur', 'Makassar'),
            ('PT Nusa Sejahtera', 'Bali'),
            ('CV Bintang Utara', 'Medan'),
            ('PT Samudra Raya', 'Pontianak'),
            ('PT Anugrah Mandiri', 'Balikpapan'),
        ]

        for nama, alamat in customers:
            tx.execute_insert('''
                INSERT INTO customers (nama_customer, alamat_customer)
                VALUES (?, ?)
            ''', (nama, alamat))
            print(f"   Created customer: {nama} ({alamat})")

        # 4. KAPALS - Create ships
        print("\n4. Creating kapals (ships)...")
        kapals = [
            ('SPIL', 'KM TANTO', 'Makassar', '2025-01-15', '2025-01-10', '2025-01-11', '2025-01-13'),
            ('TANTO', 'KM MERATUS', 'Surabaya', '2025-01-18', '2025-01-13', '2025-01-14', '2025-01-16'),
            ('PELNI', 'KM PELNI NUSANTARA', 'Bali', '2025-01-20', '2025-01-15', '2025-01-16', '2025-01-18'),
        ]

        for shipping_line, feeder, destination, etd_sub, cls, open_date, full_date in kapals:
            tx.execute_insert('''
                INSERT INTO kapals (shipping_line, feeder, destination, etd_sub, cls, "open", "full")
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (shipping_line, feeder, destination, etd_sub, cls, open_date, full_date))
            print(f"   Created kapal: {feeder} ({shipping_line}) -> {destination}")

        # 5. BARANG - Create goods with comprehensive pricing
        print("\n5. Creating barang (goods)...")

        barang_data = [
            {
                'pengirim': 'CV Mitra Abadi',
                'penerima': 'PT Sinar Harapan',
                'nama_barang': 'Elektronik - TV LED 43 inch',
                'panjang': 110.0,
                'lebar': 70.0,
                'tinggi': 15.0,
                'm3_barang': 0.115,
                'ton_barang': 0.015,
                'container_barang': 0.003,  # Berapa bagian dari container (1 container = 33 CBM)
                'm3_pp': 850000,
                'm3_pd': 1050000,
                'm3_dd': 1250000,
                'ton_pp': 5000000,
                'ton_pd': 6000000,
                'ton_dd': 7000000,
                'col_pp': 150000,
                'col_pd': 200000,
                'col_dd': 250000,
                'container_pp': 8500000,
                'container_pd': 10500000,
                'container_dd': 12500000,
                'pajak': 0,
            },
            {
                'pengirim': 'PT Cahaya Timur',
                'penerima': 'CV Mitra Abadi',
                'nama_barang': 'Furnitur - Meja Kantor',
                'panjang': 150.0,
                'lebar': 80.0,
                'tinggi': 75.0,
                'm3_barang': 0.9,
                'ton_barang': 0.05,
                'container_barang': 0.027,
                'm3_pp': 650000,
                'm3_pd': 800000,
                'm3_dd': 950000,
                'ton_pp': 3500000,
                'ton_pd': 4200000,
                'ton_dd': 5000000,
                'col_pp': 100000,
                'col_pd': 150000,
                'col_dd': 200000,
                'container_pp': 7000000,
                'container_pd': 9000000,
                'container_dd': 11000000,
                'pajak': 0,
            },
            {
                'pengirim': 'PT Nusa Sejahtera',
                'penerima': 'PT Cahaya Timur',
                'nama_barang': 'Tekstil - Kain Cotton Roll',
                'panjang': 120.0,
                'lebar': 30.0,
                'tinggi': 30.0,
                'm3_barang': 0.108,
                'ton_barang': 0.025,
                'container_barang': 0.0033,
                'm3_pp': 750000,
                'm3_pd': 920000,
                'm3_dd': 1100000,
                'ton_pp': 4000000,
                'ton_pd': 4800000,
                'ton_dd': 5600000,
                'col_pp': 120000,
                'col_pd': 170000,
                'col_dd': 220000,
                'container_pp': 7500000,
                'container_pd': 9500000,
                'container_dd': 11500000,
                'pajak': 1,
            },
            {
                'pengirim': 'CV Bintang Utara',
                'penerima': 'PT Nusa Sejahtera',
                'nama_barang': 'Makanan - Mie Instan (1 Kontainer)',
                'panjang': 600.0,
                'lebar': 240.0,
                'tinggi': 240.0,
                'm3_barang': 33.0,  # Full container
                'ton_barang': 15.0,
                'container_barang': 1.0,  # Exactly 1 container
                'm3_pp': 500000,
                'm3_pd': 600000,
                'm3_dd': 700000,
                'ton_pp': 1200000,
                'ton_pd': 1400000,
                'ton_dd': 1600000,
                'col_pp': 80000,
                'col_pd': 100000,
                'col_dd': 120000,
                'container_pp': 16500000,
                'container_pd': 19800000,
                'container_dd': 23100000,
                'pajak': 1,
            },
            {
                'pengirim': 'PT Samudra Raya',
                'penerima': 'CV Bintang Utara',
                'nama_barang': 'Spare Part Mesin',
                'panjang': 80.0,
                'lebar': 60.0,
                'tinggi': 40.0,
                'm3_barang': 0.192,
                'ton_barang': 0.08,
                'container_barang': 0.006,
                'm3_pp': 900000,
                'm3_pd': 1100000,
                'm3_dd': 1300000,
                'ton_pp': 5500000,
                'ton_pd': 6600000,
                'ton_dd': 7700000,
                'col_pp': 180000,
                'col_pd': 230000,
                'col_dd': 280000,
                'container_pp': 9000000,
                'container_pd': 11000000,
                'container_dd': 13000000,
                'pajak': 0,
            },
            {
                'pengirim': 'PT Anugrah Mandiri',
                'penerima': 'PT Samudra Raya',
                'nama_barang': 'Peralatan Rumah Tangga',
                'panjang': 50.0,
                'lebar': 40.0,
                'tinggi': 30.0,
                'm3_barang': 0.06,
                'ton_barang': 0.012,
                'container_barang': 0.0018,
                'm3_pp': 700000,
                'm3_pd': 850000,
                'm3_dd': 1000000,
                'ton_pp': 4500000,
                'ton_pd': 5400000,
                'ton_dd': 6300000,
                'col_pp': 110000,
                'col_pd': 160000,
                'col_dd': 210000,
                'container_pp': 7200000,
                'container_pd': 9200000,
                'container_dd': 11200000,
                'pajak': 0,
            },
            {
                'pengirim': 'PT Sinar Harapan',
                'penerima': 'PT Anugrah Mandiri',
                'nama_barang': 'Kertas - HVS A4 (Pallet)',
                'panjang': 100.0,
                'lebar': 100.0,
                'tinggi': 120.0,
                'm3_barang': 1.2,
                'ton_barang': 0.3,
                'container_barang': 0.036,
                'm3_pp': 600000,
                'm3_pd': 750000,
                'm3_dd': 900000,
                'ton_pp': 3000000,
                'ton_pd': 3600000,
                'ton_dd': 4200000,
                'col_pp': 90000,
                'col_pd': 130000,
                'col_dd': 170000,
                'container_pp': 6800000,
                'container_pd': 8800000,
                'container_dd': 10800000,
                'pajak': 1,
            },
        ]

        for barang in barang_data:
            pengirim_row = tx.execute_one(
                "SELECT customer_id FROM customers WHERE nama_customer = ?",
                (barang['pengirim'],)
            )
            penerima_row = tx.execute_one(
                "SELECT customer_id FROM customers WHERE nama_customer = ?",
                (barang['penerima'],)
            )
            pengirim_id = pengirim_row['customer_id'] if pengirim_row else None
            penerima_id = penerima_row['customer_id'] if penerima_row else None

            tx.execute_insert('''
                INSERT INTO barang (
                    pengirim, penerima, nama_barang,
                    panjang_barang, lebar_barang, tinggi_barang,
                    m3_barang, ton_barang, container_barang,
                    m3_pp, m3_pd, m3_dd,
                    ton_pp, ton_pd, ton_dd,
                    col_pp, col_pd, col_dd,
                    container_pp, container_pd, container_dd,
                    pajak
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pengirim_id, penerima_id, barang['nama_barang'],
                barang['panjang'], barang['lebar'], barang['tinggi'],
                barang['m3_barang'], barang['ton_barang'], barang['container_barang'],
                barang['m3_pp'], barang['m3_pd'], barang['m3_dd'],
                barang['ton_pp'], barang['ton_pd'], barang['ton_dd'],
                barang['col_pp'], barang['col_pd'], barang['col_dd'],
                barang['container_pp'], barang['container_pd'], barang['container_dd'],
                barang['pajak'],
            ))
            print(f"   Created barang: {barang['nama_barang']}")

    # Display summary (outside the transaction: it already committed,
    # these are just plain reporting reads)
    print("\n" + "="*60)
    print("SUMMARY - Initial Data Created:")
    print("="*60)

    print(f"Users:      {db.execute_one('SELECT COUNT(*) FROM users')[0]} users")
    print(f"Pengirim:   {db.execute_one('SELECT COUNT(*) FROM pengirim')[0]} senders")
    print(f"Customers:  {db.execute_one('SELECT COUNT(*) FROM customers')[0]} customers")
    print(f"Kapals:     {db.execute_one('SELECT COUNT(*) FROM kapals')[0]} ships")
    print(f"Barang:     {db.execute_one('SELECT COUNT(*) FROM barang')[0]} goods")

    print("="*60)
    print("\nLogin credentials (generated - save these now, they are not stored anywhere else):")
    for username, password, role in seeded_credentials:
        print(f"  {username}/{password}   (role: {role})")
    print("="*60)

    print("\nInitial data seeded successfully!")

except Exception as e:
    print(f"\nError: {e}")
    print("(nothing from this run was committed - the transaction was rolled back)")
    import traceback
    traceback.print_exc()

print(f"\nDatabase ({db.backend_name}) is now ready to use!")
