# Luma Event Scraper Bot

A Python-based bot that scrapes public event listings from [Luma](https://lu.ma) and extracts key data points such as event name, date, region/location, and point-of-contact (PoC) information.

## 🎯 Features

- **Event Data Extraction**: Scrapes event titles, dates, locations, organizers, and comprehensive contact information
- **Multiple Sources**: Supports Luma explore page, custom slugs, and city-specific pages
- **City-Based Scraping**: Target specific cities (e.g., lu.ma/new-delhi, lu.ma/mumbai)
- **Enhanced Contact Info**: Extracts host emails, phone numbers, and social media links
- **Keyword Filtering**: Filter events by specific keywords (e.g., "Web3", "Hackathon", "Crypto")
- **Flexible Output**: Export results in JSON, CSV, or both formats
- **Rate Limiting**: Built-in delays to respect website policies
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Headless Browser Support**: Uses Selenium for JavaScript-heavy pages

## 📋 Requirements

- Python 3.7+
- Chrome browser (for Selenium)
- Internet connection

## 🚀 Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd luma-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome browser** (if not already installed)
   - Download from: https://www.google.com/chrome/

## 📖 Usage

### Basic Usage

**Scrape from Luma explore page:**
```bash
python luma_scraper.py
```

**Scrape from a custom slug:**
```bash
python luma_scraper.py --source custom --slug web3
```

**Scrape events from a specific city:**
```bash
python luma_scraper.py --city new-delhi
```

**Filter events by keywords:**
```bash
python luma_scraper.py --keywords Web3 Hackathon Crypto
```

### Advanced Usage

**Export only to JSON:**
```bash
python luma_scraper.py --output-format json
```

**Export only to CSV:**
```bash
python luma_scraper.py --output-format csv
```

**Custom output filename prefix:**
```bash
python luma_scraper.py --output-prefix my_events
```

**Disable Selenium (use requests only):**
```bash
python luma_scraper.py --no-selenium
```

**Show browser window (disable headless mode):**
```bash
python luma_scraper.py --headless false
```

### Command Line Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--source` | Source to scrape: `explore`, `custom`, or `city` (auto-detected if `--city` or `--slug` provided) | `explore` | No |
| `--slug` | Custom slug to scrape (e.g., web3, hackathon) | None | Yes (if `--source custom`) |
| `--city` | City name to scrape (e.g., new-delhi, mumbai) | None | Yes (if `--source city`) |
| `--keywords` | Keywords to filter events | None | No |
| `--output-format` | Output format: `json`, `csv`, or `both` | `both` | No |
| `--output-prefix` | Prefix for output filenames | `luma_events` | No |
| `--headless` | Run browser in headless mode | `True` | No |
| `--no-selenium` | Disable Selenium and use requests only | `False` | No |

## 📊 Output Format

### JSON Output Example
```json
{
  "event_name": "Ethereum India Hackathon",
  "date_time": "2025-08-12 18:00 IST",
  "location": "Bangalore, India",
  "organizer_name": "ETH India",
  "organizer_contact": "https://lu.ma/u/ethindia",
  "host_email": "contact@ethindia.org",
  "host_social_media": "twitter.com/ethindia, linkedin.com/company/ethindia",
  "event_url": "https://lu.ma/ethhackbangalore"
}
```

### CSV Output
The CSV file contains the same fields as the JSON output, with headers:
- `event_name`
- `date_time`
- `location`
- `organizer_name`
- `organizer_contact`
- `host_email`
- `host_social_media`
- `event_url`

## 🔧 Configuration

### Rate Limiting
The scraper includes built-in rate limiting (1 second delay between requests) to respect Luma's servers. You can modify this in the code if needed.

### User Agent
The scraper uses a realistic user agent string to avoid being blocked. You can modify this in the `LumaScraper.__init__()` method.

### Output Files
Output files are automatically timestamped to avoid overwriting:
- `luma_events_20241201_143022.json`
- `luma_events_20241201_143022.csv`

## 🛠️ Troubleshooting

### Common Issues

1. **Chrome not found**
   - Ensure Chrome browser is installed
   - The scraper will automatically download ChromeDriver

2. **No events found**
   - Check your internet connection
   - Try different keywords
   - The website structure might have changed

3. **Selenium errors**
   - Try using `--no-selenium` flag
   - Update Chrome browser
   - Check ChromeDriver compatibility

4. **Permission errors**
   - Ensure you have write permissions in the current directory
   - Check if output files are open in another application

### Logs
The scraper creates a `luma_scraper.log` file with detailed information about the scraping process. Check this file for debugging information.

## 📝 Examples

### Example 1: Find Web3 Events
```bash
python luma_scraper.py --keywords Web3 Blockchain Crypto
```

### Example 2: Scrape Hackathon Events
```bash
python luma_scraper.py --source custom --slug hackathon --keywords Hackathon
```

### Example 3: Scrape Events from New Delhi
```bash
python luma_scraper.py --city new-delhi --keywords Web3
```

### Example 4: Export to CSV Only
```bash
python luma_scraper.py --output-format csv --output-prefix hackathon_events
```

### Example 5: Use Requests Only (No Browser)
```bash
python luma_scraper.py --no-selenium --keywords Web3
```

## 🔒 Legal and Ethical Considerations

- **Respect robots.txt**: The scraper respects website robots.txt files
- **Rate limiting**: Built-in delays to avoid overwhelming servers
- **Terms of service**: Ensure compliance with Luma's terms of service
- **Data usage**: Use scraped data responsibly and in accordance with applicable laws
- **Attribution**: Consider providing attribution when using scraped data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please ensure compliance with Luma's terms of service and applicable laws when using this tool.

## ⚠️ Disclaimer

This tool is provided as-is without any warranties. Users are responsible for ensuring compliance with website terms of service and applicable laws. The authors are not responsible for any misuse of this tool.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the log file (`luma_scraper.log`)
3. Ensure all dependencies are installed correctly
4. Check your internet connection and firewall settings 