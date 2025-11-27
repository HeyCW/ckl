"""
Script untuk generate sample data container dengan tipe 20', 21', dan 40'
Jalankan: python generate_container_sample.py
"""

import sqlite3
from datetime import datetime, timedelta
import random

# Path ke database
DB_PATH = "data/app.db"

def generate_sample_containers():
    """Generate sample containers dengan berbagai tipe"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("GENERATE SAMPLE DATA CONTAINER")
    print("="*60)

    # Cek apakah sudah ada kapal di database
    cursor.execute("SELECT kapal_id, feeder, etd_sub FROM kapals ORDER BY kapal_id LIMIT 5")
    kapals = cursor.fetchall()

    if not kapals:
        print("⚠️ Tidak ada data kapal di database!")
        print("Silahkan tambahkan kapal terlebih dahulu melalui aplikasi.")
        conn.close()
        return

    print(f"\n✓ Ditemukan {len(kapals)} kapal:")
    for k in kapals:
        print(f"  - ID {k[0]}: {k[1]} (ETD: {k[2]})")

    # Data sample untuk container types
    container_types = ["20'", "21'", "40'"]

    # Sample container numbers
    container_prefixes = ["TCLU", "MSCU", "HLBU", "CMAU", "TEMU"]

    sample_data = []

    print(f"\n📦 Membuat {len(kapals) * 6} sample containers...")

    for kapal in kapals:
        kapal_id = kapal[0]
        feeder = kapal[1]
        etd = kapal[2] or datetime.now().strftime('%Y-%m-%d')

        # Buat 6 container per kapal (2 x 20', 2 x 21', 2 x 40')
        for i in range(6):
            # Tentukan tipe container
            if i < 2:
                party_type = "20'"
            elif i < 4:
                party_type = "21'"
            else:
                party_type = "40'"

            # Generate container number
            prefix = random.choice(container_prefixes)
            number = f"{random.randint(100000, 999999)}{random.randint(0, 9)}"
            container_num = f"{prefix}{number}"

            # Generate seal number
            seal = f"SEAL{random.randint(10000, 99999)}"

            # Generate Ref JOA
            ref_joa = f"JOA/{datetime.now().year}/{random.randint(1000, 9999)}"

            sample_data.append({
                'kapal_id': kapal_id,
                'etd': etd,
                'party': party_type,
                'container': container_num,
                'seal': seal,
                'ref_joa': ref_joa,
                'feeder': feeder
            })

    # Insert ke database
    inserted = 0
    skipped = 0

    for data in sample_data:
        try:
            # Cek apakah container number sudah ada
            cursor.execute("SELECT container_id FROM containers WHERE container = ?",
                          (data['container'],))
            if cursor.fetchone():
                print(f"⏩ Skip: {data['container']} (sudah ada)")
                skipped += 1
                continue

            # Insert container
            cursor.execute("""
                INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                data['kapal_id'],
                data['etd'],
                data['party'],
                data['container'],
                data['seal'],
                data['ref_joa']
            ))

            print(f"✓ Insert: {data['party']:4} | {data['container']} | {data['feeder']} | JOA: {data['ref_joa']}")
            inserted += 1

        except Exception as e:
            print(f"❌ Error insert {data['container']}: {e}")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print(f"✅ SELESAI!")
    print(f"   - Berhasil insert: {inserted} container")
    print(f"   - Di-skip (duplikat): {skipped} container")
    print("="*60)

    # Summary per type
    print("\n📊 SUMMARY PER TYPE:")
    types_count = {}
    for data in sample_data[:inserted]:
        party = data['party']
        types_count[party] = types_count.get(party, 0) + 1

    for party_type, count in sorted(types_count.items()):
        print(f"   {party_type}: {count} containers")

    print("\n💡 TIP: Buka aplikasi dan refresh untuk melihat data baru!\n")


def delete_sample_containers():
    """Delete sample containers yang dibuat script ini"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n⚠️  HAPUS SAMPLE CONTAINERS")
    print("="*60)

    # Count containers
    cursor.execute("""
        SELECT COUNT(*) FROM containers
        WHERE container LIKE 'TCLU%' OR container LIKE 'MSCU%'
        OR container LIKE 'HLBU%' OR container LIKE 'CMAU%' OR container LIKE 'TEMU%'
    """)
    count = cursor.fetchone()[0]

    if count == 0:
        print("✓ Tidak ada sample containers untuk dihapus.")
        conn.close()
        return

    confirm = input(f"Akan menghapus {count} sample containers. Lanjutkan? (yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        cursor.execute("""
            DELETE FROM containers
            WHERE container LIKE 'TCLU%' OR container LIKE 'MSCU%'
            OR container LIKE 'HLBU%' OR container LIKE 'CMAU%' OR container LIKE 'TEMU%'
        """)
        conn.commit()
        print(f"✅ {cursor.rowcount} containers berhasil dihapus.")
    else:
        print("❌ Batal menghapus.")

    conn.close()


def show_menu():
    """Show menu"""
    print("\n" + "="*60)
    print("    SCRIPT GENERATOR SAMPLE DATA CONTAINER")
    print("="*60)
    print("1. Generate sample containers (20', 21', 40')")
    print("2. Hapus sample containers")
    print("3. Exit")
    print("="*60)

    choice = input("\nPilih menu (1-3): ")
    return choice


if __name__ == "__main__":
    while True:
        choice = show_menu()

        if choice == "1":
            generate_sample_containers()
        elif choice == "2":
            delete_sample_containers()
        elif choice == "3":
            print("\n👋 Terima kasih!\n")
            break
        else:
            print("\n❌ Pilihan tidak valid!\n")

        input("\nTekan ENTER untuk melanjutkan...")
