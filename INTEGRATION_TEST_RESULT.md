# Hasil Integration Test

Laporan hasil pengujian menyeluruh terhadap setup Postgres/Docker dan
perubahan yang menyertainya.

| | |
|---|---|
| Tanggal | 15 September 2026 |
| Suite | `test_integration.py` |
| Cara menjalankan | `docker compose up -d` lalu `python test_integration.py` |
| Durasi | ± 1 menit (bagian F mematikan & menghidupkan container) |
| Exit code | `0` |

**Hasil: 41 pemeriksaan — 39 lulus, 0 gagal, 2 celah yang sudah diketahui.**

Lingkungan: Python 3.11.8 · Windows · PostgreSQL 16.13 (`postgres:16-alpine`)
di Docker · commit dasar `022868c`.

---

## Ringkasan per bagian

| Bagian | Cakupan | Hasil |
|---|---|---|
| A. Infrastruktur | Container, koneksi, kecepatan query | 4/4 lulus |
| B. Skema & data | Tabel, data awal, integritas relasi | 3/3 lulus |
| C. Kelola User | Fitur owner: buat akun & atur password | 13/13 lulus |
| D. Query Lifting | Perbaikan kompatibilitas Postgres | 9/9 lulus |
| E. Performa menu | Preload & indikator loading | 3/3 lulus |
| F. Offline / online | Failover dan sinkronisasi | 7/9 lulus, 2 celah |

---

## A. Infrastruktur — 4/4

| Pemeriksaan | Hasil |
|---|---|
| Container postgres jalan & healthy | ✅ |
| App memakai backend `postgres` (bukan fallback) | ✅ |
| `DB_HOST` bukan `localhost` | ✅ `127.0.0.1` |
| Query kembali cepat | ✅ 1 ms |

Pemeriksaan `DB_HOST` adalah **uji regresi**. Sebelumnya `localhost` di
Windows di-resolve ke IPv6 (`::1`) lebih dulu sementara Docker hanya
mengekspos IPv4, sehingga thread connection pool menggantung tanpa pesan
error dan aplikasi diam-diam jatuh ke SQLite.

---

## B. Skema & data — 3/3

| Pemeriksaan | Hasil |
|---|---|
| Semua tabel ada di Postgres | ✅ 9 tabel |
| Data awal ter-seed | ✅ users 3, pengirim 5, customers 8, kapals 3, barang 8 |
| `barang.pengirim`/`penerima` valid `customer_id` | ✅ 0 baris yatim |

Pemeriksaan ketiga penting karena kedua kolom itu bertipe `TEXT` di
SQLite tapi `INTEGER` di Postgres — nilainya memang menyimpan
`customer_id`, bukan nama.

---

## C. Kelola User — 13/13

Fitur baru: owner bisa membuat akun dan mengatur passwordnya.

**Fungsional**

| Pemeriksaan | Hasil |
|---|---|
| Buat akun baru | ✅ |
| Login dengan password yang dipilih | ✅ |
| Ganti password — password lama ditolak | ✅ |
| Ganti password — password baru diterima | ✅ |
| Akun dinonaktifkan tidak bisa login | ✅ |
| Akun diaktifkan kembali bisa login | ✅ |
| Daftar user tampil di tabel | ✅ 4 user |

**Validasi**

| Pemeriksaan | Hasil |
|---|---|
| Username duplikat ditolak | ✅ |
| Password < 6 karakter ditolak | ✅ |

**Keamanan**

| Pemeriksaan | Hasil |
|---|---|
| Password disimpan sebagai hash bcrypt | ✅ `$2b$12$…` |
| Plaintext tidak tersimpan di database | ✅ |
| Hash tidak bocor ke tabel di layar | ✅ |
| Gate role: owner boleh, staff ditolak | ✅ |

---

## D. Query Lifting — 9/9

Perbaikan atas error `syntax error at or near "'ETD SUB'"`.

**Uji regresi kode**

| Pemeriksaan | Hasil |
|---|---|
| Tidak ada alias kutip-tunggal (khas SQLite) | ✅ 18 alias sudah diperbaiki |
| Tidak ada pola `? IS NULL` di SQL | ✅ |

**Jalur filter** — keempatnya lulus: tanpa filter, hanya tanggal awal,
hanya tanggal akhir, dan rentang penuh.

**Kebenaran angka** — diverifikasi dengan data uji (1 container, 5 biaya,
1 invoice) lalu dibersihkan kembali:

| Nilai | Diharapkan | Hasil |
|---|---|---|
| TOTAL BIAYA POL | 1jt + 2jt + 500rb = 3.500.000 | ✅ 3.500.000 |
| TOTAL BIAYA POD | 750rb + 250rb = 1.000.000 | ✅ 1.000.000 |
| PROFIT | 9.000.000 − 4.500.000 | ✅ 4.500.000 |

Query juga sudah diuji berjalan di backend SQLite, karena aplikasi bisa
jatuh ke sana saat offline.

---

## E. Performa menu utama — 3/3

