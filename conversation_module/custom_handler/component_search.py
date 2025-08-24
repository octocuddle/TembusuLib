from telegram import InlineKeyboardButton
from utils.db_search_book import get_book_by_title, get_book_by_author, get_book_copy_details

def handle_search_book():
   
        return {
            "type": "confirm",
            "text": (
                f"Do you want to search by book title or book author?"
            ),
            "buttons": [
                [InlineKeyboardButton("📖 Book Title", callback_data="search_book_title")],
                [InlineKeyboardButton("👤 Book Author", callback_data="search_book_author")]
            ]
        }

def handle_search_book_title(params, user_id=None, user_state=None):
    if user_state is None or user_id is None:
        return {
            "type": "text",
            "text": "Oops! Something went wrong. Please try searching again. 😅"
        }

    # Check if awaiting input from user state
    if user_state.get(user_id, {}).get("awaiting_input"):
        booktitle = params  # Use the typed text as the book title
        user_state[user_id]["awaiting_input"] = False
    elif isinstance(params, str):
        booktitle = [params]  # Convert string to list for consistency
    else:
        booktitle = params.get("BookTitle", ["Unknown Title"])  # Fallback if no title
    
    # Check book availability 
    if booktitle and len(booktitle) > 0:
        booktitle_str = str(booktitle[0])  # Access the first element and convert to string
    else:
        booktitle_str = "Unknown Title"  # Fallback if no title is available

    success, book_info = get_book_by_title(booktitle_str)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch book availability information: {book_info}"
        }

    if not book_info:
        return {
            "type": "text",
            "text": f"📚 Tembusu Library does not have book: {booktitle_str}."
        }

    print("This book is available:", booktitle_str)

    # Show final availability details
    lines = [f"📚 Book Availability\n"]
    for record in book_info:
        title = record.get("title", "Unknown Title")
        call_number = record.get("call_number", "Unknown Call Number")
        available_copies = record.get("available_copies", "N/A")
        
        # Get location details for the current book title
        location_success, location_data = get_book_copy_details(title)
        locations = []
        if location_success and location_data:
            locations = [item['location_name'] for item in location_data]

        lines.append(
            f"•Book Title: {title} \n  Call Number:{call_number}\n  Available Copies: {available_copies}\n  Location: {', '.join(locations) if locations else 'Not available'}\n"
        )

        if available_copies == 0:
            lines.append("Sorry, the searched book has been borrowed by another student. Please come try again next time! 😔")

    lines.append("For available books, you can find the book on the bookshelf using the location information and call number. \n\nTo borrow this book, just click 'borrow' button to start the process.")

    return {
        "type": "text",
        "text": "\n".join(lines)
    }
    


def handle_search_book_author(params, user_id=None, user_state=None):
    print("author params:",params)
    if user_state is None or user_id is None:
        return {
            "type": "text",
            "text": "Oops! Something went wrong. Please try searching again. 😅"
        }

    # Check if awaiting input from user state
    if user_state.get(user_id, {}).get("awaiting_input"):
        authorname = params  # Use the typed text as the author name
        user_state[user_id]["awaiting_input"] = False
    else:
        authorname = params.get("AuthorName", "Unknown Author") if hasattr(params, 'get') else params  # Handle both dict and str

    success, author_info = get_book_by_author(authorname)
    print('records_or_msg:', author_info)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Failed to author information: {author_info}"
        }

    if not author_info:
        return {
            "type": "text",
            "text": f"📚 Tembusu Library does not have any book by author: {authorname}."
        }

    lines = [f"📚 Book Availability by Author {authorname} \n"]

    for record in author_info:
        title = record.get("title", "Unknown Title")
        call_number = record.get("call_number", "Unknown Call Number")
        
        # Get book info for the current book title
        book_success, book_details = get_book_by_title(title)
        if book_success and book_details:
            available_copies = book_details[0].get("available_copies", "N/A")

         # Get location details for the current book title
        location_success, location_data = get_book_copy_details(title)
        locations = []
        if location_success and location_data:
            locations = [item['location_name'] for item in location_data]
        
        lines.append(
            f"•Book Title: {title} \n  Call Number:{call_number}\n  Available Copies: {available_copies}\n  Location: {', '.join(locations) if locations else 'Not available'}\n"
        )
        if available_copies == 0:
            lines.append("Sorry, the searched book has been borrowed by another student. Please come try again next time! 😔 \n")

    lines.append("For available books, you can find the book on the bookshelf using the location information and call number. \n\nTo borrow books, just click 'borrow' button to start the process.")

    return {
        "type": "text",
        "text": "\n".join(lines)
    }