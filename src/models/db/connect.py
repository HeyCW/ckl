"""Backend connection helpers used by src.models.database.

Kept separate from database.py so the SQLite-only path never has to
import psycopg (it's imported lazily, only when Postgres is actually
configured).
"""

import logging

from . import config as db_config
from .postgres_compat import CompatConnection

logger = logging.getLogger(__name__)


def open_postgres_connection():
    """Open a single Postgres connection. Raises on any failure
    (unreachable host, bad credentials, missing driver, timeout)."""
    dsn = db_config.get_postgres_dsn()
    if not dsn:
        raise RuntimeError("Postgres is not configured (DB_HOST is not set)")

    import psycopg

    conn = psycopg.connect(dsn, connect_timeout=db_config.get_connect_timeout())
    conn.autocommit = False
    return CompatConnection(conn)


def probe_postgres():
    """Try opening and immediately closing a Postgres connection.
    Returns True if reachable, False otherwise (never raises)."""
    try:
        conn = open_postgres_connection()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Postgres unreachable: {e}")
        return False
