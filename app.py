from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from luma_scraper import LumaScraper
import json
import os
import tempfile
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
import traceback
import atexit
import requests
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global scraper instance (can be configured per request)
scraper = None

# Wake-up scheduler to keep app alive on Render
def wake_up_app():
    try:
        app_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000/health')
        if app_url:
            response = requests.get(app_url)
            if response.status_code == 200:
                print(f"Successfully pinged {app_url} at {datetime.now()}")
            else:
                print(f"Failed to ping {app_url} (status code: {response.status_code}) at {datetime.now()}")
        else:
            print("APP_URL environment variable not set.")
    except Exception as e:
        print(f"Error occurred while pinging app: {e}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(wake_up_app, 'interval', minutes=10)
scheduler.start()

# Register shutdown handler
atexit.register(lambda: scheduler.shutdown())

def get_scraper(headless: bool = True, use_selenium: bool = True) -> LumaScraper:
    """
    Get or create a scraper instance
    
    Args:
        headless (bool): Run browser in headless mode
        use_selenium (bool): Use Selenium for JavaScript-heavy pages
        
    Returns:
        LumaScraper: Scraper instance
    """
    global scraper
    if scraper is None:
        scraper = LumaScraper(headless=headless, use_selenium=use_selenium)
    return scraper

def cleanup_scraper():
    """Clean up scraper resources"""
    global scraper
    if scraper:
        scraper.close()
        scraper = None

@app.route('/')
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "Luma Event Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/": "API documentation (this page)",
            "/health": "Health check endpoint",
            "/scrape/explore": "Scrape events from explore page",
            "/scrape/custom": "Scrape events from custom slug",
            "/scrape/city": "Scrape events from specific city",
            "/scrape/url": "Scrape single event from URL",
            "/export/json": "Export events to JSON",
            "/export/csv": "Export events to CSV"
        },
        "usage": {
            "GET /scrape/explore?keywords=web3,hackathon": "Scrape explore page with keyword filtering",
            "GET /scrape/custom?slug=web3&keywords=crypto": "Scrape custom slug with keywords",
            "GET /scrape/city?city=new-delhi&keywords=tech": "Scrape city events with keywords",
            "POST /scrape/url": "Scrape single event (send URL in JSON body)"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "luma-scraper-api"
    })

@app.route('/scrape/explore')
def scrape_explore():
    """
    Scrape events from Luma explore page
    
    Query Parameters:
    - keywords: Comma-separated keywords to filter events
    - headless: Boolean (default: true) - Run browser in headless mode
    - use_selenium: Boolean (default: true) - Use Selenium for JavaScript
    
    Returns:
    - JSON with scraped events
    """
    try:
        # Get query parameters
        keywords_str = request.args.get('keywords', '')
        keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else None
        
        headless = request.args.get('headless', 'true').lower() == 'true'
        use_selenium = request.args.get('use_selenium', 'true').lower() == 'true'
        
        # Get scraper instance
        scraper = get_scraper(headless=headless, use_selenium=use_selenium)
        
        # Scrape events
        logger.info(f"Scraping explore page with keywords: {keywords}")
        events = scraper.scrape_explore_page(keywords=keywords)
        
        return jsonify({
            "success": True,
            "message": f"Successfully scraped {len(events)} events",
            "count": len(events),
            "keywords": keywords,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error scraping explore page: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to scrape explore page"
        }), 500

