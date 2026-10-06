from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import time

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORY not in sys.path:
    sys.path.insert(0, DIRECTORY)

try:
    from gsc_connector import fetch_gsc_performance
except ImportError:
    fetch_gsc_performance = None

try:
    from ga4_connector import fetch_ga4_metrics
except ImportError:
    fetch_ga4_metrics = None

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
        
        res_data = {'success': True, 'synced_at': time.strftime('%Y-%m-%d %H:%M:%S')}
        
        if fetch_gsc_performance:
            try:
                res_data['gsc'] = fetch_gsc_performance('https://gurupunvaanii.com/', days=28)
            except Exception as e:
                res_data['gsc_error'] = str(e)
                
        if not res_data.get('gsc'):
            gsc_file = os.path.join(DIRECTORY, 'gsc_live_data.json')
            if os.path.exists(gsc_file):
                try:
                    with open(gsc_file, 'r', encoding='utf-8') as f:
                        res_data['gsc'] = json.load(f)
                except Exception as e:
                    res_data['gsc_error'] = str(e)
        
        if fetch_ga4_metrics:
            try:
                res_data['ga4'] = fetch_ga4_metrics('534850003', days=30)
            except Exception as e:
                res_data['ga4_error'] = str(e)
                
        if not res_data.get('ga4'):
            ga4_file = os.path.join(DIRECTORY, 'ga4_live_data.json')
            if os.path.exists(ga4_file):
                try:
                    with open(ga4_file, 'r', encoding='utf-8') as f:
                        res_data['ga4'] = json.load(f)
                except Exception as e:
                    res_data['ga4_error'] = str(e)
        
        self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        self.do_GET()
