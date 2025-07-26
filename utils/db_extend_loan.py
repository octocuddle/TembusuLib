# utils/db_extend_loan.py

import requests
import os

def extend_loan(borrow_id: int, days: int = 14):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    try:
        response = requests.put(
            f"{base_url}/api/v1/borrowing/extend/{borrow_id}?days={days}",
            timeout=5
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"{response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)
