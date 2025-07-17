# utils/db_loan_history.py
import requests
import os

# Displaying up to 25 books
def get_loan_history(matric: str, active_only=True, limit=25):

    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    
    try:
        # print(f"{base_url}/api/v1/borrowing/student/{matric}?active_only={str(active_only).lower()}&skip=0&limit={limit}")
        response = requests.get(
            f"{base_url}/api/v1/borrowing/student/{matric}?active_only={str(active_only).lower()}&skip=0&limit={limit}",
            timeout=5
        )
        # print(f"response of get_loan_history is: {response.json()}")
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"