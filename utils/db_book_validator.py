# utils/db_book_validator.py
import requests
import os

def get_book_by_qr(qr_code: str) -> tuple[bool, dict | str]:
    """
    Validate book existence and availability using the scanned QR code.
    Returns (is_valid: bool, book_info or error_msg)
    """
    
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback

    try:
        qr_code = qr_code.strip().lower()
        url = f"{base_url}/api/v1/book_copies/qr-code/{qr_code}"
        print(f"[DEBUG] Querying: {url}")
        response = requests.get(url, timeout=5)
        print(f"[DEBUG] Status: {response.status_code} | Body: {response.text}")

        if response.status_code == 200:
            book_data = response.json()
            if book_data.get("status") != "available":
                return False, f"Book is currently not available for borrowing (Status: {book_data['status']})"
            return True, book_data
        elif response.status_code == 404:
            return False, "Book not found for the scanned QR code."
        else:
            return False, f"Unexpected backend error: {response.status_code}"

    except Exception as e:
        print(f"[ERROR] get_book_by_qr: {e}")
        return False, "Backend request failed."
