import sqlite3
import random
from datetime import datetime, timedelta

def generate_test_data(db_path="data/app.db"):
    """Generate comprehensive test data for the shipping system"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starting test data generation...")
        
        # 1. Generate Customers (100 customers)
        print("📝 Generating customers...")
        companies = [
            'PT Maju Jaya', 'CV Berkah Mandiri', 'PT Sumber Rejeki', 'UD Cahaya Barokah',
            'PT Karya Utama', 'CV Rizki Abadi', 'PT Harapan Baru', 'UD Berkah Jaya',
            'PT Surya Mandiri', 'CV Mitra Sejati', 'PT Bintang Terang', 'UD Sumber Makmur',
            'PT Nusantara Jaya', 'CV Cahaya Mandiri', 'PT Karya Sejahtera', 'UD Maju Terus',
            'PT Indah Jaya', 'CV Barokah Abadi', 'PT Sejahtera Mandiri', 'UD Cahaya Baru',
            'PT Mandiri Jaya', 'CV Berkah Sejati', 'PT Sumber Berkah', 'UD Harapan Jaya',
            'PT Jaya Abadi', 'CV Mandiri Berkah', 'PT Cahaya Sejahtera', 'UD Rizki Jaya',
            'PT Berkah Mandiri', 'CV Jaya Sejati', 'PT Mandiri Abadi', 'UD Cahaya Berkah',
            'PT Sejahtera Jaya', 'CV Berkah Terang', 'PT Harapan Mandiri', 'UD Jaya Berkah',
            'PT Abadi Jaya', 'CV Mandiri Sejahtera', 'PT Berkah Jaya', 'UD Cahaya Mandiri'
        ]
        
        cities = ['Surabaya', 'Jakarta', 'Samarinda', 'Balikpapan', 'Makassar', 'Medan', 'Semarang', 'Palembang', 'Pontianak', 'Banjarmasin']
        
        customers = []
        for i in range(100):
            nama = f"{random.choice(companies)} {i+1}"
            kota = random.choice(cities)
            alamat = f"Jl. {random.choice(['Merdeka', 'Diponegoro', 'Sudirman', 'Gajah Mada', 'Ahmad Yani'])} No. {random.randint(1, 999)}, {kota}"
            customers.append((nama, alamat))
        
        cursor.executemany("""
            INSERT INTO customers (nama_customer, alamat_customer) 
            VALUES (?, ?)
        """, customers)
        
        # 2. Generate Containers (20 containers)
        print("🚢 Generating containers...")
        containers = []
        destinations = ['Surabaya', 'Jakarta', 'Samarinda', 'Balikpapan', 'Makassar', 'Medan', 'Semarang', 'Palembang']
        feeders = ['EVER GIVEN', 'MAERSK ESSEX', 'COSCO SHIPPING', 'MSC OSCAR', 'ONE STORK', 'YANG MING', 'HAPAG LLOYD']
        
        for i in range(20):
            base_date = datetime.now() - timedelta(days=random.randint(0, 90))
            
            container_data = (
                random.choice(feeders),
                (base_date + timedelta(days=random.randint(7, 21))).strftime('%Y-%m-%d'),
                f"Party {i+1}",  # Party
                (base_date + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d'),  # CLS
                (base_date + timedelta(days=random.randint(-2, 2))).strftime('%Y-%m-%d'),  # Open
                (base_date + timedelta(days=random.randint(3, 7))).strftime('%Y-%m-%d'),  # Full
                random.choice(destinations),
                f"TCLU{random.randint(1000000, 9999999)}",  # Container number
                f"S{random.randint(100000, 999999)}",  # Seal
                f"JOA{random.randint(1000, 9999)}/{datetime.now().year}"  # Ref JOA
            )
            containers.append(container_data)
        
        cursor.executemany("""
            INSERT INTO containers (feeder, etd_sub, party, cls, open, full, destination, container, seal, ref_joa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, containers)
        
        # 3. Generate Barang (200 items)
        print("📦 Generating barang...")
        barang_types = [
            'Elektronik', 'Furniture', 'Tekstil', 'Makanan', 'Minuman', 'Kosmetik', 
            'Obat-obatan', 'Mainan', 'Alat Tulis', 'Pakaian', 'Sepatu', 'Tas',
            'Peralatan Rumah Tangga', 'Buku', 'Alat Olahraga', 'Perhiasan', 'Kerajinan'
        ]
        
        barang_names = [
            'TV LED', 'Kulkas', 'Mesin Cuci', 'Sofa', 'Meja Makan', 'Lemari', 
            'Baju Batik', 'Celana Jeans', 'Sepatu Sneakers', 'Tas Ransel', 
            'Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Speaker', 'Kamera',
            'Mie Instan', 'Kopi', 'Teh', 'Biskuit', 'Cokelat', 'Permen',
            'Shampo', 'Sabun', 'Pasta Gigi', 'Lotion', 'Parfum', 'Lipstik',
            'Vitamin', 'Obat Flu', 'Plaster', 'Minyak Kayu Putih', 'Obat Sakit Kepala',
            'Boneka', 'Robot', 'Puzzle', 'Lego', 'Bola', 'Raket', 'Sepeda',
            'Pulpen', 'Pensil', 'Buku Tulis', 'Map', 'Penggaris', 'Penghapus',
            'Piring', 'Gelas', 'Sendok', 'Garpu', 'Pisau', 'Wajan', 'Panci'
        ]
        
        barang_data = []
        for i in range(200):
            # Random dimensions
            p = round(random.uniform(10, 200), 1)
            l = round(random.uniform(10, 150), 1) 
            t = round(random.uniform(5, 100), 1)
            
            # Calculate volume and weight
            m3 = round((p * l * t) / 1000000, 4)  # Convert cm³ to m³
            ton = round(m3 * random.uniform(0.1, 0.8), 4)  # Weight based on volume
            col = random.randint(1, 20)
            
            # Pricing data for combinations
            base_price_m3 = random.randint(100000, 500000)
            base_price_ton = random.randint(1000000, 3000000)
            base_price_col = random.randint(50000, 200000)
            
            barang_item = (
                random.randint(1, 100),  # pengirim (customer_id)
                random.randint(1, 100),  # penerima (customer_id)
                random.choice(barang_names),
                random.choice(barang_types),
                p, l, t, m3, ton, col,
                # m3 pricing for pp, pd, dd
                base_price_m3,
                base_price_m3 * 1.2,
                base_price_m3 * 1.5,
                # ton pricing for pp, pd, dd
                base_price_ton,
                base_price_ton * 1.2,
                base_price_ton * 1.5,
                # colli pricing for pp, pd, dd
                base_price_col,
                base_price_col * 1.2,
                base_price_col * 1.5
            )
            barang_data.append(barang_item)
        
        cursor.executemany("""
            INSERT INTO barang (pengirim, penerima, nama_barang, jenis_barang,
                              panjang_barang, lebar_barang, tinggi_barang, m3_barang, ton_barang, col_barang,
                              m3_pp, m3_pd, m3_dd, ton_pp, ton_pd, ton_dd, col_pp, col_pd, col_dd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, barang_data)
        
        # 4. Assign Barang to Containers with pricing
        print("🔗 Assigning barang to containers...")
        
        # Get all container and barang IDs
        cursor.execute("SELECT container_id FROM containers")
        container_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT barang_id FROM barang")
        barang_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(container_ids)} containers and {len(barang_ids)} barang")
        
        # Assign barang to containers (each container gets 8-15 barang)
        assignments = []
        used_barang = set()
        
        for container_id in container_ids:
            # Each container gets 8-15 barang
            num_barang = random.randint(8, 15)
            print(f"Assigning {num_barang} barang to container {container_id}")
            
            for _ in range(num_barang):
                # Pick unused barang
                available_barang = [b for b in barang_ids if b not in used_barang]
                if not available_barang:
                    print("No more available barang, breaking")
                    break
                    
                barang_id = random.choice(available_barang)
                used_barang.add(barang_id)
                
                # Random assignment details
                satuan_options = ['m3', 'ton', 'col']
                door_options = ['pp', 'pd', 'dd']
                
                satuan = random.choice(satuan_options)
                door = random.choice(door_options)
                colli_amount = random.randint(1, 5)
                
                # Get barang pricing data
                cursor.execute(f"""
                    SELECT {satuan}_{door}, m3_barang, ton_barang 
                    FROM barang WHERE barang_id = ?
                """, (barang_id,))
                barang_data = cursor.fetchone()
                
                if barang_data:
                    unit_price = barang_data[0] or 100000
                    m3_val = barang_data[1] or 0.01
                    ton_val = barang_data[2] or 0.01
                    
                    # Calculate total based on method
                    if satuan == 'm3':
                        total_price = unit_price * m3_val * colli_amount
                    elif satuan == 'ton':
                        total_price = unit_price * ton_val * colli_amount
                    else:  # colli
                        total_price = unit_price * colli_amount
                    
                    assignment = (
                        barang_id, container_id, satuan, door, colli_amount,
                        unit_price, total_price,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    assignments.append(assignment)
        
        print(f"Creating {len(assignments)} assignments...")
        cursor.executemany("""
            INSERT INTO detail_container (barang_id, container_id, satuan, door_type, colli_amount,
                                        harga_per_unit, total_harga, assigned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, assignments)
        
        # 5. Generate Container Delivery Costs
        print("🚚 Generating delivery costs...")
        delivery_costs = []
        
        cost_types_surabaya = [
            ('THC Surabaya', (5000000, 6000000)),
            ('Frezh', (500000, 700000)),
            ('Bl. LCL', (5000000, 5500000)),
            ('Seal', (80000, 120000)),
            ('Bl. Cleaning Container', (90000, 110000)),
            ('Bl. Ops Stuffing Dalam', (150000, 170000)),
            ('Bl. Antol Barang', (70000, 80000)),
            ('Bl. Oper Depo', (200000, 250000)),
            ('Bl. Admin', (180000, 190000)),
            ('TPT1 25', (8000, 12000)),
            ('TPT1 21', (18000, 22000)),
            ('Pajak', (200000, 220000))
        ]
        
        cost_types_destination = [
            ('Trucking Port-City', (1600000, 1700000)),
            ('THC Destination', (4100000, 4300000)),
            ('Dooring Barang Ringan', (250000, 290000)),
            ('Baseh Ijin & depo', (220000, 230000)),
            ('Bl. Lab Empty', (150000, 170000)),
            ('Bl. Ops Destination', (130000, 140000)),
            ('Bl. Sewa JPL & Adm', (50000, 60000)),
            ('Bl. Forklift', (340000, 360000)),
            ('Bl. Lolo', (210000, 230000)),
            ('Rekolasi', (930000, 950000))
        ]
        
        for container_id in container_ids:
            # Add Surabaya costs (90% chance)
            if random.random() < 0.9:
                for desc, (min_cost, max_cost) in cost_types_surabaya:
                    cost = random.randint(min_cost, max_cost)
                    delivery_costs.append((
                        container_id, 'Surabaya', desc, cost,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
            
            # Add destination costs (85% chance)
            if random.random() < 0.85:
                # Get container destination
                cursor.execute("SELECT destination FROM containers WHERE container_id = ?", (container_id,))
                result = cursor.fetchone()
                destination = result[0] if result else 'Unknown'
                
                for desc, (min_cost, max_cost) in cost_types_destination:
                    cost = random.randint(min_cost, max_cost)
                    delivery_costs.append((
                        container_id, destination, desc, cost,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
        
        print(f"Creating {len(delivery_costs)} delivery cost entries...")
        cursor.executemany("""
            INSERT INTO container_delivery_costs (container_id, delivery, description, cost, created_date)
            VALUES (?, ?, ?, ?, ?)
        """, delivery_costs)
        
        # Commit all changes
        conn.commit()
        
        # Calculate totals for summary
        cursor.execute("SELECT SUM(total_harga) FROM detail_container")
        total_revenue = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(cost) FROM container_delivery_costs")
        total_costs = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Print summary
        print("✅ Test data generation completed!")
        print(f"📊 Generated:")
        print(f"   • 100 Customers")
        print(f"   • 20 Containers") 
        print(f"   • 200 Barang items")
        print(f"   • {len(assignments)} Container assignments")
        print(f"   • {len(delivery_costs)} Delivery cost entries")
        print(f"   • Total estimated revenue: Rp {total_revenue:,.0f}")
        print(f"   • Total estimated costs: Rp {total_costs:,.0f}")
        print(f"   • Estimated profit: Rp {total_revenue - total_costs:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating test data: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def clear_existing_data(db_path="data/app.db"):
    """Clear existing test data (keep users table)"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️ Clearing existing data...")
        
        # Clear in correct order due to foreign keys
        cursor.execute("DELETE FROM container_delivery_costs")
        cursor.execute("DELETE FROM detail_container") 
        cursor.execute("DELETE FROM barang")
        cursor.execute("DELETE FROM containers")
        cursor.execute("DELETE FROM customers")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('customers', 'containers', 'barang', 'detail_container', 'container_delivery_costs')")
        
        conn.commit()
        conn.close()
        
        print("✅ Existing data cleared")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def verify_data(db_path="data/app.db"):
    """Verify the generated data"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying generated data...")
        
        # Check customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        print(f"   Customers: {customer_count}")
        
        # Check containers
        cursor.execute("SELECT COUNT(*) FROM containers")
        container_count = cursor.fetchone()[0]
        print(f"   Containers: {container_count}")
        
        # Check barang
        cursor.execute("SELECT COUNT(*) FROM barang")
        barang_count = cursor.fetchone()[0]
        print(f"   Barang: {barang_count}")
        
        # Check assignments
        cursor.execute("SELECT COUNT(*) FROM detail_container")
        assignment_count = cursor.fetchone()[0]
        print(f"   Assignments: {assignment_count}")
        
        # Check delivery costs
        cursor.execute("SELECT COUNT(*) FROM container_delivery_costs")
        cost_count = cursor.fetchone()[0]
        print(f"   Delivery costs: {cost_count}")
        
        # Check containers with barang
        cursor.execute("""
            SELECT c.container_id, c.container, COUNT(dc.barang_id) as barang_count,
                   SUM(dc.total_harga) as total_value
            FROM containers c
            LEFT JOIN detail_container dc ON c.container_id = dc.container_id
            GROUP BY c.container_id
            ORDER BY c.container_id
        """)
        
        containers_with_barang = cursor.fetchall()
        print(f"\n📊 Container Summary:")
        for row in containers_with_barang:
            container_id, container_name, barang_count, total_value = row
            print(f"   Container {container_id} ({container_name}): {barang_count} items, Rp {total_value or 0:,.0f}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Container Shipping Test Data Generator")
    print("=" * 50)
    
    # Ask user if they want to clear existing data
    clear = input("Clear existing data first? (y/n): ").lower().strip()
    
    if clear == 'y':
        if not clear_existing_data():
            print("Failed to clear existing data")
            exit(1)
    
    # Generate test data
    if generate_test_data():
        print("\n🎉 Test data generation successful!")
        verify_data()
        print("\nYou can now test the application with realistic data.")
    else:
        print("\n💥 Test data generation failed!")