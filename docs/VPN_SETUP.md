# Akses Database Lewat WireGuard

Catatan setup koneksi aplikasi ke PostgreSQL di server lewat tunnel
WireGuard. Ditulis supaya komputer berikutnya bisa disiapkan tanpa
menebak-nebak lagi.

## Kenapa lewat VPN

PostgreSQL tidak boleh terbuka ke internet. Dengan WireGuard, satu-satunya
port yang terbuka di IP publik adalah 51820/udp; port database hanya bisa
dijangkau dari dalam tunnel.

Alur koneksinya:

```
Aplikasi (psycopg)
    |  TCP ke 10.0.0.1:5432
    v
Adapter WireGuard di laptop (10.0.0.2)
    |  dibungkus + dienkripsi
    v
UDP ke <IP-publik-server>:51820    <- satu-satunya port terbuka
    v
wg0 di server (10.0.0.1)
    v
PostgreSQL :5432
```

Aplikasi tidak tahu ada VPN. Kodenya tidak berubah sama sekali - WireGuard
bekerja di lapisan bawah, membuat 10.0.0.1 seolah komputer sebelah. Yang
berubah hanya `DB_HOST` di `.env`.

## Sisi server

### WireGuard - /etc/wireguard/wg0.conf

```ini
[Interface]
Address    = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <private key server>

[Peer]
# nama-komputer
PublicKey  = <public key komputer itu>
AllowedIPs = 10.0.0.2/32
```

Satu blok `[Peer]` per komputer, masing-masing dengan key sendiri dan IP
sendiri. Jangan pernah memakai ulang satu key untuk dua komputer - nanti
akses satu laptop tidak bisa dicabut tanpa mematikan semuanya.

### Firewall

| Port        | Akses             | Keterangan          |
|-------------|-------------------|---------------------|
| 51820/udp   | dari mana saja    | pintu masuk WireGuard |
| 22/tcp      | dari mana saja    | SSH                 |
| 5432/tcp    | hanya lewat wg0   | PostgreSQL          |

```bash
sudo ufw allow in on wg0 to any port 5432 proto tcp
```

Bentuk `in on wg0` itu wajib. `sudo ufw allow 5432` polos akan membuka
database ke seluruh internet dan membatalkan gunanya VPN ini.

ufw menolak apa pun yang tidak disebut eksplisit, jadi port yang tidak
muncul di `ufw status` berarti tertutup - bukan berarti belum diatur.

### PostgreSQL

Batasi listener ke tunnel saja, di `postgresql.conf`:

```
listen_addresses = 'localhost,10.0.0.1'
```

Perlu `restart` (bukan reload) - parameter ini hanya dibaca saat start.
Setelah itu `ss -lntp | grep 5432` harus menampilkan `10.0.0.1:5432`,
bukan `0.0.0.0:5432`. Dengan begitu database tetap aman walau aturan
firewall salah.

Di `pg_hba.conf`:

```
host  ckl_db  ckl_user  10.0.0.0/24  scram-sha-256
```

- `host`, bukan `hostssl` - `hostssl` hanya menerima koneksi TLS,
  sedangkan aplikasi memakai `sslmode=disable`.
- `/24`, bukan `/32` - supaya komputer berikutnya tidak perlu mengedit
  file ini lagi.
- Nama database dan user harus persis sama dengan isi `.env`.

```bash
sudo systemctl reload postgresql
```

## Sisi klien (Windows)

Install WireGuard for Windows, lalu **Add empty tunnel** (jangan tulis
private key sendiri - biarkan digenerate di komputer itu).

```ini
[Interface]
PrivateKey = <biarkan hasil generate>
Address    = 10.0.0.2/32

[Peer]
PublicKey           = <public key server>
Endpoint            = <IP-publik-server>:51820
AllowedIPs          = 10.0.0.0/24
PersistentKeepalive = 25
```

- `AllowedIPs = 10.0.0.0/24` - split tunnel; hanya trafik ke jaringan VPN
  yang lewat tunnel. Kalau diisi `0.0.0.0/0`, seluruh internet dibelokkan
  ke server dan WireGuard mengaktifkan mode kill-switch.
- `PersistentKeepalive = 25` - menjaga jalur NAT tetap terbuka saat idle.

Salin *Public key* yang muncul di dialog ke blok `[Peer]` di server, lalu:

```bash
sudo wg syncconf wg0 <(wg-quick strip wg0)
```

`syncconf` menerapkan perubahan tanpa memutus tunnel yang sedang jalan.

### File .env di sebelah aplikasi

```
DB_ENGINE=postgres
DB_HOST=10.0.0.1
DB_PORT=5432
DB_NAME=ckl_db
DB_USER=ckl_user
DB_PASSWORD=<password>
DB_SSLMODE=disable
```

