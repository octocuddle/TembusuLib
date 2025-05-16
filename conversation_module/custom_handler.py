# conversation_module/custom_handler.py
from .dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_student_validator import validate_student_info
from utils.qr_decoder import decode_qr
from utils.db_book_validator import get_book_by_qr
from utils.db_add_borrow import borrow_book
from utils.db_loan_history import get_loan_history

class CustomHandler:
    def __init__(self):
        self.dialogflow = DialogflowHandler()
        self.user_state = {}  # Store user-specific info like matric and email

    def handle_request(self, text: str, user_id: str):
        # Step 1: Run Dialogflow
        df_response = self.dialogflow.raw_detect_intent(text, user_id)

        intent = df_response["intent"]
        params = df_response["parameters"]
        fulfillment = df_response["fulfillment_text"]
        print(f'intent: {intent}')
        print(f'params: {params}')
        print(f'fulfillment: {fulfillment}')

        # Stay in authentication stage if flagged
        if self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"

        if intent == "Default Fallback Intent" and self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"

        # Step 2: If it's the Welcome intent, override Dialogflow response with buttons
        if intent == "Default Welcome Intent":
            welcome_message = (
                "Welcome to Tembusu Library! I’m your assistant.\n\n"
                "What would you like to do today?"
            )
            keyboard = [
                [InlineKeyboardButton("📚 Borrow", callback_data="intent_borrow")],
                [InlineKeyboardButton("🔁 Return", callback_data="intent_return")],
                [InlineKeyboardButton("🔍 Search", callback_data="intent_search")],
                [InlineKeyboardButton("📖 Loan Record", callback_data="intent_loan")]
            ]
            return {
                "type": "buttons",
                "text": welcome_message,
                "buttons": keyboard
            }

        # Step 3: If it's borrow-authentication and both entities are present, confirm with user
        if intent == "borrow - authentication" and params.get("MatricNum") and params.get("emailAdd"):
            self.user_state[user_id] = {
                "matric": params["MatricNum"],
                "email": params["emailAdd"],
                "stage": "auth_pending"
            }
            return {
                "type": "confirm",
                "text": (
                    f"You entered:\n"
                    f"Matric Number: {params['MatricNum']}\n"
                    f"Email: {params['emailAdd']}\n\n"
                    "Is this correct?"
                ),
                "buttons": [
                    [InlineKeyboardButton("✅ Yes", callback_data="confirm_yes")],
                    [InlineKeyboardButton("❌ No", callback_data="confirm_no")]
                ]
            }

        if intent == "loanrecord - authentication" and params.get("MatricNum") and params.get("emailAdd"):
            self.user_state[user_id] = {
                "matric": params["MatricNum"],
                "email": params["emailAdd"],
                "stage": "loan_auth_pending"
            }
            return {
                "type": "confirm",
                "text": (
                    f"You entered:\n"
                    f"Matric Number: {params['MatricNum']}\n"
                    f"Email: {params['emailAdd']}\n\n"
                    "Is this correct?"
                ),
                "buttons": [
                    [InlineKeyboardButton("✅ Yes", callback_data="confirm_loan_yes")],
                    [InlineKeyboardButton("❌ No", callback_data="confirm_loan_no")]
                ]
            }


        # Step 4: Fallback to normal Dialogflow response
        return {
            "type": "text",
            "text": fulfillment or "Sorry, I didn't understand that."
        }


    def handle_callback(self, callback_data: str, user_id: str):

        print(f"[DEBUG] handle_callback triggered with {callback_data}")

        # Simulate button-triggered intent
        if callback_data == "intent_borrow":
            return self.handle_request("borrow", user_id)
        elif callback_data == "intent_return":
            return self.handle_request("return", user_id)
        elif callback_data == "intent_search":
            return self.handle_request("search", user_id)
        elif callback_data == "intent_loan":
            return self.handle_request("loanrecord", user_id)

        # Handle confirmation
        elif callback_data == "confirm_yes":
            info = self.user_state.get(user_id, {})
            matric = info.get("matric")
            email = info.get("email")

            is_valid, result = validate_student_info(matric, email)

            if is_valid:
                self.user_state[user_id]["stage"] = "authenticated"
                return {
                    "type": "text",
                    "text": f"✅ Authentication successful for {result}.\nPlease take a photo of the QR code at the back of your book that you want to borrow, and upload the photo to this conversation, so that I can borrow this book for you."
                }
            else:
                # Return failure and restart intent
                # Keep user in auth flow
                self.user_state[user_id] = {
                    "matric": matric,
                    "email": email,
                    "stage": "auth_pending"
                }
                return {
                    "type": "text",
                    "text": f"❌ Authentication failed: {result}. \nPlease enter valid matriculation number (e.g. A0012345U) and email address (e.g. john_soh@u.edu.sg) for authentication. "
                }   
        elif callback_data == "confirm_no":
            self.user_state.pop(user_id, None)
            # Restart borrow-authentication
            return self.handle_request("borrow", user_id)

        elif callback_data == "confirm_loan_yes":
            info = self.user_state.get(user_id, {})
            matric = info.get("matric")
            email = info.get("email")

            is_valid, result = validate_student_info(matric, email)

            if is_valid:
                self.user_state.pop(user_id, None)
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
                    lines.append(f"• {title} ({call})\n  Due: {due}\n  Returned: {returned or 'Not yet returned'}\n")

                return {
                    "type": "text",
                    "text": "\n".join(lines)
                }

            else:
                self.user_state[user_id] = {
                    "matric": matric,
                    "email": email,
                    "stage": "loan_auth_pending"
                }
                return {
                    "type": "text",
                    "text": f"❌ Authentication failed: {result}. Please enter valid details to view loan records."
                }

        elif callback_data == "confirm_loan_no":
            self.user_state.pop(user_id, None)
            return self.handle_request("loanrecord", user_id)



        # Fallback
        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }

    def handle_photo(self, file_path: str, user_id: str):
        # Decode QR from image path
        decoded = decode_qr(file_path)
        if not decoded:
            return {
                "type": "text",
                "text": "❌ Sorry, I couldn't read a QR code from that image. Please try again with a clearer photo."
            }

        print(f"[QR] Decoded value from image: {decoded}")
        is_valid, book_info = get_book_by_qr(decoded)

        if not is_valid:
            return {
                "type": "text",
                "text": f"❌ {book_info}"
            }

        # Check book status first
        if book_info.get("status") != "available":
            return {
                "type": "text",
                "text": f"⚠️ This book is currently not available for borrowing. Status: {book_info.get('status')}."
            }

        # Get authenticated user's matric
        student_info = self.user_state.get(user_id, {})
        matric = student_info.get("matric")
        if not matric:
            return {
                "type": "text",
                "text": "❌ You need to authenticate first. Please start again with the borrow command."
            }

        success, msg = borrow_book(copy_id=book_info["copy_id"], matric_number=matric)

        if success:
            return {
                "type": "text",
                "text": f"✅ Borrowing successful!\n📘 Title: {book_info.get('book_title')}\n🗓️ Due in 14 days."
            }
        else:
            return {
                "type": "text",
                "text": f"❌ Failed to borrow: {msg}"
            }
