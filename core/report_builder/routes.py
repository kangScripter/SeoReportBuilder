from flask import Blueprint, jsonify, request, session, current_app
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI
from datetime import datetime, timedelta
import os
import traceback
from ..auth import get_credentials
from dotenv import load_dotenv
from ..logger import logger

# Load environment variables
load_dotenv()

# Create blueprint
report_bp = Blueprint('report', __name__)

# Configure OpenAI API
openai = OpenAI(
    api_key=os.getenv('OPENAI_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL', "https://generativelanguage.googleapis.com/v1beta/openai/")
)

def get_date_range(days):
    """Get start and end dates for a given number of days.
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        tuple: (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(days))
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def parse_metrics(metrics):
    """Parse metrics to extract date ranges and units.
    
    Args:
        metrics (list): List of metric names with time units (e.g. ['clicks_28d'])
        
    Returns:
        list: List of dictionaries with startDate, endDate, and unit
    """
    end_date = datetime.now()
    range_set = set()

    for metric in metrics:
        try:
            unit = metric.split("_")[1]
            value = int(unit[:-1])
            period = unit[-1]

            if period == "d":
                delta = timedelta(days=value)
            elif period == "m":
                delta = timedelta(days=value * 28)
            elif period == "y":
                delta = timedelta(days=value * 365)
            else:
                continue

            start_date = (end_date - delta).strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            range_set.add((start_date, end_date_str, unit))

        except Exception as e:
            print(f"Invalid metric: {metric} -> {e}")
            continue
            
    return [{"startDate": s, "endDate": e, "unit":u} for s, e, u in range_set]

def get_query_data(start_date, end_date, query, credentials, property_url):
    """Get query data from Google Search Console.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        query (str): Search query to filter by
        credentials: Google API credentials
        property_url (str): Search Console property URL
        
    Returns:
        dict: Response from Search Console API
    """
    service = build('searchconsole', 'v1', credentials=credentials)
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensionFilterGroups": [{
            "filters": [{
                "dimension": "QUERY",
                "expression": query
            }]
        }]
    }
    response = service.searchanalytics().query(
        siteUrl=property_url,
        body=payload
    ).execute()
    return response

def analyze_query_intent(query):
    """Analyze search intent using OpenAI API.
    
    Args:
        query (str): Search query to analyze
        
    Returns:
        tuple: (intent, category) - Intent description and category
    """
    try:
        response = openai.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{
                "role": "system",
                "content": "You are an SEO expert analyzing search queries. In the first line, describe the user's search intent in simple language. In the second line, provide a brief category for the query. Do not include any headings or labels."
            }, {
                "role": "user",
                "content": f"Analyze the search intent and category for the query: '{query}'"
            }],
            temperature=0.7,
            max_tokens=150
        )
        
        # Parse the response
        intent_text = response.choices[0].message.content
        intent_parts = intent_text.split('\n')
        intent = intent_parts[0] if intent_parts else "Unknown"
        intent_category = intent_parts[1] if intent_parts else "Unknown"
        return intent, intent_category
    except Exception as e:
        logger.error(f"Error analyzing query intent: {str(e)}")
        return "Unknown", "Standard Content"

def get_cached_gsc_data(property_url, credentials):
    """Get cached or fresh data from Google Search Console.
    
    Args:
        property_url (str): Search Console property URL
        credentials: Google API credentials
        
    Returns:
        dict: Response from Search Console API
    """
    # Generate a unique cache key for the property
    cache_key = f"gsc_data_{property_url}"
    
    # Try to get cached data
    cached_data = current_app.cache.get(cache_key)
    if cached_data:
        logger.info("Using cached GSC data")
        return cached_data
    
    # If no cached data, fetch from GSC API
    logger.info("Fetching fresh GSC data")
    service = build('searchconsole', 'v1', credentials=credentials)
    
    # Get data for the last 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    request_body = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['query'],
        'rowLimit': 25000  # Maximum allowed by GSC API
    }
    
    response = service.searchanalytics().query(
        siteUrl=property_url,
        body=request_body
    ).execute()
    
    # Cache the response for 24 hours (86400 seconds)
    current_app.cache.set(cache_key, response, timeout=86400)
    
    return response

@report_bp.route('/api/properties', methods=['GET'])
def get_properties():
    """Get list of verified Search Console properties.
    
    Returns:
        JSON: List of verified properties or error message
    """
    try:
        credentials = get_credentials()
        if not credentials:
            return jsonify({'error': 'Not authenticated'}), 401

        service = build('searchconsole', 'v1', credentials=credentials)
        site_list = service.sites().list().execute()
        
        # Filter for verified sites
        verified_sites = [site for site in site_list.get('siteEntry', []) 
                         if site.get('permissionLevel') != 'siteUnverifiedUser']
        
        return jsonify(verified_sites)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate a report with query data and intent analysis.
    
    Returns:
        JSON: Report data with pagination or error message
    """
    try:
        data = request.get_json()
        property_url = data.get('property')
        if not property_url:
            return jsonify({'error': 'Property URL is required'}), 400

        credentials = get_credentials()
        if not credentials:
            return jsonify({'error': 'Not authenticated'}), 401

        # Get cached or fresh GSC data
        response = get_cached_gsc_data(property_url, credentials)
        
        time_range = data.get('timeRange')
        metrics = data.get('metrics', [])
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 5))
        
        # Process the response
        rows = response.get('rows', [])
        results = []
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_rows = rows[start_idx:end_idx]
        
        for row in paginated_rows:
            result = {}
            result['query'] = row['keys'][0]  # Query is always the first dimension
            parsed_metrics = parse_metrics(metrics)

            for metric in parsed_metrics:
                start_date = metric['startDate']
                end_date = metric['endDate']
                unit = metric["unit"]
                res = get_query_data(start_date, end_date, row['keys'][0], credentials, property_url)
                query_row = res["rows"][0]
                metrics_data = {
                    f'clicks_{unit}': query_row.get('clicks', 0),
                    f'impressions_{unit}': query_row.get('impressions', 0),
                    f'ctr_{unit}': round(query_row.get('ctr', 0) * 100, 2),
                    f'position_{unit}': round(query_row.get('position', 0), 1)
                }
            
                # Add only the selected metrics
                for metric in metrics:
                    if metric in metrics_data:
                        result[metric] = metrics_data[metric]
            
            # Analyze query intent
            response, category = analyze_query_intent(result['query'])
            result['intent'] = response
            result['category'] = category
            results.append(result)

        # Calculate pagination info
        total_count = len(rows)
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

        return jsonify({
            'data': results,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': total_pages,
                'has_next_page': page < total_pages,
                'has_prev_page': page > 1
            }
        })

    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# @report_bp.route('/api/export-csv', methods=['POST'])
# def export_csv():
#     # Implementation for CSV export
#     pass

# @report_bp.route('/api/export-sheets', methods=['POST'])
# def export_sheets():
#     # Implementation for Google Sheets export
#     pass 