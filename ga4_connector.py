import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_account.json')

def get_ga4_service():
    env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_CREDENTIALS')
    if env_json:
        try:
            info = json.loads(env_json) if isinstance(env_json, str) else env_json
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            return build('analyticsdata', 'v1beta', credentials=creds)
        except Exception as e:
            print(f"Error loading GA4 credentials from environment variable: {e}")
            
    if os.path.exists(CREDENTIALS_FILE):
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        return build('analyticsdata', 'v1beta', credentials=creds)
        
    raise FileNotFoundError(
        f"Credentials not found! Set 'GOOGLE_SERVICE_ACCOUNT_JSON' environment variable on server or place '{CREDENTIALS_FILE}' locally."
    )

def fetch_ga4_metrics(property_id='534850003', days=30):
    """
    Fetches Active Users, Sessions, Engagement Rate, Bounce Rate, 
    Traffic Channels, and Top Landing Pages from GA4 via REST API.
    """
    service = get_ga4_service()
    
    # 1. Overall Traffic KPIs & Daily Trends
    kpi_body = {
        'dateRanges': [{'startDate': f"{days}daysAgo", 'endDate': 'today'}],
        'dimensions': [{'name': 'date'}],
        'metrics': [
            {'name': 'activeUsers'},
            {'name': 'sessions'},
            {'name': 'screenPageViews'},
            {'name': 'engagementRate'},
            {'name': 'bounceRate'},
            {'name': 'averageSessionDuration'}
        ],
        'orderBys': [{'dimension': {'dimensionName': 'date'}}]
    }
    
    kpi_response = service.properties().runReport(
        property=f"properties/{property_id}",
        body=kpi_body
    ).execute()
    
    total_users = 0
    total_sessions = 0
    total_views = 0
    total_eng_rate = 0.0
    total_bounce_rate = 0.0
    daily_trends = []

    rows = kpi_response.get('rows', [])
    for row in rows:
        mvals = row.get('metricValues', [])
        dvals = row.get('dimensionValues', [])
        
        u = int(mvals[0].get('value', 0)) if len(mvals) > 0 else 0
        s = int(mvals[1].get('value', 0)) if len(mvals) > 1 else 0
        v = int(mvals[2].get('value', 0)) if len(mvals) > 2 else 0
        eng = float(mvals[3].get('value', 0.0)) if len(mvals) > 3 else 0.0
        b = float(mvals[4].get('value', 0.0)) if len(mvals) > 4 else 0.0
        
        total_users += u
        total_sessions += s
        total_views += v
        total_eng_rate += eng
        total_bounce_rate += b

        daily_trends.append({
            'date': dvals[0].get('value') if dvals else '',
            'activeUsers': u,
            'sessions': s,
            'screenPageViews': v,
            'engagementRate': round(eng * 100, 2),
            'bounceRate': round(b * 100, 2)
        })

    row_count = len(rows) or 1
    avg_eng_rate = round((total_eng_rate / row_count) * 100, 2)
    avg_bounce_rate = round((total_bounce_rate / row_count) * 100, 2)

    # 2. Traffic Acquisition Channels
    channel_body = {
        'dateRanges': [{'startDate': f"{days}daysAgo", 'endDate': 'today'}],
        'dimensions': [{'name': 'sessionDefaultChannelGroup'}],
        'metrics': [{'name': 'sessions'}, {'name': 'activeUsers'}],
        'orderBys': [{'metric': {'metricName': 'sessions'}, 'desc': True}]
    }
    channel_response = service.properties().runReport(
        property=f"properties/{property_id}",
        body=channel_body
    ).execute()
    
    channels = []
    for row in channel_response.get('rows', []):
        dvals = row.get('dimensionValues', [])
        mvals = row.get('metricValues', [])
        channels.append({
            'channel': dvals[0].get('value', 'Unknown') if dvals else 'Unknown',
            'sessions': int(mvals[0].get('value', 0)) if len(mvals) > 0 else 0,
            'users': int(mvals[1].get('value', 0)) if len(mvals) > 1 else 0
        })

    # 3. Top Visited Landing Pages
    page_body = {
        'dateRanges': [{'startDate': f"{days}daysAgo", 'endDate': 'today'}],
        'dimensions': [{'name': 'pagePath'}],
        'metrics': [{'name': 'screenPageViews'}, {'name': 'activeUsers'}, {'name': 'sessions'}],
        'orderBys': [{'metric': {'metricName': 'screenPageViews'}, 'desc': True}],
        'limit': 50
    }
    page_response = service.properties().runReport(
        property=f"properties/{property_id}",
        body=page_body
    ).execute()
    
    top_pages = []
    for row in page_response.get('rows', []):
        dvals = row.get('dimensionValues', [])
        mvals = row.get('metricValues', [])
        top_pages.append({
            'pagePath': dvals[0].get('value', '') if dvals else '',
            'views': int(mvals[0].get('value', 0)) if len(mvals) > 0 else 0,
            'users': int(mvals[1].get('value', 0)) if len(mvals) > 1 else 0,
            'sessions': int(mvals[2].get('value', 0)) if len(mvals) > 2 else 0
        })

    result = {
        'property_id': property_id,
        'period_days': days,
        'totals': {
            'activeUsers': total_users,
            'sessions': total_sessions,
            'screenPageViews': total_views,
            'avgEngagementRate': avg_eng_rate,
            'avgBounceRate': avg_bounce_rate
        },
        'channels': channels,
        'top_pages': top_pages,
        'daily_trends': daily_trends
    }

    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ga4_live_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Successfully fetched GA4 data for property {property_id}! Saved to {output_file}")
    return result

if __name__ == '__main__':
    import sys
    prop_id = sys.argv[1] if len(sys.argv) > 1 else '534850003'
    try:
        data = fetch_ga4_metrics(prop_id)
        print("GA4 Totals:", data['totals'])
    except Exception as e:
        print("GA4 Error:", e)
