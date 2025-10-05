# logger.py
import sqlite3
import logging
import traceback
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText

DB = "database.db"

# ------------------------
# Configure logging
# ------------------------
logging.basicConfig(
    filename="honeypot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------
# DB-backed settings helpers
# ------------------------
def get_setting(key, default=""):
    """Retrieve a setting value from the database"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception as e:
        logging.error(f"Failed to get setting {key}: {e}")
        return default

def set_setting(key, value):
    """Store or update a setting in the database"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to set setting {key}: {e}")

# ------------------------
# Telegram alert
# ------------------------
def send_telegram_alert(message):
    """Send alert message via Telegram bot"""
    enabled = get_setting("enable_telegram", "") == "1"
    if not enabled:
        return

    token = get_setting("telegram_token", "").strip()
    chat_id = get_setting("telegram_chat_id", "").strip()
    if not token or not chat_id:
        logging.info("Telegram alert skipped: token/chat_id missing")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload, timeout=5)
        if r.status_code != 200:
            logging.error("Telegram send failed: %s %s", r.status_code, r.text)
    except Exception as e:
        logging.error("Telegram alert failed: %s", e)
        logging.error(traceback.format_exc())

# ------------------------
# Email alert
# ------------------------
def send_email_alert(subject, message):
    """Send alert via email (SMTP)"""
    enabled = get_setting("enable_email", "") == "1"
    if not enabled:
        return

    smtp_server = get_setting("smtp_server", "smtp.gmail.com")
    smtp_port = int(get_setting("smtp_port", "587"))
    email_address = get_setting("email_address", "").strip()
    email_password = get_setting("email_password", "").strip()
    alert_recipient = get_setting("alert_recipient", "").strip()

    if not email_address or not email_password or not alert_recipient:
        logging.info("Email alert skipped: missing SMTP/auth/recipient")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = alert_recipient

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logging.error("Email alert failed: %s", e)
        logging.error(traceback.format_exc())

# ------------------------
# Logging attacks
# ------------------------
def log_attack_db(service, ip, data):
    """Write attack into DB (used internally by honeypot code)."""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                service TEXT,
                ip TEXT,
                data TEXT
            )
        """)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO attacks (timestamp, service, ip, data) VALUES (?, ?, ?, ?)",
            (timestamp, service, ip, data)
        )
        conn.commit()
        conn.close()
        logging.info(f"[{service}] Attack from {ip} -> {data}")
    except Exception as e:
        logging.error(f"Failed to write attack to DB: {e}")
        logging.error(traceback.format_exc())

def log_attack(service, ip, data):
    """
    Log attack and send alerts (Telegram/Email) if enabled.
    """
    log_attack_db(service, ip, data)
    alert_message = f"[{service}] Attack detected from {ip} -> {data}"
    send_telegram_alert(alert_message)
    send_email_alert("Honeypot Alert", alert_message)

def log_exception(service, ip, exc):
    """Log exceptions in honeypot services"""
    logging.error(f"[{service}] Exception from {ip}: {exc}")
    logging.error(traceback.format_exc())
    # Optionally send alerts about exceptions
    alert_message = f"[{service}] Exception from {ip}: {exc}"
    send_telegram_alert(alert_message)
    send_email_alert("Honeypot Exception Alert", alert_message)
