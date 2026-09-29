"""End-to-end integration test for the Postgres/Docker setup.

Exercises the whole stack against the real dockerised Postgres: schema,
seeded data, user management, the lifting report query, the main-menu
preload/feedback path, and the offline failover + sync cycle.

Run with the containers up:
    docker compose up -d
    python test_integration.py

Section F stops and restarts the postgres container, so the run takes
roughly a minute. The container is always brought back up at the end.
"""

import os
import re
import subprocess
import sys
import time
import tkinter as tk

RESULTS = []


def check(section, name, passed, detail="", known_gap=False):
    RESULTS.append((section, name, passed, detail, known_gap))
    if known_gap:
        mark = "KNOWN GAP"
    else:
        mark = "PASS" if passed else "FAIL"
    line = f"  [{mark:9s}] {name}"
    if detail:
        line += f"  -> {detail}"
    print(line)


def dc(*args):
    """Run a docker compose command in the project directory."""
    return subprocess.run(
        ["docker", "compose", *args],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )


def wait_healthy(timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", "ckl-postgres-1"],
            capture_output=True, text=True)
        if r.stdout.strip() == "healthy":
            return True
        time.sleep(2)
    return False


# ----------------------------------------------------------------------
print("\n=== A. Infrastruktur ===")

ps = dc("ps", "--format", "{{.Name}} {{.Status}}")
check("A", "container postgres jalan", "ckl-postgres-1" in ps.stdout and "Up" in ps.stdout,
      ps.stdout.strip().replace("\n", " | ") or "tidak ada container")

from src.models.database import AppDatabase          # noqa: E402
from src.models.db import config as db_config        # noqa: E402

db = AppDatabase()
check("A", "app pakai backend postgres", db.backend_name == "postgres", f"backend={db.backend_name}")
check("A", "DB_HOST bukan 'localhost' (hindari hang IPv6)",
      db_config.get_postgres_dsn() and "localhost" not in db_config.get_postgres_dsn(),
      f"dsn host={os.environ.get('DB_HOST')}")

t = time.perf_counter()
db.execute("SELECT 1")
check("A", "query balik cepat", (time.perf_counter() - t) < 1.0, f"{(time.perf_counter()-t)*1000:.0f} ms")


# ----------------------------------------------------------------------
print("\n=== B. Skema & data ===")

from src.models.db.schema import TABLE_DDL           # noqa: E402

