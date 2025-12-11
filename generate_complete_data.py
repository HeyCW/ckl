"""
Script untuk generate complete data:
- 3 container dengan party berbeda (20', 21', 40'HC) sharing JOA yang sama
- Barang untuk setiap container
- Biaya delivery untuk setiap container
- Auto create kapals jika belum ada (tanpa perlu seed terpisah)
"""

import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "data/app.db"


def ensure_kapals_exist(conn):
    """Create sample kapals if table is empty so generator always works"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM kapals")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"OK: Sudah ada {count} kapal")
        return

    sample_kapals = [
        ('SPIL', 'KM TANTO', 'Makassar', '2025-01-15', '2025-01-10', '2025-01-11', '2025-01-13'),
        ('TANTO', 'KM MERATUS', 'Surabaya', '2025-01-18', '2025-01-13', '2025-01-14', '2025-01-16'),
        ('PELNI', 'KM PELNI NUSANTARA', 'Bali', '2025-01-20', '2025-01-15', '2025-01-16', '2025-01-18'),
    ]
    cursor.executemany("""
        INSERT INTO kapals (shipping_line, feeder, destination, etd_sub, cls, open, full)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_kapals)
    conn.commit()
    print(f"Created {len(sample_kapals)} kapal sample")


def generate_containers_with_shared_joa():
    """Generate 3 containers (20', 21', 40'HC) dengan JOA yang sama"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Pastikan kapal tersedia
    ensure_kapals_exist(conn)

    print("\n" + "="*60)
    print("GENERATE CONTAINERS DENGAN SHARED JOA")
    print("="*60)

    # Ambil kapal yang ada
    cursor.execute("SELECT kapal_id, feeder, etd_sub, destination FROM kapals ORDER BY kapal_id LIMIT 5")
    kapals = cursor.fetchall()

    if not kapals:
        print("ERROR: Tidak ada kapal di database!")
        conn.close()
        return []

    print(f"\nDitemukan {len(kapals)} kapal")

    container_prefixes = ["TCLU", "MSCU", "HLBU", "CMAU", "TEMU", "OOLU", "HDMU"]

    # Tentukan berapa set JOA yang mau dibuat (misal 3-5 set)
    num_joa_sets = random.randint(3, 5)

    all_containers = []

    for joa_set in range(num_joa_sets):
        # Generate JOA yang sama untuk 3 container
        ref_joa = f"JOA/{datetime.now().year}/{random.randint(1000, 9999)}"

        # Pilih kapal random
        kapal = random.choice(kapals)
        kapal_id = kapal[0]
        feeder = kapal[1]
        etd = kapal[2] or datetime.now().strftime('%Y-%m-%d')
        destination = kapal[3] or "Surabaya"

        print(f"\n[SET {joa_set + 1}] JOA: {ref_joa} | Kapal: {feeder}")

        # Buat 3 container dengan party berbeda
        for party_type in ["20'", "21'", "40'HC"]:
            # Generate container number
            prefix = random.choice(container_prefixes)
            number = f"{random.randint(100000, 999999)}{random.randint(0, 9)}"
            container_num = f"{prefix}{number}"

            # Generate seal number
            seal = f"SEAL{random.randint(10000, 99999)}"

            try:
                # Cek apakah container number sudah ada
                cursor.execute("SELECT container_id FROM containers WHERE container = ?",
                             (container_num,))
                if cursor.fetchone():
                    print(f"  SKIP: {container_num} (sudah ada)")
                    continue

                # Insert container
                cursor.execute("""
                    INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (kapal_id, etd, party_type, container_num, seal, ref_joa))

                container_id = cursor.lastrowid
                all_containers.append({
                    'container_id': container_id,
                    'container': container_num,
                    'party': party_type,
                    'ref_joa': ref_joa,
                    'kapal_id': kapal_id,
                    'feeder': feeder,
                    'destination': destination
                })

                print(f"  OK: {party_type:4} | {container_num} | {seal}")

            except Exception as e:
                print(f"  ERROR: {container_num} - {e}")

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Total containers dibuat: {len(all_containers)}")
    print(f"Total JOA sets: {num_joa_sets}")
    print(f"{'='*60}")

    return all_containers


