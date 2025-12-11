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
    def on_window_restore(event=None):
        """Force window to front when restored from minimize"""
        try:
            window.lift()
            window.attributes('-topmost', True)
            window.after(100, lambda: window.attributes('-topmost', False))
            window.focus_force()
        except:
            pass

    # Bind to Map event (triggered when window is deiconified/restored)
    window.bind('<Map>', on_window_restore)
