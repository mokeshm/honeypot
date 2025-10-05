import socket
import requests
import sqlite3
import time

def test_ssh():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 22222))
        # try to read banner
        try:
            s.settimeout(2)
            banner = s.recv(2048)
        except:
            banner = b""
        s.send(b"testssh\r\n")
        time.sleep(1.0)
        s.close()
    except Exception as e:
        print("SSH test failed:", e)

def test_ftp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 21212))
        try:
            s.settimeout(2)
            welcome = s.recv(2048)
        except:
            welcome = b""
        s.send(b"USER hacker\r\nPASS 12345\r\n")
        time.sleep(1.0)
        s.close()
    except Exception as e:
        print("FTP test failed:", e)

def test_http():
    try:
        requests.get("http://127.0.0.1:8081/fakeattack", timeout=3)
    except Exception as e:
        print("HTTP test failed:", e)

def main():
    test_ssh()
    test_ftp()
    test_http()
    time.sleep(1)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    print("\n=== Recent Honeypot Attacks ===")
    for r in rows:
        print(r)

if __name__ == "__main__":
    main()
