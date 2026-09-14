"""Password hashing.

Uses bcrypt (salted, deliberately slow) for anything hashed from here on.

Existing rows may still carry the app's old unsalted SHA-256 hex digest
(64 lowercase hex chars) - verify_password() recognizes that shape and
falls back to comparing it, so already-deployed accounts keep working.
Pair that with needs_rehash(): after a legacy hash verifies correctly,
callers should re-hash the plaintext with hash_password() and store the
result, so the account is upgraded to bcrypt on its next successful
login instead of needing a bulk migration.
"""

import hashlib
import hmac
import re

import bcrypt

_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def hash_password(password):
    """Return a bcrypt hash (bytes-safe, includes its own salt)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _looks_like_legacy_sha256(stored_hash):
    return bool(_SHA256_HEX_RE.match(stored_hash or ""))


def verify_password(password, stored_hash):
    """True if password matches stored_hash, in either format."""
    if not stored_hash:
        return False

    if _looks_like_legacy_sha256(stored_hash):
        candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(candidate, stored_hash)

    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        # Not a bcrypt hash bcrypt recognizes either - fail closed.
        return False


def needs_rehash(stored_hash):
    """True if stored_hash is in the legacy SHA-256 format and should be
    upgraded to bcrypt the next time the plaintext is available (i.e.
    right after it verifies successfully)."""
    return _looks_like_legacy_sha256(stored_hash)
