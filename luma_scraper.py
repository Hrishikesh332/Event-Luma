import requests
import json
import pandas as pd
import argparse
import time
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('luma_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LumaScraper:
    """
    Main scraper class for extracting event data from Luma
    """
    
    def __init__(self, headless: bool = True, use_selenium: bool = True):
        """
        Initialize the Luma scraper
        
        Args:
            headless (bool): Run browser in headless mode
            use_selenium (bool): Use Selenium for JavaScript-heavy pages
        """
        self.base_url = "https://lu.ma"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.use_selenium = use_selenium
        self.driver = None
        
        if use_selenium:
            self._setup_selenium(headless)
    
    def _setup_selenium(self, headless: bool):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        Get page content using either requests or Selenium
        
        Args:
            url (str): URL to fetch
            
        Returns:
            Optional[str]: Page content or None if failed
        """
        if self.use_selenium and self.driver:
            try:
                self.driver.get(url)
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)  # Additional wait for dynamic content
                return self.driver.page_source
            except TimeoutException:
                logger.warning(f"Timeout loading page: {url}")
                return None
            except Exception as e:
                logger.error(f"Selenium error for {url}: {e}")
                return None
        else:
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                return None
    
    def _extract_event_data_from_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract event data from a single event page
        
        Args:
            url (str): Event page URL
            
        Returns:
            Optional[Dict[str, Any]]: Extracted event data
        """
        content = self._get_page_content(url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        event_data = {
            'event_name': '',
            'date_time': '',
            'location': '',
            'organizer_name': '',
            'organizer_contact': '',
            'host_email': '',
            'host_social_media': '',
            'event_url': url
        }
        
        try:
            # Extract event name
            name_selectors = [
                'h1[data-testid="event-title"]',
                'h1.event-title',
                'h1.title',
                'h1',
                '[data-testid="event-name"]',
                '[class*="title"]'
            ]
            
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    event_data['event_name'] = name_elem.get_text(strip=True)
                    break
            
            # Extract date and time using regex patterns
            page_text = soup.get_text()
            
            # Date patterns - comprehensive regex for various date formats
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
            
            # Time patterns - comprehensive regex for various time formats
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
            
            # Find dates
            found_dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        date_str = ' '.join(match).strip()
                    else:
                        date_str = match.strip()
                    if date_str and len(date_str) > 3:  # Filter out very short matches
                        found_dates.append(date_str)
            
            # Find times
            found_times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        time_str = ' '.join(match).strip()
                    else:
                        time_str = match.strip()
                    if time_str and len(time_str) > 3:  # Filter out very short matches
                        found_times.append(time_str)
            
            # Combine date and time
            if found_dates and found_times:
                # Take the first date and first time found
                event_data['date_time'] = f"{found_dates[0]} {found_times[0]}"
            elif found_dates:
                event_data['date_time'] = found_dates[0]
            elif found_times:
                event_data['date_time'] = found_times[0]
            
            # Clean up the date_time if it exists
            if event_data['date_time']:
                event_data['date_time'] = self._clean_datetime(event_data['date_time'])
            
            # If still no date/time found, try the old selector method as fallback
            if not event_data['date_time']:
                date_selectors = [
                    '[data-testid="event-date"]',
                    '.event-date',
                    '.date',
                    '[class*="date"]',
                    '[class*="time"]',
                    '[class*="datetime"]',
                    '[class*="title"]',
                    '[class*="desc"]'
                ]
                
                for selector in date_selectors:
                    date_elem = soup.select_one(selector)
                    if date_elem:
                        event_data['date_time'] = date_elem.get_text(strip=True)
                        break
            
            # Extract location using regex patterns
            # Location patterns - more precise regex for various location formats
            location_patterns = [
                # Emoji patterns: "📍 New York" - more precise
                r'[📍🏢🏛️🏪🏬🏭🏮🏯🏰🏱🏲🏳️🏴🏵️🏶🏷️🏸🏹🏺🏻🏼🏽🏾🏿]\s*([A-Za-z\s]+(?:[A-Za-z]+))',
                # "at" patterns: "at New York" - more precise
                r'\bat\s+([A-Za-z\s]+(?:[A-Za-z]+))',
                # "in" patterns: "in Mumbai" - more precise
                r'\bin\s+([A-Za-z\s]+(?:[A-Za-z]+))',
                # "venue" patterns: "venue: New York" - more precise
                r'\bvenue:?\s*([A-Za-z\s]+(?:[A-Za-z]+))',
                # "location" patterns: "location: Mumbai" - more precise
                r'\blocation:?\s*([A-Za-z\s]+(?:[A-Za-z]+))',
                # "where" patterns: "where: New York" - more precise
                r'\bwhere:?\s*([A-Za-z\s]+(?:[A-Za-z]+))',
                # City patterns: "New York, NY", "Mumbai, India", "London, UK"
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b',
                # Building/Room patterns: "Conference Room A", "Building 3", "Floor 2"
                r'\b(?:Conference\s+Room|Building|Floor|Room|Hall|Auditorium|Theater|Theatre|Center|Centre|Office|Studio|Workshop|Lab|Laboratory|Classroom|Meeting\s+Room)\s+[A-Za-z0-9\s]+\b',
                # Online/Virtual patterns: "Online", "Virtual", "Zoom", "Google Meet"
                r'\b(Online|Virtual|Zoom|Google\s+Meet|Microsoft\s+Teams|Webinar|Web\s+Event|Digital\s+Event|Remote\s+Event)\b',
                # Simple city names: "New Delhi", "Mumbai", "Bangalore"
                r'\b(New\s+Delhi|Delhi|Mumbai|Bangalore|Chennai|Hyderabad|Kolkata|Pune|Ahmedabad|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Thane|Bhopal|Visakhapatnam|Pimpri-Chinchwad|Patna|Vadodara|Ghaziabad|Ludhiana|Agra|Nashik|Faridabad|Meerut|Rajkot|Kalyan-Dombivli|Vasai-Virar|Varanasi|Srinagar|Aurangabad|Dhanbad|Amritsar|Allahabad|Ranchi|Howrah|Coimbatore|Jabalpur|Gwalior|Vijayawada|Jodhpur|Madurai|Raipur|Kota|Guwahati|Chandigarh|Solapur|Hubli-Dharwad|Bareilly|Moradabad|Mysore|Gurgaon|Aligarh|Jalandhar|Tiruchirappalli|Bhubaneswar|Salem|Warangal|Mira-Bhayandar|Thiruvananthapuram|Bhiwandi|Saharanpur|Gorakhpur|Guntur|Bikaner|Amravati|Noida|Jamshedpur|Bhilai|Cuttack|Firozabad|Kochi|Nellore|Bhavnagar|Dehradun|Durgapur|Asansol|Rourkela|Nanded|Kolhapur|Ajmer|Akola|Gulbarga|Jamnagar|Ujjain|Loni|Siliguri|Jhansi|Ulhasnagar|Jammu|Sangli-Miraj|Mangalore|Erode|Belgaum|Ambattur|Tirunelveli|Malegaon|Gaya|Jalgaon|Udaipur|Maheshtala|Tirupur|Davanagere|Kozhikode|Kurnool|Rajpur|Sonarpur|Bokaro|South\s+Dumdum|Bellary|Patiala|Gopalpur|Agartala|Bhagalpur|Muzaffarnagar|Bhatpara|Panihati|Latur|Dhule|Rohtak|Korba|Bhilwara|Berhampur|Muzaffarpur|Ahmednagar|Mathura|Kollam|Avadi|Kadapa|Kamarhati|Bilaspur|Shahjahanpur|Satara|Bijapur|Rampur|Shivamogga|Chandrapur|Junagadh|Thrissur|Alwar|Bardhaman|Kulti|Kakinada|Nizamabad|Parbhani|Tumkur|Hisar|Ozhukarai|Bihar\s+Sharif|Panipat|Darbhanga|Bally|Aizawl|Dewas|Ichalkaranji|Tirupati|Karnal|Bathinda|Rampur|Shivpuri|Rewa|Gondia|Hoshiarpur|Guna|Raichur|Rohtak|Korba|Bhilwara|Berhampur|Muzaffarpur|Ahmednagar|Mathura|Kollam|Avadi|Kadapa|Kamarhati|Bilaspur|Shahjahanpur|Satara|Bijapur|Rampur|Shivamogga|Chandrapur|Junagadh|Thrissur|Alwar|Bardhaman|Kulti|Kakinada|Nizamabad|Parbhani|Tumkur|Hisar|Ozhukarai|Bihar\s+Sharif|Panipat|Darbhanga|Bally|Aizawl|Dewas|Ichalkaranji|Tirupati|Karnal|Bathinda|Rampur|Shivpuri|Rewa|Gondia|Hoshiarpur|Guna|Raichur)\b'
            ]
            
            # Find locations
            found_locations = []
            for pattern in location_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        location_str = ' '.join(match).strip()
                    else:
                        location_str = match.strip()
                    if location_str and len(location_str) > 2 and len(location_str) < 100:  # Filter reasonable lengths
                        found_locations.append(location_str)
            
            # Take the first location found and clean it up
            if found_locations:
                location = found_locations[0]
                # Clean up the location
                location = self._clean_location(location)
                event_data['location'] = location
            
            # If no location found with regex, try the old selector method as fallback
            if not event_data['location'] or event_data['location'] == '':
                location_selectors = [
                    '[data-testid="event-location"]',
                    '.event-location',
                    '.location',
                    '[class*="location"]',
                    '[class*="venue"]',
                    '[class*="address"]',
                    '[class*="place"]',
                    '[class*="where"]'
                ]
                
                for selector in location_selectors:
                    loc_elem = soup.select_one(selector)
                    if loc_elem:
                        event_data['location'] = loc_elem.get_text(strip=True)
                        break
            
            # Enhanced organizer/host information extraction
            organizer_info = self._extract_organizer_info(soup)
            event_data.update(organizer_info)
            
            # Clean up empty values
            for key in event_data:
                if event_data[key] == '':
                    event_data[key] = 'N/A'
            
            return event_data
            
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {e}")
            return None
    
    def _extract_organizer_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract comprehensive organizer/host information
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            Dict[str, str]: Organizer information
        """
        organizer_info = {
            'organizer_name': '',
            'organizer_contact': '',
            'host_email': '',
            'host_social_media': ''
        }
        
        # Extract organizer name using multiple approaches
        organizer_selectors = [
            '[data-testid="organizer-name"]',
            '.organizer-name',
            '.organizer',
            '[class*="organizer"]',
            '[class*="host"]',
            '[class*="creator"]',
            '[class*="by"]',
            'a[href*="/u/"]'
        ]
        
        # First try selectors
        for selector in organizer_selectors:
            org_elem = soup.select_one(selector)
            if org_elem:
                organizer_info['organizer_name'] = self._clean_organizer(org_elem.get_text(strip=True))
                # Try to get organizer contact URL
                if org_elem.name == 'a' and org_elem.get('href'):
                    organizer_info['organizer_contact'] = urljoin(self.base_url, org_elem['href'])
                break
        
        # If no organizer found, look for any link with /u/ pattern
        if not organizer_info['organizer_contact']:
            org_links = soup.find_all('a', href=re.compile(r'/u/'))
            if org_links:
                organizer_info['organizer_contact'] = urljoin(self.base_url, org_links[0]['href'])
                if not organizer_info['organizer_name']:
                    organizer_info['organizer_name'] = org_links[0].get_text(strip=True)
        
        # If still no organizer, try text-based patterns
        if not organizer_info['organizer_name']:
            # Look for "hosted by" patterns
            hosted_by_patterns = [
                r'hosted\s+by\s*:?\s*([^,\n\r]{2,50})',
                r'organizer\s*:?\s*([^,\n\r]{2,50})',
                r'creator\s*:?\s*([^,\n\r]{2,50})',
                r'by\s+([^,\n\r]{2,50})',
                r'presented\s+by\s*:?\s*([^,\n\r]{2,50})',
                r'sponsored\s+by\s*:?\s*([^,\n\r]{2,50})'
            ]
            
            for pattern in hosted_by_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    organizer_info['organizer_name'] = self._clean_organizer(match.group(1).strip())
                    break
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text_content = soup.get_text()
        emails = re.findall(email_pattern, text_content)
        if emails:
            organizer_info['host_email'] = emails[0]  # Take first email found
        

        
        # Extract social media links - improved for Luma's JSX structure
        social_links = []
        
        # Based on the screenshot, look for social-links container with JSX classes
        # The screenshot shows: class="jsx-9577fbf62c568ee1 social-links flex-center regular"
        social_containers = soup.find_all(['div', 'section'], class_=re.compile(r'social-links', re.I))
        
        for container in social_containers:
            # Find all links within social-links containers
            links = container.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                # Check for social media platforms
                if any(platform in href for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']):
                    social_links.append(href)
        
        # Also look for social-link individual containers (from screenshot: class="jsx-c1476e59a1b29a96 social-link regular")
        social_link_elements = soup.find_all(['div', 'span'], class_=re.compile(r'social-link', re.I))
        
        for element in social_link_elements:
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                if any(platform in href for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']):
                    social_links.append(href)
        
        # Look for social media links in organizer/host sections
        host_selectors = [
            '[class*="host"]',
            '[class*="organizer"]',
            '[class*="creator"]',
            '[class*="by"]',
            '[data-testid*="host"]',
            '[data-testid*="organizer"]',
            '[data-testid*="creator"]',
            '[class*="event-creator"]',
            '[class*="event-organizer"]',
            '[class*="event-host"]'
        ]
        
        for selector in host_selectors:
            host_sections = soup.select(selector)
            for section in host_sections:
                links = section.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '').lower()
                    if any(platform in href for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']):
                        social_links.append(href)
        
        # Look for any links near "hosted by" text
        hosted_by_elements = soup.find_all(['div', 'section', 'span', 'p'], string=re.compile(r'hosted by|organizer|creator', re.I))
        for element in hosted_by_elements:
            # Look in the same container and its children
            container = element.parent if element.parent else element
            links = container.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                if any(platform in href for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']):
                    social_links.append(href)
        
        # Also search entire page for social media patterns
        social_media_patterns = [
            r'https?://(?:www\.)?(x\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(twitter\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(instagram\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(facebook\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(linkedin\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(youtube\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(tiktok\.com/[^\s"<>]+)',
            r'https?://(?:www\.)?(github\.com/[^\s"<>]+)',
            r'https?://(?:discord\.gg/[^\s"<>]+)',
            r'https?://(?:t\.me/[^\s"<>]+)'
        ]
        
        for pattern in social_media_patterns:
            matches = re.findall(pattern, text_content)
            social_links.extend(matches)
        
        # Remove duplicates and clean up
        unique_social_links = list(set(social_links))
        
        if unique_social_links:
            organizer_info['host_social_media'] = ', '.join(unique_social_links[:5])  # Limit to 5 social links
        
        # Look for contact information in specific elements
        contact_selectors = [
            '[class*="contact"]',
            '[class*="email"]',
            '[class*="phone"]',
            '[class*="social"]',
            '[data-testid*="contact"]'
        ]
        
        for selector in contact_selectors:
            contact_elem = soup.select_one(selector)
            if contact_elem:
                contact_text = contact_elem.get_text(strip=True)
                
                # Check for email
                if not organizer_info['host_email'] and '@' in contact_text:
                    email_match = re.search(email_pattern, contact_text)
                    if email_match:
                        organizer_info['host_email'] = email_match.group()
                

        
        # If we have an organizer contact URL, try to extract more social media from their profile
        if organizer_info['organizer_contact'] and organizer_info['organizer_contact'] != 'N/A':
            profile_social_links = self._extract_social_from_profile(organizer_info['organizer_contact'])
            if profile_social_links:
                # Add profile social links to existing ones
                existing_social = organizer_info['host_social_media'].split(', ') if organizer_info['host_social_media'] != 'N/A' else []
                all_social = existing_social + profile_social_links
                unique_social = list(set(all_social))
                organizer_info['host_social_media'] = ', '.join(unique_social[:5])
        
        return organizer_info
    
    def _clean_location(self, location: str) -> str:
        """
        Clean up location text by removing unwanted content
        
        Args:
            location (str): Raw location text
            
        Returns:
            str: Cleaned location text
        """
        if not location:
            return location
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Date:.*?Time:.*?',  # Remove date/time info
            r'🕓.*?📍',  # Remove time emoji and location emoji
            r'Hosted by.*',  # Remove "Hosted by" text
            r'Venue:.*?​',  # Remove "Venue:" prefix
            r'Location:.*?​',  # Remove "Location:" prefix
            r'Contact us:.*',  # Remove contact info
            r'Email:.*',  # Remove email info
            r'Telegram.*',  # Remove telegram info
            r'Kickstart.*',  # Remove descriptive text
            r'We\'re also.*',  # Remove additional info
            r'Join our.*',  # Remove call-to-action
            r'Explore Events.*',  # Remove navigation text
            r'Sign.*',  # Remove sign text
            r'Report.*',  # Remove report text
            r'​.*',  # Remove special characters
            r'\.{2,}',  # Remove multiple dots
            r'\s+',  # Normalize whitespace
        ]
        
        cleaned = location
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace and trim
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove if too short or too long
        if len(cleaned) < 2 or len(cleaned) > 100:
            return 'N/A'
        
        return cleaned
    
    def _clean_datetime(self, datetime_str: str) -> str:
        """
        Clean up datetime text by removing unwanted content
        
        Args:
            datetime_str (str): Raw datetime text
            
        Returns:
            str: Cleaned datetime text
        """
        if not datetime_str:
            return datetime_str
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'GMT\+5:30',  # Remove timezone
            r'GMT\+[0-9:]+',  # Remove any GMT timezone
            r'UTC\+[0-9:]+',  # Remove any UTC timezone
            r'\s+',  # Normalize whitespace
        ]
        
        cleaned = datetime_str
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and trim
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove if too short
        if len(cleaned) < 3:
            return 'N/A'
        
        return cleaned
    
    def _clean_organizer(self, organizer: str) -> str:
        """
        Clean up organizer text by removing unwanted content
        
        Args:
            organizer (str): Raw organizer text
            
        Returns:
            str: Cleaned organizer text
        """
        if not organizer:
            return organizer
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'\.{2,}',  # Remove multiple dots
            r'\s+',  # Normalize whitespace
            r'Access Support',  # Remove common unwanted text
            r'LinkedOut \.',  # Remove unwanted suffixes
        ]
        
        cleaned = organizer
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and trim
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove if too short or too long
        if len(cleaned) < 2 or len(cleaned) > 100:
            return 'N/A'
        
        return cleaned
    
    def _extract_social_from_profile(self, profile_url: str) -> List[str]:
        """
        Extract social media links from organizer's profile page
        
        Args:
            profile_url (str): URL of the organizer's profile page
            
        Returns:
            List[str]: List of social media links found
        """
        try:
            content = self._get_page_content(profile_url)
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            social_links = []
            
            # Look for social media links in profile page
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '').lower()
                if any(platform in href for platform in ['x.com', 'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'github.com', 'discord.gg', 'telegram.me', 't.me']):
                    social_links.append(href)
            
            return social_links[:3]  # Limit to 3 from profile
            
        except Exception as e:
            logger.debug(f"Error extracting social from profile {profile_url}: {e}")
            return []
    
    def scrape_explore_page(self, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scrape events from Luma explore page
        
        Args:
            keywords (Optional[List[str]]): Keywords to filter events
            
        Returns:
            List[Dict[str, Any]]: List of event data
        """
        explore_url = f"{self.base_url}/explore"
        logger.info(f"Scraping explore page: {explore_url}")
        
        content = self._get_page_content(explore_url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        events = []
        
        # Look for event links
        event_links = []
        
        # Try different selectors for event links
        link_selectors = [
            'a[href*="/event/"]',
            'a[href*="/e/"]',
            '[data-testid="event-card"] a',
            '.event-card a',
            'a[class*="event"]'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            if links:
                event_links.extend(links)
                break
        
        # If no specific event links found, look for any links that might be events
        if not event_links:
            all_links = soup.find_all('a', href=True)
            event_links = [link for link in all_links if '/event/' in link['href'] or '/e/' in link['href']]
        
        logger.info(f"Found {len(event_links)} potential event links")
        
        for link in event_links[:20]:  # Limit to first 20 events for demo
            href = link.get('href')
            if not href:
                continue
            
            # Make URL absolute
            event_url = urljoin(self.base_url, href)
            
            # Skip if already processed
            if any(event['event_url'] == event_url for event in events):
                continue
            
            # Extract basic info from link text for filtering
            link_text = link.get_text(strip=True).lower()
            
            # Apply keyword filter if specified
            if keywords:
                if not any(keyword.lower() in link_text for keyword in keywords):
                    continue
            
            logger.info(f"Processing event: {event_url}")
            event_data = self._extract_event_data_from_page(event_url)
            
            if event_data:
                # Apply keyword filter to full event data
                if keywords:
                    event_text = f"{event_data['event_name']} {event_data['location']} {event_data['organizer_name']}".lower()
                    if any(keyword.lower() in event_text for keyword in keywords):
                        events.append(event_data)
                else:
                    events.append(event_data)
            
            # Rate limiting
            time.sleep(1)
        
        return events
    
    def scrape_custom_slug(self, slug: str, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scrape events from a custom Luma slug
        
        Args:
            slug (str): Custom slug (e.g., 'web3', 'hackathon', 'new-delhi')
            keywords (Optional[List[str]]): Additional keywords to filter events
            
        Returns:
            List[Dict[str, Any]]: List of event data
        """
        custom_url = f"{self.base_url}/{slug}"
        logger.info(f"Scraping custom slug: {custom_url}")
        
        content = self._get_page_content(custom_url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        events = []
        
        # Look for event links
        event_links = []
        
        # Try different selectors for event links
        link_selectors = [
            'a[href*="/event/"]',
            'a[href*="/e/"]',
            '[data-testid="event-card"] a',
            '.event-card a',
            'a[class*="event"]'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            if links:
                event_links.extend(links)
                break
        
        # If no specific event links found, look for any links that might be events
        if not event_links:
            all_links = soup.find_all('a', href=True)
            event_links = [link for link in all_links if '/event/' in link['href'] or '/e/' in link['href']]
        
        logger.info(f"Found {len(event_links)} potential event links")
        
        for link in event_links[:20]:  # Limit to first 20 events for demo
            href = link.get('href')
            if not href:
                continue
            
            # Make URL absolute
            event_url = urljoin(self.base_url, href)
            
            # Skip if already processed
            if any(event['event_url'] == event_url for event in events):
                continue
            
            logger.info(f"Processing event: {event_url}")
            event_data = self._extract_event_data_from_page(event_url)
            
            if event_data:
                # Apply keyword filter if specified
                if keywords:
                    event_text = f"{event_data['event_name']} {event_data['location']} {event_data['organizer_name']}".lower()
                    if any(keyword.lower() in event_text for keyword in keywords):
                        events.append(event_data)
                else:
                    events.append(event_data)
            
            # Rate limiting
            time.sleep(1)
        
        return events
    
    def scrape_city_events(self, city: str, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scrape events from a specific city page
        
        Args:
            city (str): City name (e.g., 'new-delhi', 'mumbai', 'bangalore')
            keywords (Optional[List[str]]): Additional keywords to filter events
            
        Returns:
            List[Dict[str, Any]]: List of event data
        """
        # Normalize city name for URL
        city_slug = city.lower().replace(' ', '-').replace('_', '-')
        city_url = f"{self.base_url}/{city_slug}"
        logger.info(f"Scraping city events: {city_url}")
        
        content = self._get_page_content(city_url)
        if not content:
            logger.warning(f"Could not access city page: {city_url}")
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        events = []
        
        # Look for event links
        event_links = []
        
        # Try different selectors for event links
        link_selectors = [
            'a[href*="/event/"]',
            'a[href*="/e/"]',
            '[data-testid="event-card"] a',
            '.event-card a',
            'a[class*="event"]',
            '[class*="event"] a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            if links:
                event_links.extend(links)
                break
        
        # If no specific event links found, look for any links that might be events
        if not event_links:
            all_links = soup.find_all('a', href=True)
            event_links = [link for link in all_links if '/event/' in link['href'] or '/e/' in link['href']]
        
        logger.info(f"Found {len(event_links)} potential event links in {city}")
        
        for link in event_links[:30]:  # Increased limit for city pages
            href = link.get('href')
            if not href:
                continue
            
            # Make URL absolute
            event_url = urljoin(self.base_url, href)
            
            # Skip if already processed
            if any(event['event_url'] == event_url for event in events):
                continue
            
            logger.info(f"Processing event: {event_url}")
            event_data = self._extract_event_data_from_page(event_url)
            
            if event_data:
                # Apply keyword filter if specified
                if keywords:
                    event_text = f"{event_data['event_name']} {event_data['location']} {event_data['organizer_name']}".lower()
                    if any(keyword.lower() in event_text for keyword in keywords):
                        events.append(event_data)
                else:
                    events.append(event_data)
            
            # Rate limiting
            time.sleep(1)
        
        return events
    
    def export_to_json(self, events: List[Dict[str, Any]], filename: str = "luma_events.json"):
        """
        Export events to JSON file
        
        Args:
            events (List[Dict[str, Any]]): List of event data
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(events)} events to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
    
    def export_to_csv(self, events: List[Dict[str, Any]], filename: str = "luma_events.csv"):
        """
        Export events to CSV file
        
        Args:
            events (List[Dict[str, Any]]): List of event data
            filename (str): Output filename
        """
        try:
            df = pd.DataFrame(events)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Exported {len(events)} events to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='Luma Event Scraper Bot')
    parser.add_argument('--source', choices=['explore', 'custom', 'city'], default='explore',
                       help='Source to scrape: explore page, custom slug, or city (auto-detected if --city or --slug provided)')
    parser.add_argument('--slug', type=str, help='Custom slug to scrape (e.g., web3, hackathon)')
    parser.add_argument('--city', type=str, help='City name to scrape (e.g., new-delhi, mumbai, bangalore)')
    parser.add_argument('--keywords', nargs='+', help='Keywords to filter events')
    parser.add_argument('--output-format', choices=['json', 'csv', 'both'], default='both',
                       help='Output format for results')
    parser.add_argument('--output-prefix', type=str, default='luma_events',
                       help='Prefix for output filenames')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode')
    parser.add_argument('--no-selenium', action='store_true',
                       help='Disable Selenium and use requests only')
    
    args = parser.parse_args()
    
    # Auto-detect source based on provided arguments
    if args.city and args.source == 'explore':
        args.source = 'city'
        logger.info(f"Auto-detected city source for: {args.city}")
    elif args.slug and args.source == 'explore':
        args.source = 'custom'
        logger.info(f"Auto-detected custom source for: {args.slug}")
    
    # Validate arguments
    if args.source == 'custom' and not args.slug:
        parser.error("--slug is required when using --source custom")
    if args.source == 'city' and not args.city:
        parser.error("--city is required when using --source city")
    
    # Initialize scraper
    scraper = LumaScraper(headless=args.headless, use_selenium=not args.no_selenium)
    
    try:
        # Scrape events
        if args.source == 'explore':
            events = scraper.scrape_explore_page(keywords=args.keywords)
        elif args.source == 'custom':
            events = scraper.scrape_custom_slug(args.slug, keywords=args.keywords)
        elif args.source == 'city':
            events = scraper.scrape_city_events(args.city, keywords=args.keywords)
        
        if not events:
            logger.warning("No events found matching the criteria")
            return
        
        logger.info(f"Found {len(events)} events")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.output_format in ['json', 'both']:
            json_filename = f"{args.output_prefix}_{timestamp}.json"
            scraper.export_to_json(events, json_filename)
        
        if args.output_format in ['csv', 'both']:
            csv_filename = f"{args.output_prefix}_{timestamp}.csv"
            scraper.export_to_csv(events, csv_filename)
        
        # Print sample output
        print("\n" + "="*50)
        print("SAMPLE OUTPUT:")
        print("="*50)
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            print(json.dumps(event, indent=2))
        
        if len(events) > 3:
            print(f"\n... and {len(events) - 3} more events")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 