def add_delivery_costs_to_containers(containers):
    """Tambahkan biaya delivery untuk setiap container"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("MENAMBAHKAN BIAYA DELIVERY KE CONTAINERS")
    print("="*60)

    # Jenis biaya delivery
    delivery_types = [
        {"delivery": "Trucking", "desc": "Biaya angkut truck dari pelabuhan", "range": (1500000, 3500000)},
        {"delivery": "THC", "desc": "Terminal Handling Charge", "range": (800000, 1800000)},
        {"delivery": "Lift On/Off", "desc": "Biaya bongkar muat container", "range": (500000, 1200000)},
        {"delivery": "Storage", "desc": "Biaya penyimpanan gudang", "range": (300000, 800000)},
        {"delivery": "Dokumentasi", "desc": "Biaya pengurusan dokumen", "range": (200000, 500000)},
        {"delivery": "Cleaning", "desc": "Biaya pembersihan container", "range": (150000, 400000)}
    ]

    total_inserted = 0

    for container in containers:
        container_id = container['container_id']
        container_no = container['container']
        party = container['party']

        print(f"\n[{container_no}] Party: {party}")

        # Set setiap container dapat 3-5 jenis biaya random
        num_costs = random.randint(3, 5)
        selected_types = random.sample(delivery_types, num_costs)

        container_total = 0
        # Lokasi hanya boleh Surabaya atau destination kapal
        lokasi_options = ['Surabaya']
        if container.get('destination'):
            lokasi_options.append(container['destination'])

        for cost_type in selected_types:
            delivery_name = cost_type['delivery']
            party_label = container.get('party', '').replace("'", "")
            description = f"{cost_type['delivery']}".strip()
            cost_description = cost_type['desc']

            # Generate cost dalam range
            cost = round(random.uniform(cost_type['range'][0], cost_type['range'][1]), 0)

            # Party 40'HC biasanya lebih mahal
            if party == "40'HC":
                cost = cost * 1.3
            elif party == "21'":
                cost = cost * 1.1

            cost = round(cost, 0)

            # Lokasi random antara Surabaya atau destination kapal
            location = random.choice(lokasi_options)

            # Tanggal random dalam 30 hari terakhir
            days_ago = random.randint(0, 30)
            created_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

            try:
                cursor.execute("""
                    INSERT INTO container_delivery_costs (
                        container_id, delivery, description, cost_description, cost, created_date
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (container_id, location, description, cost_description, cost, created_date))

                print(f"  + {delivery_name:15} | {location:15} | Rp {cost:>12,.0f} | {cost_description}")
                container_total += cost
                total_inserted += 1

            except Exception as e:
                print(f"  ERROR: {delivery_name} - {e}")

        print(f"  TOTAL BIAYA: Rp {container_total:,.0f}")

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Total biaya delivery dibuat: {total_inserted}")
    print(f"{'='*60}")


def create_customers_if_not_exists():
    """Buat customers jika belum ada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("CEK & BUAT CUSTOMERS")
    print("="*60)

    # Cek jumlah customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]

    if count >= 10:
        print(f"OK: Sudah ada {count} customers")
        conn.close()
        return

    # Sample customers
    customers_list = [
        ("PT. Sejahtera Abadi", "Jl. Industri No. 123, Jakarta"),
        ("CV. Maju Jaya", "Jl. Raya Bogor KM 5, Bogor"),
        ("PT. Karya Mandiri", "Jl. Pahlawan No. 45, Surabaya"),
        ("UD. Berkah Jaya", "Jl. Merdeka No. 78, Bandung"),
        ("PT. Indah Cargo", "Jl. Pelabuhan No. 12, Semarang"),
        ("PT. Sukses Makmur", "Jl. Tanjung Priok No. 88, Jakarta Utara"),
        ("CV. Harapan Maju", "Jl. Industri Raya No. 234, Tangerang"),
        ("PT. Cahaya Sentosa", "Jl. Pemuda No. 56, Bekasi"),
        ("UD. Rezeki Lancar", "Jl. Gatot Subroto No. 99, Jakarta Selatan"),
        ("PT. Bahagia Sejahtera", "Jl. Sudirman No. 120, Jakarta Pusat")
    ]

    for nama, alamat in customers_list:
        try:
            cursor.execute("SELECT customer_id FROM customers WHERE nama_customer = ?", (nama,))
            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO customers (nama_customer, alamat_customer)
                VALUES (?, ?)
            """, (nama, alamat))
            print(f"  + {nama}")
        except:
            pass

    conn.commit()
    conn.close()


