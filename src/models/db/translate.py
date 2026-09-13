import re

# Primary key column for each table, needed to emulate sqlite3's
# cursor.lastrowid on Postgres via an appended RETURNING clause.
PRIMARY_KEYS = {
    "users": "id",
    "customers": "customer_id",
    "kapals": "kapal_id",
    "containers": "container_id",
    "barang": "barang_id",
    "barang_tax": "tax_id",
    "detail_container": "id",
    "container_delivery_costs": "id",
    "pengirim": "pengirim_id",
}

_INSERT_TABLE_RE = re.compile(r"insert\s+into\s+[\"']?(\w+)", re.IGNORECASE)
_LIKE_RE = re.compile(r"\bLIKE\b", re.IGNORECASE)
_RETURNING_RE = re.compile(r"\bRETURNING\b", re.IGNORECASE)


def translate_query(query):
    """Translate a SQLite-flavored query (as written throughout this app)
    into the equivalent Postgres/psycopg-flavored query.

    Order matters:
    1. Escape every literal ``%`` first (e.g. LIKE '%THC%', comments like
       "PPN 1.1%") so psycopg's pyformat parameter substitution doesn't
       choke on them.
    2. Convert ``?`` positional placeholders to ``%s``.
    3. Convert SQLite's case-insensitive LIKE to Postgres's ILIKE.
    """
    translated = query.replace("%", "%%")
    translated = translated.replace("?", "%s")
    translated = _LIKE_RE.sub("ILIKE", translated)
    return translated


def insert_table_name(query):
    """Best-effort extraction of the target table from an INSERT statement."""
    match = _INSERT_TABLE_RE.search(query)
    return match.group(1) if match else None


def has_returning(query):
    return bool(_RETURNING_RE.search(query))


def normalize_params(params):
    """psycopg treats an empty (but not None) params sequence as "please
    do percent-substitution with zero arguments" and chokes on any
    literal ``%`` left in the query. Passing None instead tells it to
    skip substitution entirely, matching sqlite3's own no-params path.
    """
    return params if params else None
