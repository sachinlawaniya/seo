from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import urllib.parse

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORY not in sys.path:
    sys.path.insert(0, DIRECTORY)

try:
    from gsc_connector import fetch_gsc_performance
except ImportError:
    fetch_gsc_performance = None

def has_credentials():
    return bool(
        os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or 
        os.environ.get('GOOGLE_CREDENTIALS') or 
        os.path.exists(os.path.join(DIRECTORY, 'service_account.json'))
    )

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        days = int(params.get('days', ['30'])[0]) if params.get('days') else 30
        site_url = params.get('site_url', ['https://gurupunvaanii.com/'])[0]
        
        # Try live GSC performance fetch
        if fetch_gsc_performance and has_credentials():
            try:
                live_data = fetch_gsc_performance(site_url=site_url, days=days)
                self.wfile.write(json.dumps(live_data, ensure_ascii=False).encode('utf-8'))
                return
            except Exception as e:
                print(f"[GSC Serverless] Live fetch error: {e}. Falling back to cache.")
                
        # Fallback to cached file
        cached_file = os.path.join(DIRECTORY, 'gsc_live_data.json')
        if os.path.exists(cached_file):
            with open(cached_file, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.wfile.write(json.dumps({'error': 'GSC data not available. Please configure GOOGLE_SERVICE_ACCOUNT_JSON environment variable.'}).encode('utf-8'))

    def do_POST(self):
        self.do_GET()
