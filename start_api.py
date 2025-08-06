#!/usr/bin/env python3
"""
Startup script for Luma Event Scraper API

This script provides an easy way to start the Flask API with proper configuration
and helpful startup messages.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-cors',
        'requests',
        'beautifulsoup4',
        'selenium',
        'pandas',
        'lxml',
        'webdriver-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_chrome():
    """Check if Chrome/Chromium is available for Selenium"""
    print("\n🔍 Checking Chrome/Chromium installation...")
    
    # Common Chrome/Chromium paths
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️  Chrome/Chromium not found in common locations")
        print("Selenium may not work properly. Install Chrome or Chromium.")
        print("On Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("On macOS: brew install --cask google-chrome")
        print("On Windows: Download from https://www.google.com/chrome/")
    
    return chrome_found

def create_env_file():
    """Create a .env file with default configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("\n📝 Creating .env file with default configuration...")
        
        env_content = """# Luma Scraper API Configuration
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Scraper Configuration
DEFAULT_HEADLESS=true
DEFAULT_USE_SELENIUM=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=luma_scraper.log

# Rate Limiting (seconds between requests)
REQUEST_DELAY=1

# Export Settings
MAX_EVENTS_PER_REQUEST=50
TEMP_FILE_CLEANUP=true
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def start_api():
    """Start the Flask API"""
    print("\n🚀 Starting Luma Event Scraper API...")
    print("=" * 50)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found in current directory")
        print("Make sure you're in the correct directory")
        return False
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'true')
    
    try:
        # Import and run the app
        from app import app
        
        print("✅ Flask app imported successfully")
        print(f"🌐 API will be available at: http://localhost:5000")
        print(f"📚 API Documentation: http://localhost:5000/")
        print(f"❤️  Health Check: http://localhost:5000/health")
        print("\n" + "="*50)
        print("🎯 API Endpoints:")
        print("  GET  /                    - API Documentation")
        print("  GET  /health              - Health Check")
        print("  GET  /scrape/explore      - Scrape explore page")
        print("  GET  /scrape/custom       - Scrape custom slug")
        print("  GET  /scrape/city         - Scrape city events")
        print("  POST /scrape/url          - Scrape single event")
        print("  POST /batch               - Batch scraping")
        print("  POST /export/json         - Export to JSON")
        print("  POST /export/csv          - Export to CSV")
        print("  POST /stats               - Get statistics")
        print("="*50)
        print("\n💡 Usage Examples:")
        print("  curl http://localhost:5000/scrape/explore")
        print("  curl http://localhost:5000/scrape/custom?slug=web3")
        print("  curl http://localhost:5000/scrape/city?city=new-delhi")
        print("\n🛑 Press Ctrl+C to stop the API")
        print("="*50)
        
        # Start the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid duplicate scrapers
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False

def main():
    """Main function"""
    print("🎯 Luma Event Scraper API - Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Check Chrome
    check_chrome()
    
    # Create .env file if needed
    create_env_file()
    
    # Start the API
    try:
        start_api()
    except KeyboardInterrupt:
        print("\n\n🛑 API stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 