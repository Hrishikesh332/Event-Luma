#!/usr/bin/env python3
"""
Test script for enhanced social media extraction

This script specifically tests the social media extraction from "hosted by" sections
and organizer profile pages.
"""

from luma_scraper import LumaScraper
import json
from datetime import datetime


def test_social_extraction():
    """Test the enhanced social media extraction"""
    print("🔗 Testing Enhanced Social Media Extraction")
    print("=" * 60)
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        # Test with a few events to see social media extraction
        print("🔍 Scraping events to test social media extraction...")
        
        # Try different sources to get variety
        sources = [
            ("explore", scraper.scrape_explore_page),
            ("custom web3", lambda: scraper.scrape_custom_slug("web3")),
            ("city mumbai", lambda: scraper.scrape_city_events("mumbai"))
        ]
        
        all_events = []
        
        for source_name, scrape_func in sources:
            print(f"\n📡 Testing source: {source_name}")
            events = scrape_func()
            
            if events:
                print(f"✅ Found {len(events)} events from {source_name}")
                all_events.extend(events[:3])  # Take first 3 from each source
            else:
                print(f"❌ No events found from {source_name}")
        
        if not all_events:
            print("❌ No events found to test social media extraction")
            return
        
        print(f"\n📊 Testing social media extraction on {len(all_events)} events")
        print("-" * 60)
        
        # Analyze social media extraction results
        events_with_social = 0
        total_social_links = 0
        social_platforms = {}
        
        for i, event in enumerate(all_events, 1):
            print(f"\n📋 Event {i}: {event['event_name']}")
            print(f"  Organizer: {event['organizer_name']}")
            print(f"  Contact URL: {event['organizer_contact']}")
            print(f"  Email: {event['host_email']}")
            print(f"  Phone: {event['host_phone']}")
            print(f"  Social Media: {event['host_social_media']}")
            
            # Count social media links
            if event['host_social_media'] != 'N/A':
                events_with_social += 1
                social_links = event['host_social_media'].split(', ')
                total_social_links += len(social_links)
                
                # Count platforms
                for link in social_links:
                    for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']:
                        if platform in link:
                            social_platforms[platform] = social_platforms.get(platform, 0) + 1
                            break
        
        # Print summary
        print("\n" + "=" * 60)
        print("📈 SOCIAL MEDIA EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"Total events analyzed: {len(all_events)}")
        print(f"Events with social media: {events_with_social}")
        print(f"Total social media links found: {total_social_links}")
        print(f"Average social links per event: {total_social_links/len(all_events):.1f}")
        
        if social_platforms:
            print(f"\n📱 Social Media Platforms Found:")
            for platform, count in sorted(social_platforms.items(), key=lambda x: x[1], reverse=True):
                print(f"  {platform}: {count} links")
        
        # Export detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {
            "summary": {
                "total_events": len(all_events),
                "events_with_social": events_with_social,
                "total_social_links": total_social_links,
                "average_social_links": total_social_links/len(all_events) if all_events else 0,
                "social_platforms": social_platforms
            },
            "events": all_events
        }
        
        with open(f"social_extraction_test_{timestamp}.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results exported to: social_extraction_test_{timestamp}.json")
        
    except Exception as e:
        print(f"❌ Error during social extraction test: {e}")
    finally:
        scraper.close()


def test_specific_event_social():
    """Test social extraction on a specific event URL"""
    print("\n🎯 Testing Specific Event Social Extraction")
    print("=" * 60)
    
    # You can add specific event URLs here to test
    test_urls = [
        # Add specific event URLs that you know have social media in hosted by section
    ]
    
    if not test_urls:
        print("No specific test URLs provided. Run the general test instead.")
        return
    
    scraper = LumaScraper(headless=True, use_selenium=False)
    
    try:
        for url in test_urls:
            print(f"\n🔍 Testing URL: {url}")
            event_data = scraper._extract_event_data_from_page(url)
            
            if event_data:
                print(f"✅ Event: {event_data['event_name']}")
                print(f"  Organizer: {event_data['organizer_name']}")
                print(f"  Social Media: {event_data['host_social_media']}")
            else:
                print(f"❌ Could not extract data from {url}")
    
    except Exception as e:
        print(f"❌ Error testing specific events: {e}")
    finally:
        scraper.close()


def main():
    """Run the social extraction tests"""
    print("🚀 Social Media Extraction Test Suite")
    print("=" * 60)
    print("This test focuses on extracting social media links from")
    print("'hosted by' sections and organizer profile pages.\n")
    
    test_social_extraction()
    test_specific_event_social()
    
    print("\n" + "=" * 60)
    print("✅ Social extraction tests completed!")
    print("\nTo test with real data:")
    print("python luma_scraper.py --city mumbai --keywords Web3")


if __name__ == "__main__":
    main() 