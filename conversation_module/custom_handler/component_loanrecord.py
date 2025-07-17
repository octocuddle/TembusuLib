# conversation_module/custom_handler/component_loanrecord.py

from telegram import InlineKeyboardButton
from utils.db_loan_history import get_loan_history
from utils.auth_helpers import authenticated_users
from datetime import datetime, timedelta
from utils.date_parser import pretty_date

def handle_loan_request(user_id: str):
    student_info = authenticated_users.get(user_id)
    print("[DEBUG]", student_info)

    if not student_info:
        return {
            "type": "text",
            "text": "❌ You are not authenticated. Please reconnect to continue."
        }

    name = student_info.get("full_name")
    matric = student_info.get("matric_number")

    # Get active loans
    success_active, active_loans = get_loan_history(matric, active_only=True, limit=25)
    if not success_active:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch active loans: {active_loans}"
        }
    active_loans.sort(key=lambda r: r.get("borrow_id", 0), reverse=True)
    # print("active loans are:", active_loans)

    # Get past loans
    success_past, past_loans = get_loan_history(matric, active_only=False, limit=100)
    if not success_past:
        return {
            "type": "text",
            "text": f"❌ Failed to fetch past loans: {past_loans}"
        }
    past_loans.sort(key=lambda r: r.get("borrow_id", 0), reverse=True)
    # print("past loans are:", past_loans)

    messages = [f"{name} ({matric})'s Loan Records"]

    # === ACTIVE LOANS ===
    if active_loans:
        overdue = [r for r in active_loans if r.get("is_overdue")]
        current = [r for r in active_loans if not r.get("is_overdue")]
        

        lines = [f"📌 Active Loans ({matric}):"]

        if overdue:
            lines.append("⚠️ Overdue Books:")
            for r in overdue:
                lines.append(_format_loan_record(r))

        if current:
            lines.append("\n✅ Currently Borrowed:")
            for r in current:
                lines.append(_format_loan_record(r))

        messages.append({
            "type": "text",
            "text": "\n".join(lines)
        })
    else:
        messages.append({
            "type": "text",
            "text": f"📭 No active loans found for {matric}."
        })

    # === PAST LOANS ===
    recent_cutoff = datetime.utcnow() - timedelta(days=180)
    # print("recent cutoff:", recent_cutoff)

    past_recent = []

    for r in past_loans:
        return_str = r.get("return_date")
        if return_str:
            try:
                returned_dt = datetime.fromisoformat(return_str.replace("Z", "")) 
                # print(f"return_dt: {returned_dt}")
                # print("returned_dt > recent_cutoff is", returned_dt > recent_cutoff)
                if returned_dt > recent_cutoff:
                    past_recent.append(r)
            except Exception as e:
                print(f"[ERROR] Failed to parse return_date {return_str}: {e}")
                continue

    if past_recent:
        lines = [f"📚 Past Loans (last 6 months):"]
        for r in past_recent:
            lines.append(_format_loan_record(r))
        messages.append({
            "type": "text",
            "text": "\n".join(lines)
        })

    return messages


def _format_loan_record(record):
    title = record.get("book_title", "Unknown Title")
    borrow_date = pretty_date(record.get("borrow_date", ""))
    due_date = pretty_date(record.get("due_date", ""))
    return_date = pretty_date(record.get("return_date")) if record.get("return_date") else "Not yet returned"
    status = record.get("status", "unknown").capitalize()
    overdue_note = "⚠️ Overdue" if record.get("is_overdue") else ""

    return (
        f"• {title}\n"
        f"  Status: {status}  {overdue_note}\n"
        f"  Borrowed: {borrow_date}\n"
        f"  Due: {due_date}\n"
        f"  Returned: {return_date or 'Not yet returned'}"
    )