| Pemeriksaan | Hasil |
|---|---|
| Semua modul preload bisa di-import | ✅ 7 modul |
| Cursor & tombol pulih setelah window sukses dibuka | ✅ |
| Cursor & tombol pulih setelah pembuatan window gagal | ✅ |

Pemeriksaan terakhir memastikan blok `finally` benar-benar bekerja —
tanpa itu satu kegagalan akan meninggalkan seluruh menu dalam keadaan
nonaktif dengan cursor `watch` selamanya.

Perbandingan waktu klik pertama, kondisi identik:

| Window | Sebelum | Sesudah |
|---|---|---|
| Container | 924 ms | 601 ms |
| Customer | 671 ms | 302 ms |
| Barang | 914 ms | 632 ms |
| Kapal | 765 ms | 581 ms |

---

## F. Offline / online — 7/9

| Pemeriksaan | Hasil |
|---|---|
| Failover ke SQLite saat Postgres mati | ✅ 5,0 detik |
| Waktu failover wajar (< 10 detik) | ✅ |
| Query tetap jalan saat offline | ✅ data terbaca dari mirror |
| Perubahan offline tercatat di `_sync_changes` | ✅ |
| Container hidup lagi | ✅ |
| Sync berhasil & kembali online | ✅ pushed 1, pulled 28 |
| Data offline benar-benar sampai ke Postgres | ✅ |
| Akun dibuat offline ikut ter-track | ⚠️ celah |
| Akun offline selamat setelah sync | ⚠️ celah |

### Perilaku sinkronisasi yang terukur

| Kejadian | Waktu |
|---|---|
| Postgres mati → aplikasi pindah ke SQLite | **5,0 detik** |
| Query berikutnya saat offline | instan |
| Postgres hidup lagi, tanpa tekan Sync | **tetap offline** |
| Tekan tombol 🔄 Sync | 0,1 detik → online |

Angka 5 detik berasal dari `DB_CONNECT_TIMEOUT=5` di `.env`, dan berlaku
untuk semua mode kegagalan — bahkan saat port langsung menolak koneksi —
karena pool selalu menunggu penuh `pool.wait(timeout=5)`.

> **Aplikasi tidak pernah kembali online dengan sendirinya.** Satu-satunya
> jalan kembali adalah tombol 🔄 Sync. Kalau koneksi sempat putus,
> tombol itu harus ditekan manual agar data masuk ke Postgres.

---

## Temuan yang belum ditangani

### 1. Akun yang dibuat offline hilang saat sync ⚠️

`mirror.py:16` — `MIRRORED_TABLES = [t for t in TABLE_DDL if t != "users"]`.
Tabel `users` **dikecualikan dari push** tapi tetap ikut **pull**, dan pull
menghapus lalu menimpa seluruh isi tabel.

Akibatnya, jika owner membuat akun atau mengganti password **selagi
offline**, perubahan itu hilang tanpa pesan error apa pun begitu Sync
ditekan. Diverifikasi langsung:

| Langkah | Hasil |
|---|---|
| Buat akun saat offline | tersimpan di lokal |
| Tercatat di `_sync_changes`? | **tidak — 0 entri** |
| Setelah tekan Sync | **akun hilang** |

Asumsi lama di kode berbunyi *"accounts aren't created/edited offline"* —
asumsi itu tidak lagi berlaku sejak fitur Kelola User ditambahkan.

**Pilihan perbaikan:**

1. **Nonaktifkan Kelola User saat offline** — window menolak dibuka dengan
   pesan jelas, mengikuti pola `archive_container` yang sudah ada.
   Sederhana dan tidak ada data hilang. *(disarankan)*
2. **Masukkan `users` ke push tracking** — lebih fleksibel, tapi perlu
   memikirkan penyelesaian konflik (mis. password diubah di dua tempat).

### 2. `seed_initial_data.py` tidak idempotent ⚠️

Menjalankannya pada database yang sudah terisi **menduplikasi semua
data**. Terbukti saat pengujian: pengirim 5→10, customers 8→15,
kapals 3→6, barang 8→15. Hanya pengecekan akun `staff` yang dijaga;
pengirim, customers, kapals, dan barang tidak.

Duplikat sudah dibersihkan dan data kembali ke 5/8/3/8. Perbaikannya:
tambahkan pengecekan "sudah ada, lewati" seperti yang dipakai untuk akun
`staff`.

---

## Catatan

- **Suite ini aman dijalankan berulang.** Sudah diverifikasi: jumlah data
  sebelum dan sesudah run identik (5/8/3/8), dan seluruh data uji
  (`ITEST*`) dibersihkan sendiri.
- **Container selalu dihidupkan kembali** di akhir run, termasuk jika
  bagian F gagal di tengah.
- Bagian F sengaja mematikan container `postgres`. Jangan jalankan suite
  ini terhadap database produksi.
- Data bernama `TEST` di tabel customers dan barang adalah data manual,
  bukan buatan suite ini, dan tidak ikut terhapus.
