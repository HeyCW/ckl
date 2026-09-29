"""Differential test: SQLite vs Postgres.

Runs the SAME sequence of operations against both backends on freshly
created, identically seeded databases, then compares every result -
values AND Python types. Anything that differs is a behavior change the
move to Postgres introduced.

Each backend runs in its own subprocess: database.py caches the backend
choice, the connection pools, and the AppDatabase singleton in module
globals, so two backends cannot share one interpreter.

    docker compose -f docker-compose.parity.yml up -d   # or let this script do it
    python test_parity.py

The Postgres side uses a throwaway container on port 55433 - it never
touches the app's own database on 5432, and never the server.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
from decimal import Decimal

PG = {
    "container": "ckl_parity_pg",
    "port": "55433",
    "db": "ckl_parity",
    "user": "parity",
    "password": "parity",
}

# Clock-derived columns: compare their TYPE, never their value.
VOLATILE_COLS = {"created_at", "updated_at", "assigned_at", "last_login", "changed_at"}
# Random per row (bcrypt salt).
SECRET_COLS = {"password"}


# --------------------------------------------------------------------------
# normalization
# --------------------------------------------------------------------------

def norm(v):
    """Make a value comparable across drivers."""
    if isinstance(v, Decimal):
        return round(float(v), 6)
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, datetime):
        return v.replace(microsecond=0).isoformat(sep=" ")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray)):
        return v.hex()
    return v


def tname(v):
    return type(v).__name__


def row_to_dict(row):
    if row is None:
        return None
    if hasattr(row, "keys"):
        return {k: row[k] for k in row.keys()}
    if isinstance(row, (list, tuple)):
        return {str(i): x for i, x in enumerate(row)}
    return {"0": row}


def shape(result):
    """Normalized value + type shape of whatever a probe returned."""
    if result is None:
        return {"kind": "none"}
    if isinstance(result, (str, int, float, bool, Decimal)):
        return {"kind": "scalar", "value": norm(result), "type": tname(result)}
    if isinstance(result, dict):
        return {
            "kind": "dict",
            "value": {k: norm(v) for k, v in sorted(result.items())},
            "types": {k: tname(v) for k, v in sorted(result.items())},
        }
    if isinstance(result, list):
        rows = [row_to_dict(r) for r in result]
        return {
            "kind": "rows",
            "count": len(rows),
            "value": [
                {k: norm(v) for k, v in sorted(r.items()) if k not in VOLATILE_COLS | SECRET_COLS}
                for r in rows if r is not None
            ],
            "types": (
                {k: tname(v) for k, v in sorted(rows[0].items())} if rows and rows[0] else {}
            ),
        }
    d = row_to_dict(result)
    return {
        "kind": "row",
        "value": {k: norm(v) for k, v in sorted(d.items()) if k not in VOLATILE_COLS | SECRET_COLS},
        "types": {k: tname(v) for k, v in sorted(d.items())},
    }


# --------------------------------------------------------------------------
# the probes
# --------------------------------------------------------------------------

def seed(db):
    """Deterministic data, identical on both backends. Raw SQL so no
    randomness (bcrypt) and no reliance on method signatures."""
    for t in ("detail_container", "barang_tax", "container_delivery_costs",
              "barang", "containers", "kapals", "customers", "pengirim", "users"):
        db.execute(f"DELETE FROM {t}")

    fixed_hash = "$2b$12$abcdefghijklmnopqrstuvABCDEFGHIJKLMNOPQRSTUVWXYZ0123456"
    for uname, role, active in (("admin", "admin", 1), ("owner", "owner", 1),
                                ("staff", "staff", 1), ("mati", "staff", 0)):
        db.execute(
            "INSERT INTO users (username, password, email, role, is_active) VALUES (?, ?, ?, ?, ?)",
            (uname, fixed_hash, f"{uname}@example.com", role, active),
        )

    for nama in ("PT Berkah Jaya", "cv sentosa", "PT Andalan", "PT  Zeta"):
        db.execute("INSERT INTO pengirim (nama_pengirim) VALUES (?)", (nama,))

    for nama, alamat in (("PT Sinar Harapan", "Jakarta"), ("cv mitra abadi", "Surabaya"),
                         ("PT Cahaya Timur", "Makassar"), ("PT Ångström", "Medan")):
        db.execute("INSERT INTO customers (nama_customer, alamat_customer) VALUES (?, ?)",
                   (nama, alamat))

    db.execute(
        'INSERT INTO kapals (shipping_line, feeder, etd_sub, cls, "open", "full", destination) '
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("SPIL", "KM TANTO", "2026-01-15", "2026-01-10", "2026-01-11", "2026-01-13", "Makassar"),
    )
    db.execute(
        'INSERT INTO kapals (shipping_line, feeder, etd_sub, cls, "open", "full", destination) '
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("TANTO", "KM MERATUS", None, None, None, None, "Surabaya"),
    )

    # One container with a NULL seal, one without - NULL ordering probe.
    db.execute(
        "INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, archived) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, "2026-01-15", "20FT", "CONT001", "SEAL-A", "JOA-1", 0),
    )
    db.execute(
        "INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, archived) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, "2026-02-20", "40HC", "CONT002", None, "JOA-2", 0),
    )
    db.execute(
        "INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa, archived) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (None, None, None, "CONT003", None, None, 1),
    )

    for pid, rid, nama, m3, ton, pajak in (
        (1, 2, "TV LED 43 inch", 0.115, 0.015, 0),
        (2, 3, "Meja Kantor", 0.9, 0.05, 1),
        (3, 1, "Kain Cotton Roll", 0.108, 0.025, 0),
    ):
        db.execute(
            "INSERT INTO barang (pengirim, penerima, nama_barang, m3_barang, ton_barang, "
            "container_barang, m3_pp, ton_pp, col_pp, container_pp, pajak, archived) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (pid, rid, nama, m3, ton, 0.003, 850000, 5000000, 150000, 8500000, pajak, 0),
        )

    for desc, delivery, cost in (("THC Surabaya", "Surabaya", 1000000.0),
                                 ("Freight LSS", "Surabaya", 2000000.0),
                                 ("Trucking Dooring", "Makassar", 750000.0),
                                 ("ops lain-lain", "Surabaya", 500000.5)):
        db.execute(
            "INSERT INTO container_delivery_costs (container_id, delivery, description, "
            "cost_description, cost, created_date) VALUES (?, ?, ?, ?, ?, ?)",
            (1, delivery, desc, desc, cost, "2026-01-15"),
        )

    db.execute(
        "INSERT INTO detail_container (tanggal, barang_id, container_id, satuan, door_type, "
        "colli_amount, harga_per_unit, total_harga) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("2026-01-15", 1, 1, "m3", "pp", 3, 850000.00, 2550000.00),
    )
    db.execute(
        "INSERT INTO detail_container (tanggal, barang_id, container_id, satuan, door_type, "
        "colli_amount, harga_per_unit, total_harga) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("2026-01-16", 2, 1, "ton", "pd", 1, 1234567.89, 1234567.89),
    )


SQL_PROBES = [
    # (name, sql, params)
    ("sql/null_order_asc", "SELECT container, seal FROM containers ORDER BY seal ASC, container ASC", ()),
    ("sql/null_order_desc", "SELECT container, seal FROM containers ORDER BY seal DESC, container ASC", ()),
    ("sql/like_lowercase_prefix", "SELECT COUNT(*) FROM customers WHERE nama_customer LIKE 'pt%'", ()),
    ("sql/like_uppercase_prefix", "SELECT COUNT(*) FROM customers WHERE nama_customer LIKE 'PT%'", ()),
    ("sql/like_literal_percent", "SELECT COUNT(*) FROM container_delivery_costs WHERE description LIKE '%THC%'", ()),
    ("sql/like_param", "SELECT COUNT(*) FROM container_delivery_costs WHERE description LIKE ?", ("%thc%",)),
    ("sql/order_mixed_case", "SELECT nama_customer FROM customers ORDER BY nama_customer ASC", ()),
    ("sql/order_pengirim", "SELECT nama_pengirim FROM pengirim ORDER BY nama_pengirim ASC", ()),
    ("sql/int_division", "SELECT 7/2 AS hasil", ()),
    ("sql/concat", "SELECT 'a' || 'b' AS hasil", ()),
    ("sql/sum_empty", "SELECT SUM(cost) AS s FROM container_delivery_costs WHERE 1=0", ()),
    ("sql/count_empty", "SELECT COUNT(*) AS c FROM container_delivery_costs WHERE 1=0", ()),
    ("sql/coalesce_sum_empty", "SELECT COALESCE(SUM(cost), 0) AS s FROM container_delivery_costs WHERE 1=0", ()),
    ("sql/avg", "SELECT AVG(cost) AS a FROM container_delivery_costs", ()),
    ("sql/sum_money", "SELECT SUM(total_harga) AS s FROM detail_container", ()),
    ("sql/sum_int", "SELECT SUM(colli_amount) AS s FROM detail_container", ()),
    ("sql/bool_int_compare", "SELECT COUNT(*) AS c FROM users WHERE is_active = 1", ()),
    ("sql/fk_int_compare", "SELECT COUNT(*) AS c FROM barang WHERE pengirim = 1", ()),
    ("sql/join_pengirim_customer",
     "SELECT b.nama_barang, c.nama_customer FROM barang b "
     "JOIN customers c ON b.pengirim = c.customer_id ORDER BY b.barang_id", ()),
    ("sql/group_by_pk",
     "SELECT cont.*, COUNT(dc.barang_id) AS n FROM containers cont "
     "LEFT JOIN detail_container dc ON cont.container_id = dc.container_id "
     "GROUP BY cont.container_id ORDER BY cont.container_id", ()),
    ("sql/group_by_nonpk",
     "SELECT delivery, SUM(cost) AS s FROM container_delivery_costs "
     "GROUP BY delivery ORDER BY delivery", ()),
    ("sql/max_date", "SELECT MAX(etd) AS m FROM containers", ()),
    ("sql/min_timestamp", "SELECT MIN(created_at) AS m FROM containers", ()),
    ("sql/limit", "SELECT container FROM containers ORDER BY container_id LIMIT 2", ()),
    ("sql/null_param_is_null", "SELECT COUNT(*) AS c FROM containers WHERE seal IS NULL", ()),
    ("sql/case_when",
     "SELECT SUM(CASE WHEN description LIKE '%Truck%' THEN cost ELSE 0 END) AS s "
     "FROM container_delivery_costs", ()),
    ("sql/distinct", "SELECT DISTINCT delivery FROM container_delivery_costs ORDER BY delivery", ()),
    ("sql/round", "SELECT ROUND(cost) AS r FROM container_delivery_costs ORDER BY id", ()),
    ("sql/abs_negative", "SELECT ABS(-5) AS a", ()),
    ("sql/upper_lower", "SELECT UPPER(nama_customer) AS u, LOWER(nama_customer) AS l FROM customers ORDER BY customer_id", ()),
    ("sql/length", "SELECT LENGTH(nama_customer) AS n FROM customers ORDER BY customer_id", ()),
    ("sql/in_clause", "SELECT COUNT(*) AS c FROM barang WHERE pengirim IN (1, 2)", ()),
    ("sql/between_date", "SELECT COUNT(*) AS c FROM containers WHERE etd BETWEEN '2026-01-01' AND '2026-01-31'", ()),
    ("sql/nested_subquery",
     "SELECT COUNT(*) AS c FROM barang WHERE barang_id IN "
     "(SELECT barang_id FROM detail_container WHERE container_id = 1)", ()),
]

TABLES = ["users", "customers", "kapals", "containers", "barang",
          "barang_tax", "detail_container", "container_delivery_costs", "pengirim"]


def method_probes(db):
    """(name, callable) for every business method safe to call with
    deterministic arguments."""
    return [
        ("m/get_all_users", lambda: db.get_all_users()),
        ("m/get_user_by_username", lambda: db.get_user_by_username("admin")),
        ("m/get_user_by_id", lambda: db.get_user_by_id(1)),
        ("m/get_user_by_username_missing", lambda: db.get_user_by_username("tidak_ada")),
        ("m/authenticate_wrong", lambda: db.authenticate_user("admin", "salah")),
        ("m/authenticate_inactive", lambda: db.authenticate_user("mati", "apa pun")),
        ("m/get_user_stats", lambda: db.get_user_stats(1)),

        ("m/get_all_customers", lambda: db.get_all_customers()),
        ("m/get_customer_by_id", lambda: db.get_customer_by_id(1)),
        ("m/get_customer_by_id_missing", lambda: db.get_customer_by_id(9999)),
        ("m/get_customer_id_by_name", lambda: db.get_customer_id_by_name("PT Sinar Harapan")),
        ("m/get_customer_id_by_name_case", lambda: db.get_customer_id_by_name("pt sinar harapan")),

        ("m/get_all_containers", lambda: db.get_all_containers()),
        ("m/get_all_containers_archived", lambda: db.get_all_containers(include_archived=True)),
        ("m/get_container_by_id", lambda: db.get_container_by_id(1)),
        ("m/get_container_by_id_missing", lambda: db.get_container_by_id(9999)),
        ("m/get_container_delivery_total", lambda: db.get_container_delivery_total(1)),
        ("m/get_container_total_value", lambda: db.get_container_total_value(1)),
        ("m/get_container_pricing_summary", lambda: db.get_container_pricing_summary(1)),
        ("m/get_all_containers_with_value", lambda: db.get_all_containers_with_value()),
        ("m/search_containers_by_value_range", lambda: db.search_containers_by_value_range(0, 99999999)),
        ("m/get_top_value_containers", lambda: db.get_top_value_containers(5)),

        ("m/get_all_barang", lambda: db.get_all_barang()),
        ("m/get_all_barang_archived", lambda: db.get_all_barang(include_archived=True)),
        ("m/get_all_existing_barang_keys", lambda: db.get_all_existing_barang_keys()),
        ("m/check_barang_exists", lambda: db.check_barang_exists(1, 2, "TV LED 43 inch")),
        ("m/check_barang_exists_missing", lambda: db.check_barang_exists(1, 2, "tidak ada")),
        ("m/get_barang_with_pricing_info", lambda: db.get_barang_with_pricing_info(1)),
        ("m/get_barang_in_container", lambda: db.get_barang_in_container(1)),
        ("m/get_barang_in_container_with_colli", lambda: db.get_barang_in_container_with_colli(1)),
        ("m/get_barang_in_container_with_pricing",
         lambda: db.get_barang_in_container_with_colli_and_pricing(1)),

        ("m/get_sender_by_id", lambda: db.get_sender_by_id(1)),
        ("m/get_tax_summary_empty", lambda: db.get_tax_summary(1)),
        ("m/get_dashboard_stats", lambda: db.get_dashboard_stats()),
        ("m/get_customer_container_summary", lambda: db.get_customer_container_summary_with_pricing(1)),
        ("m/get_pricing_report_by_date_range",
         lambda: db.get_pricing_report_by_date_range("2026-01-01", "2026-12-31")),
        ("m/get_customer_total_value_by_period",
         lambda: db.get_customer_total_value_by_period(1, "2026-01-01", "2026-12-31")),
    ]


def write_probes(db):
    """Mutations, in order. Each records what it returned; the final
    table dump then shows whether both backends ended up identical."""
    return [
        ("w/execute_insert_customer", lambda: db.execute_insert(
            "INSERT INTO customers (nama_customer, alamat_customer) VALUES (?, ?)",
            ("PT Baru", "Bandung"))),
        ("w/execute_insert_pengirim", lambda: db.execute_insert(
            "INSERT INTO pengirim (nama_pengirim) VALUES (?)", ("PT Kirim Baru",))),
        ("w/execute_insert_kapal", lambda: db.execute_insert(
            'INSERT INTO kapals (shipping_line, feeder, destination) VALUES (?, ?, ?)',
            ("MERATUS", "KM BARU", "Bali"))),
        ("w/execute_insert_container", lambda: db.execute_insert(
            "INSERT INTO containers (kapal_id, etd, party, container, seal) VALUES (?, ?, ?, ?, ?)",
            (1, "2026-03-01", "20FT", "CONT_NEW", "SEAL-N"))),
        ("w/execute_insert_barang", lambda: db.execute_insert(
            "INSERT INTO barang (pengirim, penerima, nama_barang, m3_barang) VALUES (?, ?, ?, ?)",
            (1, 2, "Barang Baru", 1.5))),
        # Multi-row VALUES - the shape apply_audit() was fixed for.
        ("w/execute_insert_multirow", lambda: db.execute_insert(
            "INSERT INTO pengirim (nama_pengirim) VALUES (?), (?)", ("Multi A", "Multi B"))),
        # Non-audited table (no created_by/edited_by stamping).
        ("w/execute_insert_delivery_cost", lambda: db.execute_insert(
            "INSERT INTO container_delivery_costs (container_id, delivery, description, cost, created_date) "
            "VALUES (?, ?, ?, ?, ?)", (1, "Surabaya", "Biaya Baru", 123456.78, "2026-03-01"))),
        ("w/save_tax_data", lambda: db.save_tax_data_with_return_id(1, 1, "PT Sinar Harapan", 10000000.0)),
        ("w/get_tax_summary_after", lambda: db.get_tax_summary(1)),

        ("w/update_customer", lambda: db.update_customer(1, nama_customer="PT Sinar Diubah")),
        ("w/update_pricing", lambda: db.update_barang_pricing_in_container(1, 1, 900000.0, 2700000.0)),
        ("w/assign_barang", lambda: db.assign_barang_to_container(3, 1, "m3", "dd", 2, 1000.0, 2000.0)),
        ("w/update_user_password", lambda: db.update_user_password("staff", "rahasiabaru")),
        ("w/auth_after_password_change", lambda: db.authenticate_user("staff", "rahasiabaru")),
        ("w/deactivate_user", lambda: db.deactivate_user("staff")),
        ("w/auth_after_deactivate", lambda: db.authenticate_user("staff", "rahasiabaru")),
        ("w/activate_user", lambda: db.activate_user("staff")),

        ("w/execute_many", lambda: db.execute_many(
            "INSERT INTO pengirim (nama_pengirim) VALUES (?)",
            [("Many A",), ("Many B",), ("Many C",)])),

        ("w/delete_barang", lambda: db.delete_barang(3)),
        ("w/rowcount_update", lambda: db.execute(
            "UPDATE containers SET party = ? WHERE container_id = ?", ("21FT", 2))),
        ("w/delete_no_match", lambda: db.execute(
            "DELETE FROM containers WHERE container_id = ?", (99999,))),
    ]


def run_transaction_probe(db):
    """Rollback must leave nothing behind on either backend."""
    before = db.execute_one("SELECT COUNT(*) FROM pengirim")[0]
    try:
        with db.transaction() as tx:
            tx.execute_insert("INSERT INTO pengirim (nama_pengirim) VALUES (?)", ("Rollback Me",))
            raise RuntimeError("sengaja gagal")
    except RuntimeError:
        pass
    after = db.execute_one("SELECT COUNT(*) FROM pengirim")[0]
    return {"before": before, "after": after, "rolled_back": before == after}


# --------------------------------------------------------------------------
# child process: run every probe on one backend
# --------------------------------------------------------------------------

def run_backend(out_path):
    from src.models.database import AppDatabase
    from src.models.db import audit as db_audit

    db_audit.set_current_user("penguji")

    db_path = os.environ["CKL_PARITY_DBPATH"]
    AppDatabase._instance = None
    AppDatabase._initialized = False
    db = AppDatabase(db_path)

    results = {"backend": db.backend_name, "probes": {}}

    def record(name, fn):
        try:
            results["probes"][name] = {"ok": True, "result": shape(fn())}
        except Exception as e:
            results["probes"][name] = {
                "ok": False,
                "error_type": type(e).__name__,
                "error_msg": str(e)[:200],
            }

    seed(db)

    # A. column type shape per table
    for t in TABLES:
        record(f"shape/{t}", lambda t=t: db.execute_one(f"SELECT * FROM {t} LIMIT 1"))

    # B. raw SQL semantics
    for name, sql, params in SQL_PROBES:
        record(name, lambda sql=sql, params=params: db.execute(sql, params))

    # C. read methods
    for name, fn in method_probes(db):
        record(name, fn)

    # D. transaction rollback
    record("tx/rollback", lambda: run_transaction_probe(db))

    # E. writes
    for name, fn in write_probes(db):
        record(name, fn)

    # F. full table dump after all writes
    for t in TABLES:
        record(f"dump/{t}", lambda t=t: db.execute(f"SELECT * FROM {t} ORDER BY 1"))

    # G. audit stamping landed
    record("audit/created_by", lambda: db.execute(
        "SELECT nama_customer, created_by, edited_by FROM customers ORDER BY customer_id"))
    record("audit/multirow", lambda: db.execute(
        "SELECT nama_pengirim, created_by, edited_by FROM pengirim ORDER BY pengirim_id"))

    try:
        db.close()
    except Exception:
        pass

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, default=str)


# --------------------------------------------------------------------------
# parent process
# --------------------------------------------------------------------------

def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r


def start_pg():
    sh(f'docker rm -f {PG["container"]}', check=False)
    sh(
        f'docker run -d --name {PG["container"]} '
        f'-e POSTGRES_DB={PG["db"]} -e POSTGRES_USER={PG["user"]} '
        f'-e POSTGRES_PASSWORD={PG["password"]} '
        f'-p 127.0.0.1:{PG["port"]}:5432 postgres:16-alpine'
    )
    for _ in range(60):
        r = sh(f'docker exec {PG["container"]} pg_isready -U {PG["user"]} -d {PG["db"]}', check=False)
        if r.returncode == 0:
            time.sleep(1)
            return
        time.sleep(1)
    raise RuntimeError("Postgres tidak siap")


def apply_init_sql():
    with open("scripts/init.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    r = subprocess.run(
        f'docker exec -i {PG["container"]} psql -v ON_ERROR_STOP=1 -U {PG["user"]} -d {PG["db"]}',
        shell=True, input=sql, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"init.sql gagal:\n{r.stdout}\n{r.stderr}")


def child(backend, tmpdir):
    env = dict(os.environ)
    env.pop("DB_HOST", None)
    out = os.path.join(tmpdir, f"{backend}.json")
    env["CKL_PARITY_CHILD"] = "1"
    env["CKL_PARITY_OUT"] = out
    env["CKL_PARITY_DBPATH"] = os.path.join(tmpdir, f"{backend}_app.db")

    if backend == "sqlite":
        env["DB_ENGINE"] = "sqlite"
    else:
        env.update({
            "DB_ENGINE": "postgres", "DB_HOST": "127.0.0.1", "DB_PORT": PG["port"],
            "DB_NAME": PG["db"], "DB_USER": PG["user"], "DB_PASSWORD": PG["password"],
            "DB_SSLMODE": "disable", "DB_CONNECT_TIMEOUT": "10",
        })

    r = subprocess.run([sys.executable, __file__], env=env, capture_output=True, text=True)
    if not os.path.exists(out):
        raise RuntimeError(f"child {backend} gagal:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    with open(out, encoding="utf-8") as f:
        return json.load(f)


def compare(a, b):
    """Yield (name, kind, detail) for every difference."""
    diffs = []
    for name in sorted(set(a["probes"]) | set(b["probes"])):
        pa, pb = a["probes"].get(name), b["probes"].get(name)
        if pa is None or pb is None:
            diffs.append((name, "hilang", f"sqlite={pa is not None} postgres={pb is not None}"))
            continue
        if pa["ok"] != pb["ok"]:
            fail = pa if not pa["ok"] else pb
            who = "sqlite" if not pa["ok"] else "postgres"
            diffs.append((name, "error sebelah", f"{who}: {fail['error_type']}: {fail['error_msg']}"))
            continue
        if not pa["ok"]:
            if pa["error_type"] != pb["error_type"]:
                diffs.append((name, "error beda", f"sqlite={pa['error_type']} postgres={pb['error_type']}"))
            continue

        ra, rb = pa["result"], pb["result"]
        if ra.get("value") != rb.get("value"):
            diffs.append((name, "nilai", _trim(ra.get("value")) + "  |  " + _trim(rb.get("value"))))
        ta, tb = ra.get("types") or {}, rb.get("types") or {}
        tdiff = {k: (ta.get(k), tb.get(k)) for k in set(ta) | set(tb) if ta.get(k) != tb.get(k)}
        if tdiff:
            detail = ", ".join(f"{k}: {v[0]}→{v[1]}" for k, v in sorted(tdiff.items()))
            diffs.append((name, "tipe", detail))
        if ra.get("type") and ra.get("type") != rb.get("type"):
            diffs.append((name, "tipe", f"{ra['type']}→{rb['type']}"))
    return diffs


def _trim(v, n=150):
    s = json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + "…"


def main():
    if not os.path.exists("scripts/init.sql"):
        print("scripts/init.sql tidak ditemukan - jalankan dari root repo.")
        return 2

    print("1. Menyiapkan Postgres sekali pakai di port", PG["port"])
    start_pg()
    apply_init_sql()

    tmpdir = tempfile.mkdtemp(prefix="ckl_parity_")
    try:
        print("2. Menjalankan probe di SQLite")
        a = child("sqlite", tmpdir)
        print("   backend =", a["backend"], f'({len(a["probes"])} probe)')
        if a["backend"] != "sqlite":
            print("   ! bukan sqlite, hasil tidak sah")
            return 2

        print("3. Menjalankan probe di Postgres")
        b = child("postgres", tmpdir)
        print("   backend =", b["backend"], f'({len(b["probes"])} probe)')
        if b["backend"] != "postgres":
            print("   ! jatuh ke sqlite, hasil tidak sah")
            return 2

        diffs = compare(a, b)
        total = len(set(a["probes"]) | set(b["probes"]))
        print(f"\n{'='*74}\nHASIL: {total} probe, {len(diffs)} perbedaan\n{'='*74}\n")

        by_kind = {}
        for name, kind, detail in diffs:
            by_kind.setdefault(kind, []).append((name, detail))
        for kind in ("error sebelah", "error beda", "hilang", "nilai", "tipe"):
            items = by_kind.get(kind, [])
            if not items:
                continue
            print(f"--- {kind.upper()} ({len(items)}) " + "-" * (58 - len(kind)))
            for name, detail in items:
                print(f"  {name}")
                print(f"      {detail}")
            print()

        if not diffs:
            print("Tidak ada perbedaan. Perilaku kedua backend identik pada probe ini.")
        return 1 if diffs else 0
    finally:
        sh(f'docker rm -f {PG["container"]}', check=False)


if __name__ == "__main__":
    if os.environ.get("CKL_PARITY_CHILD"):
        run_backend(os.environ["CKL_PARITY_OUT"])
    else:
        sys.exit(main())
