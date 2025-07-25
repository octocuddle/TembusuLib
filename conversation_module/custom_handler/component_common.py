from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def show_welcome():
    welcome_message = (
        "Welcome to Tembusu Library! I’m your assistant.\n\n"
        "What would you like to do today?"
    )
    keyboard = [
        [InlineKeyboardButton("📚 Borrow", callback_data="intent_borrow")],
        [InlineKeyboardButton("🔁 Return", callback_data="intent_return")],
        [InlineKeyboardButton("🔍 Search", callback_data="intent_search")],
        [InlineKeyboardButton("📖 Loan Record", callback_data="intent_loan")],
        [InlineKeyboardButton("🏫 Library Rules FAQ", callback_data="intent_faq")]
    ]
    return {
        "type": "buttons",
        "text": welcome_message,
        "buttons": keyboard
    }
