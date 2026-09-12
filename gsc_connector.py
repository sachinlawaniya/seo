import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_account.json')

def get_gsc_service():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Credentials file '{CREDENTIALS_FILE}' not found! "
            f"Please place your Google Cloud Service Account JSON key as 'service_account.json' in the project folder."
        )
    
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=creds)
    return service

def fetch_gsc_performance(site_url, days=30):
    """
    Fetches Clicks, Impressions, CTR, Average Position, Top Queries, and Top Pages from GSC.
    site_url format: 'https://gurupunvaanii.com/' or 'sc-domain:gurupunvaanii.com'
    """
    service = get_gsc_service()
    
    end_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = (datetime.date.today() - datetime.timedelta(days=days + 2)).strftime('%Y-%m-%d')
    
    print(f"Fetching GSC Data for '{site_url}' from {start_date} to {end_date}...")

    # 1. Overall Totals
    request_totals = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['date'],
        'rowLimit': 5000
    }
    response_totals = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()
    
    total_clicks = 0
    total_impressions = 0
    total_ctr = 0.0
    total_pos = 0.0
    date_rows = response_totals.get('rows', [])
    
    for row in date_rows:
        total_clicks += row.get('clicks', 0)
        total_impressions += row.get('impressions', 0)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_position = (sum(r.get('position', 0) for r in date_rows) / len(date_rows)) if date_rows else 0

    # 2. Top Keywords / Queries with Landing Pages (Up to 1000)
    request_queries = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query', 'page'],
        'rowLimit': 1000
    }
    response_queries = service.searchanalytics().query(siteUrl=site_url, body=request_queries).execute()
    top_queries = []
    for row in response_queries.get('rows', []):
        top_queries.append({
            'query': row['keys'][0],
            'page': row['keys'][1] if len(row['keys']) > 1 else site_url,
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': round(row.get('ctr', 0) * 100, 2),
            'position': round(row.get('position', 0), 1)
        })

    # 3. Top Pages
    request_pages = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['page'],
        'rowLimit': 500
    }
    response_pages = service.searchanalytics().query(siteUrl=site_url, body=request_pages).execute()
    top_pages = []
    for row in response_pages.get('rows', []):
        top_pages.append({
            'page': row['keys'][0],
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': round(row.get('ctr', 0) * 100, 2),
            'position': round(row.get('position', 0), 1)
        })

    result = {
        'site_url': site_url,
        'period_days': days,
        'start_date': start_date,
        'end_date': end_date,
        'totals': {
            'clicks': total_clicks,
            'impressions': total_impressions,
            'avg_ctr': round(avg_ctr, 2),
            'avg_position': round(avg_position, 1)
        },
        'daily_trends': [
            {
                'date': r['keys'][0],
                'clicks': r.get('clicks', 0),
                'impressions': r.get('impressions', 0),
                'ctr': round(r.get('ctr', 0) * 100, 2),
                'position': round(r.get('position', 0), 1)
            }
            for r in date_rows
        ],
        'top_queries': top_queries,
        'top_pages': top_pages
    }
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gsc_live_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        
    print(f"Successfully fetched GSC data! Saved to {output_file}")
    return result

if __name__ == '__main__':
    # Default website URL
    target_site = 'https://gurupunvaanii.com/'
    try:
        data = fetch_gsc_performance(target_site)
        print("Total Clicks:", data['totals']['clicks'])
        print("Total Impressions:", data['totals']['impressions'])
        print("Top 5 Queries:", data['top_queries'][:5])
    except Exception as e:
        print("GSC Error:", e)
