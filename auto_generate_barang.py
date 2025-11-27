"""
Script untuk auto generate sample data barang dan memasukkannya ke container
"""

import sqlite3
from datetime import datetime, timedelta
import random

# Path ke database
DB_PATH = "data/app.db"

def create_sample_customers():
    """Buat sample customers untuk pengirim dan penerima"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("MEMBUAT SAMPLE CUSTOMERS (Pengirim & Penerima)")
    print("="*60)

    # Sample pengirim (senders)
    pengirim_list = [
        ("PT. Sejahtera Abadi", "Jl. Industri No. 123, Jakarta"),
        ("CV. Maju Jaya", "Jl. Raya Bogor KM 5, Bogor"),
        ("PT. Karya Mandiri", "Jl. Pahlawan No. 45, Surabaya"),
        ("UD. Berkah Jaya", "Jl. Merdeka No. 78, Bandung"),
        ("PT. Indah Cargo", "Jl. Pelabuhan No. 12, Semarang")
    ]

    # Sample penerima (receivers)
    penerima_list = [
        ("PT. Sukses Makmur", "Jl. Tanjung Priok No. 88, Jakarta Utara"),
        ("CV. Harapan Maju", "Jl. Industri Raya No. 234, Tangerang"),
        ("PT. Cahaya Sentosa", "Jl. Pemuda No. 56, Bekasi"),
        ("UD. Rezeki Lancar", "Jl. Gatot Subroto No. 99, Jakarta Selatan"),
        ("PT. Bahagia Sejahtera", "Jl. Sudirman No. 120, Jakarta Pusat")
    ]

    all_customers = pengirim_list + penerima_list
    inserted_ids = []

    for nama, alamat in all_customers:
        try:
            # Cek apakah customer sudah ada
            cursor.execute("SELECT customer_id FROM customers WHERE nama_customer = ?", (nama,))
            existing = cursor.fetchone()

            if existing:
                print(f"SKIP: {nama} (sudah ada)")
                inserted_ids.append(existing[0])
            else:
                cursor.execute("""
                    INSERT INTO customers (nama_customer, alamat_customer)
                    VALUES (?, ?)
                """, (nama, alamat))
                customer_id = cursor.lastrowid
                inserted_ids.append(customer_id)
                print(f"OK: {nama} (ID: {customer_id})")
        except Exception as e:
            print(f"ERROR: {nama} - {e}")

    conn.commit()
    conn.close()

    print(f"\nTotal customers: {len(inserted_ids)}")
    return inserted_ids


def generate_sample_barang():
    """Generate sample barang dengan berbagai jenis"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("MEMBUAT SAMPLE BARANG")
    print("="*60)

    # Ambil customer IDs untuk pengirim dan penerima
    cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 10")
    customers = [row[0] for row in cursor.fetchall()]

    if len(customers) < 2:
        print("ERROR: Minimal butuh 2 customers di database!")
        conn.close()
        return []

    # Sample barang dengan berbagai jenis
    barang_types = [
        {"nama": "Elektronik - TV LED 42 inch", "range": (0.5, 1.5), "ton": (0.1, 0.3)},
        {"nama": "Furniture - Meja Kayu Jati", "range": (1.0, 2.5), "ton": (0.3, 0.8)},
        {"nama": "Tekstil - Kain Cotton", "range": (0.3, 1.0), "ton": (0.1, 0.5)},
        {"nama": "Alat Berat - Mesin Produksi", "range": (3.0, 8.0), "ton": (1.5, 5.0)},
        {"nama": "Bahan Kimia - Cat Industrial", "range": (0.5, 1.5), "ton": (0.5, 1.2)},
        {"nama": "Makanan - Mie Instan", "range": (0.8, 2.0), "ton": (0.3, 0.9)},
        {"nama": "Minuman - Air Mineral Kemasan", "range": (1.0, 2.5), "ton": (0.8, 1.5)},
        {"nama": "Spare Part - Komponen Mobil", "range": (0.4, 1.2), "ton": (0.2, 0.6)},
        {"nama": "Plastik - Pallet Plastik", "range": (0.6, 1.8), "ton": (0.1, 0.4)},
        {"nama": "Kertas - Kertas HVS A4", "range": (1.5, 3.0), "ton": (0.5, 1.0)}
    ]

    barang_ids = []

    # Generate 20-30 barang
    total_barang = random.randint(20, 30)

    for i in range(total_barang):
        # Pilih random barang type
        barang_type = random.choice(barang_types)
        nama_barang = barang_type["nama"]

        # Random pengirim dan penerima
        pengirim_id = random.choice(customers)
        penerima_id = random.choice([c for c in customers if c != pengirim_id])

        # Generate dimensi
        panjang = round(random.uniform(100, 300), 2)
        lebar = round(random.uniform(80, 250), 2)
        tinggi = round(random.uniform(80, 200), 2)

        # Hitung m3 dari dimensi (dalam cm, konversi ke m3)
        m3 = round((panjang * lebar * tinggi) / 1000000, 3)

        # Generate ton
        ton = round(random.uniform(barang_type["ton"][0], barang_type["ton"][1]), 3)

        # Container barang (20' atau 40')
        container_barang = random.choice([20, 40])

        # Generate pricing untuk PP, PD, DD
        # M3 pricing
        m3_pp = round(random.uniform(300000, 800000), 0)
        m3_pd = round(m3_pp * random.uniform(0.7, 0.9), 0)
        m3_dd = round(m3_pp * random.uniform(0.6, 0.8), 0)

        # TON pricing
        ton_pp = round(random.uniform(500000, 1500000), 0)
        ton_pd = round(ton_pp * random.uniform(0.7, 0.9), 0)
        ton_dd = round(ton_pp * random.uniform(0.6, 0.8), 0)

        # Colli (jumlah barang)
        col_pp = random.randint(5, 50)
        col_pd = random.randint(3, 30)
        col_dd = random.randint(2, 20)

        # Container pricing (per container)
        container_pp = round(random.uniform(5000000, 15000000), 0)
        container_pd = round(container_pp * random.uniform(0.7, 0.9), 0)
        container_dd = round(container_pp * random.uniform(0.6, 0.8), 0)

        # Pajak (70% punya pajak)
        pajak = 1 if random.random() < 0.7 else 0

        try:
            cursor.execute("""
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
            """, (
                pengirim_id, penerima_id, nama_barang,
                panjang, lebar, tinggi,
                m3, ton, container_barang,
                m3_pp, m3_pd, m3_dd,
                ton_pp, ton_pd, ton_dd,
                col_pp, col_pd, col_dd,
                container_pp, container_pd, container_dd,
                pajak
            ))

            barang_id = cursor.lastrowid
            barang_ids.append(barang_id)
            pajak_status = "PAJAK" if pajak == 1 else "NO-TAX"
            print(f"OK: ID {barang_id} | {nama_barang} | {m3:.2f}m3 | {ton:.2f}ton | [{pajak_status}]")

        except Exception as e:
            print(f"ERROR: {nama_barang} - {e}")

    conn.commit()
    conn.close()

    print(f"\nTotal barang dibuat: {len(barang_ids)}")
    return barang_ids


