def _format_audit_timestamp(value):
    """Timestamps come back as a datetime object (Postgres) or a raw
    string (SQLite stores TIMESTAMP as TEXT) - normalize either into
    DD/MM/YYYY HH:MM for display."""
    if value is None:
        return None
    from datetime import datetime as _dt
    if isinstance(value, _dt):
        return value.strftime('%d/%m/%Y %H:%M')
    text = str(value)
    for pattern in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            return _dt.strptime(text[:26], pattern).strftime('%d/%m/%Y %H:%M')
        except ValueError:
            continue
    return text


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