@app.route('/scrape/custom')
def scrape_custom():
    """
    Scrape events from custom Luma slug
    
    Query Parameters:
    - slug: Custom slug to scrape (required)
    - keywords: Comma-separated keywords to filter events
    - headless: Boolean (default: true) - Run browser in headless mode
    - use_selenium: Boolean (default: true) - Use Selenium for JavaScript
    
    Returns:
    - JSON with scraped events
    """
    try:
        # Get query parameters
        slug = request.args.get('slug')
        if not slug:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: slug"
            }), 400
        
        keywords_str = request.args.get('keywords', '')
        keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else None
        
        headless = request.args.get('headless', 'true').lower() == 'true'
        use_selenium = request.args.get('use_selenium', 'true').lower() == 'true'
        
        # Get scraper instance
        scraper = get_scraper(headless=headless, use_selenium=use_selenium)
        
        # Scrape events
        logger.info(f"Scraping custom slug '{slug}' with keywords: {keywords}")
        events = scraper.scrape_custom_slug(slug, keywords=keywords)
        
        return jsonify({
            "success": True,
            "message": f"Successfully scraped {len(events)} events from slug '{slug}'",
            "count": len(events),
            "slug": slug,
            "keywords": keywords,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error scraping custom slug: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to scrape custom slug"
        }), 500

@app.route('/scrape/city')
def scrape_city():
    """
    Scrape events from specific city
    
    Query Parameters:
    - city: City name to scrape (required)
    - keywords: Comma-separated keywords to filter events
    - headless: Boolean (default: true) - Run browser in headless mode
    - use_selenium: Boolean (default: true) - Use Selenium for JavaScript
    
    Returns:
    - JSON with scraped events
    """
    try:
        # Get query parameters
        city = request.args.get('city')
        if not city:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: city"
            }), 400
        
        keywords_str = request.args.get('keywords', '')
        keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else None
        
        headless = request.args.get('headless', 'true').lower() == 'true'
        use_selenium = request.args.get('use_selenium', 'true').lower() == 'true'
        
        # Get scraper instance
        scraper = get_scraper(headless=headless, use_selenium=use_selenium)
        
        # Scrape events
        logger.info(f"Scraping city '{city}' with keywords: {keywords}")
        events = scraper.scrape_city_events(city, keywords=keywords)
        
        return jsonify({
            "success": True,
            "message": f"Successfully scraped {len(events)} events from city '{city}'",
            "count": len(events),
            "city": city,
            "keywords": keywords,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error scraping city: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to scrape city events"
        }), 500

@app.route('/scrape/url', methods=['POST'])
def scrape_single_url():
    """
    Scrape single event from URL
    
    Request Body (JSON):
    - url: Event URL to scrape (required)
    - headless: Boolean (default: true) - Run browser in headless mode
    - use_selenium: Boolean (default: true) - Use Selenium for JavaScript
    
    Returns:
    - JSON with scraped event data
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing JSON body"
            }), 400
        
        url = data.get('url')
        if not url:
            return jsonify({
                "success": False,
                "error": "Missing required field: url"
            }), 400
        
        headless = data.get('headless', True)
        use_selenium = data.get('use_selenium', True)
        
        # Get scraper instance
        scraper = get_scraper(headless=headless, use_selenium=use_selenium)
        
        # Scrape single event
        logger.info(f"Scraping single event from URL: {url}")
        event_data = scraper._extract_event_data_from_page(url)
        
        if not event_data:
            return jsonify({
                "success": False,
                "error": "Failed to extract event data from URL"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Successfully scraped event data",
            "event": event_data,
            "url": url,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error scraping single URL: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to scrape event from URL"
        }), 500

@app.route('/export/json', methods=['POST'])
def export_to_json():
    """
    Export events to JSON file
    
    Request Body (JSON):
    - events: List of event data (required)
    - filename: Optional filename (default: auto-generated)
    
    Returns:
    - JSON file download
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing JSON body"
            }), 400
        
        events = data.get('events')
        if not events:
            return jsonify({
                "success": False,
                "error": "Missing required field: events"
            }), 400
        
        filename = data.get('filename', f"luma_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to export to JSON"
        }), 500

