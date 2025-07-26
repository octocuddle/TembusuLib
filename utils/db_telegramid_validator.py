# utils/db_telegramid_validator.py
import requests
from typing import Union
import os

def validate_student_by_telegram_id(telegram_id: str) -> tuple[bool, Union[dict, str]]:
    """
    Validate student by checking if the Telegram ID is associated with a registered student.
    Returns (is_valid: bool, student_name_or_error: dict or str)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # fallback for dev
    url = f"{base_url}/api/v1/student/search?query={telegram_id}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            students = response.json()
            if not students:
                return False, "You're not registered. Please contact the library admin at @LibraryAdminEmail."

            student_data = students[0]  # Take the first match 

            if student_data.get("status") == "active":
                return True, student_data
            else:
                return False, "You are not an active student and could not use the library service. Please contact the library admin at @LibraryAdminEmail."

        elif response.status_code == 404:
            return False, "You're not registered. Please contact the library admin at @LibraryAdminEmail."
        else:
            return False, f"Unexpected error from backend: {response.status_code}"

    except Exception as e:
        print(f"[ERROR] Telegram ID validation failed: {e}")
        return False, "Internal error during authentication. Please try again later."
