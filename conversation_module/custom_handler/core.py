# conversation_module/custom_handler/core.py

from ..dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from conversation_module.custom_handler.component_borrow import (
    start_borrow_flow,
    handle_borrow_photo,
    handle_confirm_borrow,
    handle_cancel_borrow
)
from conversation_module.custom_handler.component_loanrecord import handle_loan_request, handle_loan_response
from conversation_module.custom_handler.component_extendloan import handle_extend_request
from conversation_module.custom_handler.component_common import show_welcome


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

        '''if self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"

        if intent == "Default Fallback Intent" and self.user_state.get(user_id, {}).get("stage") == "auth_pending":
            intent = "borrow - authentication"'''

        if intent == "Default Welcome Intent":
            return show_welcome()

        if intent == "borrow":
            return start_borrow_flow(user_id, self.user_state, fulfillment)

        if intent == "loanrecord":
            return handle_loan_request(user_id)
        
        if intent == "extendloan":
            return handle_extend_request(user_id)

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
        
        elif callback_data == "intent_extendloan":
            return self.handle_request("extendloan", user_id)
        
        elif callback_data.startswith("extend_borrow_id_"):
            borrow_id = int(callback_data.split("_")[-1])
            return handle_extend_request(user_id, borrow_id)

        if callback_data == "confirm_borrow_yes":
            return handle_confirm_borrow(user_id, self.user_state)
        elif callback_data == "confirm_borrow_no":
            return handle_cancel_borrow(user_id, self.user_state)


        if callback_data == "loanrecord_view_active":
            return handle_loan_response(user_id, choice="active")
        elif callback_data == "loanrecord_view_past":
            return handle_loan_response(user_id, choice="past")
        elif callback_data == "loanrecord_extend_yes":
            return handle_extend_request(user_id)
        elif callback_data == "loanrecord_extend_no":
            return {
                "type": "text",
                "text": "👌 Use Menu to continue accessing library services. \nHave a nice day."
            }

        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }
    
    def handle_photo(self, file_path: str, user_id: str):
        stage = self.user_state.get(user_id, {}).get("stage")

        if stage == "borrow_waiting_qr":
            return handle_borrow_photo(file_path, user_id, self.user_state)

        return {
            "type": "text",
            "text": "⚠️ I wasn't expecting a photo. Please use the menu to begin."
        }
