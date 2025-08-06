#!/usr/bin/env python3
"""
Test script for improved regex patterns

This script tests the enhanced regex patterns for extracting
dates, times, locations, and organizers from event pages.
"""

import re


def test_date_patterns():
    """Test date extraction patterns"""
    print("📅 Testing Date Patterns")
    print("=" * 40)
    
    # Test cases for dates
    test_dates = [
        "Monday 6 October",
        "Friday 15th March",
        "Sunday, 22nd December",
        "6 October",
        "15th March",
        "22nd December",
        "October 6",
        "March 15th",
        "December 22nd",
        "2024-10-06",
        "06/10/2024",
        "10/06/2024",
        "Today",
        "Tomorrow",
        "Yesterday"
    ]
    
    # Date patterns
    date_patterns = [
        # Day + Date formats: "Monday 6 October", "Friday 15th March", "Sunday, 22nd December"
        r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,\s]+(\d{1,2})(?:st|nd|rd|th)?[,\s]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
        # Date + Month formats: "6 October", "15th March", "22nd December"
        r'\b(\d{1,2})(?:st|nd|rd|th)?[,\s]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
        # Month + Date formats: "October 6", "March 15th", "December 22nd"
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+(\d{1,2})(?:st|nd|rd|th)?\b',
        # ISO-like formats: "2024-10-06", "06/10/2024", "10/06/2024"
        r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
        # Today, Tomorrow, Yesterday
        r'\b(Today|Tomorrow|Yesterday)\b'
    ]
    
    for test_date in test_dates:
        found = False
        for pattern in date_patterns:
            match = re.search(pattern, test_date, re.IGNORECASE)
            if match:
                if isinstance(match.groups(), tuple):
                    result = ' '.join(match.groups()).strip()
                else:
                    result = match.group()
                print(f"✅ '{test_date}' -> '{result}'")
                found = True
                break
        if not found:
            print(f"❌ '{test_date}' -> No match")


def test_time_patterns():
    """Test time extraction patterns"""
    print("\n⏰ Testing Time Patterns")
    print("=" * 40)
    
    # Test cases for times
    test_times = [
        "10:00 - 19:00",
        "9:30 AM - 5:00 PM",
        "14:30-16:45",
        "10:00 AM",
        "14:30",
        "9:30 PM",
        "10 AM - 5 PM",
        "9:30 AM to 6:00 PM",
        "14:00-16:00",
        "09:30 - 17:45"
    ]
    
    # Time patterns
    time_patterns = [
        # Standard time formats: "10:00 - 19:00", "9:30 AM - 5:00 PM", "14:30-16:45"
        r'\b(\d{1,2}):(\d{2})(?:\s*(AM|PM|am|pm))?\s*[-–—]\s*(\d{1,2}):(\d{2})(?:\s*(AM|PM|am|pm))?\b',
        # Single time: "10:00 AM", "14:30", "9:30 PM"
        r'\b(\d{1,2}):(\d{2})(?:\s*(AM|PM|am|pm))?\b',
        # Time ranges without colons: "10 AM - 5 PM", "9:30 AM to 6:00 PM"
        r'\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\s*[-–—to]\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b',
        # 24-hour format: "14:00-16:00", "09:30 - 17:45"
        r'\b(\d{2}):(\d{2})\s*[-–—]\s*(\d{2}):(\d{2})\b'
    ]
    
    for test_time in test_times:
        found = False
        for pattern in time_patterns:
            match = re.search(pattern, test_time, re.IGNORECASE)
            if match:
                if isinstance(match.groups(), tuple):
                    result = ' '.join(match.groups()).strip()
                else:
                    result = match.group()
                print(f"✅ '{test_time}' -> '{result}'")
                found = True
                break
        if not found:
            print(f"❌ '{test_time}' -> No match")


