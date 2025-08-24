# notification/due_date_notifier.py
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime

def send_telegram_message(chat_id,message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Failed to send message to {chat_id}: {e}")
        return {"ok": False, "error": str(e)}

def check_due_soon():
    """
    Attempt to create a borrow record in the backend.
    Returns (is_successful: bool, message: str)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/borrowing/due-soon?days=3&limit=100",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("get due soon books")
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    

def check_overdue():
    """
    Attempt to create a borrow record in the backend.
    Returns (is_successful: bool, message: str)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")  # default fallback
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/borrowing/overdue?skip=0&limit=100",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("get overdue books")
            return True, data
        else:
            return False, f"{response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    
def send_reminder_message():
    # fetch due-soon books
    success_due_soon, data_due_soon = check_due_soon()
    due_soon_dict = {}
    if success_due_soon and data_due_soon:
        for record in data_due_soon:
            student_id = record["student_telegram_id"]
            if student_id not in due_soon_dict:
                    due_soon_dict[student_id] = []
            due_soon_dict[student_id].append({
                "student_name":record["student_name"],
                "book_title": record["book_title"],
                #"author": record.get("author", "Unknown Author"),
                "borrow_date": record["borrow_date"],
                "due_date": record["due_date"]
            })

    # fetch overdue books
    success_overdue, data_overdue = check_overdue()
    overdue_dict = {}
    if success_overdue and data_overdue:
        for record in data_overdue:
            student_id = record["student_telegram_id"]
            if student_id not in overdue_dict:
                    overdue_dict[student_id] = []
            overdue_dict[student_id].append({
                "student_name":record["student_name"],
                "book_title": record["book_title"],
                #"author": record.get("author", "Unknown Author"),
                "borrow_date": record["borrow_date"],
                "due_date": record["due_date"]
            })

    # Send reminders for due-soon and overdue books (single message per user)
    for chat_id,records in due_soon_dict.items():
        message_due_soon = [f"📚 Reminder: You have the following book(s) due soon:\n\n"]
        for item in records:
            # Format borrow_date to dd/mm/yyyy
            borrow_date = datetime.strptime(item["borrow_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            due_date = datetime.strptime(item["due_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            message_due_soon.append (
                f"• Book title: {item['book_title']}\n"
                f"  Borrowed: {borrow_date}\n"
                f"  Due: {due_date}\n"
            )
        message_due_soon.append("\nPlease return due-soon books promptly!")

        message = "".join(message_due_soon).rstrip()
        send_telegram_message(chat_id, message)

    for chat_id,records in overdue_dict.items():
        message_overdue = [f"⚠️ Warning: You have the following book(s) already overdue:\n\n"]
        for item in records:
            # Format borrow_date to yyyy-mm-dd
            borrow_date = datetime.strptime(item["borrow_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            due_date = datetime.strptime(item["due_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            message_overdue.append (
                f"• Book title: {item['book_title']}\n"
                f"  Borrowed: {borrow_date}\n"
                f"  Due: {due_date}\n"
            )
        message_overdue.append("\nPlease return overdue books soon to avoid additional charges.")

        message = "".join(message_overdue).rstrip()
        send_telegram_message(chat_id, message)


def start_scheduler():
    # Define Singapore timezone (UTC+8)
    sg_timezone = timezone('Asia/Singapore')
    
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    # Add job with cron trigger set to 10 AM SG time
    scheduler.add_job(
        send_reminder_message,
        trigger=CronTrigger(hour=10, minute=0, timezone=sg_timezone)
    )
    
    # Start the scheduler
    scheduler.start()
    print("Reminder scheduler started...")

if __name__ == "__main__":
    start_scheduler()
    # Keep the script running
    while True:
        pass



