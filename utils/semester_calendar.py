# utils/semester_calendar.py
from datetime import date, datetime
import os

def parse_env_date(key: str) -> date:
    value = os.getenv(key)  # e.g., "01-01"
    if not value:
        raise ValueError(f"Missing {key} in environment.")
    return datetime.strptime(f"{date.today().year}-{value}", "%Y-%m-%d").date()

SEMESTER_PERIODS = [
    {
        "name": "Sem1",
        "start": parse_env_date("SEM1_START"),
        "end": parse_env_date("SEM1_END")
    },
    {
        "name": "Sem1_Holiday",
        "start": parse_env_date("HOL1_START"),
        "end": parse_env_date("HOL1_END")
    },
    {
        "name": "Sem2",
        "start": parse_env_date("SEM2_START"),
        "end": parse_env_date("SEM2_END")
    },
    {
        "name": "Sem2_Holiday",
        "start": parse_env_date("HOL2_START"),
        "end": parse_env_date("HOL2_END")
    },
]

def get_period(today=None):
    today = today or date.today()
    for period in SEMESTER_PERIODS:
        if period["start"] <= today <= period["end"]:
            return period
    return None  # If today doesn't match any range

def get_days_until_period_end(today=None):
    today = today or date.today()
    current = get_period(today)
    if not current:
        return None, None
    return (current["end"] - today).days, current["end"]

def get_next_semester_start(today=None):
    today = today or date.today()
    current = get_period(today)
    
    if not current:
        return None  # Outside known semester/holiday ranges

    if "Sem1" in current["name"]:
        next_sem_key = "SEM2_START"
    elif "Sem2" in current["name"]:
        next_sem_key = "SEM1_START"
    else:
        return None  # Unexpected label

    mm_dd = os.getenv(next_sem_key)  # e.g., "08-01"
    return mm_dd  # return as "MM-DD" string
