# Luma Event Scraper API

A comprehensive Flask API for scraping event data from Luma (lu.ma). This API provides RESTful endpoints to extract event information including event names, dates, locations, organizers, and social media links.

## Features

- **Multiple Scraping Sources**: Explore page, custom slugs, city-specific pages, and individual URLs
- **Keyword Filtering**: Filter events by keywords across all sources
- **Flexible Export**: Export data to JSON or CSV formats
- **Batch Processing**: Scrape multiple sources in a single request
- **Statistics**: Get insights from scraped event data
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin resource sharing enabled

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd luma-scraper-main
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Home & Documentation
- **GET** `/` - API documentation and endpoint list

### 2. Health Check
- **GET** `/health` - Health check endpoint

### 3. Scraping Endpoints

#### Explore Page Scraping
- **GET** `/scrape/explore`
  - Query Parameters:
    - `keywords` (optional): Comma-separated keywords to filter events
    - `headless` (optional): Boolean, default `true`
    - `use_selenium` (optional): Boolean, default `true`

#### Custom Slug Scraping
- **GET** `/scrape/custom`
  - Query Parameters:
    - `slug` (required): Custom slug to scrape (e.g., "web3", "hackathon")
    - `keywords` (optional): Comma-separated keywords
    - `headless` (optional): Boolean, default `true`
    - `use_selenium` (optional): Boolean, default `true`

#### City Events Scraping
- **GET** `/scrape/city`
  - Query Parameters:
    - `city` (required): City name (e.g., "new-delhi", "mumbai")
    - `keywords` (optional): Comma-separated keywords
    - `headless` (optional): Boolean, default `true`
    - `use_selenium` (optional): Boolean, default `true`

#### Single URL Scraping
- **POST** `/scrape/url`
  - Request Body (JSON):
    ```json
    {
      "url": "https://lu.ma/event/example",
      "headless": true,
      "use_selenium": true
    }
    ```

### 4. Export Endpoints

#### Export to JSON
- **POST** `/export/json`
  - Request Body (JSON):
    ```json
    {
      "events": [...],
      "filename": "optional_filename.json"
    }
    ```

#### Export to CSV
- **POST** `/export/csv`
  - Request Body (JSON):
    ```json
    {
      "events": [...],
      "filename": "optional_filename.csv"
    }
    ```

### 5. Advanced Endpoints

#### Batch Scraping
- **POST** `/batch`
  - Request Body (JSON):
    ```json
    {
      "sources": [
        {
          "type": "explore",
          "params": {"keywords": ["web3", "crypto"]}
        },
        {
          "type": "custom",
          "params": {"slug": "hackathon"}
        },
        {
          "type": "city",
          "params": {"city": "new-delhi"}
        }
      ],
      "keywords": ["tech", "innovation"],
      "headless": true,
      "use_selenium": true
    }
    ```

#### Statistics
- **POST** `/stats`
  - Request Body (JSON):
    ```json
    {
      "events": [...]
    }
    ```

## Usage Examples

### 1. Basic Explore Page Scraping

```bash
curl "http://localhost:5000/scrape/explore"
```

### 2. Scraping with Keywords

```bash
curl "http://localhost:5000/scrape/explore?keywords=web3,hackathon,crypto"
```

### 3. Scraping Custom Slug

```bash
curl "http://localhost:5000/scrape/custom?slug=web3&keywords=crypto"
```

### 4. Scraping City Events

```bash
curl "http://localhost:5000/scrape/city?city=new-delhi&keywords=tech"
```

### 5. Scraping Single Event

```bash
curl -X POST "http://localhost:5000/scrape/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://lu.ma/event/example-event"}'
```

### 6. Batch Scraping

```bash
curl -X POST "http://localhost:5000/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"type": "explore", "params": {"keywords": ["web3"]}},
      {"type": "custom", "params": {"slug": "hackathon"}},
      {"type": "city", "params": {"city": "mumbai"}}
    ],
    "keywords": ["tech"]
  }'
```

### 7. Export to JSON

```bash
curl -X POST "http://localhost:5000/export/json" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [...],
    "filename": "my_events.json"
  }'
```

### 8. Get Statistics

```bash
curl -X POST "http://localhost:5000/stats" \
  -H "Content-Type: application/json" \
  -d '{"events": [...]}'
```

## Response Format

All successful responses follow this format:

```json
{
  "success": true,
  "message": "Success message",
  "count": 10,
  "events": [...],
  "timestamp": "2024-01-01T12:00:00"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description",
  "message": "Error message"
}
```

## Event Data Structure

Each event contains the following fields:

```json
{
  "event_name": "Event Name",
  "date_time": "Event Date and Time",
  "location": "Event Location",
  "organizer_name": "Organizer Name",
  "organizer_contact": "Organizer Profile URL",
  "host_email": "Contact Email",
  "host_social_media": "Social Media Links",
  "event_url": "Event URL"
}
```

## Configuration Options

### Scraper Configuration
- `headless`: Run browser in headless mode (default: true)
- `use_selenium`: Use Selenium for JavaScript-heavy pages (default: true)

### Rate Limiting
The API includes built-in rate limiting to be respectful to the target website. Each scraping operation includes delays between requests.

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Missing required parameters or invalid request format
- **404 Not Found**: Endpoint not found or event not found
- **500 Internal Server Error**: Unexpected errors during scraping

## Logging

The API logs all operations to help with debugging:

- INFO: Successful operations
- WARNING: Non-critical issues
- ERROR: Critical errors with full stack traces

## CORS Support

The API includes CORS support for cross-origin requests, making it suitable for web applications.

## Security Considerations

- The API does not store any scraped data permanently
- All temporary files are cleaned up automatically
- No authentication is implemented (add as needed for production)
- Rate limiting is built into the scraper

## Production Deployment

For production deployment:

1. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. Add authentication and rate limiting
3. Configure proper logging
4. Set up monitoring and health checks
5. Use environment variables for configuration

## Troubleshooting

### Common Issues

1. **Selenium WebDriver Issues**: Ensure Chrome/Chromium is installed
2. **Memory Issues**: The scraper can be memory-intensive; monitor usage
3. **Rate Limiting**: The API includes delays to avoid being blocked
4. **Network Issues**: Ensure stable internet connection for scraping

### Debug Mode

Run with debug mode for detailed logging:
```bash
export FLASK_ENV=development
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed information
3. Include error logs and request examples 