import threading
from ssh_honeypot import ssh_honeypot
from http_honeypot import run_http
from ftp_honeypot import ftp_honeypot
import time

if __name__ == "__main__":
    threads = []
    threads.append(threading.Thread(target=ssh_honeypot))
    threads.append(threading.Thread(target=run_http))
    threads.append(threading.Thread(target=ftp_honeypot))

    for t in threads:
        t.daemon = True
        t.start()

    print("[*] Honeypot services running... Press CTRL+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping honeypot services.\n")
