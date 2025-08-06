#!/usr/bin/env python3
"""
Demo script for Luma City Scraping Feature

This script demonstrates the new city-based scraping functionality
with enhanced contact information extraction.
"""

from luma_scraper import LumaScraper
import json
from datetime import datetime


def demo_city_scraping():
    """Demo the city scraping feature"""
    print("🌆 Luma City Scraping Demo")
    print("=" * 50)
    
    # List of cities to try
    cities = ["new-delhi", "mumbai", "bangalore", "hyderabad", "chennai"]
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        for city in cities:
            print(f"\n📍 Scraping events from: {city}")
            print("-" * 30)
            
            # Scrape events from city
            events = scraper.scrape_city_events(city)
            
            if events:
                print(f"✅ Found {len(events)} events in {city}")
                
                # Show first event with enhanced contact info
                event = events[0]
                print(f"\n📅 Sample Event:")
                print(f"  Name: {event['event_name']}")
                print(f"  Date: {event['date_time']}")
                print(f"  Location: {event['location']}")
                print(f"  Organizer: {event['organizer_name']}")
                print(f"  Contact URL: {event['organizer_contact']}")
                print(f"  Email: {event['host_email']}")
                print(f"  Social Media: {event['host_social_media']}")
                
                # Export city-specific results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"city_{city}_{timestamp}.json"
                scraper.export_to_json(events, filename)
                print(f"💾 Exported to: {filename}")
            else:
                print(f"❌ No events found in {city}")
            
            print("-" * 30)
    
    except Exception as e:
        print(f"Error during city scraping: {e}")
    finally:
        scraper.close()


def demo_enhanced_contact_extraction():
    """Demo the enhanced contact information extraction"""
    print("\n📞 Enhanced Contact Information Demo")
    print("=" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Try to scrape from explore page to show contact extraction
        print("🔍 Scraping from explore page to demonstrate contact extraction...")
        events = scraper.scrape_explore_page()
        
        if events:
            print(f"✅ Found {len(events)} events")
            
            # Show events with contact information
            for i, event in enumerate(events[:3], 1):
                print(f"\n📋 Event {i}:")
                print(f"  Name: {event['event_name']}")
                print(f"  Organizer: {event['organizer_name']}")
                print(f"  Contact URL: {event['organizer_contact']}")
                print(f"  Email: {event['host_email']}")
                print(f"  Social Media: {event['host_social_media']}")
        else:
            print("❌ No events found")
    
    except Exception as e:
        print(f"Error during contact extraction demo: {e}")
    finally:
        scraper.close()


def main():
    """Run the demo"""
    print("🚀 Luma Event Scraper - City Scraping Demo")
    print("=" * 60)
    print("This demo showcases the new city-based scraping feature")
    print("and enhanced contact information extraction.\n")
    
    # Run demos
    demo_city_scraping()
    demo_enhanced_contact_extraction()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("\nTo use the city scraping feature:")
    print("python luma_scraper.py --city new-delhi")
    print("\nTo scrape with keywords:")
    print("python luma_scraper.py --city mumbai --keywords Web3")


if __name__ == "__main__":
    main() 