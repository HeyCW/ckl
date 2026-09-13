"""Backend connection helpers used by src.models.database.

Kept separate from database.py so the SQLite-only path never has to
import psycopg (it's imported lazily, only when Postgres is actually
configured).

Connections come from a psycopg_pool.ConnectionPool rather than being
opened per query. The app is single-threaded so this isn't about
concurrency - it's that a full connect (TCP + TLS + auth) costs several
round trips, and cloud Postgres closes idle connections out from under
a long-running desktop app. The pool keeps a connection warm and
replaces it when the server has dropped it.
"""

import logging
import time

from . import config as db_config
from .postgres_compat import CompatConnection

logger = logging.getLogger(__name__)

_pool = None

# A connection used this recently is assumed still alive, so we skip the
# liveness ping. Keeps a screen that fires ten queries in a row from
# paying ten extra round trips, while still catching connections the
# server dropped during an idle stretch.
_LIVENESS_TRUST_WINDOW = 60.0
_LAST_CHECKED_ATTR = "_ckl_last_checked"


def _check_connection(conn):
    """Pool check hook: ping only if the connection has been idle a
    while. Raising marks the connection bad, and the pool replaces it."""
    from psycopg_pool import ConnectionPool

    last_checked = getattr(conn, _LAST_CHECKED_ATTR, None)
    now = time.monotonic()
    if last_checked is not None and (now - last_checked) < _LIVENESS_TRUST_WINDOW:
        return
    ConnectionPool.check_connection(conn)
    setattr(conn, _LAST_CHECKED_ATTR, now)


def _create_pool():
    dsn = db_config.get_postgres_dsn()
    if not dsn:
        raise RuntimeError("Postgres is not configured (DB_HOST is not set)")

    from psycopg_pool import ConnectionPool

    timeout = db_config.get_connect_timeout()
    pool = ConnectionPool(
        dsn,
        min_size=db_config.get_pool_min_size(),
        max_size=db_config.get_pool_max_size(),
        timeout=timeout,
        kwargs={"connect_timeout": timeout, "autocommit": False},
        # Validates the connection before handing it out, so one the
        # server closed during an idle stretch gets replaced instead of
        # failing the caller's query.
        check=_check_connection,
        open=False,
    )
    pool.open()
    try:
        # Surfaces an unreachable/misconfigured server now rather than
        # on the first query.
        pool.wait(timeout=timeout)
    except Exception:
        pool.close()
        raise
    return pool


def get_pool():
    global _pool
    if _pool is None:
        _pool = _create_pool()
    return _pool


def close_pool():
    """Drop the pool (on failover to SQLite, or at shutdown) so it stops
    holding/reconnecting connections. A later call re-creates it."""
    global _pool
    if _pool is not None:
        try:
            _pool.close()
        except Exception as e:
            logger.warning(f"Error closing Postgres pool: {e}")
        _pool = None


def open_postgres_connection():
    """Check a connection out of the pool. Raises on any failure
    (unreachable host, bad credentials, missing driver, timeout).

    The returned CompatConnection returns it to the pool on close()/
    context-manager exit rather than closing the socket.
    """
    pool = get_pool()
    conn = pool.getconn()
    return CompatConnection(conn, pool=pool)


def probe_postgres():
    """Check out and return a connection to confirm Postgres is
    reachable. Returns True/False, never raises."""
    try:
        conn = open_postgres_connection()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Postgres unreachable: {e}")
        close_pool()
        return False
