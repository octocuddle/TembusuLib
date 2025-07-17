from telegram import InlineKeyboardButton
from utils.db_loan_history import get_loan_history
from utils.auth_helpers import authenticated_users
from utils.db_extend_loan import extend_loan
from utils.date_parser import pretty_date


def handle_extend_request(user_id, borrow_id=None):
    student_info = authenticated_users.get(user_id)

    if not student_info:
        return {
            "type": "text",
            "text": "❌ You are not authenticated. Please reconnect to continue."
        }

    matric = student_info.get("matric_number")
    name = student_info.get("full_name")

    # === Case 1: Initial view: show loans to choose ===
    if borrow_id is None:
        success, active_loans = get_loan_history(matric, active_only=True, limit=25)
        if not success:
            return {
                "type": "text",
                "text": f"❌ Could not fetch active loans: {active_loans}"
            }

        if not active_loans:
            return {
                "type": "text",
                "text": f"📭 No active loans to extend for {matric}."
            }

        overdue_loans = [r for r in active_loans if r.get("is_overdue")]
        extendable_loans = [r for r in active_loans if not r.get("is_overdue")]

        message_lines = [f"👤 {name} ({matric}), you have the following active loans:"]

        if overdue_loans:
            message_lines.append("\n❗ Overdue items (please return them as soon as possible):")
            for idx, r in enumerate(overdue_loans, 1):
                title = r.get("book_title", "Unknown Title")
                borrow_date = pretty_date(r.get("borrow_date", ""))
                due_date = pretty_date(r.get("due_date", ""))
                message_lines.append(
                    f"\n🔴 {idx}. {title}\n"
                    f"    Borrowed: {borrow_date}\n"
                    f"    Due: {due_date}"
                )

        if extendable_loans:
            message_lines.append("\n⏳ Books eligible for extension:")
            for idx, r in enumerate(extendable_loans, 1):
                title = r.get("book_title", "Unknown Title")
                borrow_date = pretty_date(r.get("borrow_date", ""))
                due_date = pretty_date(r.get("due_date", ""))
                message_lines.append(
                    f"\n📘 {idx}. {title}\n"
                    f"    Borrowed: {borrow_date}\n"
                    f"    Due: {due_date}"
                )
        else:
            message_lines.append("\n✅ No books are eligible for extension.")

        # Buttons only for extendable books
        buttons = [
            [InlineKeyboardButton(f"⏳ Extend: {r['book_title'][:30]}", callback_data=f"extend_borrow_id_{r['borrow_id']}")]
            for r in extendable_loans
        ]

        return {
            "type": "buttons" if buttons else "text",
            "text": "\n".join(message_lines),
            "buttons": buttons if buttons else None
        }

    # === Case 2: User clicked to extend a specific book ===
    success, result = extend_loan(borrow_id)

    if success:
        book = result.get("book_title")
        new_due = result.get("due_date")[:10]
        return {
            "type": "text",
            "text": f"✅ Successfully extended *{book}*.\nNew due date: *{new_due}*"
        }
    else:
        return {
            "type": "text",
            "text": f"❌ Extension failed:\n{result}"
        }
