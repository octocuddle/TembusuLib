from ..dialogflow_handler import DialogflowHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from conversation_module.custom_handler.component_borrow import handle_borrow_auth, handle_confirm_borrow
from conversation_module.custom_handler.component_loanrecord import handle_loan_auth, handle_confirm_loan
from conversation_module.custom_handler.component_search import handle_search_book,handle_search_book_title, handle_search_book_author
from conversation_module.custom_handler.component_faq import handle_faq, handle_book_borrow_rules, handle_book_return_rules, handle_overdue_rules, handle_lost_damage_rules
from conversation_module.custom_handler.component_common import show_welcome
from conversation_module.custom_handler.component_photo import handle_photo as handle_photo_component


class CustomHandler:
    def __init__(self):
        self.dialogflow = DialogflowHandler()
        self.user_state = {}

    def handle_request(self, text: str, user_id: str):
        # Initialize user state if not present
        self.user_state[user_id] = self.user_state.get(user_id, {})
        
        # Check if awaiting input
        if self.user_state[user_id].get("awaiting_input"):
            search_mode = self.user_state[user_id].get("search_mode")
            if search_mode == "title":
                self.user_state[user_id]["awaiting_input"] = False
                return handle_search_book_title(text, user_id, self.user_state)
            elif search_mode == "author":
                self.user_state[user_id]["awaiting_input"] = False
                return handle_search_book_author(text, user_id, self.user_state)

        # Proceed with Dialogflow intent detection
        df_response = self.dialogflow.raw_detect_intent(text, user_id)
        intent = df_response["intent"]
        params = df_response["parameters"]
        fulfillment = df_response["fulfillment_text"]
        output_contexts = df_response["output_contexts"]
        print("output_contexts",output_contexts)
        output_params = output_contexts[0].parameters
        print("output_params",output_params)

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
        
        if intent == "searchbook":
            return handle_search_book()

        if intent == "searchbook - title - confirm":
            return handle_search_book_title(output_params, user_id, self.user_state)
        
        if intent == "searchbook - author - confirm":
            return handle_search_book_author(output_params, user_id, self.user_state)

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
        elif callback_data == "intent_search":
            return self.handle_request("search", user_id)

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
        
        if callback_data == "search_book_title":
            self.user_state[user_id] = self.user_state.get(user_id, {})
            self.user_state[user_id]["awaiting_input"] = True
            self.user_state[user_id]["search_mode"] = "title"
            return {
                "type": "text",
                "text": "Got! Please type the book title you’d like to search for. 😊"
            }
        elif callback_data == "search_book_author":
            self.user_state[user_id] = self.user_state.get(user_id, {})
            self.user_state[user_id]["awaiting_input"] = True
            self.user_state[user_id]["search_mode"] = "author"
            return {
                "type": "text",
                "text": "Got it! Please type the author name you’d like to search for. 😊"
            }
        
        if callback_data == "intent_faq":
            return handle_faq()
        elif callback_data == "book_borrow_rules":
            return handle_book_borrow_rules()
        elif callback_data == "book_return_rules":
            return handle_book_return_rules()
        elif callback_data == "overdue_rules":
            return handle_overdue_rules()
        elif callback_data == "lost_damage_rules":
            return handle_lost_damage_rules()
        
        return {
            "type": "text",
            "text": "Sorry, I didn't understand that button action."
        }
    
    def handle_photo(self, file_path: str, user_id: str):
        return handle_photo_component(file_path, user_id, self.user_state)
'''

'''
