"""Auto-injects created_by/edited_by (and edited_at, via each table's
existing updated_at column) into INSERT/UPDATE statements for the
audited tables, so ~40 call sites across the app don't each need to be
taught about who's logged in.

Deliberately table-scoped and query-shape-aware rather than a general
SQL rewriter - the app's SQL is too varied to safely rewrite blind (see
the sync engine's row-snapshot design for the same lesson learned the
hard way). Every shape this module has to handle has been read first;
see the two regexes below and the tests exercising them.
"""

import re

# Tables the user asked to attribute. barang_tax and container_delivery_costs
# are deliberately excluded - see the plan discussion: barang_tax is
# system-generated, and the delivery-costs decision wasn't made.
AUDITED_TABLES = {"barang", "containers", "customers", "kapals", "pengirim", "detail_container"}

_current_user = {"username": None}


def set_current_user(username):
    """Called once at login. None/empty clears it back to 'system'
    (used by scripts that write to the DB without going through login,
    e.g. seed_initial_data.py)."""
    _current_user["username"] = username or None


def get_current_user():
    return _current_user["username"] or "system"


# INSERT INTO table (col, col, ...) VALUES (?, ?, ...)[, (?, ?, ...), ...] [trailing text]
# The tuples group grabs one or more comma-separated (?, ?, ...) groups
# in a row - a multi-row VALUES list, as a batch insert uses - leaving
# anything after the last tuple (a RETURNING clause, a trailing `;`) in
# suffix. None of this app's placeholders are ever nested parens, so a
# plain [^()]* per tuple is safe.
_INSERT_RE = re.compile(
    r'^(?P<prefix>\s*INSERT\s+INTO\s+"?(?P<table>\w+)"?\s*)'
    r"\((?P<cols>[^)]*)\)"
    r"(?P<values_kw>\s*VALUES\s*)"
    r"(?P<tuples>(?:\([^()]*\)\s*,?\s*)+)"
    r"(?P<suffix>.*)$",
    re.IGNORECASE | re.DOTALL,
)

_TUPLE_RE = re.compile(r"\(([^()]*)\)")

# UPDATE table SET ... WHERE ...  (every UPDATE in this app has a WHERE)
_UPDATE_RE = re.compile(
    r'^(?P<prefix>\s*UPDATE\s+"?(?P<table>\w+)"?\s+SET\s+)'
    r"(?P<set_clause>.*?)"
    r"(?P<where_and_rest>\bWHERE\b.*)$",
    re.IGNORECASE | re.DOTALL,
)

_EDITED_BY_RE = re.compile(r"\bedited_by\s*=", re.IGNORECASE)
_UPDATED_AT_RE = re.compile(r"\bupdated_at\s*=", re.IGNORECASE)


def apply_audit(query, params):
    """Rewrite an INSERT/UPDATE on an audited table to stamp
    created_by/edited_by (and edited_at via updated_at). Returns the
    query/params unchanged for anything else - a different table, a
    SELECT/DELETE, or a shape the regexes don't recognize (fails open
    rather than risk mangling a query it doesn't understand).
    """
    m = _INSERT_RE.match(query)
    if m and m.group("table") in AUDITED_TABLES:
        return _rewrite_insert(m, params)

    m = _UPDATE_RE.match(query)
    if m and m.group("table") in AUDITED_TABLES:
        return _rewrite_update(m, params)

    return query, params


def _rewrite_insert(m, params):
    """created_by/edited_by are brand-new columns - no existing INSERT
    can already reference them, so this always appends both, no
    detection needed (unlike the UPDATE case for updated_at below)."""
    username = get_current_user()
    cols = m.group("cols").rstrip()
    tuple_strs = _TUPLE_RE.findall(m.group("tuples"))

    new_cols = f"{cols}, created_by, edited_by"
    new_tuples = ", ".join(f"({t.rstrip()}, ?, ?)" for t in tuple_strs)
    new_query = (
        f"{m.group('prefix')}({new_cols}){m.group('values_kw')}"
        f"{new_tuples}{m.group('suffix')}"
    )

    # Each VALUES tuple gets its own (username, username) pair inserted
    # after its own placeholders - params are one flat tuple, ordered
    # tuple-by-tuple, so this can't just be appended once at the end
    # the way the single-row case could. Split by placeholder count per
    # tuple (not by column count) so a tuple mixing ? with a literal
    # still lines up correctly.
    placeholders_per_tuple = [t.count("?") for t in tuple_strs]
    if sum(placeholders_per_tuple) != len(params):
        # Shape doesn't match what we expected (e.g. a literal contains
        # a literal '?') - fail open rather than risk misaligning params.
        return m.string, params

    new_params = []
    offset = 0
    for n in placeholders_per_tuple:
        new_params.extend(params[offset:offset + n])
        new_params.append(username)
        new_params.append(username)
        offset += n
    return new_query, tuple(new_params)


def _rewrite_update(m, params):
    """edited_by can never already be set (new column). updated_at
    already exists on 5 of 6 audited tables and several call sites
    already set it explicitly (container/kapal edit forms) - detect
    and skip those rather than emit a duplicate SET target, which
    Postgres rejects outright.
    """
    username = get_current_user()
    set_clause = m.group("set_clause")

    # How many `?` placeholders the *original* SET clause consumes,
    # so the new edited_by param lands at the matching position - it
    # must appear before the WHERE clause's own params in the tuple,
    # since params are positional against left-to-right ? occurrence.
    original_placeholder_count = set_clause.count("?")

    additions = []
    new_params = list(params)
    if not _EDITED_BY_RE.search(set_clause):
        additions.append("edited_by = ?")
        new_params.insert(original_placeholder_count, username)
    if not _UPDATED_AT_RE.search(set_clause):
        additions.append("updated_at = CURRENT_TIMESTAMP")

    if not additions:
        return m.string, params  # nothing to add (already fully audited)

    new_set = set_clause.rstrip()
    if not new_set.endswith(","):
        new_set += ","
    new_set += " " + ", ".join(additions) + " "

    new_query = f"{m.group('prefix')}{new_set}{m.group('where_and_rest')}"
    return new_query, tuple(new_params)
