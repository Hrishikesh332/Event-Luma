# Luma Event Scraper API - Deployment Troubleshooting

## 🚨 **Common Deployment Issues & Solutions**

### **1. Pandas Build Error (Python 3.13)**

#### **Problem**
```
error: too few arguments to function '_PyLong_AsByteArray'
pandas/_libs/tslibs/base.cpython-313-x86_64-linux-gnu.so.p/meson-generated_pandas__libs_tslibs_base.pyx.c:5397:27
```

#### **Cause**
- pandas 2.1.3 is not compatible with Python 3.13
- Python 3.13 has breaking changes in C API

#### **Solutions**

**Option A: Use Python 3.11 (Recommended)**
```yaml
# In render.yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0
```

**Option B: Use Latest Pandas**
```txt
# In requirements-render.txt
pandas>=2.2.0
```

**Option C: Use Pre-built Wheels**
```txt
# In requirements-render.txt
pandas==2.2.0
numpy>=1.26.0
```

### **2. Selenium/Chrome Issues**

#### **Problem**
```
Failed to initialize Selenium: 'NoneType' object has no attribute 'split'
```

#### **Cause**
- Chrome not available in container
- webdriver-manager can't find Chrome

#### **Solutions**

**Option A: Use Requests Only (Recommended for Production)**
```python
# In app.py, modify scraper initialization
scraper = get_scraper(headless=True, use_selenium=False)
```

**Option B: Install Chrome in Container**
```dockerfile
# Add to Dockerfile if using Docker
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*
```

**Option C: Use Chromium**
```python
# In luma_scraper.py
chrome_options.binary_location = "/usr/bin/chromium-browser"
```

### **3. Memory Issues**

#### **Problem**
```
MemoryError: Unable to allocate array
```

#### **Solutions**

**Option A: Reduce Workers**
```txt
# In Procfile
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**Option B: Increase Memory Allocation**
- Upgrade to paid plan on Render/Heroku
- Use larger instance on AWS

**Option C: Optimize Scraping**
```python
# Limit number of events scraped
events = scraper.scrape_explore_page(keywords=keywords)[:10]
```

### **4. Port Issues**

#### **Problem**
```
Address already in use
```

#### **Solution**
```python
# In app.py
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### **5. Environment Variables**

#### **Problem**
```
PermissionError: [Errno 1] Operation not permitted: '/Users/hrishikesh/Downloads/.env'
```

#### **Solution**
```bash
# Create .env file in project directory
touch .env
```

## 🔧 **Platform-Specific Solutions**

### **Render**

#### **Build Command**
```bash
pip install -r requirements-render.txt
```

#### **Start Command**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

#### **Environment Variables**
```yaml
PYTHON_VERSION: 3.11.0
FLASK_ENV: production
FLASK_DEBUG: false
```

### **Heroku**

#### **Procfile**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

#### **Requirements**
```txt
# requirements.txt
requests>=2.31.0
beautifulsoup4>=4.12.2
selenium>=4.15.2
pandas>=2.2.0
lxml>=4.9.3
webdriver-manager>=4.0.1
python-dateutil>=2.8.2
flask>=2.3.3
flask-cors>=4.0.0
gunicorn>=21.2.0
```

### **Railway**

#### **Start Command**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

## 🛠️ **Debug Commands**

### **Check Python Version**
```bash
python --version
```

### **Check Dependencies**
```bash
pip list | grep -E "(pandas|flask|selenium)"
```

### **Test Scraper Locally**
```bash
python -c "from luma_scraper import LumaScraper; print('Scraper works!')"
```

### **Test API Locally**
```bash
python app.py
curl http://localhost:5000/health
```

## 📋 **Deployment Checklist**

### **Before Deployment**
- [ ] Python version is 3.11 or 3.12
- [ ] All dependencies are in requirements file
- [ ] app.py uses `$PORT` environment variable
- [ ] .env file exists (if needed)
- [ ] Procfile is present (for Heroku/Railway)
- [ ] render.yaml is present (for Render)

### **After Deployment**
- [ ] Health check endpoint responds
- [ ] API documentation loads
- [ ] Scraping endpoints work
- [ ] Export endpoints work
- [ ] Error handling works
- [ ] Logs are accessible

## 🚀 **Quick Fix Commands**

### **Fix Pandas Issue**
```bash
# Update requirements
echo "pandas>=2.2.0" > requirements-render.txt
echo "python-3.11.0" > runtime.txt
```

### **Fix Selenium Issue**
```bash
# Disable Selenium in production
export USE_SELENIUM=false
```

### **Fix Memory Issue**
```bash
# Reduce workers
echo "web: gunicorn app:app --bind 0.0.0.0:\$PORT --workers 1 --timeout 120" > Procfile
```

### **Fix Port Issue**
```bash
# Ensure app.py uses PORT environment variable
grep -n "PORT" app.py
```

## 📞 **Getting Help**

### **Logs to Check**
```bash
# Render
render logs

# Heroku
heroku logs --tail

# Railway
railway logs
```

### **Common Error Patterns**
- `pandas` + `Python 3.13` = Use Python 3.11
- `selenium` + `NoneType` = Disable Selenium or install Chrome
- `MemoryError` = Reduce workers or increase memory
- `Address already in use` = Use `$PORT` environment variable

### **Contact Information**
- Check the logs first
- Try the solutions above
- If still stuck, provide:
  - Platform (Render/Heroku/Railway)
  - Error message
  - Python version
  - Requirements file content 