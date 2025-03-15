# telegram_module/telegram_bot.py
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from conversation_module import get_conversation_handler  # Import the factory function

# Read environment variables
TOKEN: Final = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("Please set the TELEGRAM_TOKEN environment variable.")

BOT_USERNAME: Final = '@TembusuLib_bot'

# Initialize ConversationHandler based on service provider
def start_bot(service_provider: str):
    conversation_handler = get_conversation_handler(service_provider)  # Use factory function

    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! Welcome to Tembusu Reading Room.")

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please type something so I can respond =)")

    async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("This is a custom command!")

    # Handle messages
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type: str = update.message.chat.type
        text: str = update.message.text
        user_id: str = str(update.message.chat.id)

        print(f'User ({user_id}) in {message_type}: "{text}"')

        if message_type == 'group':
            if BOT_USERNAME in text:
                new_text: str = text.replace(BOT_USERNAME, '').strip()
                response: str = conversation_handler.handle_request(new_text, user_id)
            else: 
                return
        else:
            response: str = conversation_handler.handle_request(text, user_id)
        
        print('Bot:', response)
        await update.message.reply_text(response)

    # Error handler
    async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} cause error {context.error}')

    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)