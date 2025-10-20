# conversation_module/custom_handler/component_loanrecord.py

from telegram import InlineKeyboardButton
from utils.db_loan_history import get_loan_history_by_student
from utils.auth_helpers import authenticated_users
from datetime import datetime, timedelta
from utils.date_parser import pretty_date

def handle_loan_request(user_id: str):
    student_info = authenticated_users.get(user_id)

    if not student_info:
        return {
            "type": "text",
            "text": "❌ You are not authenticated. Please reconnect to continue."
        }
    
    print(f"[DEBUG] student info in handle_loan_request: {student_info}\n\n")

    name = student_info.get("full_name")
    matric = student_info.get("matric_number")
    lines = []

    # Fetch all active loans once (needed for both purposes)
    success_active, active_loans = get_loan_history_by_student(matric, active_only=True, limit=25)
    if not success_active:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch active loans: {active_loans}"
        }

    active_loans.sort(key=lambda r: r.get("borrow_id", 0), reverse=True)
    print(f"sorted active_loans: {active_loans}\n\n")

    # Display active loan
    if active_loans:
        overdue = [r for r in active_loans if r.get("is_overdue")]
        current = [r for r in active_loans if not r.get("is_overdue")]

        lines = [f"{name} ({matric})'s 📌 Active Loans:"]
        if overdue:
            lines.append("\n⚠️ Overdue Books:")
            for r in overdue:
                lines.append(_format_loan_record(r))

        if current:
            lines.append("\n✅ Currently Borrowed:")
            for r in current:
                lines.append(_format_loan_record(r))

        # messages.append({"type": "text", "text": "\n".join(lines)})
    else:
        lines = [f"📭 No active loans found for {matric}."]
        #messages.append({"type": "text", "text": f"📭 No active loans found for {matric}."})

    lines.append("Would you like to view your past loan records?")

    buttons = [
        [InlineKeyboardButton("✅ Yes", callback_data="loanrecord_past_yes")],
        [InlineKeyboardButton("❌ No", callback_data="loanrecord_past_no")]
    ]
    print(f"final lines: {lines}\n\n")

    return {
        "type": "buttons",
        "text": "\n".join(lines),
        "buttons": buttons
    }

def handle_loan_response(user_id: str, choice: str):
    student_info = authenticated_users.get(user_id)
    if not student_info:
        return {
            "type": "text",
            "text": "❌ You are not authenticated. Please reconnect to continue."
        }

    name = student_info.get("full_name")
    matric = student_info.get("matric_number")
    lines = []

    success_active, active_loans = get_loan_history_by_student(matric, active_only=True, limit=25)
    if not success_active:
        active_loans = []

    if choice == "past":
        max_history_record = 31 #47 is the max tested on a short book title "The Great Gatsby"
        success_past, past_loans = get_loan_history_by_student(matric, active_only=False, limit=max_history_record)
        if not success_past:
            return {
                "type": "text",
                "text": f"❌ Failed to fetch past loans: {past_loans}"
            }

        past_loans.sort(key=lambda r: r.get("borrow_id", 0), reverse=True)
        recent_cutoff = datetime.utcnow() - timedelta(days=180)
        past_recent = []

        for r in past_loans:
            return_str = r.get("return_date")
            if return_str:
                try:
                    returned_dt = datetime.fromisoformat(return_str.replace("Z", ""))
                    if returned_dt > recent_cutoff:
                        past_recent.append(r)
                except Exception as e:
                    print(f"[ERROR] Failed to parse return_date {return_str}: {e}")
                    continue

        if past_recent:
            lines = [f"{name} ({matric})'s 📚 Past Loans (last 6 months, max {max_history_record-1} books):"]
            for r in past_recent:
                lines.append(_format_loan_record(r))
            # messages.append({"type": "text", "text": "\n".join(lines)})
        else:
            # messages.append({"type": "text", "text": "📭 No recent past loans found."})
            lines = ["📭 No recent past loans found."]

    # === Extend Option if eligible ===
    extendable_loans = [r for r in active_loans if not r.get("is_overdue")]

    if extendable_loans:
        buttons = [
            [InlineKeyboardButton("✅ Yes", callback_data="loanrecord_extend_yes")],
            [InlineKeyboardButton("❌ No", callback_data="loanrecord_extend_no")]
        ]
        lines.append("Would you like to extend any of your current eligible books?")
        return {
            "type": "buttons",
            "text": "\n".join(lines),
            "buttons": buttons
        }
    elif not extendable_loans:
        lines.append("Use Menu to continue accessing library services.")
        return {
            "type": "text",
            "text": "\n".join(lines)
        }

    # return messages


def _format_loan_record(record):
    title = record.get("book_title", "Unknown Title")
    borrow_date = pretty_date(record.get("borrow_date", ""))
    due_date = pretty_date(record.get("due_date", ""))
    return_date = pretty_date(record.get("return_date")) if record.get("return_date") else "Not yet returned"
    overdue_note = "⚠️ Overdue" if record.get("is_overdue") else ""

    return (
        f"• {title} {overdue_note}\n"
        f"  Borrowed: {borrow_date}\n"
        f"  Due: {due_date}\n"
        f"  Returned: {return_date or 'Not yet returned'}\n"
    )
