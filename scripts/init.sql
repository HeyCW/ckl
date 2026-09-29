-- CKL database schema for PostgreSQL.
--
-- GENERATED from src/models/db/schema.py by scripts/generate_init_sql.py -
-- edit schema.py and regenerate rather than editing this file by hand.
--
-- Safe to re-run: every statement is CREATE TABLE IF NOT EXISTS.
--
-- Run it as the role the app connects as (DB_USER), so that role owns the
-- tables; tables owned by another role (e.g. "postgres") are not
-- accessible to the app without extra GRANTs:
--   psql -h <host> -U ckl_app -d ckl -1 -f scripts/init.sql
-- (-1 runs it as a single transaction; omit it in pgAdmin.)
--
-- Table order matters: a table must exist before a FOREIGN KEY references it.
--
-- The initial "admin"/"owner" accounts are NOT created here. The app
-- creates them on first start with the fixed passwords defined in
-- DEFAULT_ACCOUNTS (see Database.insert_default_data).


-- users
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
);

-- customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    nama_customer TEXT NOT NULL,
    alamat_customer TEXT NOT NULL,
    created_by TEXT,
    edited_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- kapals
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
);

-- containers
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
);

-- barang
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
);

-- barang_tax
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
);

-- detail_container
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
);

-- container_delivery_costs
CREATE TABLE IF NOT EXISTS container_delivery_costs (
    id SERIAL PRIMARY KEY,
    container_id INTEGER NOT NULL,
    delivery TEXT,
    description TEXT NOT NULL,
    cost_description TEXT,
    cost DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_date TEXT NOT NULL,
    created_by TEXT,
    edited_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (container_id) REFERENCES containers (container_id)
);

-- pengirim
CREATE TABLE IF NOT EXISTS pengirim (
    pengirim_id SERIAL PRIMARY KEY,
    nama_pengirim TEXT NOT NULL,
    created_by TEXT,
    edited_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
