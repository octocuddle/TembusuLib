# utils/db_loan_history.py
import requests
import os

# Displaying up to 25 books
def get_loan_history(matric: str):

    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/borrowing/student/{matric}/history?include_active=True&limit=25",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"