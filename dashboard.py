import sqlite3
import threading
from flask import Flask, render_template_string, redirect, url_for, send_file, request
import socket
import requests
import time
from datetime import datetime

app = Flask(__name__)
DB = "database.db"

# -----------------------
# Database Initialization
# -----------------------
def init_db():
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_setting(key, default=""):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# -----------------------
# HTML Template
# -----------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Honeypot Dashboard</title>
    <style>
        body { font-family: Arial; background: #f7f7f7; padding: 20px; }
        h1 { text-align:center; }
        table { width:100%; border-collapse: collapse; background:#fff; margin-bottom:20px; }
        th, td { padding:10px; border:1px solid #ddd; text-align:left; }
        th { background:#333; color:white; }
        tr:nth-child(even) { background:#f2f2f2; }
        .btn { background:#28a745; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; margin:2px; display:inline-block;}
        .btn:hover { background:#218838; }
        form { background:#fff; padding:15px; border:1px solid #ccc; border-radius:5px; margin-bottom:20px; }
        label { display:block; margin-top:10px; }
        input[type=text], input[type=password], input[type=checkbox] { width:100%; padding:5px; margin-top:5px; }
        input[type=submit] { width:auto; padding:10px 20px; margin-top:10px; background:#007bff; color:#fff; border:none; border-radius:5px; cursor:pointer;}
        input[type=submit]:hover { background:#0069d9; }
    </style>
</head>
<body>
    <h1>Cyber Honeypot Attack Logs</h1>
    <p style="text-align:center;">
        <a class="btn" href="{{ url_for('run_self_test_route') }}">Run Self-Test</a>
        <a class="btn" href="{{ url_for('save_logs') }}">Save Logs to Text</a>
        <a class="btn" href="{{ url_for('clear_logs') }}" onclick="return confirm('Are you sure you want to clear all logs?');">Clear Logs</a>
    </p>

    <h2>Configure Alerts</h2>
    <form method="POST" action="{{ url_for('save_settings') }}">
        <h3>Telegram Alerts</h3>
        <label>Enable Telegram <input type="checkbox" name="enable_telegram" {% if settings.enable_telegram == '1' %}checked{% endif %}></label>
        <label>Bot Token: <input type="text" name="telegram_token" value="{{ settings.telegram_token }}"></label>
        <label>Chat ID: <input type="text" name="telegram_chat_id" value="{{ settings.telegram_chat_id }}"></label>

        <h3>Email Alerts</h3>
        <label>Enable Email <input type="checkbox" name="enable_email" {% if settings.enable_email == '1' %}checked{% endif %}></label>
        <label>SMTP Server: <input type="text" name="smtp_server" value="{{ settings.smtp_server }}"></label>
        <label>SMTP Port: <input type="text" name="smtp_port" value="{{ settings.smtp_port }}"></label>
        <label>Email Address: <input type="text" name="email_address" value="{{ settings.email_address }}"></label>
        <label>Email Password: <input type="password" name="email_password" value="{{ settings.email_password }}"></label>
        <label>Recipient Email: <input type="text" name="alert_recipient" value="{{ settings.alert_recipient }}"></label>

        <input type="submit" value="Save Settings">
    </form>

    <table>
        <tr><th>ID</th><th>Timestamp</th><th>Service</th><th>IP</th><th>Data</th></tr>
        {% for attack in attacks %}
        <tr>
            <td>{{ attack[0] }}</td><td>{{ attack[1] }}</td><td>{{ attack[2] }}</td><td>{{ attack[3] }}</td><td>{{ attack[4] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# -----------------------
# Self-test functions
# -----------------------
def test_ssh():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 22222))
        s.settimeout(2)
        try: _ = s.recv(2048)
        except: pass
        s.send(b"testssh\r\n")
        time.sleep(1)
        s.close()
    except: pass

def test_ftp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 21212))
        s.settimeout(2)
        try: _ = s.recv(2048)
        except: pass
        s.send(b"USER hacker\r\nPASS 12345\r\n")
        time.sleep(1)
        s.close()
    except: pass

def test_http():
    try:
        requests.get("http://127.0.0.1:8081/fakeattack", timeout=3)
    except: pass

def run_self_test():
    def t(): test_ssh(); test_ftp(); test_http(); time.sleep(1)
    threading.Thread(target=t).start()

# -----------------------
# Routes
# -----------------------
@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks ORDER BY id DESC")
    attacks = cursor.fetchall()
    conn.close()

    # Load settings
    settings = {
        "enable_telegram": get_setting("enable_telegram", ""),
        "telegram_token": get_setting("telegram_token", ""),
        "telegram_chat_id": get_setting("telegram_chat_id", ""),
        "enable_email": get_setting("enable_email", ""),
        "smtp_server": get_setting("smtp_server", "smtp.gmail.com"),
        "smtp_port": get_setting("smtp_port", "587"),
        "email_address": get_setting("email_address", ""),
        "email_password": get_setting("email_password", ""),
        "alert_recipient": get_setting("alert_recipient", "")
    }

    return render_template_string(HTML_TEMPLATE, attacks=attacks, settings=settings)

@app.route("/run_self_test")
def run_self_test_route():
    run_self_test()
    return redirect(url_for('index'))

@app.route("/save_logs")
def save_logs():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    filename = f"honeypot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}\n")

    return send_file(filename, as_attachment=True)

@app.route("/clear_logs")
def clear_logs():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attacks")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/save_settings", methods=["POST"])
def save_settings():
    set_setting("enable_telegram", "1" if request.form.get("enable_telegram") else "0")
    set_setting("telegram_token", request.form.get("telegram_token", "").strip())
    set_setting("telegram_chat_id", request.form.get("telegram_chat_id", "").strip())

    set_setting("enable_email", "1" if request.form.get("enable_email") else "0")
    set_setting("smtp_server", request.form.get("smtp_server", "").strip())
    set_setting("smtp_port", request.form.get("smtp_port", "").strip())
    set_setting("email_address", request.form.get("email_address", "").strip())
    set_setting("email_password", request.form.get("email_password", "").strip())
    set_setting("alert_recipient", request.form.get("alert_recipient", "").strip())

    return redirect(url_for('index'))

# -----------------------
# Run server
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
