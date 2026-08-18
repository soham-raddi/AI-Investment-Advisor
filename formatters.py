"""Shared formatting helpers for Streamlit displays."""


def safe_percent_format(value, default="N/A"):
    """Safely format a value as percentage, handling None/NaN/strings."""
    try:
        return f"{float(value):.2%}"
    except (ValueError, TypeError):
        return default


def safe_decimal_format(value, decimals=2, prefix="", suffix="", default="N/A"):
    """Safely format a value with a fixed number of decimal places."""
    try:
        return f"{prefix}{float(value):.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return default
