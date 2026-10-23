"""Replay server: serves the REAL hobson/static/index.html + static assets and answers /start and /turn
with the responses captured from the live game on Felina's Mac (capture_s7.json), with the real delays."""
import json, time, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
STATIC = sys.argv[1]; CAP = json.load(open(sys.argv[2])); PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
SPEED = float(os.environ.get("SPEED", "1.0"))  # 1.0 = real latency
state = {"i": 0}
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/": return self._send(200, open(f"{STATIC}/index.html", "rb").read(), "text/html; charset=utf-8")
        if p.startswith("/scene/"):
            f = f"{STATIC}/scene/{p.rsplit('/', 1)[-1]}"
            if os.path.exists(f):
                return self._send(200, open(f, "rb").read(), "image/svg+xml")
        if p.startswith("/static/"):
            f = f"{STATIC}/{p[len('/static/'):]}"
            if os.path.exists(f):
                ct = {"css": "text/css", "js": "application/javascript", "png": "image/png", "svg": "image/svg+xml"}.get(f.rsplit(".", 1)[-1], "application/octet-stream")
                return self._send(200, open(f, "rb").read(), ct)
        self._send(404, b"", "text/plain")
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); self.rfile.read(n)
        if self.path == "/start": state["i"] = 0
        rec = CAP[state["i"]]; state["i"] += 1
        time.sleep(rec["ms"] / 1000 * SPEED)
        self._send(200, json.dumps(rec["res"]).encode(), "application/json")
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