@app.route('/export/csv', methods=['POST'])
def export_to_csv():
    """
    Export events to CSV file
    
    Request Body (JSON):
    - events: List of event data (required)
    - filename: Optional filename (default: auto-generated)
    
    Returns:
    - CSV file download
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing JSON body"
            }), 400
        
        events = data.get('events')
        if not events:
            return jsonify({
                "success": False,
                "error": "Missing required field: events"
            }), 400
        
        filename = data.get('filename', f"luma_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        # Import pandas here to avoid dependency issues
        import pandas as pd
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(events)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f, index=False, encoding='utf-8')
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to export to CSV"
        }), 500

@app.route('/batch', methods=['POST'])
def batch_scrape():
    """
    Batch scrape multiple sources
    
    Request Body (JSON):
    - sources: List of scraping configurations
      - type: "explore", "custom", "city", or "url"
      - params: Parameters for the scraping type
    - keywords: Optional global keywords to apply to all sources
    - headless: Boolean (default: true)
    - use_selenium: Boolean (default: true)
    
    Returns:
    - JSON with results from all sources
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing JSON body"
            }), 400
        
        sources = data.get('sources', [])
        if not sources:
            return jsonify({
                "success": False,
                "error": "Missing required field: sources"
            }), 400
        
        global_keywords = data.get('keywords')
        headless = data.get('headless', True)
        use_selenium = data.get('use_selenium', True)
        
        # Get scraper instance
        scraper = get_scraper(headless=headless, use_selenium=use_selenium)
        
        results = []
        total_events = 0
        
        for source in sources:
            source_type = source.get('type')
            params = source.get('params', {})
            
            try:
                if source_type == 'explore':
                    keywords = params.get('keywords', global_keywords)
                    events = scraper.scrape_explore_page(keywords=keywords)
                    
                elif source_type == 'custom':
                    slug = params.get('slug')
                    if not slug:
                        continue
                    keywords = params.get('keywords', global_keywords)
                    events = scraper.scrape_custom_slug(slug, keywords=keywords)
                    
                elif source_type == 'city':
                    city = params.get('city')
                    if not city:
                        continue
                    keywords = params.get('keywords', global_keywords)
                    events = scraper.scrape_city_events(city, keywords=keywords)
                    
                elif source_type == 'url':
                    url = params.get('url')
                    if not url:
                        continue
                    event_data = scraper._extract_event_data_from_page(url)
                    events = [event_data] if event_data else []
                    
                else:
                    continue
                
                results.append({
                    "type": source_type,
                    "params": params,
                    "count": len(events),
                    "events": events,
                    "success": True
                })
                
                total_events += len(events)
                
            except Exception as e:
                results.append({
                    "type": source_type,
                    "params": params,
                    "count": 0,
                    "events": [],
                    "success": False,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "message": f"Batch scraping completed. Total events: {total_events}",
            "total_events": total_events,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in batch scraping: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to perform batch scraping"
        }), 500

@app.route('/stats', methods=['POST'])
def get_stats():
    """
    Get statistics from scraped events
    
    Request Body (JSON):
    - events: List of event data (required)
    
    Returns:
    - JSON with statistics
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing JSON body"
            }), 400
        
        events = data.get('events', [])
        if not events:
            return jsonify({
                "success": False,
                "error": "Missing required field: events"
            }), 400
        
        # Calculate statistics
        total_events = len(events)
        
        # Location statistics
        locations = {}
        for event in events:
            location = event.get('location', 'Unknown')
            locations[location] = locations.get(location, 0) + 1
        
        # Organizer statistics
        organizers = {}
        for event in events:
            organizer = event.get('organizer_name', 'Unknown')
            organizers[organizer] = organizers.get(organizer, 0) + 1
        
        # Date statistics (basic)
        dates = {}
        for event in events:
            date_time = event.get('date_time', 'Unknown')
            dates[date_time] = dates.get(date_time, 0) + 1
        
        # Top locations and organizers
        top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_organizers = sorted(organizers.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            "success": True,
            "message": f"Statistics calculated for {total_events} events",
            "total_events": total_events,
            "unique_locations": len(locations),
            "unique_organizers": len(organizers),
            "top_locations": top_locations,
            "top_organizers": top_organizers,
            "location_distribution": locations,
            "organizer_distribution": organizers,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to calculate statistics"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

@app.teardown_appcontext
def cleanup(error):
    """Clean up resources when app context ends"""
    cleanup_scraper()

if __name__ == '__main__':
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 