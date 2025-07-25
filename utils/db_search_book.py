# utils/db_loan_history.py
import requests
import os

# Displaying up to 25 books
def get_book_by_title(booktitle: str):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    try:
        response = requests.get(
            f"{base_url}/api/v1/book/search/title/{booktitle}?exact_match=false&limit=20",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    

def get_book_by_author(authorname: str):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    try:
        response = requests.get(
            f"{base_url}/api/v1/book/search/author/{authorname}?limit=20",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    

def get_book_copy_details(booktitle: str):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    try:
        response = requests.get(
            f"{base_url}/api/v1/book_copies/?limit=20&book_title={booktitle}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    
def get_book_borrow_history(bookid: int):
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    try:
        response = requests.get(
            f"{base_url}/api/v1/borrowing/book/{bookid}?skip=0&limit=100",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
