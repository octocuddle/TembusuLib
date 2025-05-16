# telegram_module/telegram_bot.py
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardMarkup
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
        message = update.message
        user = message.from_user
        user_id = str(user.id)
        username = user.username or user.first_name or "Unknown"

        if message.photo:
            print(f"[PHOTO] From @{username} (ID: {user_id}) - Received image")

            file = await message.photo[-1].get_file()
            file_path = await file.download_to_drive()
            print(f"[PHOTO] From @{username} (ID: {user_id}) → File saved to: {file_path}")
            response = conversation_handler.handle_photo(file_path, user_id)

        else:
            text = message.text
            print(f'[TEXT] From @{username} (ID: {user_id}): "{text}"')
            response = conversation_handler.handle_request(text, user_id)

        # Handle response
        if isinstance(response, str):
            await message.reply_text(response)
            print(f'[BOT → @{username}] Sent text: {response}')
            return

        if response["type"] == "text":
            await message.reply_text(response["text"])
            print(f'[BOT → @{username}] Sent text: {response["text"]}')
        elif response["type"] in ("buttons", "confirm"):
            reply_markup = InlineKeyboardMarkup(response["buttons"])
            await message.reply_text(response["text"], reply_markup=reply_markup)
            print(f'[BOT → @{username}] Sent message with buttons: {response["text"]}')


    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
        data = query.data

        response = conversation_handler.handle_callback(data, user_id)
        print(f'[CALLBACK] From @{query.from_user.username or query.from_user.first_name} (ID: {user_id}) clicked: {data}')

        if isinstance(response, str):
            await query.message.reply_text(response)
        elif response["type"] == "text":
            await query.message.reply_text(response["text"])
        elif response["type"] in ("buttons", "confirm"):
            reply_markup = InlineKeyboardMarkup(response["buttons"])
            await query.message.reply_text(response["text"], reply_markup=reply_markup)



    # Error handler
    async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} cause error {context.error}')

    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)