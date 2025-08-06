#!/usr/bin/env python3
"""
Test script for Luma Event Scraper Bot

This script tests the scraper functionality with sample data and basic functionality.
"""

import json
import tempfile
import os
from luma_scraper import LumaScraper


def test_scraper_initialization():
    """Test scraper initialization"""
    print("Testing scraper initialization...")
    
    # Test with Selenium
    try:
        scraper = LumaScraper(headless=True, use_selenium=True)
        print("✓ Selenium scraper initialized successfully")
        scraper.close()
    except Exception as e:
        print(f"✗ Selenium scraper failed: {e}")
    
    # Test without Selenium
    try:
        scraper = LumaScraper(headless=True, use_selenium=False)
        print("✓ Requests-only scraper initialized successfully")
        scraper.close()
    except Exception as e:
        print(f"✗ Requests-only scraper failed: {e}")


def test_export_functions():
    """Test export functions with sample data"""
    print("\nTesting export functions...")
    
    sample_events = [
        {
            "event_name": "Ethereum India Hackathon",
            "date_time": "2025-08-12 18:00 IST",
            "location": "Bangalore, India",
            "organizer_name": "ETH India",
            "organizer_contact": "https://lu.ma/u/ethindia",
            "host_email": "contact@ethindia.org",
            "host_social_media": "twitter.com/ethindia, linkedin.com/company/ethindia",
            "event_url": "https://lu.ma/ethhackbangalore"
        },
        {
            "event_name": "Web3 Developer Meetup",
            "date_time": "2025-01-15 19:00 EST",
            "location": "New York, NY",
            "organizer_name": "Web3 NYC",
            "organizer_contact": "https://lu.ma/u/web3nyc",
            "host_email": "hello@web3nyc.com",
            "host_social_media": "twitter.com/web3nyc, instagram.com/web3nyc",
            "event_url": "https://lu.ma/web3meetup"
        },
        {
            "event_name": "Crypto Trading Workshop",
            "date_time": "2025-02-20 14:00 GMT",
            "location": "London, UK",
            "organizer_name": "Crypto Academy",
            "organizer_contact": "https://lu.ma/u/cryptoacademy",
            "host_email": "info@cryptoacademy.co.uk",
            "host_social_media": "linkedin.com/company/cryptoacademy, youtube.com/cryptoacademy",
            "event_url": "https://lu.ma/cryptoworkshop"
        }
    ]
    
    scraper = LumaScraper(use_selenium=False)
    
    # Test JSON export
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_json_file = f.name
        
        scraper.export_to_json(sample_events, temp_json_file)
        
        # Verify file was created and contains correct data
        with open(temp_json_file, 'r') as f:
            exported_data = json.load(f)
        
        if len(exported_data) == len(sample_events):
            print("✓ JSON export successful")
        else:
            print("✗ JSON export failed - data count mismatch")
        
        os.unlink(temp_json_file)
    except Exception as e:
        print(f"✗ JSON export failed: {e}")
    
    # Test CSV export
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_csv_file = f.name
        
        scraper.export_to_csv(sample_events, temp_csv_file)
        
        # Verify file was created
        if os.path.exists(temp_csv_file) and os.path.getsize(temp_csv_file) > 0:
            print("✓ CSV export successful")
        else:
            print("✗ CSV export failed - file not created or empty")
        
        os.unlink(temp_csv_file)
    except Exception as e:
        print(f"✗ CSV export failed: {e}")
    
    scraper.close()


def test_sample_output():
    """Display sample output format"""
    print("\nSample Output Format:")
    print("=" * 50)
    
    sample_event = {
        "event_name": "Ethereum India Hackathon",
        "date_time": "2025-08-12 18:00 IST",
        "location": "Bangalore, India",
        "organizer_name": "ETH India",
        "organizer_contact": "https://lu.ma/u/ethindia",
        "host_email": "contact@ethindia.org",
        "host_social_media": "twitter.com/ethindia, linkedin.com/company/ethindia",
        "event_url": "https://lu.ma/ethhackbangalore"
    }
    
    print(json.dumps(sample_event, indent=2))


def main():
    """Run all tests"""
    print("🧪 Luma Event Scraper Bot - Test Suite")
    print("=" * 50)
    
    test_scraper_initialization()
    test_export_functions()
    test_sample_output()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo run the actual scraper:")
    print("python luma_scraper.py --keywords Web3 Hackathon")
    print("\nFor more options:")
    print("python luma_scraper.py --help")


if __name__ == "__main__":
    main() 