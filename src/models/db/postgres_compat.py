"""Thin compatibility layer so the app's existing sqlite3-shaped call
sites (cursor.execute("... ? ...", params), cursor.lastrowid,
row['col'] / row[0], dict(row)) work unchanged against Postgres.

Only used when the active backend is Postgres — the SQLite path keeps
using the native sqlite3 connection/cursor untouched.
"""

from .row import Row
from .translate import (
    translate_query,
    normalize_params,
    insert_table_name,
    has_returning,
    PRIMARY_KEYS,
)


class CompatCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, query, params=()):
        translated = translate_query(query)
        bind = normalize_params(params)

        stripped = query.strip()
        appended_returning = False
        if stripped[:6].upper() == "INSERT" and not has_returning(query):
            table = insert_table_name(query)
            pk = PRIMARY_KEYS.get(table)
            if pk:
                translated = f"{translated.rstrip().rstrip(';')} RETURNING {pk}"
                appended_returning = True

        self._cursor.execute(translated, bind)

        if appended_returning:
            row = self._cursor.fetchone()
            self.lastrowid = row[0] if row else None
        else:
            self.lastrowid = None

        return self

    def executemany(self, query, params_list):
        translated = translate_query(query)
        self._cursor.executemany(translated, list(params_list))
        return self

    def fetchone(self):
        # Unlike sqlite3, psycopg raises if the last statement produced
        # no result set at all (e.g. CREATE TABLE, or a plain INSERT
        # with no RETURNING) instead of just returning None/[].
        if self._cursor.description is None:
            return None
        row = self._cursor.fetchone()
        if row is None:
            return None
        columns = [d[0] for d in self._cursor.description]
        return Row(columns, row)

    def fetchall(self):
        if self._cursor.description is None:
            return []
        rows = self._cursor.fetchall()
        if not rows:
            return []
        columns = [d[0] for d in self._cursor.description]
        return [Row(columns, r) for r in rows]

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def close(self):
        self._cursor.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class CompatConnection:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return CompatCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()
        return False

    def __getattr__(self, name):
        return getattr(self._conn, name)
