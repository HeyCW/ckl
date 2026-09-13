class Row:
    """Mapping+sequence row object mirroring sqlite3.Row semantics.

    Used only for the Postgres backend so call sites written against
    sqlite3.Row (row[0], row['col'], dict(row)) keep working unchanged.
    """

    __slots__ = ("_values", "_index")

    def __init__(self, columns, values):
        self._index = {col: i for i, col in enumerate(columns)}
        self._values = tuple(values)

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._values[key]
        return self._values[self._index[key]]

    def __contains__(self, key):
        return key in self._index

    def get(self, key, default=None):
        i = self._index.get(key)
        return self._values[i] if i is not None else default

    def keys(self):
        return list(self._index.keys())

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __eq__(self, other):
        if isinstance(other, Row):
            return self._values == other._values and self._index == other._index
        return NotImplemented

    def __repr__(self):
        return f"Row({dict(zip(self._index, self._values))})"


def rows_from_cursor(cursor, raw_rows):
    """Wrap raw tuples returned by a DB-API cursor into Row objects."""
    if not raw_rows:
        return []
    columns = [d[0] for d in cursor.description]
    return [Row(columns, r) for r in raw_rows]
