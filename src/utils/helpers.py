def safe_error_message(e, default="Terjadi kesalahan pada database. Coba lagi atau hubungi admin."):
    """Text safe to put in a user-facing messagebox for an exception
    caught from a db.* call.

    DatabaseError text is built by wrapping whatever the driver raised
    (see src/models/database.py) - for a Postgres connection failure
    that includes host/port/database/username, which has no business
    showing up in a dialog box on someone's screen. The underlying
    db.* call already logged the full detail (see app_database.log),
    so nothing is lost by not repeating it here.

    Anything else (ValueError from a form validation, etc.) is already
    written to be shown to the user, so it passes through unchanged.
    """
    from src.models.db.errors import DatabaseError
    if isinstance(e, DatabaseError):
        return default
    return str(e)


def format_db_timestamp(value, fmt='%d/%m/%Y %H:%M'):
    """Render a created_at/updated_at value in the machine's local time.

    Both backends store these columns as UTC with no timezone attached,
    so the raw value is 7 hours behind a user in WIB. Postgres fills
    DEFAULT CURRENT_TIMESTAMP from a session whose TimeZone is UTC, and
    SQLite's CURRENT_TIMESTAMP is UTC by definition (and cannot be
    changed). Displaying the stored value as-is is what made a kapal
    created at 15:58 show up as 08:58.

    The value arrives as a datetime (psycopg) or a string (sqlite3), so
    both shapes are parsed, tagged as UTC, then converted to local.

    NOT for columns written from Python with datetime.now() - those are
    already local and would be shifted a second time. In practice that
    means detail_container.assigned_at/created_at (see
    assign_barang_to_container_with_pricing), which no caller passes
    through here.
    """
    if value is None or value == '':
        return None
    from datetime import datetime as _dt, timezone as _tz

    if isinstance(value, _dt):
        moment = value
    else:
        text = str(value).replace('T', ' ')
        moment = None
        for pattern in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                moment = _dt.strptime(text[:26], pattern)
                break
            except ValueError:
                continue
        if moment is None:
            return str(value)  # unrecognized shape - show it rather than hide it

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=_tz.utc)
    return moment.astimezone().strftime(fmt)


def _format_audit_timestamp(value):
    """Audit timestamps for display, converted from stored UTC to local."""
    return format_db_timestamp(value)


def format_audit_line(record, placeholder="—"):
    """'Dibuat: budi • 01/02/2026 14:30   |   Diubah: siti • 03/02/2026 09:15'
    from a record's created_by/created_at/edited_by/updated_at columns.
    Rows written before this feature existed have NULL audit columns,
    which render as the placeholder rather than blank/None.
    """
    if not record:
        return ""

    def part(who, when):
        who_text = who or placeholder
        when_text = _format_audit_timestamp(when) or placeholder
        return f"{who_text} • {when_text}"

    created = part(record.get('created_by'), record.get('created_at'))
    edited = part(record.get('edited_by'), record.get('updated_at'))
    return f"Dibuat: {created}   |   Diubah: {edited}"


def format_ton(value):
    """
    Format ton value with exactly 3 decimal places.
    - Always shows 3 decimal places (no trailing zero removal)
    - Rounds to 3 decimal places if value has more decimals

    Examples:
        1.5 -> "1.500"
        1.50 -> "1.500"
        1.234 -> "1.234"
        1.2374 -> "1.237"
        1.0 -> "1.000"
        0.5 -> "0.500"
    """
    try:
        if value in [None, '', '-']:
            return "0.000"

        ton_value = float(value)

        # Round to 3 decimal places
        rounded_value = round(ton_value, 3)

        # Format with exactly 3 decimal places (no trailing zero removal)
        formatted = f"{rounded_value:.3f}"

        return formatted
    except (ValueError, TypeError):
        return "0.000"


def setup_window_restore_behavior(window):
    """
    Setup window to properly restore from minimize.

    This fixes the issue where window doesn't come to front after minimize/restore.
    Works for both Tk root windows and Toplevel windows.

    Args:
        window: tk.Tk or tk.Toplevel window instance
    """
    # Track if window was actually minimized
    window._was_minimized = False

    def on_window_unmap(event=None):
        """Track when window is minimized"""
        try:
            # Check if this is a minimize event (not just hidden by other windows)
            if window.state() == 'iconic':
                window._was_minimized = True
        except:
            pass

    def on_window_restore(event=None):
        """Force window to front when restored from minimize"""
        try:
            # Only lift if window was actually minimized before
            if getattr(window, '_was_minimized', False):
                window._was_minimized = False
                window.lift()
                window.attributes('-topmost', True)
                window.after(100, lambda: window.attributes('-topmost', False))
                window.focus_force()
        except:
            pass

    # Bind to Unmap event (triggered when window is minimized/hidden)
    window.bind('<Unmap>', on_window_unmap)
    # Bind to Map event (triggered when window is deiconified/restored)
    window.bind('<Map>', on_window_restore)
