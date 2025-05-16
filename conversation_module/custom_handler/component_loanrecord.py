from telegram import InlineKeyboardButton
from utils.db_student_validator import validate_student_info
from utils.db_loan_history import get_loan_history

def handle_loan_auth(user_id, params, user_state):
    matric = params.get("MatricNum")
    email = params.get("emailAdd")

    if matric and email:
        user_state[user_id] = {
            "matric": matric,
            "email": email,
            "stage": "loan_auth_pending"
        }
        return {
            "type": "confirm",
            "text": (
                f"You entered:\n"
                f"Matric Number: {matric}\n"
                f"Email: {email}\n\n"
                "Is this correct?"
            ),
            "buttons": [
                [InlineKeyboardButton("✅ Yes", callback_data="confirm_loan_yes")],
                [InlineKeyboardButton("❌ No", callback_data="confirm_loan_no")]
            ]
        }
    else:
        return {
            "type": "text",
            "text": "❌ Missing information. Please enter your Matric Number and Email."
        }


def handle_confirm_loan(user_id, user_state):
    info = user_state.get(user_id, {})
    matric = info.get("matric")
    email = info.get("email")

    is_valid, result = validate_student_info(matric, email)

    if not is_valid:
        user_state[user_id] = {
            "matric": matric,
            "email": email,
            "stage": "loan_auth_pending"
        }
        return {
            "type": "text",
            "text": f"❌ Authentication failed: {result}. Please enter valid details to view loan records."
        }

    # Clear state after successful validation
    user_state.pop(user_id, None)

    success, records_or_msg = get_loan_history(matric)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch loan records: {records_or_msg}"
        }

    if not records_or_msg:
        return {
            "type": "text",
            "text": f"📭 No loan records found for {matric}."
        }

    lines = [f"📚 Loan Records for {matric}:"]
    for record in records_or_msg:
        title = record.get("book_title", "Unknown Title")
        call = record.get("call_number", "Unknown Call Number")
        due = record.get("due_date", "N/A")
        returned = record.get("return_date")
        lines.append(
            f"• {title} ({call})\n  Due: {due}\n  Returned: {returned or 'Not yet returned'}\n"
        )

    return {
        "type": "text",
        "text": "\n".join(lines)
    }
