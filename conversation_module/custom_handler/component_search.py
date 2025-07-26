from telegram import InlineKeyboardButton
from utils.db_search_book import get_book_by_title, get_book_by_author

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

def handle_search_book_title(params):
    booktitle = params.get("BookTitle")
    
    # Convert RepeatedComposite to string by taking the first element
    if booktitle and len(booktitle) > 0:
        booktitle_str = str(booktitle[0])  # Access the first element and convert to string
    else:
        booktitle_str = "Unknown Title"  # Fallback if no title is available

    print("Converted booktitle:", booktitle_str)

    success, records_or_msg = get_book_by_title(booktitle_str)
    print('records_or_msg:',records_or_msg)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch book availability information: {records_or_msg}"
        }

    if not records_or_msg:
        return {
            "type": "text",
            "text": f"📚 Tembusu Library does not have book: {booktitle_str}."
        }

    lines = [f"📚 Book Availability"]
    for record in records_or_msg:
        title = record.get("title", "Unknown Title")
        call_number = record.get("call_number", "Unknown Call Number")
        available_copies = record.get("available_copies", "N/A")
        lines.append(
            f"•Book Title: {title} \n  Call Number:{call_number}\n  Available Copies: {available_copies}\n  Location: \n "
        )

    lines.append("Please find the book on the bookshelf using the location information and call number. \nTo borrow this book, just type 'borrow' to start the process.")
    
    return {
        "type": "text",
        "text": "\n".join(lines)
    }


def handle_search_book_author(params):
    authorname = params.get("AuthorName")    

    success, records_or_msg = get_book_by_author(authorname)
    print('records_or_msg:',records_or_msg)

    if not success:
        return {
            "type": "text",
            "text": f"❌ Failed to author information: {records_or_msg}"
        }

    if not records_or_msg:
        return {
            "type": "text",
            "text": f"📚 Tembusu Library does not have any book by author: {authorname}."
        }

    lines = [f"📚 Book Availability by Author {authorname}"]

    for record in records_or_msg:
        title = record.get("title", "Unknown Title")
        call_number = record.get("call_number", "Unknown Call Number")
        available_copies = record.get("available_copies", "N/A")
        lines.append(
            f"•Book Title: {title} \n  Call Number:{call_number}\n  Available Copies: {available_copies}\n  Location: \n "
        )

    lines.append("Please find the book on the bookshelf using the location information and call number. \nTo borrow this book, just type 'borrow' to start the process.")
    
    return {
        "type": "text",
        "text": "\n".join(lines)
    }