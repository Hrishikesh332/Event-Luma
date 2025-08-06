#!/bin/bash

# Luma Event Scraper API - Deployment Script
# This script helps deploy the API to various platforms

set -e

echo "🚀 Luma Event Scraper API - Deployment Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Make sure you're in the project directory."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "🐍 Python version: $python_version"

if [[ "$python_version" == "3.13" ]]; then
    echo "⚠️  Warning: Python 3.13 may have compatibility issues with pandas"
    echo "   Consider using Python 3.11 or 3.12 for production"
fi

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    required_packages=("flask" "selenium" "pandas" "requests" "beautifulsoup4")
    
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            echo "✅ $package"
        else
            echo "❌ $package - Missing"
            return 1
        fi
    done
    
    echo "✅ All dependencies are installed!"
    return 0
}

# Function to test the API locally
test_api() {
    echo "🧪 Testing API locally..."
    
    # Start API in background
    python3 app.py &
    API_PID=$!
    
    # Wait for API to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "✅ API is running and responding"
    else
        echo "❌ API is not responding"
        kill $API_PID 2>/dev/null
        return 1
    fi
    
    # Test scraping endpoint
    if curl -s "http://localhost:5000/scrape/explore" > /dev/null; then
        echo "✅ Scraping endpoint is working"
    else
        echo "❌ Scraping endpoint failed"
        kill $API_PID 2>/dev/null
        return 1
    fi
    
    # Stop API
    kill $API_PID 2>/dev/null
    echo "✅ Local testing completed successfully"
}

# Function to deploy to Render
deploy_render() {
    echo "🚀 Deploying to Render..."
    
    if [ ! -f "render.yaml" ]; then
        echo "❌ render.yaml not found"
        return 1
    fi
    
    echo "📝 Make sure you have:"
    echo "   1. Connected your GitHub repository to Render"
    echo "   2. Created a new Web Service"
    echo "   3. Set the build command: pip install -r requirements-prod.txt"
    echo "   4. Set the start command: gunicorn app:app --bind 0.0.0.0:\$PORT"
    echo ""
    echo "🔗 Your API will be available at: https://your-app-name.onrender.com"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🚀 Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Install it first:"
        echo "   https://devcenter.heroku.com/articles/heroku-cli"
        return 1
    fi
    
    if [ ! -f "Procfile" ]; then
        echo "❌ Procfile not found"
        return 1
    fi
    
    echo "📝 Deploying to Heroku..."
    echo "   This will create a new Heroku app and deploy your code"
    
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        heroku create
        git add .
        git commit -m "Deploy to Heroku"
        git push heroku main
        heroku open
    fi
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚀 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Install it first:"
        echo "   npm install -g @railway/cli"
        return 1
    fi
    
    echo "📝 Deploying to Railway..."
    railway login
    railway init
    railway up
}

# Main menu
show_menu() {
    echo ""
    echo "🎯 Choose deployment option:"
    echo "1) Test dependencies"
    echo "2) Test API locally"
    echo "3) Deploy to Render"
    echo "4) Deploy to Heroku"
    echo "5) Deploy to Railway"
    echo "6) Show deployment guide"
    echo "7) Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            check_dependencies
            ;;
        2)
            test_api
            ;;
        3)
            deploy_render
            ;;
        4)
            deploy_heroku
            ;;
        5)
            deploy_railway
            ;;
        6)
            echo "📖 Opening deployment guide..."
            if command -v open &> /dev/null; then
                open DEPLOYMENT.md
            elif command -v xdg-open &> /dev/null; then
                xdg-open DEPLOYMENT.md
            else
                echo "📖 Deployment guide: DEPLOYMENT.md"
            fi
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            ;;
    esac
}

# Check if requirements files exist
if [ ! -f "requirements-prod.txt" ]; then
    echo "❌ requirements-prod.txt not found"
    exit 1
fi

if [ ! -f "app.py" ]; then
    echo "❌ app.py not found"
    exit 1
fi

# Show menu
while true; do
    show_menu
    echo ""
    read -p "Press Enter to continue..."
done 