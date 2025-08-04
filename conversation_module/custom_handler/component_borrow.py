# conversation_module/custom_handler/component_borrow.py

from telegram import InlineKeyboardButton
from utils.qr_decoder import decode_qr
from utils.db_book_validator import get_book_by_qr
from utils.db_add_borrow import borrow_book
from utils.auth_helpers import authenticated_users
from utils.date_parser import pretty_date
from utils.db_loan_history import get_loan_history_by_student
from utils.semester_calendar import get_period, get_days_until_period_end,get_next_semester_start
from utils.date_parser import pretty_date
from datetime import date, datetime
import os

MAX_BORROW_LIMIT = int(os.getenv("MAX_BORROW_LIMIT"))

def start_borrow_flow(user_id: str, user_state: dict, fulfillment_text: str):
    user_state[user_id] = user_state.get(user_id, {})
    student_info = authenticated_users.get(user_id)

    if not student_info:
        return {
            "type": "text",
            "text": "❌ You are not authenticated. Please use /start to begin."
        }


    today = date.today()
    period = get_period(today)

    if not period:
        return {
            "type": "text",
            "text": "📚 The library is closed. No valid semester or holiday found in config."
        }
    
    if "Holiday" in period["name"]:
        next_mmdd = get_next_semester_start(today)
        if next_mmdd:
            next_start_str = datetime.strptime(next_mmdd, "%m-%d").strftime("%-d %B")  # → "1 August"
        else:
            next_start_str = "the next semester"
    
        return {
            "type": "text",
            "text": (
                "📚 The library is currently closed for maintenance during the break.\n"
                f"📆 Holiday period: {pretty_date(period['start'])} to {pretty_date(period['end'])}.\n"
                f"Please visit us again next semester, starting from {next_start_str}."
            )
        }
    
    remaining_days, sem_end = get_days_until_period_end(today)
    if remaining_days == 0:
        next_mmdd = get_next_semester_start(today)
        if next_mmdd:
            next_start_str = datetime.strptime(next_mmdd, "%m-%d").strftime("%-d %B")  # → "1 August"
        else:
            next_start_str = "the next semester"

        return {
            "type": "text",
            "text": (
                f"📚 Today is the last day of the current semester (ends on {sem_end}).\n"
                "Borrowing is not allowed on the semester end date due to return logistics.\n"
                f"Please visit us again next semester, starting from {next_start_str}."
            )
        }

    matric = student_info.get("matric_number")
    success, active_loans = get_loan_history_by_student(matric)

    if not success:
        return {
            "type": "text",
            "text": f"⚠️ Unable to check your borrow record right now.\n\nPlease try again later or contact @LibraryAdmin.\n\nError: {active_loans}"
        }
    

    if len(active_loans) >= MAX_BORROW_LIMIT:
        return {
            "type": "text",
            "text": (
                f"📚 You have already borrowed {len(active_loans)} book(s), which is the maximum allowed.\n\n"
                "❗ Please return a book before borrowing a new one.\n"
                "You can check your loan record using the menu."
            )
        }

    user_state[user_id]["stage"] = "borrow_waiting_qr"
    print(f"[STATE] Set {user_id} stage to borrow_waiting_qr")
    # Save max loan days in state for later use
    user_state[user_id]["loan_days"] = min(14, remaining_days)

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
    user_state[user_id]["stage"] = "borrow_confirm"
    user_state[user_id]["book_info"] = book_info

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

def handle_confirm_borrow(user_id: str, user_state: dict):
    book_info = user_state.get(user_id, {}).get("book_info")
    student_info = authenticated_users.get(user_id)

    if not book_info or not student_info:
        return {
            "type": "text",
            "text": "❌ Missing session data. Please start again with the borrow option."
        }

    matric = student_info.get("matric_number")
    loan_days = user_state.get(user_id, {}).get("loan_days", 14)
    
    success, result = borrow_book(copy_id=book_info["copy_id"], matric_number=matric, loan_days=loan_days)

    # Clean up user state
    user_state.pop(user_id, None)

    if not success:
        user_state.pop(user_id, None)
        return {
            "type": "text",
            "text": f"❌ Borrow failed: {result}. \n\nUse menu to start a new request. \nIf you encounter further problem, please contact the @LibraryAdmin."
        }
    print(f'\n Borrow successful: {result}\n')

    # result is the borrow record
    student_name = result.get("student_name", "Unknown")
    student_matric = result.get("matric_number", "N/A")
    due_date = pretty_date(result.get("due_date", ""))

    lines = [
            f"👤 {student_name} ({student_matric})",
            f"✅ You have successfully borrowed the following book:\n",
            f"📖 Title: {book_info.get("book_title", "Untitled")}",
            f"✍️ Author: {book_info.get("book_author", "Unknown Author")}",
            f"🏷️ ISBN: {book_info.get("book_isbn", "N/A")}",
            f"📅 Due date: {due_date}\n",
            f"Use Menu to continue accessing library services. \nOtherwise, have a nice day."
    ]

    if loan_days<14:
        lines.append(f"\n⚠️ This book is due in {loan_days} days as semester is ending. Please return it before semester end.")

    return {
        "type": "text",
        "text": "\n".join(lines)
    }

def handle_cancel_borrow(user_id: str, user_state: dict):
    user_state.pop(user_id, None)
    return {
        "type": "text",
        "text": "ℹ️ Borrowing cancelled. Please choose another option from the menu."
    }
