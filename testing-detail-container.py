import sqlite3
import os
from datetime import datetime

def get_all_detail_container(db_path="data/app.db"):
    """Get all data from detail_container table with full details"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        print("=" * 100)
        print(f"📦 ALL DETAIL CONTAINER DATA")
        print("=" * 100)
        
        # Get all detail_container with related info
        query = """
            SELECT 
                dc.id as detail_id,
                dc.container_id,
                dc.barang_id,
                c.container as container_name,
                c.kapal_feeder,
                b.nama_barang,
                s.nama_customer as sender,
                r.nama_customer as receiver,
                dc.satuan,
                dc.door_type,
                dc.colli_amount,
                dc.harga_per_unit,
                dc.total_harga,
                dc.tax_id,
                dc.assigned_at,
                dc.tanggal
            FROM detail_container dc
            LEFT JOIN containers c ON dc.container_id = c.container_id
            LEFT JOIN barang b ON dc.barang_id = b.barang_id
            LEFT JOIN customers s ON b.pengirim = s.customer_id
            LEFT JOIN customers r ON b.penerima = r.customer_id
            ORDER BY dc.container_id, dc.assigned_at DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("❌ No data found in detail_container table")
            conn.close()
            return
        
        print(f"\n📊 Total records: {len(results)}\n")
        
        # Group by container
        current_container = None
        container_count = 0
        
        for row in results:
            container_id = row['container_id']
            
            # Print container header when changing container
            if current_container != container_id:
                if current_container is not None:
                    print("-" * 100)
                
                current_container = container_id
                container_count += 1
                
                print(f"\n{'='*100}")
                print(f"🚢 CONTAINER #{container_count}: {row['container_name']} (ID: {container_id})")
                print(f"   Feeder: {row['kapal_feeder']}")
                print(f"{'='*100}")
                print()
            
            # Print detail
            print(f"   📦 Detail ID: {row['detail_id']}")
            print(f"      ├─ Barang ID      : {row['barang_id']}")
            print(f"      ├─ Nama Barang    : {row['nama_barang']}")
            print(f"      ├─ Sender         : {row['sender']}")
            print(f"      ├─ Receiver       : {row['receiver']}")
            print(f"      ├─ Satuan         : {row['satuan']}")
            print(f"      ├─ Door Type      : {row['door_type']}")
            print(f"      ├─ Colli          : {row['colli_amount']}")
            print(f"      ├─ Harga/Unit     : Rp {row['harga_per_unit']:,.0f}" if row['harga_per_unit'] else "      ├─ Harga/Unit     : -")
            print(f"      ├─ Total Harga    : Rp {row['total_harga']:,.0f}" if row['total_harga'] else "      ├─ Total Harga    : -")
            print(f"      ├─ Tax ID         : {row['tax_id']}" if row['tax_id'] else "      ├─ Tax ID         : -")
            print(f"      ├─ Assigned At    : {row['assigned_at']}")
            print(f"      └─ Tanggal        : {row['tanggal']}" if row['tanggal'] else "      └─ Tanggal        : -")
            print()
        
        print("=" * 100)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def get_detail_container_by_container(db_path="data/app.db", container_id=None):
    """Get detail_container for specific container"""
    
    if not container_id:
        print("❌ Please specify container_id")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 100)
        print(f"📦 DETAIL CONTAINER FOR CONTAINER ID: {container_id}")
        print("=" * 100)
        
        # Get container info
        cursor.execute("SELECT * FROM containers WHERE container_id = ?", (container_id,))
        container = cursor.fetchone()
        
        if not container:
            print(f"❌ Container ID {container_id} not found")
            conn.close()
            return
        
        print(f"\n🚢 Container: {container['container']}")
        print(f"   Feeder: {container['kapal_feeder']}")
        print(f"   Seal: {container['seal']}")
        print(f"   Ref JOA: {container['ref_joa']}")
        print()
        
        # Get detail_container
        query = """
            SELECT 
                dc.*,
                b.nama_barang,
                s.nama_customer as sender,
                r.nama_customer as receiver
            FROM detail_container dc
            LEFT JOIN barang b ON dc.barang_id = b.barang_id
            LEFT JOIN customers s ON b.pengirim = s.customer_id
            LEFT JOIN customers r ON b.penerima = r.customer_id
            WHERE dc.container_id = ?
            ORDER BY dc.assigned_at DESC
        """
        
        cursor.execute(query, (container_id,))
        results = cursor.fetchall()
        
        if not results:
            print(f"❌ No barang found in container {container_id}")
            conn.close()
            return
        
        print(f"📊 Total barang: {len(results)}\n")
        print("-" * 100)
        
        total_colli = 0
        total_nilai = 0
        
        for idx, row in enumerate(results, 1):
            print(f"\n{idx}. Detail ID: {row['id']}")
            print(f"   ├─ Barang ID      : {row['barang_id']}")
            print(f"   ├─ Nama Barang    : {row['nama_barang']}")
            print(f"   ├─ Sender         : {row['sender']}")
            print(f"   ├─ Receiver       : {row['receiver']}")
            print(f"   ├─ Satuan         : {row['satuan']}")
            print(f"   ├─ Door Type      : {row['door_type']}")
            print(f"   ├─ Colli          : {row['colli_amount']}")
            print(f"   ├─ Harga/Unit     : Rp {row['harga_per_unit']:,.0f}" if row['harga_per_unit'] else "   ├─ Harga/Unit     : -")
            print(f"   ├─ Total Harga    : Rp {row['total_harga']:,.0f}" if row['total_harga'] else "   ├─ Total Harga    : -")
            print(f"   ├─ Tax ID         : {row['tax_id']}" if row['tax_id'] else "   ├─ Tax ID         : -")
            print(f"   ├─ Assigned At    : {row['assigned_at']}")
            print(f"   └─ Tanggal        : {row['tanggal']}" if row['tanggal'] else "   └─ Tanggal        : -")
            
            total_colli += row['colli_amount'] if row['colli_amount'] else 0
            total_nilai += row['total_harga'] if row['total_harga'] else 0
        
        print("\n" + "=" * 100)
        print(f"📊 SUMMARY:")
        print(f"   Total Barang: {len(results)}")
        print(f"   Total Colli : {total_colli}")
        print(f"   Total Nilai : Rp {total_nilai:,.0f}")
        print("=" * 100)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_duplicate_barang_in_container(db_path="data/app.db"):
    """Check for duplicate barang (same name, sender, receiver) in containers"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 100)
        print(f"🔍 CHECKING FOR DUPLICATE BARANG IN CONTAINERS")
        print("=" * 100)
        
        query = """
            SELECT 
                dc.container_id,
                c.container as container_name,
                b.nama_barang,
                s.nama_customer as sender,
                r.nama_customer as receiver,
                COUNT(*) as count,
                GROUP_CONCAT(dc.barang_id) as barang_ids,
                GROUP_CONCAT(dc.assigned_at) as assigned_dates
            FROM detail_container dc
            JOIN barang b ON dc.barang_id = b.barang_id
            JOIN customers s ON b.pengirim = s.customer_id
            JOIN customers r ON b.penerima = r.customer_id
            JOIN containers c ON dc.container_id = c.container_id
            GROUP BY dc.container_id, b.nama_barang, s.nama_customer, r.nama_customer
            HAVING COUNT(*) > 1
            ORDER BY dc.container_id, count DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("✅ No duplicates found!")
            conn.close()
            return
        
        print(f"\n⚠️ Found {len(results)} groups with duplicate barang:\n")
        
        for idx, row in enumerate(results, 1):
            print(f"{idx}. Container: {row['container_name']} (ID: {row['container_id']})")
            print(f"   Barang    : {row['nama_barang']}")
            print(f"   Sender    : {row['sender']}")
            print(f"   Receiver  : {row['receiver']}")
            print(f"   Count     : {row['count']} entries")
            print(f"   Barang IDs: {row['barang_ids']}")
            print(f"   Dates     : {row['assigned_dates']}")
            print()
        
        print("=" * 100)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def export_detail_container_to_csv(db_path="data/app.db", output_file="detail_container_export.csv"):
    """Export detail_container to CSV"""
    
    try:
        import csv
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                dc.id,
                dc.container_id,
                c.container,
                dc.barang_id,
                b.nama_barang,
                s.nama_customer as sender,
                r.nama_customer as receiver,
                dc.satuan,
                dc.door_type,
                dc.colli_amount,
                dc.harga_per_unit,
                dc.total_harga,
                dc.tax_id,
                dc.assigned_at,
                dc.tanggal
            FROM detail_container dc
            LEFT JOIN containers c ON dc.container_id = c.container_id
            LEFT JOIN barang b ON dc.barang_id = b.barang_id
            LEFT JOIN customers s ON b.pengirim = s.customer_id
            LEFT JOIN customers r ON b.penerima = r.customer_id
            ORDER BY dc.container_id, dc.assigned_at DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("❌ No data to export")
            return
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'detail_id', 'container_id', 'container_name', 'barang_id', 
                'nama_barang', 'sender', 'receiver', 'satuan', 'door_type',
                'colli_amount', 'harga_per_unit', 'total_harga', 'tax_id',
                'assigned_at', 'tanggal'
            ])
            
            # Write data
            for row in results:
                writer.writerow([
                    row['id'], row['container_id'], row['container'], row['barang_id'],
                    row['nama_barang'], row['sender'], row['receiver'], row['satuan'],
                    row['door_type'], row['colli_amount'], row['harga_per_unit'],
                    row['total_harga'], row['tax_id'], row['assigned_at'], row['tanggal']
                ])
        
        print(f"✅ Exported {len(results)} records to {output_file}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Get all detail_container data")
    print("2. Get detail_container for specific container")
    print("3. Check for duplicates")
    print("4. Export to CSV")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        get_all_detail_container()
    elif choice == "2":
        container_id = input("Enter container_id: ").strip()
        get_detail_container_by_container(container_id=int(container_id))
    elif choice == "3":
        check_duplicate_barang_in_container()
    elif choice == "4":
        output = input("Enter output filename (default: detail_container_export.csv): ").strip()
        if not output:
            output = "detail_container_export.csv"
        export_detail_container_to_csv(output_file=output)
    else:
        print("❌ Invalid choice")