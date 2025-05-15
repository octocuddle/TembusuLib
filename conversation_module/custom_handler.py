# conversation_module/custom_handler.py
from .dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
                [InlineKeyboardButton("📖 History", callback_data="intent_history")]
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
                "email": params["emailAdd"]
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
        elif callback_data == "intent_history":
            return self.handle_request("history", user_id)

        # Handle confirmation
        elif callback_data == "confirm_yes":
            info = self.user_state.get(user_id, {})
            # Later: validate with backend
            return {
                "type": "text",
                "text": "Thank you! Validating your information now..."
            }
        elif callback_data == "confirm_no":
            self.user_state.pop(user_id, None)
            return {
                "type": "text",
                "text": "Okay, let's start over. Please enter your matric number."
            }

        # Fallback
        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }
