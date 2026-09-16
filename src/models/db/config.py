"""Reads Postgres connection settings from the environment (a local .env
file when python-dotenv is installed, falling back to real env vars).

Postgres is considered "configured" as soon as DB_HOST is set. Set
DB_ENGINE=sqlite to force SQLite even if DB_HOST is present.
"""

import os
import sys

_dotenv_loaded = False


def app_root():
    """Directory the app's .env sits in.

    Frozen (PyInstaller) builds: next to the .exe. Running from source:
    the repo root, four levels up from src/models/db/config.py.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    path = os.path.abspath(__file__)
    for _ in range(4):
        path = os.path.dirname(path)
    return path


def _ensure_dotenv_loaded():
    """Load .env, anchored to the app directory rather than the cwd.

    load_dotenv() with no path searches upward from the current working
    directory once the app is frozen, so an .exe started from a desktop
    shortcut (cwd = wherever the shortcut points) never finds the .env
    sitting beside it. DB_HOST then comes back empty, the app decides
    Postgres isn't configured at all, and it runs as plain SQLite with
    no mirror and no sync - so the work done in that session has no way
    back to the server. Resolving the path ourselves makes the lookup
    independent of how the app was launched.
    """
    global _dotenv_loaded
    if _dotenv_loaded:
        return
    _dotenv_loaded = True
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = os.path.join(app_root(), ".env")
    if os.path.isfile(env_path):
        load_dotenv(env_path)
    else:
        # No .env beside the app - fall back to the library's own search
        # so existing source checkouts and real env vars keep working.
        load_dotenv()


def postgres_requested():
    _ensure_dotenv_loaded()
    if os.environ.get("DB_ENGINE", "").strip().lower() == "sqlite":
        return False
    return bool(os.environ.get("DB_HOST"))


def get_postgres_dsn():
    """Build a libpq connection string from the environment.

    Uses psycopg's conninfo builder rather than string concatenation so
    values containing spaces or "keyword=value"-shaped text (a password
    like "p@ss host=other" is the dangerous case) can't be
    misinterpreted as extra/overriding connection parameters.
    """
    _ensure_dotenv_loaded()
    host = os.environ.get("DB_HOST")
    if not host:
        return None

    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    sslmode = os.environ.get("DB_SSLMODE", "require")

    from psycopg.conninfo import make_conninfo

    return make_conninfo(
        host=host,
        port=port,
        dbname=name,
        user=user,
        password=password,
        sslmode=sslmode,
    )


def get_connect_timeout():
    _ensure_dotenv_loaded()
    try:
        return float(os.environ.get("DB_CONNECT_TIMEOUT", "5"))
    except ValueError:
        return 5.0


def _int_env(name, default):
    _ensure_dotenv_loaded()
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def get_pool_min_size():
    return _int_env("DB_POOL_MIN", 1)


def get_pool_max_size():
    # The app is single-threaded, so 1 connection is normally enough;
    # the headroom only exists so a nested checkout can never deadlock.
    return _int_env("DB_POOL_MAX", 4)
