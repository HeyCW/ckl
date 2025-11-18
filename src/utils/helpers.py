def format_ton(value):
    """
    Format ton value with maximum 2 decimal places.
    - If value has <= 2 decimal places, show as-is
    - If value has > 2 decimal places, round to 2 decimal places
    - Removes trailing zeros after decimal point

    Examples:
        1.5 -> "1.5"
        1.50 -> "1.5"
        1.234 -> "1.23"
        1.237 -> "1.24"
        1.0 -> "1"
        0.5 -> "0.5"
    """
    try:
        if value in [None, '', '-']:
            return "0"

        ton_value = float(value)

        # Round to 2 decimal places
        rounded_value = round(ton_value, 2)

        # Format with up to 2 decimal places, removing trailing zeros
        formatted = f"{rounded_value:.2f}".rstrip('0').rstrip('.')

        return formatted
    except (ValueError, TypeError):
        return "0"
