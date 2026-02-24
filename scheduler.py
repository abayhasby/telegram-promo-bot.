from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import asyncio

from promo_tracker import search_shopee_promos, search_tiktok_promos, check_url_for_promo
from database import get_all_users, get_user_id, get_telegram_id_from_user_id, add_promo, get_all_keywords_for_scheduler, get_all_tracked_urls_for_scheduler
from config import PROMO_CHECK_INTERVAL

# Placeholder for the Telegram bot application instance
# This will be set by the main bot.py file
application = None

def set_telegram_application(app):
    global application
    application = app

async def send_promo_notification_async(telegram_id, promo):
    if application:
        message = f"*Promo Baru!*\n\nPlatform: {promo["platform"]}\nJudul: {promo["title"]}\nDeskripsi: {promo.get("description", "Tidak ada deskripsi")}\nLink: {promo["url"]}"
        await application.bot.send_message(chat_id=telegram_id, text=message, parse_mode=\'Markdown\')
    else:
        print(f"Failed to send promo to {telegram_id}: Telegram application not set.")

def check_for_promos_job():
    if not application:
        print("Telegram application not set in scheduler.")
        return

    print(f"[{datetime.now()}] Running promo check job...")

    # Check keywords
    all_keywords_data = get_all_keywords_for_scheduler()
    for user_id, keyword in all_keywords_data:
        shopee_promos = search_shopee_promos(keyword)
        tiktok_promos = search_tiktok_promos(keyword)

        telegram_id = get_telegram_id_from_user_id(user_id)
        if telegram_id:
            for promo in shopee_promos + tiktok_promos:
                application.create_task(send_promo_notification_async(telegram_id, promo))
                add_promo(user_id, promo["platform"], promo["title"], promo.get("description", ""), promo["url"])

    # Check tracked URLs
    all_tracked_urls_data = get_all_tracked_urls_for_scheduler()
    for user_id, url in all_tracked_urls_data:
        promo_info = check_url_for_promo(url)
        telegram_id = get_telegram_id_from_user_id(user_id)
        if telegram_id and promo_info:
            application.create_task(send_promo_notification_async(telegram_id, promo_info))
            add_promo(user_id, promo_info["platform"], promo_info["title"], promo_info.get("description", ""), promo_info["url"])

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_for_promos_job, \'interval\', seconds=PROMO_CHECK_INTERVAL, max_instances=1)
    scheduler.start()
    print("Scheduler started.")
