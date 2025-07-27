# conversation_module/custom_handler/component_common.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def show_welcome():
    welcome_message = (
        "Welcome to Tembusu Library! I’m your assistant.\n\n"
        "What would you like to do today?"
    )
    keyboard = [
        [InlineKeyboardButton("📚 Borrow", callback_data="intent_borrow")],
        [InlineKeyboardButton("⏪️ Return", callback_data="intent_return")],
        [InlineKeyboardButton("⏳ Extend Loan", callback_data="intent_extendloan")],
        [InlineKeyboardButton("📖 Loan Record", callback_data="intent_loan")],
        [InlineKeyboardButton("🔍 Search Books", callback_data="intent_search")],
        [InlineKeyboardButton("🏫 Library Rules FAQ", callback_data="intent_faq")]
    ]
    return {
        "type": "buttons",
        "text": welcome_message,
        "buttons": keyboard
    }

def expired_welcome_keyboard():
    expired_keyboard = [
        [InlineKeyboardButton("📚 Borrow", callback_data="expired_disabled")],
        [InlineKeyboardButton("⏪️ Return", callback_data="expired_disabled")],
        [InlineKeyboardButton("⏳ Extend Loan", callback_data="expired_disabled")],
        [InlineKeyboardButton("📖 Loan Record", callback_data="expired_disabled")],
        [InlineKeyboardButton("🔍 Search Books", callback_data="expired_disabled")],
        [InlineKeyboardButton("🏫 Library Rules FAQ", callback_data="expired_disabled")]
    ]
    return InlineKeyboardMarkup(expired_keyboard)
