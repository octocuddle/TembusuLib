# conversation_module/custom_handler/component_return.py
from telegram import InlineKeyboardButton
from utils.qr_decoder import decode_qr
from utils.db_book_validator import get_book_by_qr
from utils.db_return_book import return_book
from utils.auth_helpers import authenticated_users
from utils.db_loan_history import get_loan_history_by_student, get_active_loan_by_qr_code
from utils.db_location_validator import get_locationqr_by_id


def start_return_flow(user_id: str, user_state: dict, fulfillment_text: str):
    user_state[user_id] = user_state.get(user_id, {})
    user_state[user_id]["stage"] = "return_waiting_book_qr"
    return {
        "type": "text",
        "text": fulfillment_text or "📸 Please submit a photo of the book QR code."
    }

def handle_return_book_photo(file_path: str, user_id: str, user_state: dict):
    decoded = decode_qr(file_path)
    if not decoded:
        return {"type": "text", "text": "❌ Could not read QR code. Try a clearer image."}

    is_valid, book_info = get_book_by_qr(decoded, mode="return")
    if not is_valid:
        return {"type": "text", "text": f"❌ {book_info}"}

    student_info = authenticated_users.get(user_id)
    if not student_info:
        return {"type": "text", "text": "❌ You are not authenticated. Please try again."}

    matric = student_info.get("matric_number")
    copy_id = book_info["copy_id"]

    # Get student's active loans
    success, loan_data = get_loan_history_by_student(matric=matric, active_only=True)
    if not success:
        return {"type": "text", "text": f"❌ Could not verify borrower: {loan_data}"}

    # Is this book under the student's account?
    owns_loan = any(loan["copy_id"] == copy_id for loan in loan_data)

    user_state[user_id] = {
        "book_info": book_info,
        "stage": "return_waiting_location_qr" if owns_loan else "return_awaiting_proxy_confirmation"
    }

    if owns_loan:
        return {
            "type": "text",
            "text": (
                "📖 Book verified under your account.\n"
                f"Book Shelf: {book_info.get('location_name')}\n\n"
                "📸 Please place the book on the correct shelf and then submit a photo of the location QR code."
            )
        }

    # Book is not under this user's loan records
    return {
        "type": "confirm",
        "text": (
            "📖 This book is not currently on your loan record.\n"
            "Would you like to return it on behalf of someone else?\n\n"
            f"Book Shelf: {book_info.get('location_name')}\n"
        ),
        "buttons": [
            [InlineKeyboardButton("✅ Yes", callback_data="return_proxy_yes")],
            [InlineKeyboardButton("❌ No", callback_data="return_proxy_no")]
        ]
    }

def handle_return_location_photo(file_path: str, user_id: str, user_state: dict):
    decoded_location = decode_qr(file_path)
    if not decoded_location:
        return {"type": "text", "text": "❌ Could not read location QR code. Try again."}

    book_info = user_state.get(user_id, {}).get("book_info")
    student_info = authenticated_users.get(user_id)
    if not book_info or not student_info:
        return {"type": "text", "text": "❌ Missing session data. Please start again."}

    # Fetch correct location info by ID
    location_id = book_info.get("location_id")
    success, location_info = get_locationqr_by_id(location_id)
    if not success:
        return {"type": "text", "text": f"❌ Failed to verify shelf: {location_info}"}

    expected_qr = location_info.get("location_qr_code")
    expected_name = location_info.get("location_name")

    if decoded_location != expected_qr:
        return {
            "type": "text",
            "text": (
                f"❌ Incorrect shelf or QR code.\n\n"
                f"The correct location for this book is:\n"
                f"📍 {expected_name}\n\n"
                "📸 Please take a photo of the correct location QR code to complete the return."
            )
        }
    
    # Get active loans to find the borrow_id (even if it's not their own)
    success, matched_loan = get_active_loan_by_qr_code(book_info["qr_code"])
    if not success:
        return {"type": "text", "text": f"⚠️ {matched_loan}"}
    
    borrow_id = matched_loan["borrow_id"]
    user_state[user_id]["borrow_record"] = matched_loan

    returned_by = authenticated_users[user_id]["matric_number"]
    borrowed_by = user_state[user_id]["borrow_record"]["matric_number"]
    if returned_by != borrowed_by:
        print(f"[DEBUG] Proxy return: {returned_by} returned for {borrowed_by}")
        
    success, result = return_book(borrow_id=borrow_id)
    user_state.pop(user_id, None)

    

    if not success:
        return {"type": "text", "text": f"❌ Return failed: {result}"}
    print(f"book info: {book_info}")
    return {
        "type": "text",

        "text": (
            f"✅ Book returned successfully:\n"
            f"📖 {book_info.get('book_title')}\n"
            f"📍 Returned at location: {book_info.get("location_name")}\n\n"
            "Use Menu to continue accessing library services."
        )        
    }

'''def handle_return_proxy_decision(user_id: str, user_state: dict, choice: str):
    if choice == "yes":
        user_state[user_id]["stage"] = "return_waiting_location_qr"
        return {
            "type": "text",
            "text": (
                "👍 Thank you! Please place the book back on the correct shelf and then submit a photo of the location QR code."
            )
        }
    else:
        user_state.pop(user_id, None)
        return {
            "type": "text",
            "text": (
                "👍 No problem. Please remind the borrower to return it themselves.\n"
                "Use the Menu to continue accessing library services."
            )
        }'''

def handle_return_proxy_decision(user_id: str, user_state: dict, choice: str):
    if choice == "yes":
        user_state[user_id]["stage"] = "return_waiting_location_qr"
        return {
            "type": "text",
            "text": (
                "👍 Thank you! Please place the book back on the correct shelf and then submit a photo of the location QR code."
            )
        }
    else:
        book_info = user_state.get(user_id, {}).get("book_info")
        user_state[user_id]["stage"] = "return_waiting_location_qr"

        return {
            "type": "text",
            "text": (
                "📸 Please still place the book back on the correct shelf and then submit a photo of the location QR code to complete the return process.\n\n"
                f"Book Shelf: {book_info.get('location_name')}\n\n"
                "📨 Since you're returning this on behalf of someone else, kindly message the library admin on Telegram to notify them.\n\n"
                "🔔 Admin Contact: @LibraryAdmin\n"
                "Thank you for your help!"
            )
        }

