# conversation_module/__init__.py
from .lex_handler import LexHandler
from .dialogflow_handler import DialogflowHandler
from .custom_handler import CustomHandler 

def get_conversation_handler(service_provider: str):
    """
    Factory function to return the appropriate chatbot service based on the provider.
    """
    if service_provider == "lex":
        return LexHandler()
    elif service_provider == "dialogflow":
        return DialogflowHandler()
    elif service_provider == "custom":
        return CustomHandler()
    else:
        raise ValueError(f"Unsupported service provider: {service_provider}")