#!/usr/bin/env python3
"""
Test script for the wake-up scheduler functionality
"""

import os
import requests
from datetime import datetime

def test_wake_up_app():
    """Test the wake-up function"""
    try:
        app_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000/health')
        if app_url:
            print(f"Testing wake-up function with URL: {app_url}")
            response = requests.get(app_url)
            if response.status_code == 200:
                print(f"✅ Successfully pinged {app_url} at {datetime.now()}")
                return True
            else:
                print(f"❌ Failed to ping {app_url} (status code: {response.status_code}) at {datetime.now()}")
                return False
        else:
            print("⚠️  APP_URL environment variable not set.")
            return False
    except Exception as e:
        print(f"❌ Error occurred while pinging app: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing wake-up scheduler functionality...")
    success = test_wake_up_app()
    if success:
        print("✅ Wake-up function is working correctly!")
    else:
        print("❌ Wake-up function failed!") 