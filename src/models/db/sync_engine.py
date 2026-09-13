"""Push/pull sync between the SQLite mirror and Postgres.

Push replays rows changed while offline up to Postgres, remapping any
offline-allocated temp IDs to the real IDs Postgres assigns. Pull then
refreshes the mirror from Postgres so it's current for the next offline
stretch. Push always runs before pull, so a refresh can never discard a
local change that hasn't been sent up yet.

Talks to Postgres directly via the connection pool (native %s
placeholders), not through AppDatabase.execute() - the queries here are
built dynamically per-row and already control their own placeholder
style, so routing them through the app's ?-to-%s translator would
double-translate them.
"""

import datetime
import logging
from decimal import Decimal

from . import connect as db_connect
from . import mirror
from .fk_map import FOREIGN_KEYS, REFERENCING, OFFLINE_ID_BASE
from .schema import TABLE_DDL
from .translate import PRIMARY_KEYS

# Pull includes `users` (read-only, so login works while offline) even
# though it's excluded from mirror.MIRRORED_TABLES, which governs what
# gets *push* tracking (accounts aren't created/edited offline).
_PULL_TABLES = list(TABLE_DDL.keys())

logger = logging.getLogger(__name__)


class SyncResult:
    def __init__(self, ok, pushed=0, pulled=0, reason=None):
        self.ok = ok
        self.pushed = pushed
        self.pulled = pulled
        self.reason = reason

    def __repr__(self):
        if self.ok:
            return f"SyncResult(ok=True, pushed={self.pushed}, pulled={self.pulled})"
        return f"SyncResult(ok=False, reason={self.reason!r}, pushed={self.pushed})"


def _pg_safe(v):
    """SQLite can return bytes/str for values Postgres wants typed;
    values already come from the app's own column set so no coercion
    is needed there - this only guards the id_map lookup path."""
    return v


