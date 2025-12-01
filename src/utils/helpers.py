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
