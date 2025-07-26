from telegram import InlineKeyboardButton

# Handler functions for each FAQ section
def handle_book_borrow_rules():
    content = (
        "📚 Hey there! Let’s talk about borrowing books! \n\n"
        "・You can borrow a book for up to 14 days—plenty of time to enjoy your read!\n\n"
        "・Want more time? You can extend it once per book for another 14 days. Click 'Loan Record' button to start the loan extension! \n\n"
        "・A quick heads-up: you can borrow up to 3 books at a time. If you’ve hit the limit, return one or two before grabbing a new one."
    )
    return {
        "type": "text",
        "text": content
    }

def handle_book_return_rules():
    content = (
        "🔁 Time to return your books? \n\n"
        "・Just pop them back on the corresponding bookshelf by the due date—easy peasy!  \n\n"
        "・Please click 'Return' button to start your book return flow."
    )
    return {
        "type": "text",
        "text": content
    }

def handle_overdue_rules():
    content = (
        "⚠️ Oops, running late? Here’s what happens:\n\n"
        "・ You will receive a friendly reminder 3 days before your due date right here on Telegram. If you’re overdue, I’ll check in every day to nudge you.\n\n"
        "・ If it’s been a week, our awesome library staff might give you a call and a small fine of $0.1 per day will kick in. Let’s avoid that, okay?"
    )
    return {
        "type": "text",
        "text": content
    }

def handle_lost_damage_rules():
    content = (
        "💰 Lost or damaged a book? No worries, just let us know!\n\n"
        "・ Report it to library staff right away, and we’ll sort it out.\n\n"
        "・ Please take note that you’ll need to cover the replacement cost, which will be the book’s current market price."
    )
    return {
        "type": "text",
        "text": content
    }

# Initial FAQ menu
def handle_faq():
    return {
        "type": "confirm",
        "text": (
            f"What would you like to learn more about? (Updated: {get_current_date_time_str()})"
        ),
        "buttons": [
            [InlineKeyboardButton("📚 Book Borrow Rules", callback_data="book_borrow_rules")],
            [InlineKeyboardButton("🔁 Book Return Rules", callback_data="book_return_rules")],
            [InlineKeyboardButton("⚠️ Overdue Policies & Fines", callback_data="overdue_rules")],
            [InlineKeyboardButton("💰 Lost & Damaged Book", callback_data="lost_damage_rules")]
        ]
    }

# Helper function to get current date and time
def get_current_date_time_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")