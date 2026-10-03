from http.server import BaseHTTPRequestHandler
import json
import os

import sys
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORY not in sys.path:
    sys.path.insert(0, DIRECTORY)

try:
    import db
except Exception:
    db = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if db:
            try:
                db_data, err = db.get_latest_audit_from_db()
                if db_data and not err:
                    self.wfile.write(json.dumps(db_data, ensure_ascii=False).encode('utf-8'))
                    return
            except Exception:
                pass

        data_file = os.path.join(DIRECTORY, 'audit_raw_data.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.wfile.write(json.dumps({'error': 'No audit data available'}).encode('utf-8'))

