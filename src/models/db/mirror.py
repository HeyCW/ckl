"""Bootstraps and maintains the local SQLite mirror used for offline
sync. Operates on a raw sqlite3 connection to db_path directly, never
through AppDatabase.get_connection() - the mirror must exist and be
kept current regardless of which backend (Postgres or SQLite) is
currently active, so it can't be gated behind self.backend_name.
"""

import sqlite3

from .schema import ddl_for, TABLE_DDL
from .translate import PRIMARY_KEYS
from .fk_map import OFFLINE_ID_BASE

# Tables mirrored for offline use. `users` is deliberately excluded -
# accounts aren't created/edited offline.
MIRRORED_TABLES = [t for t in TABLE_DDL if t != "users"]


def open_mirror_connection(db_path):
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_mirror_schema(conn):
    """Create every business table (if missing), the archived columns,
    and the sync bookkeeping tables. Safe to call on every startup."""
    for table in TABLE_DDL:
        conn.execute(ddl_for(table, "sqlite"))

    _add_column_if_missing(conn, "containers", "archived", "INTEGER DEFAULT 0")
    _add_column_if_missing(conn, "barang", "archived", "INTEGER DEFAULT 0")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS _sync_changes (
            change_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            row_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _sync_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    install_triggers(conn)
    # A prior run that crashed mid-pull could have left triggers
    # suspended; never let that persist across a restart, or local
    # writes would silently stop being tracked for sync.
    resume_triggers(conn)


def _add_column_if_missing(conn, table, column, col_type):
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        conn.commit()


def install_triggers(conn):
    """(Re)install change-capture triggers on every mirrored table.

    Fires on any INSERT/UPDATE/DELETE regardless of which application
    code path caused it - this is what lets sync work without parsing
    the app's often-ad-hoc UPDATE/DELETE SQL: SQLite tracks the change
    at the row level for us.
    """
    for table in MIRRORED_TABLES:
        pk = PRIMARY_KEYS[table]
        for suffix, event, ref in (("ai", "INSERT", "NEW"), ("au", "UPDATE", "NEW"), ("ad", "DELETE", "OLD")):
            op = "DELETE" if event == "DELETE" else "UPSERT"
            conn.execute(f"DROP TRIGGER IF EXISTS trg_{table}_{suffix}")
            conn.execute(f"""
                CREATE TRIGGER trg_{table}_{suffix} AFTER {event} ON {table}
                WHEN NOT EXISTS (SELECT 1 FROM _sync_meta WHERE key = 'suspend_triggers')
                BEGIN
                    INSERT INTO _sync_changes (table_name, row_id, operation)
                    VALUES ('{table}', {ref}.{pk}, '{op}');
                END
            """)
    conn.commit()


def suspend_triggers(conn):
    """Silence change-capture triggers - used while the mirror is being
    bulk-refreshed from Postgres, so the refresh itself doesn't get
    logged as a pending local change to push back up."""
    conn.execute("INSERT OR REPLACE INTO _sync_meta (key, value) VALUES ('suspend_triggers', '1')")
    conn.commit()


def resume_triggers(conn):
    conn.execute("DELETE FROM _sync_meta WHERE key = 'suspend_triggers'")
    conn.commit()


def pending_change_count(conn):
    row = conn.execute("SELECT COUNT(*) FROM _sync_changes").fetchone()
    return row[0] if row else 0


def seed_offline_sequences(conn):
    """Push every mirrored table's AUTOINCREMENT counter up to
    OFFLINE_ID_BASE, so a row created while offline can never collide
    with a real Postgres-assigned ID once it's pushed during sync.
    Idempotent - never moves a counter backward.
    """
    for table in MIRRORED_TABLES:
        row = conn.execute("SELECT seq FROM sqlite_sequence WHERE name = ?", (table,)).fetchone()
        current = row[0] if row else 0
        if current < OFFLINE_ID_BASE:
            if row:
                conn.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (OFFLINE_ID_BASE, table))
            else:
                conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)", (table, OFFLINE_ID_BASE))
    conn.commit()
