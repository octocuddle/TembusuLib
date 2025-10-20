# conversation_module/custom_handler/component_extendloan.py

from telegram import InlineKeyboardButton
from utils.db_loan_history import get_loan_history_by_student
from utils.auth_helpers import authenticated_users
from utils.db_extend_loan import extend_loan
from utils.date_parser import pretty_date
from utils.semester_calendar import get_period, get_days_until_period_end, get_next_semester_start
from datetime import date, datetime


async def handle_extend_request(user_id, user_state: dict, borrow_id=None):
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
        today = date.today()
        period = get_period(today)

        if not period or "Holiday" in period["name"]:
            next_mmdd = get_next_semester_start(today)
            next_start_str = datetime.strptime(next_mmdd, "%m-%d").strftime("%-d %B") if next_mmdd else "next semester"
            return {
                "type": "text",
                "text": (
                    "📚 The library is currently closed for maintenance during the holiday.\n"
                    "Loan extensions are not allowed during this period.\n"
                    f"Please visit us again next semester, starting from {next_start_str}."
                )
            }

        success, active_loans = get_loan_history_by_student(matric, active_only=True, limit=25)
        if not success:
            return {
                "type": "text",
                "text": f"❌ Could not fetch active loans: {active_loans}"
            }

        if not active_loans:
            return {
                "type": "text",
                "text": f"📭 No active loan to extend for {matric}.\n\nUse Menu to access library services."
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

        # Store extendable loan records for later use in extension
        user_state[user_id] = user_state.get(user_id, {})
        user_state[user_id]["extendable_loans"] = extendable_loans

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
    today = date.today()
    period = get_period(today)

    remaining_days, sem_end = get_days_until_period_end(today)
    print(f"remaining_days: {remaining_days}")

    # Get the specific loan info from stored list
    loan_list = user_state.get(user_id, {}).get("extendable_loans", [])
    loan = next((r for r in loan_list if r.get("borrow_id") == borrow_id), None)

    if not loan:
        return {
            "type": "text",
            "text": "⚠️ Could not find the loan record for extension. Please start again."
        }

    current_due_date = datetime.strptime(loan["due_date"][:10], "%Y-%m-%d").date()
    delta_days = (sem_end - current_due_date).days
    print(f"Current due: {current_due_date}, Sem end: {sem_end}, Delta: {delta_days}")

    if delta_days <= 0:
        next_mmdd = get_next_semester_start(today)
        next_start_str = datetime.strptime(next_mmdd, "%m-%d").strftime("%-d %B") if next_mmdd else "next semester"
        return {
            "type": "text",
            "text": (
                f"📅 Your current due date is already at or beyond the semester end ({sem_end}).\n"
                f"Loan extension is not possible.\n\n"
                f"Please return your book before semester end and visit us again next semester, starting from {next_start_str}."
            )
        }

    extension_days = min(14, delta_days)
    print(f"extension_days: {extension_days}")

    success, result = extend_loan(borrow_id, days=extension_days)
    
    user_state.pop(user_id, None)
    
    if success:
        book = result.get("book_title")
        new_due = pretty_date(result.get("due_date"))
        return {
            "type": "text",
            "text": (
                f"✅ Successfully extended\n📖 {book}.\n"
                f"📅 New due date: {new_due}\n" +
                (f"\n⚠️ This book is extended for {extension_days} days only as semester is ending. Please return it before semester end." if extension_days < 14 else "")
            )
        }
    else:
        return {
            "type": "text",
            "text": f"❌ Extension failed:\n{result}\n\nUse Menu to continue accessing library services."
        }