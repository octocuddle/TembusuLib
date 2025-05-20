# utils/db_student_validator.py

import requests
import os

def validate_student_info(matric: str, email: str) -> tuple[bool, str]:
    """
    Validate student info by checking if both matric and email belong to the same student.
    Returns (is_valid: bool, student_name_or_error: str)
    """
    matric = matric.lower()
    email = email.lower()
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    search_url = f"{base_url}/api/v1/student/search"

    try:
        # Query by matric
        matric_res = requests.get(search_url, params={"query": matric, "skip": 0, "limit": 1}, timeout=5)
        email_res = requests.get(search_url, params={"query": email, "skip": 0, "limit": 1}, timeout=5)

        if matric_res.status_code != 200 or email_res.status_code != 200:
            return False, "Backend query failed."

        matric_data = matric_res.json()
        email_data = email_res.json()

        if not matric_data or not email_data:
            return False, "No student record found for one or both fields."

        for student_m in matric_data:
            for student_e in email_data:
                if student_m["matric_number"].lower() == student_e["matric_number"].lower():
                    return True, student_m.get("full_name", "the student")

        return False, "Matric number and email do not match the same student."

    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")
        return False, "Internal server error during validation."
