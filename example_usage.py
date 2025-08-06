#!/usr/bin/env python3
"""
Example usage of Luma Event Scraper Bot

This script demonstrates how to use the scraper programmatically
for different use cases.
"""

from luma_scraper import LumaScraper
import json
from datetime import datetime


def example_basic_scraping():
    """Example: Basic scraping from explore page"""
    print("🔍 Example 1: Basic scraping from explore page")
    print("-" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Scrape events from explore page
        events = scraper.scrape_explore_page()
        
        print(f"Found {len(events)} events")
        
        # Display first 3 events
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            print(f"  Name: {event['event_name']}")
            print(f"  Date: {event['date_time']}")
            print(f"  Location: {event['location']}")
            print(f"  Organizer: {event['organizer_name']}")
        
        # Export to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.export_to_json(events, f"example_basic_{timestamp}.json")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_keyword_filtering():
    """Example: Filtering events by keywords"""
    print("\n🔍 Example 2: Filtering events by keywords")
    print("-" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Keywords to filter for
        keywords = ["Web3", "Hackathon", "Crypto"]
        
        # Scrape events with keyword filtering
        events = scraper.scrape_explore_page(keywords=keywords)
        
        print(f"Found {len(events)} events matching keywords: {keywords}")
        
        # Display filtered events
        for i, event in enumerate(events[:5], 1):
            print(f"\nEvent {i}:")
            print(f"  Name: {event['event_name']}")
            print(f"  Date: {event['date_time']}")
            print(f"  Location: {event['location']}")
        
        # Export to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.export_to_csv(events, f"example_keywords_{timestamp}.csv")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_custom_slug():
    """Example: Scraping from custom slug"""
    print("\n🔍 Example 3: Scraping from custom slug")
    print("-" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Custom slug to scrape
        slug = "web3"
        
        # Scrape events from custom slug
        events = scraper.scrape_custom_slug(slug)
        
        print(f"Found {len(events)} events from slug: {slug}")
        
        # Display events
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            print(f"  Name: {event['event_name']}")
            print(f"  Date: {event['date_time']}")
            print(f"  Organizer: {event['organizer_name']}")
        
        # Export to both formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.export_to_json(events, f"example_slug_{timestamp}.json")
        scraper.export_to_csv(events, f"example_slug_{timestamp}.csv")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_city_scraping():
    """Example: Scraping events from a specific city"""
    print("\n🔍 Example 4: Scraping events from a specific city")
    print("-" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # City to scrape
        city = "new-delhi"
        
        # Scrape events from city
        events = scraper.scrape_city_events(city)
        
        print(f"Found {len(events)} events from city: {city}")
        
        # Display events with enhanced contact info
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            print(f"  Name: {event['event_name']}")
            print(f"  Date: {event['date_time']}")
            print(f"  Location: {event['location']}")
            print(f"  Organizer: {event['organizer_name']}")
            print(f"  Email: {event['host_email']}")
            print(f"  Social Media: {event['host_social_media']}")
        
        # Export to both formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.export_to_json(events, f"example_city_{timestamp}.json")
        scraper.export_to_csv(events, f"example_city_{timestamp}.csv")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_data_analysis():
    """Example: Basic data analysis of scraped events"""
    print("\n📊 Example 5: Basic data analysis")
    print("-" * 50)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Scrape events
        events = scraper.scrape_explore_page()
        
        if not events:
            print("No events found for analysis")
            return
        
        # Basic statistics
        print(f"Total events found: {len(events)}")
        
        # Count events by location
        locations = {}
        for event in events:
            location = event['location']
            locations[location] = locations.get(location, 0) + 1
        
        print(f"\nEvents by location:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {location}: {count} events")
        
        # Count events by organizer
        organizers = {}
        for event in events:
            organizer = event['organizer_name']
            organizers[organizer] = organizers.get(organizer, 0) + 1
        
        print(f"\nTop organizers:")
        for organizer, count in sorted(organizers.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {organizer}: {count} events")
        
        # Export analysis results
        analysis_data = {
            "total_events": len(events),
            "locations": locations,
            "organizers": organizers,
            "events": events
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\nAnalysis exported to: analysis_{timestamp}.json")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def main():
    """Run all examples"""
    print("🚀 Luma Event Scraper Bot - Example Usage")
    print("=" * 60)
    
    # Note: These examples might not find events if the website structure changes
    # or if there are no events matching the criteria
    
    print("Note: These examples demonstrate the scraper functionality.")
    print("Actual results may vary depending on current Luma content.\n")
    
    # Run examples
    example_basic_scraping()
    example_keyword_filtering()
    example_custom_slug()
    example_city_scraping()
    example_data_analysis()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("\nCheck the generated files for results:")
    print("- example_basic_*.json")
    print("- example_keywords_*.csv")
    print("- example_slug_*.json/csv")
    print("- example_city_*.json/csv")
    print("- analysis_*.json")


if __name__ == "__main__":
    main() 