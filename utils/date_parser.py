# utils/date_parser.py

from datetime import datetime

'''def pretty_date(date_str):

    try:
        dt = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
        return dt
    except:
        return date_str'''

def pretty_date(date_str):
    """
    Converts an ISO date string into 'YYYY-MM-DD Mon' format.
    Falls back gracefully if the input format is not ISO-compatible.
    """
    try:
        # Handle both '2025-10-20' and '2025-10-20T00:00:00Z'
        clean_str = date_str.replace("Z", "").replace("T", " ")
        dt = datetime.fromisoformat(clean_str.strip())
        return dt.strftime("%Y-%m-%d %a")  # e.g., 2025-10-20 Mon
    except Exception:
        return date_str  # fallback for unexpected formats
