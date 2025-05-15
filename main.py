# main.py
from telegram_bot import start_bot

if __name__ == '__main__':
    # Choose the chatbot service provider
    service_provider = "custom"  # Switch to "lex", "dialogflow" or "custom" as needed

    # Start the bot with the chosen service provider
    start_bot(service_provider)
