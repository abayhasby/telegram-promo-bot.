import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from database import init_db, add_user, add_keyword, get_keywords, remove_keyword, add_tracked_url, get_tracked_urls, remove_tracked_url, get_user_id
from scheduler import start_scheduler, set_telegram_application

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    add_user(user_telegram_id)
    await update.message.reply_text(
        "Halo! Saya Asisten Belanja Cerdas Anda. Saya akan membantu Anda melacak promo dari Shopee dan TikTok Shop. "
        "Gunakan /help untuk melihat daftar perintah."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Daftar perintah:\n"
        "/start - Memulai bot dan mendaftarkan Anda.\n"
        "/add_keyword <kata_kunci> - Menambahkan kata kunci untuk melacak promo (contoh: /add_keyword elektronik).\n"
        "/remove_keyword <kata_kunci> - Menghapus kata kunci.\n"
        "/list_keywords - Melihat daftar kata kunci yang Anda lacak.\n"
        "/track_url <url> - Melacak promo atau perubahan harga pada URL produk tertentu (contoh: /track_url https://shopee.co.id/productA).\n"
        "/untrack_url <url> - Berhenti melacak URL.\n"
        "/list_tracked_urls - Melihat daftar URL yang Anda lacak.\n"
        "/help - Menampilkan daftar perintah ini."
    )

async def add_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text("Mohon sertakan kata kunci. Contoh: /add_keyword elektronik")
        return

    keyword = " ".join(context.args).strip()
    add_keyword(user_id, keyword)
    await update.message.reply_text(f"Kata kunci \'{keyword}\' telah ditambahkan untuk pelacakan promo.")

async def remove_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text("Mohon sertakan kata kunci yang ingin dihapus. Contoh: /remove_keyword elektronik")
        return

    keyword = " ".join(context.args).strip()
    remove_keyword(user_id, keyword)
    await update.message.reply_text(f"Kata kunci \'{keyword}\' telah dihapus.")

async def list_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    keywords = get_keywords(user_id)
    if keywords:
        keyword_list = "\n".join([f"- {k}" for k in keywords])
        await update.message.reply_text(f"Kata kunci yang Anda lacak:\n{keyword_list}")
    else:
        await update.message.reply_text("Anda belum melacak kata kunci apapun. Gunakan /add_keyword untuk menambahkannya.")

async def track_url_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    if not context.args or not context.args[0].startswith("http"):
        await update.message.reply_text("Mohon sertakan URL yang valid. Contoh: /track_url https://shopee.co.id/productA")
        return

    url = context.args[0].strip()
    if add_tracked_url(user_id, url):
        await update.message.reply_text(f"URL \'{url}\' telah ditambahkan untuk pelacakan promo/harga.")
    else:
        await update.message.reply_text(f"URL \'{url}\' sudah Anda lacak sebelumnya.")

async def untrack_url_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    if not context.args or not context.args[0].startswith("http"):
        await update.message.reply_text("Mohon sertakan URL yang ingin dihapus. Contoh: /untrack_url https://shopee.co.id/productA")
        return

    url = context.args[0].strip()
    remove_tracked_url(user_id, url)
    await update.message.reply_text(f"URL \'{url}\' telah dihapus dari daftar pelacakan.")

async def list_tracked_urls_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        await update.message.reply_text("Anda belum terdaftar. Silakan gunakan /start terlebih dahulu.")
        return

    urls = get_tracked_urls(user_id)
    if urls:
        url_list = "\n".join([f"- {u}" for u in urls])
        await update.message.reply_text(f"URL yang Anda lacak:\n{url_list}")
    else:
        await update.message.reply_text("Anda belum melacak URL apapun. Gunakan /track_url untuk menambahkannya.")

def main() -> None:
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    set_telegram_application(application)
    start_scheduler()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_keyword", add_keyword_command))
    application.add_handler(CommandHandler("remove_keyword", remove_keyword_command))
    application.add_handler(CommandHandler("list_keywords", list_keywords_command))
    application.add_handler(CommandHandler("track_url", track_url_command))
    application.add_handler(CommandHandler("untrack_url", untrack_url_command))
    application.add_handler(CommandHandler("list_tracked_urls", list_tracked_urls_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables. Please set it in a .env file or directly.")
    else:
        main()
