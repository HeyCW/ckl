"""Classifies a query as safe to run on the autocommit (read) pool.

Conservative on purpose: only a query that starts with SELECT/WITH AND
contains no INSERT/UPDATE/DELETE anywhere in its text counts as
read-only. Verified against this app's whole query surface before this
was written: the sole CTE in the codebase (lifting_window.py's
invoice/delivery aggregation) is pure SELECT, nothing uses
SELECT ... FOR UPDATE, and no UPDATE/DELETE uses RETURNING (which
would still be caught anyway, since the keyword scan runs on the whole
string regardless of clause position).

This only decides which pool a *single* execute()/execute_one() call
gets - it says nothing about whether a caller running several
statements against the same connection should use it. That decision
belongs to the caller: see AppDatabase.get_connection()'s docstring.
"""

import re

_READONLY_START_RE = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_WRITE_KEYWORD_RE = re.compile(r"\b(INSERT|UPDATE|DELETE)\b", re.IGNORECASE)


def is_readonly_query(query):
    return bool(_READONLY_START_RE.match(query)) and not _WRITE_KEYWORD_RE.search(query)
