
# app/utils/oc_callback_bridge.py
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class OCHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        qs = parse_qs(parsed.query or "")
        code  = (qs.get("code")  or [None])[0]
        state = (qs.get("state") or [None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code")
            return

        # Leva o navegador ao callback Flask
        location = f"http://127.0.0.1:5000/auth/callback?code={code}&state={state or ''}"
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

def start_oc_callback_bridge(host="127.0.0.1", port=9090):
    server = HTTPServer((host, port), OCHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t
