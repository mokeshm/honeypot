from http.server import BaseHTTPRequestHandler, HTTPServer
from logger import log_attack, log_exception

class HoneypotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.client_address[0]
        try:
            log_attack("HTTP", ip, f"GET {self.path}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Fake Web Server</h1>")
        except Exception as e:
            log_exception("HTTP", ip, e)

    def do_POST(self):
        ip = self.client_address[0]
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length > 0 else b''
            log_attack("HTTP", ip, f"POST {self.path} BODY: {body.decode(errors='ignore')}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Fake Web Server</h1>")
        except Exception as e:
            log_exception("HTTP", ip, e)

def run_http():
    server = HTTPServer(("0.0.0.0", 8081), HoneypotHandler)
    print("[+] HTTP Honeypot running on port 8081")
    server.serve_forever()

if __name__ == "__main__":
    run_http()
