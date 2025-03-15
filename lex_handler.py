# conversation_module/lex_handler.py
import boto3
import os

class LexHandler:
    def __init__(self):
        self.lex_client = boto3.client('lexv2-runtime', region_name=os.getenv('AWS_DEFAULT_REGION'))

    def handle_request(self, text: str, user_id: str) -> str:
        try:
            response = self.lex_client.recognize_text(
                botId=os.getenv('LEX_BOT_ID'),
                botAliasId=os.getenv('LEX_BOT_ALIAS_ID'),
                localeId='en_US',
                sessionId=user_id,
                text=text
            )

            messages = response.get("messages", [])
            if not messages:
                return "No response from bot."

            return "\n".join([msg["content"] for msg in messages])

        except Exception as e:
            print(f"Error communicating with AWS Lex: {e}")
            return "I encountered an error while processing your request."