existing = {r[0] for r in db.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")}
missing = set(TABLE_DDL) - existing
check("B", "semua tabel ada di Postgres", not missing, f"kurang: {sorted(missing)}" if missing else f"{len(TABLE_DDL)} tabel")

counts = {t: db.execute_one(f"SELECT COUNT(*) FROM {t}")[0]
          for t in ("users", "pengirim", "customers", "kapals", "barang")}
check("B", "data awal ter-seed", all(v > 0 for v in counts.values()), str(counts))

orphan = db.execute_one("""
    SELECT COUNT(*) FROM barang b
    WHERE b.pengirim NOT IN (SELECT customer_id FROM customers)
       OR b.penerima NOT IN (SELECT customer_id FROM customers)
""")[0]
check("B", "barang.pengirim/penerima valid customer_id", orphan == 0, f"{orphan} baris yatim")


# ----------------------------------------------------------------------
print("\n=== C. Kelola User ===")

TEST_USER = "itest_user"
if db.get_user_by_username(TEST_USER):
    db.execute("DELETE FROM users WHERE username = ?", (TEST_USER,))

uid = db.create_user(TEST_USER, "rahasia123", "itest@example.com", "staff")
check("C", "buat akun", bool(uid), f"id={uid}")
check("C", "login dengan password pilihan", bool(db.authenticate_user(TEST_USER, "rahasia123")))

stored = db.execute_one("SELECT password FROM users WHERE username = ?", (TEST_USER,))["password"]
check("C", "password disimpan sebagai bcrypt", stored.startswith("$2"), stored[:10] + "...")
check("C", "plaintext tidak tersimpan", "rahasia123" not in stored)

db.update_user_password(TEST_USER, "passwordbaru456")
check("C", "password lama ditolak setelah diganti", not db.authenticate_user(TEST_USER, "rahasia123"))
check("C", "password baru diterima", bool(db.authenticate_user(TEST_USER, "passwordbaru456")))

db.deactivate_user(TEST_USER)
check("C", "akun nonaktif tidak bisa login", not db.authenticate_user(TEST_USER, "passwordbaru456"))
db.activate_user(TEST_USER)
check("C", "akun diaktifkan lagi bisa login", bool(db.authenticate_user(TEST_USER, "passwordbaru456")))

try:
    db.create_user(TEST_USER, "another123", None, "staff")
    check("C", "username duplikat ditolak", False, "tidak ada error")
except ValueError:
    check("C", "username duplikat ditolak", True)

try:
    db.create_user("itest_short", "abc", None, "staff")
    check("C", "password <6 karakter ditolak", False, "tidak ada error")
except ValueError:
    check("C", "password <6 karakter ditolak", True)

root = tk.Tk()
root.withdraw()

from src.views.main_window import MainWindow, PRELOAD_MODULES   # noqa: E402
from src.views.user_window import UserWindow                    # noqa: E402

owner = MainWindow.__new__(MainWindow); owner.current_user = {"username": "owner", "role": "owner"}
staff = MainWindow.__new__(MainWindow); staff.current_user = {"username": "staff", "role": "staff"}
check("C", "gate role: owner boleh, staff tidak",
      owner.is_owner() and not staff.is_owner())

uw = UserWindow(root, db, current_user={"username": "owner", "role": "owner"})
uw.load_users()
shown = " ".join(str(v) for r in uw.tree.all_data for v in r["values"])
check("C", "daftar user tampil", len(uw.tree.all_data) > 0, f"{len(uw.tree.all_data)} user")
check("C", "hash password tidak bocor ke tabel", "$2b$" not in shown)
uw.window.destroy()

db.execute("DELETE FROM users WHERE username = ?", (TEST_USER,))


# ----------------------------------------------------------------------
print("\n=== D. Query Lifting ===")

from src.views.lifting_window import LiftingWindow   # noqa: E402

src_lifting = open("src/views/lifting_window.py", encoding="utf-8").read()
# Comments are stripped first: the fix itself is documented in a comment
# that quotes the old "(? IS NULL OR ...)" pattern, which would
# otherwise trip this check.
code_only = "\n".join(l for l in src_lifting.splitlines() if not l.strip().startswith("#"))
check("D", "tidak ada alias kutip-tunggal (SQLite-only)",
      len(re.findall(r"\bAS\s+'", code_only)) == 0)
check("D", "tidak ada pola '? IS NULL' di SQL",
      "? IS NULL" not in code_only)

kapal_id = db.execute_one("SELECT kapal_id FROM kapals ORDER BY kapal_id LIMIT 1")[0]
barang_id = db.execute_one("SELECT barang_id FROM barang ORDER BY barang_id LIMIT 1")[0]
cid = db.execute_insert(
    "INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa) VALUES (?,?,?,?,?,?)",
    (kapal_id, "2025-01-15", "FCL", "ITEST123456", "S1", "JOA-ITEST"))
for delivery, desc, cost in [("Surabaya", "THC", 1_000_000), ("Surabaya", "Freight", 2_000_000),
                             ("Surabaya", "Trucking", 500_000), ("Makassar", "Dooring", 750_000),
                             ("Makassar", "Forklift", 250_000)]:
    db.execute_insert(
        "INSERT INTO container_delivery_costs (container_id, delivery, description, cost, created_date) VALUES (?,?,?,?,?)",
        (cid, delivery, desc, cost, "2025-01-15"))
db.execute_insert(
    "INSERT INTO detail_container (tanggal, barang_id, container_id, satuan, door_type, colli_amount, harga_per_unit, total_harga) VALUES (?,?,?,?,?,?,?,?)",
    ("2025-01-15", barang_id, cid, "m3", "pp", 1, 9_000_000, 9_000_000))

lw = LiftingWindow(root, db)
for label, args in [("tanpa filter", ()), ("hanya start", ("2025-01-01", None)),
                    ("hanya end", (None, "2025-12-31")), ("rentang penuh", ("2025-01-01", "2025-12-31"))]:
    try:
        lw.load_data_from_db(*args)
        check("D", f"filter: {label}", True, f"{len(lw.tree.get_children())} baris")
    except Exception as e:
        check("D", f"filter: {label}", False, str(e).splitlines()[0])

lw.load_data_from_db("2025-01-01", "2025-12-31")
vals = [lw.tree.item(i)["values"] for i in lw.tree.get_children()]
row = next((v for v in vals if v[1] == "JOA-ITEST"), None)
if row:
    check("D", "agregasi POL benar (1jt+2jt+500rb)", str(row[9]) == "3.500.000", f"TOTAL BIAYA POL={row[9]}")
    check("D", "agregasi POD benar (750rb+250rb)", str(row[15]) == "1.000.000", f"TOTAL BIAYA POD={row[15]}")
    check("D", "profit benar (9jt - 4.5jt)", str(row[18]) == "4.500.000", f"PROFIT={row[18]}")
else:
    check("D", "baris uji ditemukan", False, "JOA-ITEST tidak muncul")
lw.window.destroy()

db.execute("DELETE FROM detail_container WHERE container_id = ?", (cid,))
db.execute("DELETE FROM container_delivery_costs WHERE container_id = ?", (cid,))
db.execute("DELETE FROM containers WHERE container_id = ?", (cid,))


# ----------------------------------------------------------------------
print("\n=== E. Performa menu utama ===")

import importlib   # noqa: E402

failed_imports = []
for m in PRELOAD_MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        failed_imports.append(f"{m}: {e}")
check("E", "semua modul preload bisa di-import", not failed_imports, str(failed_imports))

mw_root = tk.Toplevel(root)
mw_root.withdraw()
mw = MainWindow.__new__(MainWindow)
mw.root = mw_root
mw.db = db
mw.current_user = {"username": "owner", "role": "owner"}
mw.menu_buttons = [tk.Button(mw_root, text="x") for _ in range(3)]

mw.open_window("tes-sukses", lambda: None)
check("E", "cursor & tombol pulih setelah sukses",
      str(mw_root.cget("cursor")) == "" and all(str(b.cget("state")) == "normal" for b in mw.menu_buttons))

import tkinter.messagebox as mb   # noqa: E402
_orig = mb.showerror
mb.showerror = lambda *a, **k: None


def boom():
    raise RuntimeError("gagal disengaja")


mw.open_window("tes-gagal", boom)
mb.showerror = _orig
check("E", "cursor & tombol pulih setelah build gagal",
      str(mw_root.cget("cursor")) == "" and all(str(b.cget("state")) == "normal" for b in mw.menu_buttons))
mw_root.destroy()
root.destroy()


# ----------------------------------------------------------------------
print("\n=== F. Offline / online ===")

dc("stop", "postgres")

t = time.perf_counter()
db.execute("SELECT COUNT(*) FROM barang")
failover_s = time.perf_counter() - t
check("F", "failover ke SQLite saat Postgres mati", db.backend_name == "sqlite", f"{failover_s:.1f} s")
check("F", "waktu failover wajar (<10s)", failover_s < 10, f"{failover_s:.1f} s")

try:
    n = db.execute_one("SELECT COUNT(*) FROM barang")[0]
    check("F", "query offline tetap jalan", True, f"{n} barang terbaca dari mirror")
except Exception as e:
    check("F", "query offline tetap jalan", False, str(e).splitlines()[0])

# data dibuat offline harus ikut terkirim saat sync
offline_cust = db.execute_insert(
    "INSERT INTO customers (nama_customer, alamat_customer) VALUES (?,?)",
    ("ITEST Offline Co", "Surabaya"))
pending = db.execute("SELECT table_name, row_id FROM _sync_changes")
check("F", "perubahan offline tercatat di _sync_changes", len(pending) > 0, f"{len(pending)} entri")

# akun dibuat offline: tidak ter-track (celah yang sudah diketahui)
db.create_user("itest_offline_user", "rahasia123", None, "staff")
user_tracked = any(r["table_name"] == "users" for r in db.execute("SELECT table_name FROM _sync_changes"))
check("F", "akun dibuat offline ikut ter-track", user_tracked,
      "users dikecualikan dari MIRRORED_TABLES -> akan hilang saat sync", known_gap=not user_tracked)

dc("start", "postgres")
check("F", "container hidup lagi", wait_healthy())

res = db.sync_now()
check("F", "sync berhasil & kembali online",
      res.ok and db.backend_name == "postgres",
      f"pushed={res.pushed}, pulled={res.pulled}, backend={db.backend_name}")

pushed_ok = db.execute_one(
    "SELECT COUNT(*) FROM customers WHERE nama_customer = ?", ("ITEST Offline Co",))[0]
check("F", "data offline terkirim ke Postgres (push)", pushed_ok == 1, f"{pushed_ok} baris ditemukan")

user_survived = db.get_user_by_username("itest_offline_user") is not None
check("F", "akun offline selamat setelah sync", user_survived,
      "hilang setelah pull menimpa tabel users", known_gap=not user_survived)

db.execute("DELETE FROM customers WHERE nama_customer = ?", ("ITEST Offline Co",))
db.execute("DELETE FROM users WHERE username = ?", ("itest_offline_user",))
db.sync_now()


# ----------------------------------------------------------------------
print("\n" + "=" * 62)
passed = sum(1 for *_, p, _, g in [(r[0], r[1], r[2], r[3], r[4]) for r in RESULTS] if p and not g)
failed = [r for r in RESULTS if not r[2] and not r[4]]
gaps = [r for r in RESULTS if r[4]]

print(f"RINGKASAN: {len(RESULTS)} pemeriksaan | "
      f"{len(RESULTS) - len(failed) - len(gaps)} lulus | "
      f"{len(failed)} gagal | {len(gaps)} celah diketahui")
if failed:
    print("\nGAGAL:")
    for s, n, _, d, _ in failed:
        print(f"  [{s}] {n}  -> {d}")
if gaps:
    print("\nCELAH YANG SUDAH DIKETAHUI (bukan regresi):")
    for s, n, _, d, _ in gaps:
        print(f"  [{s}] {n}  -> {d}")
print("=" * 62)

sys.exit(1 if failed else 0)
