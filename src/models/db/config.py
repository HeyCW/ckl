"""Reads Postgres connection settings from the environment (a local .env
file when python-dotenv is installed, falling back to real env vars).

Postgres is considered "configured" as soon as DB_HOST is set. Set
DB_ENGINE=sqlite to force SQLite even if DB_HOST is present.
"""

import os

_dotenv_loaded = False


def _ensure_dotenv_loaded():
    global _dotenv_loaded
    if _dotenv_loaded:
        return
    _dotenv_loaded = True
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def postgres_requested():
    _ensure_dotenv_loaded()
    if os.environ.get("DB_ENGINE", "").strip().lower() == "sqlite":
        return False
    return bool(os.environ.get("DB_HOST"))


def get_postgres_dsn():
    _ensure_dotenv_loaded()
    host = os.environ.get("DB_HOST")
    if not host:
        return None

    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    sslmode = os.environ.get("DB_SSLMODE", "require")

    return (
        f"host={host} port={port} dbname={name} user={user} "
        f"password={password} sslmode={sslmode}"
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
