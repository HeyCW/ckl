"""Regenerate scripts/init.sql from the Postgres DDL in src/models/db/schema.py.

    python scripts/generate_init_sql.py
"""
import importlib.util
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Load schema.py by path so importing it doesn't pull in the rest of the app.
spec = importlib.util.spec_from_file_location("schema", ROOT / "src" / "models" / "db" / "schema.py")
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)

HEADER = """\
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

"""

# Same order as Database.init_db().
ORDER = [
    "users",
    "customers",
    "kapals",
    "containers",
    "barang",
    "barang_tax",
    "detail_container",
    "container_delivery_costs",
    "pengirim",
]

missing = set(schema.TABLE_DDL) - set(ORDER)
if missing:
    raise SystemExit(f"schema.py has tables not listed in ORDER: {sorted(missing)}")

parts = [HEADER]
for table in ORDER:
    ddl = textwrap.dedent(schema.ddl_for(table, "postgres")).strip()
    parts.append(f"-- {table}\n{ddl};\n")

out = ROOT / "scripts" / "init.sql"
out.write_text("\n".join(parts), encoding="utf-8", newline="\n")
print(f"Wrote {out}")
