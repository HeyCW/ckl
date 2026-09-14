"""DDL for every table, one variant per backend.

Kept side by side (rather than auto-translated) because the SQLite and
Postgres flavors differ in more than syntax:

- Two foreign keys in the original SQLite schema point at columns that
  don't exist (``containers.id`` and ``barang_tax.id`` — the real
  primary keys are ``container_id`` and ``tax_id``). SQLite silently
  ignores this because foreign key enforcement is off by default;
  Postgres enforces FKs and would refuse to create the table, so the
  Postgres DDL below points at the real primary key columns.
- ``barang.pengirim``/``barang.penerima`` are declared TEXT in SQLite
  but every call site (see get_customer_id_by_name, barang_window.py)
  actually stores an integer customer_id in them, and joins compare
  them against ``customers.customer_id`` (INTEGER). SQLite's dynamic
  typing coerces this silently; Postgres does not, and raises
  "operator does not exist: text = integer" on the join. The Postgres
  DDL declares them INTEGER to match how the data is actually used.
- ``users.is_active`` is declared BOOLEAN in SQLite, but every call
  site writes/compares it as a plain integer (0/1), which Postgres's
  distinct boolean type rejects. The Postgres DDL uses INTEGER instead.
"""

TABLE_DDL = {
    "users": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0
            )
        """,
    },
    "customers": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_customer TEXT NOT NULL,
                alamat_customer TEXT NOT NULL,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                nama_customer TEXT NOT NULL,
                alamat_customer TEXT NOT NULL,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
    "kapals": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS kapals (
                kapal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipping_line TEXT,
                feeder TEXT,
                etd_sub DATE,
                cls DATE,
                open DATE,
                full DATE,
                destination TEXT,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS kapals (
                kapal_id SERIAL PRIMARY KEY,
                shipping_line TEXT,
                feeder TEXT,
                etd_sub DATE,
                cls DATE,
                "open" DATE,
                "full" DATE,
                destination TEXT,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
    "containers": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS containers (
                container_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kapal_id INTEGER,
                etd DATE,
                party TEXT,
                container TEXT NOT NULL,
                seal TEXT,
                ref_joa TEXT,
                archived INTEGER DEFAULT 0,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kapal_id) REFERENCES kapals(kapal_id) ON DELETE SET NULL
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS containers (
                container_id SERIAL PRIMARY KEY,
                kapal_id INTEGER,
                etd DATE,
                party TEXT,
                container TEXT NOT NULL,
                seal TEXT,
                ref_joa TEXT,
                archived INTEGER DEFAULT 0,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kapal_id) REFERENCES kapals(kapal_id) ON DELETE SET NULL
            )
        """,
    },
    "barang": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS barang (
                barang_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pengirim TEXT NOT NULL,
                penerima TEXT NOT NULL,
                nama_barang TEXT NOT NULL,
                panjang_barang  REAL,
                lebar_barang REAL,
                tinggi_barang REAL,
                m3_barang REAL,
                ton_barang REAL,
                container_barang REAL,
                m3_pp REAL,
                m3_pd REAL,
                m3_dd REAL,
                ton_pp REAL,
                ton_pd REAL,
                ton_dd REAL,
                col_pp INTEGER,
                col_pd INTEGER,
                col_dd INTEGER,
                container_pp REAL,
                container_pd REAL,
                container_dd REAL,
                container_20_pp REAL,
                container_20_pd REAL,
                container_20_dd REAL,
                container_21_pp REAL,
                container_21_pd REAL,
                container_21_dd REAL,
                container_40hc_pp REAL,
                container_40hc_pd REAL,
                container_40hc_dd REAL,
                pajak INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS barang (
                barang_id SERIAL PRIMARY KEY,
                pengirim INTEGER NOT NULL,
                penerima INTEGER NOT NULL,
                nama_barang TEXT NOT NULL,
                panjang_barang DOUBLE PRECISION,
                lebar_barang DOUBLE PRECISION,
                tinggi_barang DOUBLE PRECISION,
                m3_barang DOUBLE PRECISION,
                ton_barang DOUBLE PRECISION,
                container_barang DOUBLE PRECISION,
                m3_pp DOUBLE PRECISION,
                m3_pd DOUBLE PRECISION,
                m3_dd DOUBLE PRECISION,
                ton_pp DOUBLE PRECISION,
                ton_pd DOUBLE PRECISION,
                ton_dd DOUBLE PRECISION,
                col_pp INTEGER,
                col_pd INTEGER,
                col_dd INTEGER,
                container_pp DOUBLE PRECISION,
                container_pd DOUBLE PRECISION,
                container_dd DOUBLE PRECISION,
                container_20_pp DOUBLE PRECISION,
                container_20_pd DOUBLE PRECISION,
                container_20_dd DOUBLE PRECISION,
                container_21_pp DOUBLE PRECISION,
                container_21_pd DOUBLE PRECISION,
                container_21_dd DOUBLE PRECISION,
                container_40hc_pp DOUBLE PRECISION,
                container_40hc_pd DOUBLE PRECISION,
                container_40hc_dd DOUBLE PRECISION,
                pajak INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
    "barang_tax": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS barang_tax (
                tax_id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id INTEGER NOT NULL,
                barang_id INTEGER NOT NULL,
                penerima TEXT NOT NULL,
                total_nilai_barang REAL NOT NULL,
                ppn_rate REAL DEFAULT 0.011,
                pph23_rate REAL DEFAULT 0.02,
                ppn_amount REAL NOT NULL,
                pph23_amount REAL NOT NULL,
                total_tax REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (container_id) REFERENCES containers (container_id),
                FOREIGN KEY (barang_id) REFERENCES barang (barang_id)
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS barang_tax (
                tax_id SERIAL PRIMARY KEY,
                container_id INTEGER NOT NULL,
                barang_id INTEGER NOT NULL,
                penerima TEXT NOT NULL,
                total_nilai_barang DOUBLE PRECISION NOT NULL,
                ppn_rate DOUBLE PRECISION DEFAULT 0.011,
                pph23_rate DOUBLE PRECISION DEFAULT 0.02,
                ppn_amount DOUBLE PRECISION NOT NULL,
                pph23_amount DOUBLE PRECISION NOT NULL,
                total_tax DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (container_id) REFERENCES containers (container_id),
                FOREIGN KEY (barang_id) REFERENCES barang (barang_id)
            )
        """,
    },
    "detail_container": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS detail_container (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal DATE NOT NULL,
                barang_id INTEGER NOT NULL,
                container_id INTEGER NOT NULL,
                tax_id INTEGER,
                satuan TEXT NOT NULL,
                door_type TEXT NOT NULL,
                colli_amount INTEGER NOT NULL DEFAULT 1,
                harga_per_unit DECIMAL(15,2) DEFAULT 0,
                total_harga DECIMAL(15,2) DEFAULT 0,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (barang_id) REFERENCES barang (barang_id),
                FOREIGN KEY (container_id) REFERENCES containers (container_id),
                FOREIGN KEY (tax_id) REFERENCES barang_tax (id)
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS detail_container (
                id SERIAL PRIMARY KEY,
                tanggal DATE NOT NULL,
                barang_id INTEGER NOT NULL,
                container_id INTEGER NOT NULL,
                tax_id INTEGER,
                satuan TEXT NOT NULL,
                door_type TEXT NOT NULL,
                colli_amount INTEGER NOT NULL DEFAULT 1,
                harga_per_unit NUMERIC(15,2) DEFAULT 0,
                total_harga NUMERIC(15,2) DEFAULT 0,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (barang_id) REFERENCES barang (barang_id),
                FOREIGN KEY (container_id) REFERENCES containers (container_id),
                FOREIGN KEY (tax_id) REFERENCES barang_tax (tax_id)
            )
        """,
    },
    "container_delivery_costs": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS container_delivery_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id INTEGER NOT NULL,
                delivery TEXT,
                description TEXT NOT NULL,
                cost_description TEXT,
                cost REAL NOT NULL DEFAULT 0,
                created_date TEXT NOT NULL,
                FOREIGN KEY (container_id) REFERENCES containers (id)
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS container_delivery_costs (
                id SERIAL PRIMARY KEY,
                container_id INTEGER NOT NULL,
                delivery TEXT,
                description TEXT NOT NULL,
                cost_description TEXT,
                cost DOUBLE PRECISION NOT NULL DEFAULT 0,
                created_date TEXT NOT NULL,
                FOREIGN KEY (container_id) REFERENCES containers (container_id)
            )
        """,
    },
    "pengirim": {
        "sqlite": """
            CREATE TABLE IF NOT EXISTS pengirim (
                pengirim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pengirim TEXT NOT NULL,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "postgres": """
            CREATE TABLE IF NOT EXISTS pengirim (
                pengirim_id SERIAL PRIMARY KEY,
                nama_pengirim TEXT NOT NULL,
                created_by TEXT,
                edited_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
    },
}


def ddl_for(table, dialect):
    return TABLE_DDL[table][dialect]
