# utils/db_return_book.py

import requests
import os

def return_book(borrow_id: int):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
    try:
        response = requests.put(
            f"{base_url}/api/v1/borrowing/return/{borrow_id}",
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Return failed: {response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
