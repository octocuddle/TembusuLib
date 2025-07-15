# utils/auth_helpers.py

from utils.db_telegramid_validator import validate_student_by_telegram_id

# Global cache shared from main bot module
authenticated_users = {}

def get_authenticated_user(user_id: str) -> tuple[bool, dict | str]:
    if user_id in authenticated_users:
        return True, authenticated_users[user_id]

    is_valid, result = validate_student_by_telegram_id(user_id)
    if is_valid:
        authenticated_users[user_id] = result
        return True, result
    else:
        return False, result