`sslmode=disable` aman di sini: seluruh jalur sudah dienkripsi WireGuard
dan 5432 tidak terbuka ke publik. Memakai `hostssl` + `require` menuntut
sertifikat di server, dan dua sisi harus diubah bersamaan.

Untuk build `.exe`, `.env` harus berada **di direktori yang sama dengan
executable**. Lihat `app_root()` di `src/models/db/config.py`.

## Tentang kunci

Ada empat kunci, dua per mesin:

> Tiap config berisi **private key miliknya sendiri** dan **public key
> milik lawan bicaranya**.

Patokan untuk mengecek:

- public key interface **server** = `[Peer] PublicKey` di **client**
- public key interface **client** = `[Peer] PublicKey` di **server**

Private key tidak pernah keluar dari mesin tempat ia dibuat. Yang boleh
dikirim lewat chat, email, atau WhatsApp hanya public key.

Kalau public key sendiri muncul di blok `[Peer]` sendiri, tunnel itu
menunjuk ke dirinya sendiri dan handshake tidak akan pernah berhasil.

## Urutan pengecekan kalau bermasalah

Periksa berurutan - tiap lapisan bergantung pada lapisan sebelumnya.

| # | Cek           | Perintah                                       | Kalau gagal                              |
|---|---------------|------------------------------------------------|------------------------------------------|
| 1 | Handshake     | `sudo wg show` (server)                        | key salah, atau UDP 51820 terblokir      |
| 2 | Alamat        | `ipconfig` (Windows)                           | adapter harus dapat 10.0.0.2             |
| 3 | Routing       | `ping 10.0.0.1`                                | `AllowedIPs` tidak cocok                 |
| 4 | Port database | `Test-NetConnection 10.0.0.1 -Port 5432`       | firewall, atau `listen_addresses`        |
| 5 | Izin login    | tes psycopg                                    | `pg_hba.conf`                            |

Status "Active" di aplikasi WireGuard **tidak** berarti terhubung - itu
hanya berarti adapter lokal menyala. Yang membuktikan koneksi adalah baris
`latest handshake` dan angka *received* yang bukan 0.

`Test-NetConnection` hanya bisa menguji TCP, jadi tidak bisa dipakai untuk
port 51820 yang berbasis UDP. WireGuard juga sengaja tidak pernah membalas
paket yang tidak terautentikasi, jadi "tidak ada balasan" bukan bukti apa-apa.

### Membaca pesan error

| Pesan                          | Artinya                                | Perbaikannya di |
|--------------------------------|----------------------------------------|-----------------|
| `connection timeout expired`   | paket hilang                           | alamat/port, firewall |
| `connection refused`           | alamat benar, tidak ada yang mendengar | Postgres mati, salah port |
| `no pg_hba.conf entry`         | jaringan sudah tembus                  | `pg_hba.conf`   |
| `password authentication failed` | izin sudah benar                     | `DB_PASSWORD`   |

Urutan dari atas ke bawah itu tanda kemajuan.

Kalau `pg_hba.conf` sudah diedit tapi errornya tidak berubah, pastikan
server membaca file yang sama dengan yang Anda edit (bisa ada lebih dari
satu cluster Postgres di satu mesin):

```bash
sudo -u postgres psql -p 5432 -c "SHOW hba_file;"
sudo -u postgres psql -p 5432 -c \
  "SELECT line_number, type, database, user_name, address, auth_method, error
     FROM pg_hba_file_rules WHERE database::text LIKE '%ckl%';"
```

Query kedua membaca isi **file**, bukan yang aktif di memori - jadi kalau
barisnya sudah benar di situ tapi koneksi masih ditolak, reload-nya yang
belum kena.

## Menambah komputer baru

1. Install WireGuard, **Add empty tunnel**, salin *Public key*-nya
2. Isi config seperti di atas, `Address` diganti `10.0.0.3/32`
3. Tambahkan blok `[Peer]` baru di server dengan `AllowedIPs = 10.0.0.3/32`
4. `sudo wg syncconf wg0 <(wg-quick strip wg0)`
5. Salin `.env` ke komputer itu

`pg_hba.conf` tidak perlu disentuh karena sudah memakai `/24`.

## Mode offline

Kalau tunnel mati, aplikasi tidak error - ia pindah ke mirror SQLite lokal
dan mencatat perubahan di change-log. Indikator di pojok berubah jadi
`Offline (n belum sync)`, dan tombol **Sync** mengirim perubahan itu ke
server begitu tunnel hidup lagi. Lihat `src/models/db/sync_engine.py`.

Jadi VPN mati bukan keadaan darurat. Yang perlu dipastikan adalah orang
menekan Sync setelah koneksi pulih.
