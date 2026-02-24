import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_NAME = "promo_tracker.db"

# Interval untuk pengecekan promo (dalam detik)
PROMO_CHECK_INTERVAL = 3600 # Setiap 1 jam
