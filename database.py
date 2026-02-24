import sqlite3
from config import DATABASE_NAME

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            notification_enabled BOOLEAN DEFAULT TRUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL UNIQUE,
            last_checked TEXT,
            last_price REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            found_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(telegram_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?) RETURNING user_id", (telegram_id,))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        # User already exists
        cursor.execute("SELECT user_id FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_user_id(telegram_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE telegram_id = ?", (telegram_id,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def add_keyword(user_id, keyword):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keywords (user_id, keyword) VALUES (?, ?)", (user_id, keyword))
    conn.commit()
    conn.close()

def get_keywords(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM keywords WHERE user_id = ?", (user_id,))
    keywords = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keywords

def remove_keyword(user_id, keyword):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keywords WHERE user_id = ? AND keyword = ?", (user_id, keyword))
    conn.commit()
    conn.close()

def add_tracked_url(user_id, url):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tracked_urls (user_id, url) VALUES (?, ?)", (user_id, url))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False # URL already tracked

def get_tracked_urls(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM tracked_urls WHERE user_id = ?", (user_id,))
    urls = [row[0] for row in cursor.fetchall()]
    conn.close()
    return urls

def remove_tracked_url(user_id, url):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tracked_urls WHERE user_id = ? AND url = ?", (user_id, url))
    conn.commit()
    conn.close()

def add_promo(user_id, platform, title, description, url):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    from datetime import datetime
    found_date = datetime.now().isoformat()
    cursor.execute("INSERT INTO promos (user_id, platform, title, description, url, found_date) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, platform, title, description, url, found_date))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE notification_enabled = TRUE")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def get_all_keywords():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, keyword FROM keywords")
    keywords = cursor.fetchall()
    conn.close()
    return keywords

def get_all_tracked_urls_for_scheduler():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT t.user_id, t.url FROM tracked_urls t JOIN users u ON t.user_id = u.user_id WHERE u.notification_enabled = TRUE")
    urls = cursor.fetchall()
    conn.close()
    return urls

def get_latest_promo_for_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT platform, title, description, url, found_date FROM promos WHERE user_id = ? ORDER BY found_date DESC LIMIT 1", (user_id,))
    promo = cursor.fetchone()
    conn.close()
    return promo



def get_telegram_id_from_user_id(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE user_id = ?", (user_id,))
    telegram_id = cursor.fetchone()
    conn.close()
    return telegram_id[0] if telegram_id else None

def get_all_keywords_for_scheduler():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT k.user_id, k.keyword FROM keywords k JOIN users u ON k.user_id = u.user_id WHERE u.notification_enabled = TRUE")
    keywords_data = cursor.fetchall()
    conn.close()
    return keywords_data
