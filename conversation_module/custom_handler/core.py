# conversation_module/custom_handler/core.py

from ..dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from conversation_module.custom_handler.component_borrow import (
    start_borrow_flow,
    handle_borrow_photo,
    handle_confirm_borrow,
    handle_cancel_borrow,
    expired_confirm_borrow_keyboard
)
from conversation_module.custom_handler.component_return import (
    start_return_flow,
    handle_return_book_photo,
    handle_return_location_photo,
    handle_return_proxy_decision
)
from conversation_module.custom_handler.component_loanrecord import handle_loan_request, handle_loan_response
from conversation_module.custom_handler.component_extendloan import handle_extend_request
from conversation_module.custom_handler.component_common import show_welcome, expired_welcome_keyboard
from conversation_module.custom_handler.component_search import handle_search_book,handle_search_book_title, handle_search_book_author


class CustomHandler:
    def __init__(self):
        self.dialogflow = DialogflowHandler()
        self.user_state = {}

    async def handle_request(self, text: str, user_id: str):
        df_response = self.dialogflow.raw_detect_intent(text, user_id)
        intent = df_response["intent"]
        params = df_response["parameters"]
        fulfillment = df_response["fulfillment_text"]
        print(f'intent: {intent}')
        print(f'params: {params}')
        print(f'fulfillment: {fulfillment}\n')

        output_contexts = df_response["output_contexts"]
        print("output_contexts (from dialogflow)",output_contexts)
        output_params = {}
        if intent in ("searchbook - title - confirm", "searchbook - author - confirm") and output_contexts:
            output_params = output_contexts[0].parameters

        if intent == "Default Welcome Intent":
            return show_welcome()

        elif intent == "borrow":
            return start_borrow_flow(user_id, self.user_state, fulfillment)
        
        elif intent == "return":
            return start_return_flow(user_id, self.user_state, fulfillment)

        elif intent == "loanrecord":
            return handle_loan_request(user_id)
        
        elif intent == "extendloan":
            return await handle_extend_request(user_id)
        
        elif intent == "searchbook":
            return handle_search_book()

        elif intent == "searchbook - title - confirm":
            return handle_search_book_title(output_params)
        
        elif intent == "searchbook - author - confirm":
            return handle_search_book_author(output_params)

        return {
            "type": "text",
            "text": fulfillment or "Sorry, I didn't understand that."
        }

    async def handle_callback(self, query, user_id: str):
        callback_data = query.data
        print(f"[DEBUG] handle_callback triggered with {callback_data}")

        await query.answer()

        # Immediately expire welcome menu buttons
        if callback_data.startswith("intent_"):
            await query.edit_message_reply_markup(reply_markup=expired_welcome_keyboard())
        elif callback_data.startswith(("confirm_borrow_", "return_proxy_", "loanrecord_extend_", "loanrecord_past_")):
            await query.edit_message_reply_markup(reply_markup=expired_confirm_borrow_keyboard())


        if callback_data == "intent_borrow":
            return await self.handle_request("borrow", user_id)
        
        elif callback_data == "intent_return":
            return await self.handle_request("return", user_id)

        elif callback_data == "intent_loan":
            return await self.handle_request("loanrecord", user_id)
        
        elif callback_data == "intent_extendloan":
            return await self.handle_request("extendloan", user_id)
        
        elif callback_data.startswith("extend_borrow_id_"):
            borrow_id = int(callback_data.split("_")[-1])
            # Remove keyboard immediately
            await query.edit_message_reply_markup(reply_markup=None)
            return await handle_extend_request(user_id, borrow_id)
        
        elif callback_data == "intent_search":
            return await self.handle_request("search", user_id)
        
        elif callback_data == "return_proxy_yes":
            return handle_return_proxy_decision(user_id, self.user_state, "yes")
        elif callback_data == "return_proxy_no":
            return handle_return_proxy_decision(user_id, self.user_state, "no")

        elif callback_data == "confirm_borrow_yes":
            return handle_confirm_borrow(user_id, self.user_state)
        elif callback_data == "confirm_borrow_no":
            return handle_cancel_borrow(user_id, self.user_state)


        elif callback_data == "loanrecord_past_no":
            return handle_loan_response(user_id, choice="")
        elif callback_data == "loanrecord_past_yes":
            return handle_loan_response(user_id, choice="past")
        elif callback_data == "loanrecord_extend_yes":
            return await handle_extend_request(user_id)
        elif callback_data == "loanrecord_extend_no":
            return {
                "type": "text",
                "text": "👌 Use Menu to continue accessing library services. \nHave a nice day."
            }
        
        elif callback_data == "search_book_title":
            return await self.handle_request("search book via book title", user_id)
        elif callback_data == "search_book_author":
            return await self.handle_request("search book via book author", user_id)
        
        # Ignore expired button taps
        elif callback_data == "expired_disabled":
            return {
                "type": "text",
                "text": "❌ This menu has already been used. Please use /start or main menu to continue."
            }

        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }
    
    def handle_photo(self, file_path: str, user_id: str):
        stage = self.user_state.get(user_id, {}).get("stage")
        print(f"[PHOTO HANDLER] user_id={user_id}, stage={stage}")
        
        if stage == "borrow_waiting_qr":
            return handle_borrow_photo(file_path, user_id, self.user_state)
        
        elif stage == "return_waiting_book_qr":
            return handle_return_book_photo(file_path, user_id, self.user_state)
        elif stage == "return_waiting_location_qr":
            return handle_return_location_photo(file_path, user_id, self.user_state)

        return {
            "type": "text",
            "text": "⚠️ I wasn't expecting a photo. Please use the menu to begin."
        }
