# utils/db_book_validator.py
import requests
import os

def get_book_by_qr(qr_code: str, mode: str = "borrow") -> tuple[bool, dict | str]:
    """
    Validate book existence based on QR code.
    In 'borrow' mode, ensures book is available.
    In 'return' mode, accepts borrowed books.
    Returns (is_valid: bool, combined_book_info or error_msg)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    try:
        qr_code = qr_code.strip().lower()
        url = f"{base_url}/api/v1/book_copies/qr-code/{qr_code}"
        print(f"[DEBUG] Querying: {url}")
        response = requests.get(url, timeout=5)
        print(f"[DEBUG] Status: {response.status_code} | Body: {response.text}")

        if response.status_code != 200:
            if response.status_code == 404:
                return False, "Book not found for the scanned QR code."
            return False, f"Unexpected backend error: {response.status_code}"
        
        copy_data = response.json()

        if mode == "borrow":
            if copy_data.get("status") != "available":
                return False, (
                    f"Book is currently not available for borrowing (Status: {copy_data['status']}). \n"
                    f"You can take a photo of another book to borrow, or use the Start button in Menu to access other services."
                )
        elif mode == "return":
            if copy_data.get("status") != "borrowed":
                return False, f"⚠️ This book is not currently borrowed, so it cannot be returned."

        # Continue to fetch full book details
        book_id = copy_data.get("book_id")
        if not book_id:
            return False, "Book ID not found in book copy data."

        book_url = f"{base_url}/api/v1/book/search/id/{book_id}"
        book_response = requests.get(book_url, timeout=5)

        print(f"[DEBUG] Book details: {book_response.status_code} | Body: {book_response.text}")

        if book_response.status_code != 200:
            return False, f"Failed to retrieve full book details for book ID {book_id}."

        book_info = book_response.json()
        if not book_info:
            return False, f"No matching book found for title '{book_id}'."

        combined = {
            **copy_data,
            **{
                "book_author": book_info.get("author_name"),
                "book_isbn": book_info.get("isbn"),
                "book_publisher": book_info.get("publisher_name"),
                "book_year": book_info.get("publication_year"),
                "book_call_number": book_info.get("call_number"),
            }
        }

        return True, combined

    except Exception as e:
        print(f"[ERROR] get_book_by_qr: {e}")
        return False, "Backend request failed."
