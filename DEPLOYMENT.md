# Luma Event Scraper API - Deployment Guide

## 🚀 **Deployment Options**

This API can be deployed on various platforms. Here are the recommended deployment methods:

## 📋 **Prerequisites**

1. **Python Version**: Use Python 3.11 or 3.12 (avoid 3.13 due to pandas compatibility issues)
2. **Dependencies**: All required packages are in `requirements-prod.txt`
3. **Chrome/Chromium**: Required for Selenium (handled automatically by webdriver-manager)

## 🎯 **Deployment Methods**

### 1. **Render (Recommended)**

#### **Automatic Deployment**
1. Connect your GitHub repository to Render
2. Use the `render.yaml` configuration file
3. Render will automatically detect and deploy the API

#### **Manual Deployment**
1. Create a new Web Service on Render
2. Set the following:
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.11.0`
     - `FLASK_ENV`: `production`
     - `FLASK_DEBUG`: `false`

### 2. **Heroku**

#### **Using Heroku CLI**
```bash
# Install Heroku CLI
# Create new app
heroku create your-app-name

# Set buildpacks
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open the app
heroku open
```

#### **Using Heroku Dashboard**
1. Connect your GitHub repository
2. Enable automatic deploys
3. The `Procfile` will be used automatically

### 3. **Railway**

1. Connect your GitHub repository
2. Railway will auto-detect the Python app
3. Use the `Procfile` for startup command

### 4. **DigitalOcean App Platform**

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements-prod.txt`
3. Set run command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 5. **AWS Elastic Beanstalk**

#### **Create `requirements.txt` for AWS**
```txt
# Use the same as requirements-prod.txt
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
pandas==2.2.0
lxml==4.9.3
webdriver-manager==4.0.1
python-dateutil==2.8.2
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
```

#### **Deploy Steps**
1. Create Elastic Beanstalk environment
2. Upload your code
3. Set environment variables in the console

## 🔧 **Environment Variables**

### **Required Variables**
- `PORT`: Port number (usually set by platform)
- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `false`

### **Optional Variables**
- `DEFAULT_HEADLESS`: `true` (for Selenium)
- `DEFAULT_USE_SELENIUM`: `true`
- `LOG_LEVEL`: `INFO`
- `REQUEST_DELAY`: `1` (seconds between requests)

## 📁 **File Structure for Deployment**

```
luma-scraper-main/
├── app.py                 # Main Flask application
├── luma_scraper.py       # Core scraper logic
├── requirements-prod.txt  # Production dependencies
├── render.yaml           # Render configuration
├── Procfile              # Heroku/Railway configuration
├── .env                  # Local environment (optional)
└── README.md            # Documentation
```

## 🚀 **Quick Deploy Commands**

### **Render**
```bash
# Just push to GitHub with render.yaml
git add .
git commit -m "Deploy to Render"
git push origin main
```

### **Heroku**
```bash
# Deploy to Heroku
heroku create your-app-name
git push heroku main
heroku open
```

### **Railway**
```bash
# Deploy to Railway
railway login
railway init
railway up
```

## 🔍 **Post-Deployment Testing**

### **Health Check**
```bash
curl https://your-app-url.herokuapp.com/health
```

### **API Testing**
```bash
# Test explore scraping
curl "https://your-app-url.herokuapp.com/scrape/explore"

# Test with keywords
curl "https://your-app-url.herokuapp.com/scrape/explore?keywords=tech,berlin"
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Pandas Build Error**
- **Cause**: Python 3.13 compatibility issue
- **Solution**: Use Python 3.11 or 3.12
- **Fix**: Update `render.yaml` or set Python version in platform settings

#### **2. Selenium Issues**
- **Cause**: Chrome not available in container
- **Solution**: webdriver-manager handles this automatically
- **Fix**: Ensure `webdriver-manager>=4.0.1` is installed

#### **3. Memory Issues**
- **Cause**: Large scraping operations
- **Solution**: Increase memory allocation or optimize scraping
- **Fix**: Set worker timeout in Procfile: `--timeout 120`

#### **4. Port Issues**
- **Cause**: Platform-specific port requirements
- **Solution**: Use `$PORT` environment variable
- **Fix**: Already handled in `app.py`

### **Debug Commands**

#### **Check Dependencies**
```bash
pip list | grep -E "(flask|selenium|pandas|requests)"
```

#### **Test Scraper Locally**
```bash
python -c "from luma_scraper import LumaScraper; print('Scraper works!')"
```

#### **Check Logs**
```bash
# Render
render logs

# Heroku
heroku logs --tail

# Railway
railway logs
```

## 📊 **Performance Optimization**

### **For Production**
1. **Use Gunicorn**: Already configured in `Procfile`
2. **Set Workers**: `--workers 2` (adjust based on memory)
3. **Increase Timeout**: `--timeout 120` for long scraping operations
4. **Enable Caching**: Consider Redis for caching scraped data
5. **Rate Limiting**: Implement API rate limiting

### **Memory Management**
- Scraper instances are cleaned up automatically
- Temporary files are removed after export
- Consider implementing connection pooling

## 🔒 **Security Considerations**

### **Production Security**
1. **Environment Variables**: Never commit secrets
2. **CORS**: Already configured for web apps
3. **Input Validation**: Implemented in all endpoints
4. **Rate Limiting**: Consider adding for production
5. **Authentication**: Add if needed for production use

### **API Security**
```python
# Example: Add basic auth (optional)
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function
```

## 🎯 **Monitoring & Logs**

### **Health Monitoring**
- Use `/health` endpoint for monitoring
- Set up alerts for 5xx errors
- Monitor response times

### **Log Analysis**
```bash
# View recent logs
heroku logs --tail

# Filter for errors
heroku logs | grep ERROR

# Monitor specific endpoint
heroku logs | grep "/scrape/explore"
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- Deploy multiple instances behind a load balancer
- Use Redis for session management
- Implement proper connection pooling

### **Vertical Scaling**
- Increase memory allocation
- Use more powerful CPU instances
- Optimize scraping algorithms

## 🎉 **Success Checklist**

- ✅ API responds to health check
- ✅ All endpoints return proper JSON
- ✅ Scraping functionality works
- ✅ Export features work
- ✅ Error handling is robust
- ✅ Logs are accessible
- ✅ Environment variables are set
- ✅ SSL/HTTPS is enabled
- ✅ CORS is configured
- ✅ Performance is acceptable

Your API is now ready for production use! 🚀 