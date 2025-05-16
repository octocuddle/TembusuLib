from telegram import InlineKeyboardButton
from utils.db_student_validator import validate_student_info

def handle_borrow_auth(user_id, params, user_state):
    matric = params.get("MatricNum")
    email = params.get("emailAdd")

    if matric and email:
        user_state[user_id] = {
            "matric": matric,
            "email": email,
            "stage": "auth_pending"
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
                [InlineKeyboardButton("✅ Yes", callback_data="confirm_yes")],
                [InlineKeyboardButton("❌ No", callback_data="confirm_no")]
            ]
        }
    else:
        return {
            "type": "text",
            "text": "❌ Missing information. Please enter your Matric Number and Email."
        }


def handle_confirm_borrow(user_id, user_state):
    info = user_state.get(user_id, {})
    matric = info.get("matric")
    email = info.get("email")

    is_valid, result = validate_student_info(matric, email)

    if is_valid:
        user_state[user_id]["stage"] = "authenticated"
        return {
            "type": "text",
            "text": (
                f"✅ Authentication successful for {result}.\n"
                "Please take a photo of the QR code at the back of your book that you want to borrow, "
                "and upload the photo to this conversation, so that I can borrow this book for you."
            )
        }
    else:
        # Revert to auth_pending state with same info
        user_state[user_id] = {
            "matric": matric,
            "email": email,
            "stage": "auth_pending"
        }
        return {
            "type": "text",
            "text": (
                f"❌ Authentication failed: {result}. \n"
                "Please enter valid matriculation number (e.g. A0012345U) and email address (e.g. john_soh@u.edu.sg) for authentication."
            )
        }
