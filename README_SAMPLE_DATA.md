# Generate Sample Data Container

Script ini digunakan untuk membuat data sample container dengan tipe **20'**, **21'**, dan **40'**.

## 🚀 Cara Menggunakan

### 1. Pastikan sudah ada data kapal di database
Sebelum menjalankan script, pastikan Anda sudah menambahkan minimal 1 kapal melalui aplikasi.

### 2. Jalankan script
Buka terminal/command prompt di folder project, lalu jalankan:

```bash
python generate_container_sample.py
```

### 3. Pilih menu
```
1. Generate sample containers (20', 21', 40') - Buat data sample baru
2. Hapus sample containers - Hapus semua data sample
3. Exit - Keluar dari script
```

## 📦 Apa yang dibuat script ini?

Script akan membuat **6 container** untuk setiap kapal yang ada di database:
- **2 container tipe 20'**
- **2 container tipe 21'**
- **2 container tipe 40'**

Setiap container akan memiliki:
- ✅ Nomor container unik (TCLU123456, MSCU789012, dll)
- ✅ Party/tipe container (20', 21', atau 40')
- ✅ Seal number
- ✅ Ref JOA (nomor referensi Job Order Account)
- ✅ Terhubung ke kapal yang sudah ada

## 📊 Contoh Output

```
===========================================================
GENERATE SAMPLE DATA CONTAINER
===========================================================

✓ Ditemukan 3 kapal:
  - ID 1: EVER GIVEN (ETD: 2025-01-15)
  - ID 2: MAERSK LINE (ETD: 2025-01-20)
  - ID 3: CMA CGM (ETD: 2025-01-25)

📦 Membuat 18 sample containers...
✓ Insert: 20'  | TCLU1234567 | EVER GIVEN | JOA: JOA/2025/1234
✓ Insert: 20'  | MSCU7890123 | EVER GIVEN | JOA: JOA/2025/1235
✓ Insert: 21'  | HLBU4567890 | EVER GIVEN | JOA: JOA/2025/1236
...

===========================================================
✅ SELESAI!
   - Berhasil insert: 18 container
   - Di-skip (duplikat): 0 container
===========================================================

📊 SUMMARY PER TYPE:
   20': 6 containers
   21': 6 containers
   40': 6 containers

💡 TIP: Buka aplikasi dan refresh untuk melihat data baru!
```

## ⚠️ Catatan Penting

1. **Duplikat**: Script akan otomatis skip jika nomor container sudah ada di database
2. **Kapal**: Minimal harus ada 1 kapal di database sebelum menjalankan script
3. **Hapus data**: Gunakan menu #2 untuk menghapus semua sample containers yang dibuat script ini

## 🔧 Troubleshooting

**Error: "Tidak ada data kapal di database!"**
- Solusi: Buka aplikasi, masuk ke menu Kapal, dan tambahkan minimal 1 kapal terlebih dahulu

**Container tidak muncul di aplikasi**
- Solusi: Tutup dan buka ulang aplikasi, atau klik tombol Refresh di halaman Container

## 💻 Kode SQL Manual (Opsional)

Jika ingin menambahkan container secara manual via SQL, gunakan query berikut:

```sql
INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, created_at)
VALUES (
    1,                      -- kapal_id (sesuaikan dengan ID kapal yang ada)
    '2025-01-15',          -- ETD
    '20''',                -- Party (20', 21', atau 40')
    'TCLU1234567',         -- Nomor container
    'SEAL12345',           -- Seal number
    'JOA/2025/1234',       -- Ref JOA
    CURRENT_TIMESTAMP      -- Waktu dibuat
);
```

---

📝 **Catatan**: Pastikan tipe party ditulis dengan benar: `20'`, `21'`, atau `40'`
