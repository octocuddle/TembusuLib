# utils/db_add_borrow.py
import requests
import os

def borrow_book(copy_id: int, matric_number: str, loan_days: int = 14):
    """
    Attempt to create a borrow record in the backend.
    Returns (is_successful: bool, message: str)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback

    try:
        response = requests.post(
            f"{base_url}/api/v1/borrowing/",
            json={
                "copy_id": copy_id,
                "matric_number": matric_number,
                "loan_days": loan_days
            },
            timeout=5
        )

        if response.status_code == 201:
            return True, "Borrowing record successfully created."
        else:
            return False, f"Borrowing failed: {response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