def _mirror_safe(v):
    """Coerce a value fetched from Postgres into something sqlite3 can
    bind. Decimal (NUMERIC columns) and datetime/date (TIMESTAMP/DATE
    columns) aren't accepted by sqlite3's parameter binding."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime.datetime, datetime.date)):
        return str(v)
    return v


def _remap_mirror_id(mirror_conn, table, old_id, new_id):
    """After an offline-created row is pushed and gets a real Postgres
    ID, rewrite that row's own PK and every mirror row referencing it,
    so the mirror stays internally consistent and later local edits
    target the ID Postgres actually knows about."""
    if old_id == new_id:
        return
    pk = PRIMARY_KEYS[table]
    mirror.suspend_triggers(mirror_conn)
    try:
        mirror_conn.execute(f"UPDATE {table} SET {pk} = ? WHERE {pk} = ?", (new_id, old_id))
        for child_table, fk_col in REFERENCING.get(table, []):
            mirror_conn.execute(
                f"UPDATE {child_table} SET {fk_col} = ? WHERE {fk_col} = ?", (new_id, old_id)
            )
        mirror_conn.commit()
    finally:
        mirror.resume_triggers(mirror_conn)


def push_pending(app_db):
    """Replay every pending offline change to Postgres. Raises if
    Postgres is unreachable (that's the caller's cue to stay offline)."""
    pool = db_connect.get_pool()  # raises if unreachable
    pg_conn = pool.getconn()
    mirror_conn = mirror.open_mirror_connection(app_db.db_path)
    try:
        changes = mirror_conn.execute(
            "SELECT change_id, table_name, row_id, operation FROM _sync_changes ORDER BY change_id ASC"
        ).fetchall()
        if not changes:
            # Nothing to push, but checking out the connection (and its
            # liveness ping) may have opened a transaction under
            # autocommit=False - close it out before returning the
            # connection to the pool.
            pg_conn.rollback()
            return SyncResult(ok=True, pushed=0)

        # Only the final operation per row matters; keep first-seen
        # order across distinct rows so parents are pushed before
        # children (the app always creates a barang before assigning
        # it to a container, etc.).
        order = []
        seen = set()
        final_op = {}
        for row in changes:
            key = (row["table_name"], row["row_id"])
            if key not in seen:
                seen.add(key)
                order.append(key)
            final_op[key] = row["operation"]

        id_map = {}  # (table, offline_local_id) -> real Postgres id
        pg_cursor = pg_conn.cursor()
        pushed = 0

        for table, local_id in order:
            op = final_op[(table, local_id)]
            pk = PRIMARY_KEYS[table]

            if op == "DELETE":
                if local_id >= OFFLINE_ID_BASE and (table, local_id) not in id_map:
                    continue  # created and deleted entirely offline - never existed upstream
                real_id = id_map.get((table, local_id), local_id)
                pg_cursor.execute(f'DELETE FROM {table} WHERE "{pk}" = %s', (real_id,))
                pushed += 1
                continue

            row = mirror_conn.execute(f"SELECT * FROM {table} WHERE {pk} = ?", (local_id,)).fetchone()
            if row is None:
                continue  # locally deleted again since; nothing to push
            values = dict(row)

            for fk_col, parent_table in FOREIGN_KEYS.get(table, {}).items():
                v = values.get(fk_col)
                if v is not None and (parent_table, v) in id_map:
                    values[fk_col] = id_map[(parent_table, v)]

            is_new = local_id >= OFFLINE_ID_BASE
            if is_new:
                cols = [c for c in values if c != pk]
                collist = ",".join(f'"{c}"' for c in cols)
                ph = ",".join(["%s"] * len(cols))
                pg_cursor.execute(
                    f'INSERT INTO {table} ({collist}) VALUES ({ph}) RETURNING "{pk}"',
                    [values[c] for c in cols],
                )
                real_id = pg_cursor.fetchone()[0]
                id_map[(table, local_id)] = real_id
                _remap_mirror_id(mirror_conn, table, local_id, real_id)
                pushed += 1
            else:
                cols = [c for c in values if c != pk]
                setlist = ",".join(f'"{c}"=%s' for c in cols)
                pg_cursor.execute(
                    f'UPDATE {table} SET {setlist} WHERE "{pk}"=%s',
                    [values[c] for c in cols] + [local_id],
                )
                if pg_cursor.rowcount == 0:
                    # Row was deleted server-side while we were offline;
                    # last-write-wins here means our edit recreates it.
                    collist = ",".join(f'"{c}"' for c in values)
                    ph = ",".join(["%s"] * len(values))
                    pg_cursor.execute(
                        f"INSERT INTO {table} ({collist}) VALUES ({ph})", list(values.values())
                    )
                pushed += 1

        pg_conn.commit()
        mirror_conn.execute("DELETE FROM _sync_changes")
        mirror_conn.commit()
        return SyncResult(ok=True, pushed=pushed)
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        mirror_conn.close()
        pool.putconn(pg_conn)


# Non-master tables are scoped to non-archived containers; master data
# (customers, kapals, pengirim) always syncs in full.
_ARCHIVE_FILTERED = {
    "containers": "WHERE archived = 0",
    "barang": "WHERE archived = 0",
    "detail_container": "WHERE container_id IN (SELECT container_id FROM containers WHERE archived = 0)",
    "barang_tax": "WHERE container_id IN (SELECT container_id FROM containers WHERE archived = 0)",
    "container_delivery_costs": (
        "WHERE container_id IN (SELECT container_id FROM containers WHERE archived = 0)"
    ),
}


def pull_mirror(app_db):
    """Refresh the mirror from Postgres (non-archived data only).
    Wrapped in one mirror transaction so a download that fails partway
    leaves the existing mirror untouched rather than half-empty.
    """
    pool = db_connect.get_pool()  # raises if unreachable
    pg_conn = pool.getconn()
    mirror_conn = mirror.open_mirror_connection(app_db.db_path)
    try:
        pg_cursor = pg_conn.cursor()
        fetched = {}
        for table in _PULL_TABLES:
            where = _ARCHIVE_FILTERED.get(table, "")
            pg_cursor.execute(f"SELECT * FROM {table} {where}")
            rows = pg_cursor.fetchall()
            cols = [d[0] for d in pg_cursor.description]
            fetched[table] = (cols, [tuple(_mirror_safe(v) for v in r) for r in rows])

        total = sum(len(rows) for _, rows in fetched.values())

        mirror.suspend_triggers(mirror_conn)
        try:
            mirror_conn.execute("BEGIN")
            for table in _PULL_TABLES:
                cols, rows = fetched[table]
                mirror_conn.execute(f"DELETE FROM {table}")
                if rows:
                    collist = ",".join(f'"{c}"' for c in cols)
                    ph = ",".join(["?"] * len(cols))
                    mirror_conn.executemany(f"INSERT INTO {table} ({collist}) VALUES ({ph})", rows)
            mirror_conn.commit()
        except Exception:
            mirror_conn.rollback()
            raise
        finally:
            mirror.resume_triggers(mirror_conn)

        # Read-only against Postgres; roll back rather than commit so
        # the connection goes back to the pool with a clean transaction
        # state instead of the pool having to do it defensively.
        pg_conn.rollback()
        return SyncResult(ok=True, pulled=total)
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        mirror_conn.close()
        pool.putconn(pg_conn)


def sync_now(app_db):
    """Push pending offline changes, then refresh the mirror. Returns a
    SyncResult; failure to reach Postgres is a normal outcome (stay
    offline), not an exception the caller needs to handle specially.
    """
    from . import config as db_config

    if not db_config.postgres_requested():
        return SyncResult(ok=False, reason="Postgres is not configured")

    try:
        push_result = push_pending(app_db)
    except Exception as e:
        logger.info(f"Sync skipped, Postgres unreachable: {e}")
        return SyncResult(ok=False, reason=str(e))

    try:
        pull_result = pull_mirror(app_db)
    except Exception as e:
        logger.warning(f"Pushed {push_result.pushed} change(s) but mirror refresh failed: {e}")
        return SyncResult(ok=False, reason=str(e), pushed=push_result.pushed)

    app_db.backend_name = "postgres"
    logger.info(f"Sync complete: pushed {push_result.pushed}, pulled {pull_result.pulled}")
    return SyncResult(ok=True, pushed=push_result.pushed, pulled=pull_result.pulled)
