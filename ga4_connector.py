import os
import json
from googleapiclient.discovery import build
try:
    from credentials_helper import get_credentials, SCOPES_GA4
except ImportError:
    from .credentials_helper import get_credentials, SCOPES_GA4

def get_ga4_service():
    creds = get_credentials(SCOPES_GA4)
    return build('analyticsdata', 'v1beta', credentials=creds)

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

    # Safely save to local cache if filesystem is writable (fails gracefully on serverless read-only lambda)
    try:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ga4_live_data.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"Successfully fetched GA4 data for property {property_id}! Saved to {output_file}")
    except (OSError, IOError, PermissionError) as write_err:
        print(f"[GA4] Live data fetched successfully (disk write skipped in read-only environment: {write_err})")

    return result

if __name__ == '__main__':
    import sys
    prop_id = sys.argv[1] if len(sys.argv) > 1 else '534850003'
    try:
        data = fetch_ga4_metrics(prop_id)
        print("GA4 Totals:", data['totals'])
    except Exception as e:
        print("GA4 Error:", e)
