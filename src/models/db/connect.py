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

# Two pools: _write_pool (autocommit=False, one BEGIN/COMMIT per
# statement - needed for the handful of call sites that run several
# statements as one atomic unit) and _read_pool (autocommit=True, no
# transaction wrapper at all). A read issued as BEGIN/SELECT/COMMIT is
# 3 network round trips where 1 would do; seen directly in the
# server's own query log during validation. Kept as two separate pools
# rather than toggling autocommit on a shared one so a write path can
# never accidentally get a connection with the wrong transaction
# semantics.
_write_pool = None
_read_pool = None
_adapters_registered = False


def _register_type_adapters():
    """Return NUMERIC columns as float, the way SQLite always did.

    psycopg decodes NUMERIC to decimal.Decimal, but the app's money
    columns (detail_container.harga_per_unit/total_harga) get mixed with
    float literals throughout the views - `total * 0.011` for tax,
    `total += harga` in summaries. Decimal and float don't combine in
    Python (TypeError), so the default would break those paths on
    Postgres while they worked fine on SQLite.
    """
    global _adapters_registered
    if _adapters_registered:
        return
    import psycopg
    from psycopg.types.numeric import FloatLoader

    psycopg.adapters.register_loader("numeric", FloatLoader)
    _adapters_registered = True


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


def _create_pool(autocommit):
    dsn = db_config.get_postgres_dsn()
    if not dsn:
        raise RuntimeError("Postgres is not configured (DB_HOST is not set)")

    from psycopg_pool import ConnectionPool

    _register_type_adapters()
    timeout = db_config.get_connect_timeout()
    pool = ConnectionPool(
        dsn,
        min_size=db_config.get_pool_min_size(),
        max_size=db_config.get_pool_max_size(),
        timeout=timeout,
        kwargs={
            "connect_timeout": timeout,
            "autocommit": autocommit,
            # The server is reached over a VPN tunnel (e.g. WireGuard),
            # where a dead path (NAT/peer drop, VPS reboot) often closes
            # silently - no RST ever reaches this side. Without these,
            # a query on a half-open socket blocks on TCP retransmit for
            # minutes (Linux default ~15) instead of failing fast, which
            # freezes the single-threaded UI and skips the SQLite
            # failover in _attempt(). tcp_user_timeout bounds how long a
            # send can go unacknowledged before the kernel gives up.
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 3,
            "tcp_user_timeout": 15000,  # ms
        },
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
    """The write pool (autocommit=False) - every existing caller of
    this name gets transactional semantics unchanged."""
    global _write_pool
    if _write_pool is None:
        _write_pool = _create_pool(autocommit=False)
    return _write_pool


def get_read_pool():
    """The read pool (autocommit=True). Created lazily on first read so
    a session that never runs a Postgres query (or fails over to
    SQLite before one does) never pays for it."""
    global _read_pool
    if _read_pool is None:
        _read_pool = _create_pool(autocommit=True)
    return _read_pool


def close_pool():
    """Drop both pools (on failover to SQLite, or at shutdown) so they
    stop holding/reconnecting connections. A later call re-creates
    whichever pool is next needed."""
    global _write_pool, _read_pool
    for name, pool in (("write", _write_pool), ("read", _read_pool)):
        if pool is not None:
            try:
                pool.close()
            except Exception as e:
                logger.warning(f"Error closing Postgres {name} pool: {e}")
    _write_pool = None
    _read_pool = None


def open_postgres_connection(readonly=False):
    """Check a connection out of the write pool (default) or the read
    pool (readonly=True). Raises on any failure (unreachable host, bad
    credentials, missing driver, timeout).

    The returned CompatConnection returns it to the same pool it came
    from on close()/context-manager exit rather than closing the
    socket.
    """
    pool = get_read_pool() if readonly else get_pool()
    conn = pool.getconn()
    return CompatConnection(conn, pool=pool)


def probe_postgres():
    """Check out and return a connection to confirm Postgres is
    reachable. Returns True/False, never raises.

    Only probes the write pool - if it's reachable the read pool will
    be too (same server, same DSN minus autocommit), and creating it
    here would cost a connection before anything has asked to read.
    """
    try:
        conn = open_postgres_connection()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Postgres unreachable: {e}")
        close_pool()
        return False
