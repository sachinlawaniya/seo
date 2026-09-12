import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_account.json')

def get_ga4_client():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found!")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
    return BetaAnalyticsDataClient()

def fetch_ga4_metrics(property_id, days=30):
    """
    Fetches Active Users, Sessions, Engagement Rate, Bounce Rate, 
    Traffic Channels, and Top Landing Pages from GA4.
    """
    client = get_ga4_client()
    
    # 1. Overall Traffic KPIs
    kpi_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="engagementRate"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")]
    )
    kpi_response = client.run_report(kpi_request)
    
    total_users = 0
    total_sessions = 0
    total_views = 0
    total_eng_rate = 0.0
    total_bounce_rate = 0.0
    daily_trends = []

    for row in kpi_response.rows:
        u = int(row.metric_values[0].value)
        s = int(row.metric_values[1].value)
        v = int(row.metric_values[2].value)
        eng = float(row.metric_values[3].value)
        b = float(row.metric_values[4].value)
        
        total_users += u
        total_sessions += s
        total_views += v
        total_eng_rate += eng
        total_bounce_rate += b

        daily_trends.append({
            'date': row.dimension_values[0].value,
            'activeUsers': u,
            'sessions': s,
            'screenPageViews': v,
            'engagementRate': round(eng * 100, 2),
            'bounceRate': round(b * 100, 2)
        })

    row_count = len(kpi_response.rows) or 1
    avg_eng_rate = round((total_eng_rate / row_count) * 100, 2)
    avg_bounce_rate = round((total_bounce_rate / row_count) * 100, 2)

    # 2. Traffic Acquisition Channels (Organic Search, Direct, Social, Referral, Paid)
    channel_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions"), Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")]
    )
    channel_response = client.run_report(channel_request)
    channels = []
    for row in channel_response.rows:
        channels.append({
            'channel': row.dimension_values[0].value,
            'sessions': int(row.metric_values[0].value),
            'users': int(row.metric_values[1].value)
        })

    # 3. Top Visited Landing Pages
    page_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"), Metric(name="sessions")],
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        limit=50
    )
    page_response = client.run_report(page_request)
    top_pages = []
    for row in page_response.rows:
        top_pages.append({
            'pagePath': row.dimension_values[0].value,
            'views': int(row.metric_values[0].value),
            'users': int(row.metric_values[1].value),
            'sessions': int(row.metric_values[2].value)
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
    prop_id = sys.argv[1] if len(sys.argv) > 1 else 'YOUR_GA4_PROPERTY_ID'
    try:
        data = fetch_ga4_metrics(prop_id)
        print("GA4 Totals:", data['totals'])
    except Exception as e:
        print("GA4 Error:", e)
