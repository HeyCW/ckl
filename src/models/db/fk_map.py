"""Foreign key relationships needed to remap offline-allocated IDs to
the real IDs Postgres assigns when a row is pushed during sync.
"""

FOREIGN_KEYS = {
    "containers": {"kapal_id": "kapals"},
    "barang_tax": {"container_id": "containers", "barang_id": "barang"},
    "detail_container": {
        "barang_id": "barang",
        "container_id": "containers",
        "tax_id": "barang_tax",
    },
    "container_delivery_costs": {"container_id": "containers"},
}

# New rows created while offline get IDs from this range so they can
# never collide with a real Postgres-assigned ID. Chosen far above any
# plausible real row count.
OFFLINE_ID_BASE = 900_000_000

# Reverse of FOREIGN_KEYS: parent table -> [(child table, fk column), ...].
# Used to cascade an ID remap (offline temp ID -> real Postgres ID) into
# every mirror row that references it, so the mirror doesn't end up with
# dangling FK values pointing at an ID that no longer exists locally.
REFERENCING = {}
for _child, _fks in FOREIGN_KEYS.items():
    for _fk_col, _parent in _fks.items():
        REFERENCING.setdefault(_parent, []).append((_child, _fk_col))
