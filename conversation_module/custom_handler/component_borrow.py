# conversation_module/custom_handler/component_borrow.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.qr_decoder import decode_qr
from utils.db_book_validator import get_book_by_qr
from utils.db_add_borrow import borrow_book
from utils.auth_helpers import authenticated_users
from utils.date_parser import pretty_date

def start_borrow_flow(user_id: str, user_state: dict, fulfillment_text: str):
    user_state[user_id] = user_state.get(user_id, {})
    user_state[user_id]["stage"] = "borrow_waiting_qr"
    print(f"[STATE] Set {user_id} stage to borrow_waiting_qr")
    return {
        "type": "text",
        "text": "Your request to borrow is received.\n\n📸 Please submit a photo of the QR code at the back of the book, so that I can process your request."
    }

def handle_borrow_photo(file_path: str, user_id: str, user_state: dict):
    decoded = decode_qr(file_path)
    if not decoded:
        return {
            "type": "text",
            "text": "❌ Could not read QR code. Try a clearer image."
        }

    is_valid, book_info = get_book_by_qr(decoded)
    if not is_valid:
        return {
            "type": "text",
            "text": f"❌ {book_info}"
        }

    # Save decoded book info temporarily in state
    user_state[user_id] = {
        "stage": "borrow_confirm",
        "book_info": book_info
    }

    return {
        "type": "confirm",
        "text": (
            "Do you want to borrow the following book?\n"
            f"📖 Title: {book_info.get("book_title")}\n"
            f"✍️ Author: {book_info.get("book_author")}\n"
            f"🏷️ ISBN: {book_info.get("book_isbn")}\n"
            f"💾 Call Number: {book_info.get("book_call_number")}"
            
        ),
        "buttons": [
            [InlineKeyboardButton("✅ Yes", callback_data="confirm_borrow_yes")],
            [InlineKeyboardButton("❌ No", callback_data="confirm_borrow_no")]
        ]
    }

def expired_confirm_borrow_keyboard():
    expired_keyboard = [
        [InlineKeyboardButton("✅ Yes", callback_data="expired_disabled")],
        [InlineKeyboardButton("❌ No", callback_data="expired_disabled")]
    ]
    return InlineKeyboardMarkup(expired_keyboard)

def handle_confirm_borrow(user_id: str, user_state: dict):
    book_info = user_state.get(user_id, {}).get("book_info")
    student_info = authenticated_users.get(user_id)

    if not book_info or not student_info:
        return {
            "type": "text",
            "text": "❌ Missing session data. Please start again with the borrow option."
        }

    matric = student_info.get("matric_number")
    success, result = borrow_book(copy_id=book_info["copy_id"], matric_number=matric)

    # Clean up user state
    user_state.pop(user_id, None)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Borrow failed: {result}. Please contact the @LibraryAdmin."
        }
    print(f'\n Borrow successful: {result}\n')

    # result is the borrow record
    student_name = result.get("student_name", "Unknown")
    student_matric = result.get("matric_number", "N/A")
    due_date = pretty_date(result.get("due_date", ""))

    return {
        "type": "text",
        "text": (
            f"👤 {student_name} ({student_matric})\n"
            f"✅ You have successfully borrowed the following book:\n\n"
            f"📖 Title: {book_info.get("book_title", "Untitled")}\n"
            f"✍️ Author: {book_info.get("book_author", "Unknown Author")}\n"
            f"🏷️ ISBN: {book_info.get("book_isbn", "N/A")}\n"
            f"📅 Due date: {due_date}\n\n"
            f"Use Menu to continue accessing library services. \nOtherwise, have a nice day."
        )
    }

def handle_cancel_borrow(user_id: str, user_state: dict):
    user_state.pop(user_id, None)
    return {
        "type": "text",
        "text": "ℹ️ Borrowing cancelled. Please choose another option from the menu."
    }
