# conversation_module/__init__.py
from .lex_handler import LexHandler
#from .dialogflow_handler import DialogflowHandler

def get_conversation_handler(service_provider: str):
    """
    Factory function to return the appropriate chatbot service based on the provider.
    """
    if service_provider == "lex":
        return LexHandler()
    elif service_provider == "dialogflow":
        #    return DialogflowHandler()
        pass
    elif service_provider == "custom":
        # Return a custom handler if implemented
        pass
    else:
        raise ValueError(f"Unsupported service provider: {service_provider}")