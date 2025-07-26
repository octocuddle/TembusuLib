# utils/db_loan_history.py
import requests
import os

# Displaying up to 25 books
def get_loan_history_by_student(matric: str, active_only=True, limit=25):

    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/borrowing/student/{matric}?active_only={str(active_only).lower()}&skip=0&limit={limit}",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    

def get_active_loan_by_qr_code(qr_code: str):
    """
    Given a book QR code, returns the active borrow record for that specific copy_id.
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    try:
        # Step 1: Get copy_id and book_id from QR
        qr_url = f"{base_url}/api/v1/book_copies/qr-code/{qr_code.strip().lower()}"
        qr_res = requests.get(qr_url, timeout=5)
        if qr_res.status_code != 200:
            return False, f"QR not found: {qr_res.status_code}"

        copy_info = qr_res.json()
        copy_id = copy_info["copy_id"]
        book_id = copy_info["book_id"]

        # Step 2: Get all borrow history for the book
        history_url = f"{base_url}/api/v1/borrowing/book/{book_id}?skip=0&limit=100"
        history_res = requests.get(history_url, timeout=5)
        if history_res.status_code != 200:
            return False, f"Failed to get borrow history for book {book_id}"

        history = history_res.json()
        print("get_active_loan_by_qr_code:")
        print(f"book_id: {book_id}")
        print(f"copy_id: {copy_id}")
        print(f"history:\n{history}")
        

        # Step 3: Find active borrow for this copy
        for record in history:
            if record["copy_id"] == copy_id and record["status"] == "borrowed":
                return True, record

        return False, "No active borrow found for this copy."

    except Exception as e:
        return False, f"Exception: {e}"
