# conversation_module/dialogflow_handler.py
from google.cloud import dialogflow_v2 as dialogflow
import os

class DialogflowHandler:
    def __init__(self):
        self.project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
        self.language_code = "en"
        self.session_client = dialogflow.SessionsClient()

    def handle_request(self, text: str, user_id: str) -> str:
        session = self.session_client.session_path(self.project_id, user_id)
        text_input = dialogflow.TextInput(text=text, language_code=self.language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        try:
            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )
            result = response.query_result
            return result.fulfillment_text or "No response from Dialogflow."
        except Exception as e:
            print(f"Dialogflow error: {e}")
            return "Oops! Something went wrong on my end. Please try your request again, or contact our @LibraryAdmin on Telegram if you need immediate help."

    def raw_detect_intent(self, text: str, user_id: str) -> dict:
        session = self.session_client.session_path(self.project_id, user_id)
        text_input = dialogflow.TextInput(text=text, language_code=self.language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        try:
            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )
            result = response.query_result

            return {
                "intent": result.intent.display_name,
                "parameters": dict(result.parameters),
                "fulfillment_text": result.fulfillment_text,
                "output_contexts": result.output_contexts,
                "confidence": result.intent_detection_confidence
            }

        except Exception as e:
            print(f"Dialogflow error: {e}")
            return {
                "intent": None,
                "parameters": {},
                "fulfillment_text": "Oops! Something went wrong on my end. Please try your request again, or contact our @LibraryAdmin on Telegram if you need immediate help.",
                "confidence": 0
            }
