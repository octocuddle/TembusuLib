# utils/db_loan_history.py
import requests

# Displaying up to 25 books
def get_loan_history(matric: str, base_url="http://localhost:8000"):
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