from ..dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from conversation_module.custom_handler.component_borrow import handle_borrow_auth, handle_confirm_borrow
from conversation_module.custom_handler.component_loanrecord import handle_loan_auth, handle_confirm_loan
from conversation_module.custom_handler.component_common import show_welcome
from conversation_module.custom_handler.component_photo import handle_photo as handle_photo_component


class CustomHandler:
    def __init__(self):
        self.dialogflow = DialogflowHandler()
        self.user_state = {}

    def handle_request(self, text: str, user_id: str):
        df_response = self.dialogflow.raw_detect_intent(text, user_id)
        intent = df_response["intent"]
        params = df_response["parameters"]
        fulfillment = df_response["fulfillment_text"]
        print(f'intent: {intent}')
        print(f'params: {params}')
        print(f'fulfillment: {fulfillment}')

        if self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"

        if intent == "Default Fallback Intent" and self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"

        if intent == "Default Welcome Intent":
            return show_welcome()

        if intent == "borrow - authentication":
            return handle_borrow_auth(user_id, params, self.user_state)

        if intent == "loanrecord - authentication":
            return handle_loan_auth(user_id, params, self.user_state)

        return {
            "type": "text",
            "text": fulfillment or "Sorry, I didn't understand that."
        }

    def handle_callback(self, callback_data: str, user_id: str):
        print(f"[DEBUG] handle_callback triggered with {callback_data}")
        if callback_data == "intent_borrow":
            return self.handle_request("borrow", user_id)
        elif callback_data == "intent_loan":
            return self.handle_request("loanrecord", user_id)

        if callback_data == "confirm_yes":
            return handle_confirm_borrow(user_id, self.user_state)
        elif callback_data == "confirm_no":
            self.user_state.pop(user_id, None)
            return self.handle_request("borrow", user_id)

        if callback_data == "confirm_loan_yes":
            return handle_confirm_loan(user_id, self.user_state)
        elif callback_data == "confirm_loan_no":
            self.user_state.pop(user_id, None)
            return self.handle_request("loanrecord", user_id)

        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }
    
    def handle_photo(self, file_path: str, user_id: str):
        return handle_photo_component(file_path, user_id, self.user_state)
