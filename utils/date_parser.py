# utils/date_parser.py

from datetime import datetime

def pretty_date(date_str):

    try:
        dt = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
        return dt
    except:
        return date_str