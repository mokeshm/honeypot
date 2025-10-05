import socket
from logger import log_attack, log_exception

def ssh_honeypot():
    host = "0.0.0.0"
    port = 22222
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[+] SSH Honeypot running on {host}:{port}")

    while True:
        client, addr = server.accept()
        ip = addr[0]
        try:
            client.settimeout(5.0)
            try:
                client.send(b"SSH-2.0-OpenSSH_7.9p1 Debian-10\r\n")
            except Exception as e:
                # send may fail if client closed quickly
                log_exception("SSH", ip, e)
            data_parts = []
            try:
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    data_parts.append(chunk)
            except socket.timeout:
                pass
            data = b''.join(data_parts).decode(errors='ignore') if data_parts else "<no data>"
            log_attack("SSH", ip, data)
        except Exception as e:
            log_exception("SSH", ip, e)
            log_attack("SSH", ip, f"error: {e}")
        finally:
            try:
                client.close()
            except:
                pass

if __name__ == "__main__":
    ssh_honeypot()
