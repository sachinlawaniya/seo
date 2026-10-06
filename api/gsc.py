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

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Cache-Control')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        days = int(params.get('days', ['30'])[0]) if params.get('days') else 30
        site_url = params.get('site_url', ['https://gurupunvaanii.com/'])[0]
        
        # 1. Attempt live GSC performance fetch via Google Search Console API
        if fetch_gsc_performance:
            try:
                live_data = fetch_gsc_performance(site_url=site_url, days=days)
                if live_data and live_data.get('totals'):
                    self.wfile.write(json.dumps(live_data, ensure_ascii=False).encode('utf-8'))
                    return
            except Exception as e:
                print(f"[GSC Serverless] Live fetch error: {e}. Falling back to cache.")
                
        # 2. Fallback to cached file
        cached_file = os.path.join(DIRECTORY, 'gsc_live_data.json')
        if os.path.exists(cached_file):
            try:
                with open(cached_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            except Exception as e:
                print(f"[GSC Serverless] Cache read error: {e}")

        self.wfile.write(json.dumps({
            'success': False,
            'error': 'GSC data temporarily unavailable.'
        }).encode('utf-8'))

    def do_POST(self):
        self.do_GET()