def assign_barang_to_containers():
    """Assign barang ke container yang ada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("MEMASUKKAN BARANG KE CONTAINER")
    print("="*60)

    # Ambil semua containers
    cursor.execute("SELECT container_id, container FROM containers ORDER BY container_id")
    containers = cursor.fetchall()

    if not containers:
        print("ERROR: Tidak ada container di database!")
        conn.close()
        return

    print(f"\nDitemukan {len(containers)} container")

    # Ambil semua barang yang belum di-assign
    cursor.execute("""
        SELECT b.barang_id, b.nama_barang, b.m3_barang, b.ton_barang,
               b.m3_pp, b.ton_pp, b.container_pp, b.pajak,
               c.nama_customer as penerima_name
        FROM barang b
        LEFT JOIN customers c ON b.penerima = c.customer_id
        WHERE b.barang_id NOT IN (SELECT barang_id FROM detail_container)
        ORDER BY b.barang_id
    """)
    barang_list = cursor.fetchall()

    if not barang_list:
        print("SKIP: Semua barang sudah di-assign ke container")
        conn.close()
        return

    print(f"Ditemukan {len(barang_list)} barang yang belum di-assign")

    inserted = 0

    # Distribute barang ke containers secara merata
    for idx, barang in enumerate(barang_list):
        barang_id = barang[0]
        nama_barang = barang[1]
        m3 = barang[2]
        ton = barang[3]
        m3_pp = barang[4]
        ton_pp = barang[5]
        container_pp = barang[6]
        pajak = barang[7]
        penerima_name = barang[8]

        # Pilih container secara round-robin
        container = containers[idx % len(containers)]
        container_id = container[0]
        container_no = container[1]

        # Random satuan (M3, TON, atau CONTAINER)
        satuan = random.choice(['M3', 'TON', 'CONTAINER'])

        # Random door type (PP, PD, atau DD)
        door_type = random.choice(['PP', 'PD', 'DD'])

        # Random colli amount (1-10)
        colli_amount = random.randint(1, 10)

        # Hitung harga based on satuan and door_type
        if satuan == 'M3':
            harga_per_unit = m3_pp if door_type == 'PP' else (m3_pp * 0.8 if door_type == 'PD' else m3_pp * 0.7)
        elif satuan == 'TON':
            harga_per_unit = ton_pp if door_type == 'PP' else (ton_pp * 0.8 if door_type == 'PD' else ton_pp * 0.7)
        else:  # CONTAINER
            harga_per_unit = container_pp if door_type == 'PP' else (container_pp * 0.8 if door_type == 'PD' else container_pp * 0.7)

        total_harga = harga_per_unit * colli_amount

        # Random tanggal dalam 30 hari terakhir
        days_ago = random.randint(0, 30)
        tanggal = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

        try:
            # Insert ke detail_container
            cursor.execute("""
                INSERT INTO detail_container (
                    tanggal, barang_id, container_id, satuan, door_type,
                    colli_amount, harga_per_unit, total_harga
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tanggal, barang_id, container_id, satuan, door_type,
                colli_amount, harga_per_unit, total_harga
            ))

            # Jika barang punya pajak, insert ke barang_tax
            if pajak == 1:
                ppn_rate = 0.011  # PPN 1.1%
                pph23_rate = 0.02  # PPH 23 2%
                ppn_amount = total_harga * ppn_rate
                pph23_amount = total_harga * pph23_rate
                total_tax = ppn_amount + pph23_amount

                cursor.execute("""
                    INSERT INTO barang_tax (
                        container_id, barang_id, penerima, total_nilai_barang,
                        ppn_rate, pph23_rate, ppn_amount, pph23_amount, total_tax
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    container_id, barang_id, penerima_name, total_harga,
                    ppn_rate, pph23_rate, ppn_amount, pph23_amount, total_tax
                ))

            pajak_mark = "[TAX]" if pajak == 1 else ""
            print(f"OK: {nama_barang[:30]:30} -> {container_no} | {satuan:9} | {door_type} | Rp {total_harga:>12,.0f} {pajak_mark}")
            inserted += 1

        except Exception as e:
            print(f"ERROR: {nama_barang} - {e}")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print(f"SELESAI!")
    print(f"   - Berhasil insert: {inserted} barang ke container")
    print("="*60)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("    AUTO GENERATE BARANG & ASSIGN KE CONTAINER")
    print("="*60)

    # Step 1: Buat sample customers
    create_sample_customers()

    # Step 2: Generate sample barang
    barang_ids = generate_sample_barang()

    # Step 3: Assign barang ke containers
    if barang_ids:
        assign_barang_to_containers()

    print("\nSEMUA PROSES SELESAI!")
    print("Buka aplikasi dan refresh untuk melihat data baru!\n")


if __name__ == "__main__":
    main()
