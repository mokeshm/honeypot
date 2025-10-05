# Python Cyber Honeypot Dashboard

A Python-based honeypot framework to monitor suspicious activities on SSH, FTP, and HTTP services. Logs attacks in a SQLite database and sends **real-time alerts** via **Telegram** and **Email**.

---

## Features

- Multi-service honeypot: **SSH**, **FTP**, **HTTP**  
- Attack logging with **SQLite**  
- **Real-time alerts** via Telegram Bot and Email  
- Web-based dashboard to:
  - View attack logs
  - Run self-tests
  - Clear logs
  - Save logs to text
  - Configure Telegram & Email settings

---

## Requirements

- Python 3.8+  
- Install dependencies:

---

#Honeypot Services

SSH → port 22222

FTP → port 21212

HTTP → port 8081

⚠ Ensure ports are open and Python runs as administrator if required.

---

---

#Setup

Clone the repository:


git clone https://github.com/yourusername/cyber-honeypot.git
cd cyber-honeypot


Install dependencies (if requirements.txt exists):

pip install -r requirements.txt


Run the Flask dashboard:

python dashboard.py


Open your browser at:

http://localhost:5000

---

```bash

pip install flask requests
