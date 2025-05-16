from utils.qr_decoder import decode_qr
from utils.db_book_validator import get_book_by_qr
from utils.db_add_borrow import borrow_book

def handle_photo(file_path: str, user_id: str, user_state: dict):
    decoded = decode_qr(file_path)
    if not decoded:
        return {
            "type": "text",
            "text": "❌ Sorry, I couldn't read a QR code from that image. Please try again with a clearer photo."
        }

    print(f"[QR] Decoded value from image: {decoded}")
    is_valid, book_info = get_book_by_qr(decoded)

    if not is_valid:
        return {
            "type": "text",
            "text": f"❌ {book_info}"
        }

    if book_info.get("status") != "available":
        return {
            "type": "text",
            "text": f"⚠️ This book is currently not available for borrowing. Status: {book_info.get('status')}."
        }

    student_info = user_state.get(user_id, {})
    matric = student_info.get("matric")
    if not matric:
        return {
            "type": "text",
            "text": "❌ You need to authenticate first. Please start again with the borrow command."
        }

    success, msg = borrow_book(copy_id=book_info["copy_id"], matric_number=matric)

    if success:
        return {
            "type": "text",
            "text": f"✅ Borrowing successful!\n📘 Title: {book_info.get('book_title')}\n🗓️ Due in 14 days."
        }
    else:
        return {
            "type": "text",
            "text": f"❌ Failed to borrow: {msg}"
        }
