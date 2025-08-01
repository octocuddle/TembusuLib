# utils/photo_cleaning.py

import os
import time
import threading
# from datetime import datetime, timedelta

PHOTO_DIR = "telegram_photo"
MAX_FILE_AGE_SECONDS = int(os.getenv("MAX_FILE_AGE_SECONDS"))  # 2 weeks, 14*24*60*60=1209600
PHOTO_CLEANING_INTERVAL = int(os.getenv("PHOTO_CLEANING_INTERVAL")) # 1 min, 1*60 = 60

def clean_old_photos():
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)

    now = time.time()
    for filename in os.listdir(PHOTO_DIR):
        file_path = os.path.join(PHOTO_DIR, filename)
        try:
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > MAX_FILE_AGE_SECONDS:
                    os.remove(file_path)
                    print(f"[CLEANUP] Deleted old photo: {filename}")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

    # Schedule the next cleanup in 86400 sec (1 day)
    threading.Timer(PHOTO_CLEANING_INTERVAL, clean_old_photos).start()
