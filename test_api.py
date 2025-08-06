#!/usr/bin/env python3
"""
Test script for Luma Event Scraper API

This script demonstrates how to use the Flask API endpoints
and provides examples for testing the functionality.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_home():
    """Test home endpoint"""
    print("\n🔍 Testing home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"API Version: {data.get('version')}")
        print(f"Endpoints: {list(data.get('endpoints', {}).keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_explore():
    """Test explore page scraping"""
    print("\n🔍 Testing explore page scraping...")
    try:
        # Test without keywords
        response = requests.get(f"{BASE_URL}/scrape/explore")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Count: {data.get('count')}")
            print(f"Message: {data.get('message')}")
            
            # Show first event if available
            events = data.get('events', [])
            if events:
                print(f"First event: {events[0].get('event_name', 'N/A')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_explore_with_keywords():
    """Test explore page scraping with keywords"""
    print("\n🔍 Testing explore page scraping with keywords...")
    try:
        keywords = "web3,hackathon"
        response = requests.get(f"{BASE_URL}/scrape/explore?keywords={keywords}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Count: {data.get('count')}")
            print(f"Keywords: {data.get('keywords')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_custom():
    """Test custom slug scraping"""
    print("\n🔍 Testing custom slug scraping...")
    try:
        slug = "web3"
        response = requests.get(f"{BASE_URL}/scrape/custom?slug={slug}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Count: {data.get('count')}")
            print(f"Slug: {data.get('slug')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_city():
    """Test city scraping"""
    print("\n🔍 Testing city scraping...")
    try:
        city = "new-delhi"
        response = requests.get(f"{BASE_URL}/scrape/city?city={city}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Count: {data.get('count')}")
            print(f"City: {data.get('city')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_single_url():
    """Test single URL scraping"""
    print("\n🔍 Testing single URL scraping...")
    try:
        # Example URL (replace with actual Luma event URL)
        url = "https://lu.ma/event/example-event"
        
        payload = {
            "url": url,
            "headless": True,
            "use_selenium": True
        }
        
        response = requests.post(
            f"{BASE_URL}/scrape/url",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Event: {data.get('event', {}).get('event_name', 'N/A')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_batch_scraping():
    """Test batch scraping"""
    print("\n🔍 Testing batch scraping...")
    try:
        payload = {
            "sources": [
                {
                    "type": "explore",
                    "params": {"keywords": ["web3"]}
                },
                {
                    "type": "custom",
                    "params": {"slug": "hackathon"}
                }
            ],
            "keywords": ["tech"],
            "headless": True,
            "use_selenium": True
        }
        
        response = requests.post(
            f"{BASE_URL}/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total events: {data.get('total_events')}")
            print(f"Results count: {len(data.get('results', []))}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_export_json():
    """Test JSON export"""
    print("\n🔍 Testing JSON export...")
    try:
        # Sample events data
        sample_events = [
            {
                "event_name": "Sample Event 1",
                "date_time": "2024-01-01 10:00 AM",
                "location": "Sample Location",
                "organizer_name": "Sample Organizer",
                "event_url": "https://lu.ma/event/sample1"
            },
            {
                "event_name": "Sample Event 2",
                "date_time": "2024-01-02 2:00 PM",
                "location": "Another Location",
                "organizer_name": "Another Organizer",
                "event_url": "https://lu.ma/event/sample2"
            }
        ]
        
        payload = {
            "events": sample_events,
            "filename": "test_export.json"
        }
        
        response = requests.post(
            f"{BASE_URL}/export/json",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("JSON export successful")
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_export_csv():
    """Test CSV export"""
    print("\n🔍 Testing CSV export...")
    try:
        # Sample events data
        sample_events = [
            {
                "event_name": "Sample Event 1",
                "date_time": "2024-01-01 10:00 AM",
                "location": "Sample Location",
                "organizer_name": "Sample Organizer",
                "event_url": "https://lu.ma/event/sample1"
            },
            {
                "event_name": "Sample Event 2",
                "date_time": "2024-01-02 2:00 PM",
                "location": "Another Location",
                "organizer_name": "Another Organizer",
                "event_url": "https://lu.ma/event/sample2"
            }
        ]
        
        payload = {
            "events": sample_events,
            "filename": "test_export.csv"
        }
        
        response = requests.post(
            f"{BASE_URL}/export/csv",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("CSV export successful")
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stats():
    """Test statistics endpoint"""
    print("\n🔍 Testing statistics endpoint...")
    try:
        # Sample events data
        sample_events = [
            {
                "event_name": "Event 1",
                "location": "Location A",
                "organizer_name": "Organizer 1"
            },
            {
                "event_name": "Event 2",
                "location": "Location A",
                "organizer_name": "Organizer 2"
            },
            {
                "event_name": "Event 3",
                "location": "Location B",
                "organizer_name": "Organizer 1"
            }
        ]
        
        payload = {
            "events": sample_events
        }
        
        response = requests.post(
            f"{BASE_URL}/stats",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total events: {data.get('total_events')}")
            print(f"Unique locations: {data.get('unique_locations')}")
            print(f"Unique organizers: {data.get('unique_organizers')}")
            
            return True
        else:
            print(f"Error response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Luma Event Scraper API - Test Suite")
    print("=" * 50)
    
    # Check if API is running
    print("Checking if API is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("❌ API is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:5000")
        print("Start the API with: python app.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Home Endpoint", test_home),
        ("Explore Scraping", test_scrape_explore),
        ("Explore with Keywords", test_scrape_explore_with_keywords),
        ("Custom Slug Scraping", test_scrape_custom),
        ("City Scraping", test_scrape_city),
        ("Single URL Scraping", test_scrape_single_url),
        ("Batch Scraping", test_batch_scraping),
        ("JSON Export", test_export_json),
        ("CSV Export", test_export_csv),
        ("Statistics", test_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 