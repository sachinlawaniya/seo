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

def fetch_gsc_performance(site_url='https://gurupunvaanii.com/', days=28):
    """
    Fetches exact GSC Performance matching Google Search Console Insights.
    Detects latest date available to ensure 100% parity with GSC dashboard.
    """
    service = get_gsc_service()
    
    # 1. Detect latest available date in GSC (GSC usually has a 2-3 day lag)
    check_req = {
        'startDate': (datetime.date.today() - datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
        'endDate': datetime.date.today().strftime('%Y-%m-%d'),
        'dimensions': ['date'],
    }
    resp_check = service.searchanalytics().query(siteUrl=site_url, body=check_req).execute()
    rows = resp_check.get('rows', [])
    if rows:
        latest_date_str = rows[-1]['keys'][0]
        latest_date = datetime.datetime.strptime(latest_date_str, '%Y-%m-%d').date()
    else:
        latest_date = datetime.date.today() - datetime.timedelta(days=2)

    # Calculate exact 28-day and 7-day ranges ending on latest_date
    start_date_28 = (latest_date - datetime.timedelta(days=27)).strftime('%Y-%m-%d')
    end_date_28 = latest_date.strftime('%Y-%m-%d')
    
    start_date_7 = (latest_date - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
    end_date_7 = latest_date.strftime('%Y-%m-%d')

    print(f"Fetching GSC Data for '{site_url}' from {start_date_28} to {end_date_28} (Latest: {latest_date})...")

    # 1. Overall Daily Totals for 28 Days
    request_totals = {
        'startDate': start_date_28,
        'endDate': end_date_28,
        'dimensions': ['date'],
        'rowLimit': 5000
    }
    response_totals = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()
    date_rows = response_totals.get('rows', [])
    
    total_clicks_28 = sum(r.get('clicks', 0) for r in date_rows)
    total_impr_28 = sum(r.get('impressions', 0) for r in date_rows)
    avg_ctr_28 = (total_clicks_28 / total_impr_28 * 100) if total_impr_28 > 0 else 0
    avg_pos_28 = (sum(r.get('position', 0) for r in date_rows) / len(date_rows)) if date_rows else 0

    # 7-Day Slice Totals
    slice_7_rows = [r for r in date_rows if r['keys'][0] >= start_date_7]
    total_clicks_7 = sum(r.get('clicks', 0) for r in slice_7_rows)
    total_impr_7 = sum(r.get('impressions', 0) for r in slice_7_rows)
    avg_ctr_7 = (total_clicks_7 / total_impr_7 * 100) if total_impr_7 > 0 else 0
    avg_pos_7 = (sum(r.get('position', 0) for r in slice_7_rows) / len(slice_7_rows)) if slice_7_rows else 0

    # 2. Top Keywords / Queries with Landing Pages (Up to 1000)
    request_queries = {
        'startDate': start_date_28,
        'endDate': end_date_28,
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

    # 3. Top Pages (Matching GSC Insights Content View)
    request_pages = {
        'startDate': start_date_28,
        'endDate': end_date_28,
        'dimensions': ['page'],
        'rowLimit': 100
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

    daily_trends = [
        {
            'date': r['keys'][0],
            'clicks': r.get('clicks', 0),
            'impressions': r.get('impressions', 0),
            'ctr': round(r.get('ctr', 0) * 100, 2),
            'position': round(r.get('position', 0), 1)
        }
        for r in date_rows
    ]

    result = {
        'site_url': site_url,
        'period_days': 28,
        'start_date': start_date_28,
        'end_date': end_date_28,
        'latest_available_date': latest_date.strftime('%Y-%m-%d'),
        'totals_28d': {
            'clicks': total_clicks_28,
            'impressions': total_impr_28,
            'avg_ctr': round(avg_ctr_28, 2),
            'avg_position': round(avg_pos_28, 1)
        },
        'totals_7d': {
            'clicks': total_clicks_7,
            'impressions': total_impr_7,
            'avg_ctr': round(avg_ctr_7, 2),
            'avg_position': round(avg_pos_7, 1)
        },
        'totals': {
            'clicks': total_clicks_28,
            'impressions': total_impr_28,
            'avg_ctr': round(avg_ctr_28, 2),
            'avg_position': round(avg_pos_28, 1)
        },
        'daily_trends': daily_trends,
        'top_queries': top_queries,
        'top_pages': top_pages
    }
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gsc_live_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        
    print(f"Successfully fetched GSC data! 28D Clicks: {total_clicks_28}, 7D Clicks: {total_clicks_7}. Saved to {output_file}")
    return result

if __name__ == '__main__':
    target_site = 'https://gurupunvaanii.com/'
    try:
        data = fetch_gsc_performance(target_site)
        print("28D Clicks:", data['totals_28d']['clicks'], "Impressions:", data['totals_28d']['impressions'])
        print("7D Clicks:", data['totals_7d']['clicks'], "Impressions:", data['totals_7d']['impressions'])
    except Exception as e:
        print("GSC Error:", e)