def test_location_patterns():
    """Test location extraction patterns"""
    print("\n📍 Testing Location Patterns")
    print("=" * 40)
    
    # Test cases for locations
    test_locations = [
        "📍 New York",
        "🏢 Office Building",
        "at New York",
        "at 123 Main St",
        "at Conference Center",
        "in Mumbai",
        "in the conference room",
        "in Building A",
        "venue: New York",
        "Venue: Conference Center",
        "location: Mumbai",
        "Location: Office Building",
        "where: New York",
        "Where: Conference Center",
        "123 Main St",
        "Building A, Floor 3",
        "New York, NY",
        "Mumbai, India",
        "London, UK",
        "Conference Room A",
        "Building 3",
        "Floor 2",
        "Online",
        "Virtual",
        "Zoom",
        "Google Meet"
    ]
    
    # Location patterns
    location_patterns = [
        # Emoji patterns: "📍 New York", "🏢 Office Building"
        r'[📍🏢🏛️🏪🏬🏭🏮🏯🏰🏱🏲🏳️🏴🏵️🏶🏷️🏸🏹🏺🏻🏼🏽🏾🏿]\s*([^,\n\r]{3,50})',
        # "at" patterns: "at New York", "at 123 Main St", "at Conference Center"
        r'\bat\s+([^,\n\r]{3,50})\b',
        # "in" patterns: "in Mumbai", "in the conference room", "in Building A"
        r'\bin\s+([^,\n\r]{3,50})\b',
        # "venue" patterns: "venue: New York", "Venue: Conference Center"
        r'\bvenue:?\s*([^,\n\r]{3,50})\b',
        # "location" patterns: "location: Mumbai", "Location: Office Building"
        r'\blocation:?\s*([^,\n\r]{3,50})\b',
        # "where" patterns: "where: New York", "Where: Conference Center"
        r'\bwhere:?\s*([^,\n\r]{3,50})\b',
        # Address patterns: "123 Main St", "Building A, Floor 3"
        r'\b(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Place|Pl|Court|Ct|Way|Terrace|Ter|Circle|Cir|Square|Sq|Highway|Hwy|Parkway|Pkwy|Alley|Aly|Bend|Bluff|Branch|Br|Bridge|Brg|Brook|Burg|Center|Ctr|Creek|Crescent|Crest|Crossing|Xing|Dale|Dam|Divide|Div|Estates|Exp|Extension|Ext|Falls|Ferry|Field|Forest|Fork|Fort|Gardens|Glen|Green|Grove|Heights|Hills|Hollow|Inlet|Island|Isle|Junction|Jct|Lake|Landing|Lights|Lodge|Loop|Manor|Meadows|Mills|Mission|Mount|Mountain|Mtn|Neck|Orchard|Park|Pass|Path|Pike|Pine|Plains|Plaza|Point|Port|Prairie|Ranch|Rapid|Rest|Ridge|River|Shoals|Shore|Springs|Spur|Station|Summit|Swamp|Trace|Trail|Tunnel|Turnpike|Underpass|Union|Valley|Viaduct|View|Village|Ville|Vista|Walk|Wall|Way|Well|Wells|Woods|Yard|Yards|Zone|Zoo))\b',
        # City patterns: "New York, NY", "Mumbai, India", "London, UK"
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b',
        # Building/Room patterns: "Conference Room A", "Building 3", "Floor 2"
        r'\b(?:Conference\s+Room|Building|Floor|Room|Hall|Auditorium|Theater|Theatre|Center|Centre|Office|Studio|Workshop|Lab|Laboratory|Classroom|Meeting\s+Room)\s+[A-Za-z0-9\s]+\b',
        # Online/Virtual patterns: "Online", "Virtual", "Zoom", "Google Meet"
        r'\b(Online|Virtual|Zoom|Google\s+Meet|Microsoft\s+Teams|Webinar|Web\s+Event|Digital\s+Event|Remote\s+Event)\b'
    ]
    
    for test_location in test_locations:
        found = False
        for pattern in location_patterns:
            match = re.search(pattern, test_location, re.IGNORECASE)
            if match:
                if isinstance(match.groups(), tuple):
                    result = ' '.join(match.groups()).strip()
                else:
                    result = match.group()
                print(f"✅ '{test_location}' -> '{result}'")
                found = True
                break
        if not found:
            print(f"❌ '{test_location}' -> No match")


def test_organizer_patterns():
    """Test organizer extraction patterns"""
    print("\n👤 Testing Organizer Patterns")
    print("=" * 40)
    
    # Test cases for organizers
    test_organizers = [
        "hosted by: ETH Global",
        "organizer: Web3 NYC",
        "creator: Crypto Academy",
        "by ETH India",
        "presented by: Blockchain Foundation",
        "sponsored by: Tech Corp"
    ]
    
    # Organizer patterns
    organizer_patterns = [
        r'hosted\s+by\s*:?\s*([^,\n\r]{2,50})',
        r'organizer\s*:?\s*([^,\n\r]{2,50})',
        r'creator\s*:?\s*([^,\n\r]{2,50})',
        r'by\s+([^,\n\r]{2,50})',
        r'presented\s+by\s*:?\s*([^,\n\r]{2,50})',
        r'sponsored\s+by\s*:?\s*([^,\n\r]{2,50})'
    ]
    
    for test_organizer in test_organizers:
        found = False
        for pattern in organizer_patterns:
            match = re.search(pattern, test_organizer, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"✅ '{test_organizer}' -> '{result}'")
                found = True
                break
        if not found:
            print(f"❌ '{test_organizer}' -> No match")


def main():
    """Run all pattern tests"""
    print("🧪 Regex Pattern Testing Suite")
    print("=" * 50)
    print("Testing improved regex patterns for event data extraction\n")
    
    test_date_patterns()
    test_time_patterns()
    test_location_patterns()
    test_organizer_patterns()
    
    print("\n" + "=" * 50)
    print("✅ All pattern tests completed!")
    print("\nThese patterns will be used by the scraper to extract:")
    print("- Dates: Monday 6 October, 2024-10-06, etc.")
    print("- Times: 10:00 - 19:00, 9:30 AM - 5:00 PM, etc.")
    print("- Locations: 📍 New York, at Conference Center, Online, etc.")
    print("- Organizers: hosted by ETH Global, organizer: Web3 NYC, etc.")


if __name__ == "__main__":
    main() 