def generate_barang_for_containers(containers):
    """Generate barang dan assign ke containers"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("GENERATE BARANG & ASSIGN KE CONTAINERS")
    print("="*60)

    # Ambil customers
    cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 10")
    customers = [row[0] for row in cursor.fetchall()]

    if len(customers) < 2:
        print("ERROR: Minimal butuh 2 customers!")
        conn.close()
        return

    # Jenis barang
    barang_types = [
        {"nama": "Elektronik - TV LED 42 inch", "m3": (0.5, 1.5), "ton": (0.1, 0.3)},
        {"nama": "Furniture - Meja Kayu Jati", "m3": (1.0, 2.5), "ton": (0.3, 0.8)},
        {"nama": "Tekstil - Kain Cotton", "m3": (0.3, 1.0), "ton": (0.1, 0.5)},
        {"nama": "Alat Berat - Mesin Produksi", "m3": (3.0, 8.0), "ton": (1.5, 5.0)},
        {"nama": "Bahan Kimia - Cat Industrial", "m3": (0.5, 1.5), "ton": (0.5, 1.2)},
        {"nama": "Makanan - Mie Instan", "m3": (0.8, 2.0), "ton": (0.3, 0.9)},
        {"nama": "Minuman - Air Mineral", "m3": (1.0, 2.5), "ton": (0.8, 1.5)},
        {"nama": "Spare Part - Komponen Mobil", "m3": (0.4, 1.2), "ton": (0.2, 0.6)},
    ]

    total_barang_created = 0
    total_assigned = 0

    # Untuk setiap container, buat 3-7 barang
    for container in containers:
        container_id = container['container_id']
        container_no = container['container']
        ref_joa = container['ref_joa']

        print(f"\n[{container_no}] JOA: {ref_joa}")

        num_barang = random.randint(3, 7)

        for i in range(num_barang):
            barang_type = random.choice(barang_types)
            nama_barang = barang_type['nama']

            # Random pengirim dan penerima
            pengirim_id = random.choice(customers)
            penerima_id = random.choice([c for c in customers if c != pengirim_id])

            # Generate dimensi
            panjang = round(random.uniform(100, 300), 2)
            lebar = round(random.uniform(80, 250), 2)
            tinggi = round(random.uniform(80, 200), 2)
            m3 = round((panjang * lebar * tinggi) / 1000000, 3)
            ton = round(random.uniform(barang_type['ton'][0], barang_type['ton'][1]), 3)

            container_barang = random.choice([20, 40])

            # Pricing - M3
            m3_pp = round(random.uniform(300000, 800000), 0)
            m3_pd = round(random.uniform(350000, 900000), 0)
            m3_dd = round(random.uniform(400000, 1000000), 0)

            # Pricing - Ton
            ton_pp = round(random.uniform(500000, 1500000), 0)
            ton_pd = round(random.uniform(600000, 1700000), 0)
            ton_dd = round(random.uniform(700000, 2000000), 0)

            # Pricing - Colli
            col_pp = random.randint(20000, 50000)
            col_pd = random.randint(25000, 60000)
            col_dd = random.randint(30000, 70000)

            # Pricing - Container 20'
            container_20_pp = round(random.uniform(8000000, 10000000), 0)
            container_20_pd = round(random.uniform(10000000, 12000000), 0)
            container_20_dd = round(random.uniform(12000000, 14000000), 0)

            # Pricing - Container 21'
            container_21_pp = round(random.uniform(8500000, 11000000), 0)
            container_21_pd = round(random.uniform(10500000, 13000000), 0)
            container_21_dd = round(random.uniform(12500000, 15000000), 0)

            # Pricing - Container 40' HC
            container_40hc_pp = round(random.uniform(15000000, 18000000), 0)
            container_40hc_pd = round(random.uniform(17000000, 20000000), 0)
            container_40hc_dd = round(random.uniform(19000000, 22000000), 0)

            pajak = 1 if random.random() < 0.7 else 0

            try:
                # Insert barang
                cursor.execute("""
                    INSERT INTO barang (
                        pengirim, penerima, nama_barang,
                        panjang_barang, lebar_barang, tinggi_barang,
                        m3_barang, ton_barang, container_barang,
                        m3_pp, m3_pd, m3_dd,
                        ton_pp, ton_pd, ton_dd,
                        col_pp, col_pd, col_dd,
                        container_20_pp, container_20_pd, container_20_dd,
                        container_21_pp, container_21_pd, container_21_dd,
                        container_40hc_pp, container_40hc_pd, container_40hc_dd,
                        pajak
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pengirim_id, penerima_id, nama_barang,
                    panjang, lebar, tinggi,
                    m3, ton, container_barang,
                    m3_pp, m3_pd, m3_dd,
                    ton_pp, ton_pd, ton_dd,
                    col_pp, col_pd, col_dd,
                    container_20_pp, container_20_pd, container_20_dd,
                    container_21_pp, container_21_pd, container_21_dd,
                    container_40hc_pp, container_40hc_pd, container_40hc_dd,
                    pajak
                ))

                barang_id = cursor.lastrowid
                total_barang_created += 1

                # Assign ke container
                # Satuan fisik barang
                satuan = random.choice(['PALLET', 'KOLI', 'PACKAGE', 'DOS', 'PCS'])
                # Metode pricing
                pricing_method = random.choice(['M3', 'TON', 'COLLI', 'CONTAINER'])
                door_type = random.choice(['PP', 'PD', 'DD'])
                colli_amount = random.randint(1, 50)

                # Get container party size
                party = container.get('party', "20'")

                # Select price based on pricing_method and door_type
                if pricing_method == 'M3':
                    if door_type == 'PP':
                        harga_per_unit = m3_pp
                    elif door_type == 'PD':
                        harga_per_unit = m3_pd
                    else:  # DD
                        harga_per_unit = m3_dd
                elif pricing_method == 'TON':
                    if door_type == 'PP':
                        harga_per_unit = ton_pp
                    elif door_type == 'PD':
                        harga_per_unit = ton_pd
                    else:  # DD
                        harga_per_unit = ton_dd
                elif pricing_method == 'COLLI':
                    if door_type == 'PP':
                        harga_per_unit = col_pp
                    elif door_type == 'PD':
                        harga_per_unit = col_pd
                    else:  # DD
                        harga_per_unit = col_dd
                else:  # CONTAINER - pilih berdasarkan ukuran container
                    if party == "20'":
                        if door_type == 'PP':
                            harga_per_unit = container_20_pp
                        elif door_type == 'PD':
                            harga_per_unit = container_20_pd
                        else:  # DD
                            harga_per_unit = container_20_dd
                    elif party == "21'":
                        if door_type == 'PP':
                            harga_per_unit = container_21_pp
                        elif door_type == 'PD':
                            harga_per_unit = container_21_pd
                        else:  # DD
                            harga_per_unit = container_21_dd
                    else:  # 40'HC
                        if door_type == 'PP':
                            harga_per_unit = container_40hc_pp
                        elif door_type == 'PD':
                            harga_per_unit = container_40hc_pd
                        else:  # DD
                            harga_per_unit = container_40hc_dd

                total_harga = harga_per_unit * colli_amount

                # Tanggal
                days_ago = random.randint(0, 30)
                tanggal = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

                # Insert detail_container
                cursor.execute("""
                    INSERT INTO detail_container (
                        tanggal, barang_id, container_id, satuan, door_type,
                        colli_amount, harga_per_unit, total_harga
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tanggal, barang_id, container_id, satuan, door_type,
                     colli_amount, harga_per_unit, total_harga))

                # Tax jika ada
                if pajak == 1:
                    cursor.execute("SELECT nama_customer FROM customers WHERE customer_id = ?",
                                 (penerima_id,))
                    penerima_name = cursor.fetchone()[0]

                    ppn_amount = total_harga * 0.011
                    pph23_amount = total_harga * 0.02
                    total_tax = ppn_amount + pph23_amount

                    cursor.execute("""
                        INSERT INTO barang_tax (
                            container_id, barang_id, penerima, total_nilai_barang,
                            ppn_rate, pph23_rate, ppn_amount, pph23_amount, total_tax
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (container_id, barang_id, penerima_name, total_harga,
                         0.011, 0.02, ppn_amount, pph23_amount, total_tax))

                pajak_mark = "[TAX]" if pajak == 1 else ""
                print(f"  + {nama_barang[:30]:30} | {colli_amount:>3} {satuan:7} | {pricing_method:9} | {door_type} | Rp {total_harga:>12,.0f} {pajak_mark}")
                total_assigned += 1

            except Exception as e:
                print(f"  ERROR: {nama_barang} - {e}")

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Total barang dibuat: {total_barang_created}")
    print(f"Total assigned: {total_assigned}")
    print(f"{'='*60}")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("    GENERATE COMPLETE DATA (CONTAINERS + BARANG + BIAYA)")
    print("="*70)

    # Step 1: Pastikan ada customers
    create_customers_if_not_exists()

    # Step 2: Generate containers dengan shared JOA
    containers = generate_containers_with_shared_joa()

    if not containers:
        print("\nERROR: Gagal membuat containers!")
        return

    # Step 3: Tambahkan biaya delivery
    add_delivery_costs_to_containers(containers)

    # Step 4: Generate barang dan assign ke containers
    generate_barang_for_containers(containers)

    print("\n" + "="*70)
    print("SEMUA PROSES SELESAI!")
    print("="*70)
    print("\nRingkasan:")
    print(f"  - {len(containers)} containers dibuat (dengan shared JOA)")
    print(f"  - Setiap container punya 3-5 jenis biaya delivery")
    print(f"  - Setiap container punya 3-7 barang")
    print(f"  - 70% barang punya pajak (PPN 1.1% + PPH23 2%)")
    print("\nBuka aplikasi dan refresh untuk melihat data!\n")


if __name__ == "__main__":
    main()
