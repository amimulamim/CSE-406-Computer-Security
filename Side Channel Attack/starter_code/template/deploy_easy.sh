#!/bin/bash

echo "🚀 Side Channel Attack - Quick Deploy Script"
echo "============================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to deploy to Railway
deploy_railway() {
    echo "📡 Deploying to Railway..."
    if command_exists railway; then
        railway login
        railway link
        railway up
    else
        echo "❌ Railway CLI not found. Install it first:"
        echo "npm install -g @railway/cli"
        echo "Or deploy via web interface at railway.app"
    fi
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🔮 Deploying to Heroku..."
    if command_exists heroku; then
        echo "Enter your Heroku app name:"
        read app_name
        heroku create $app_name
        git add .
        git commit -m "Deploy to Heroku"
        git push heroku main
        heroku open
    else
        echo "❌ Heroku CLI not found. Install it first:"
        echo "https://devcenter.heroku.com/articles/heroku-cli"
    fi
}

# Function to run locally
run_local() {
    echo "🏠 Running locally..."
    if command_exists python3; then
        echo "Installing dependencies..."
        pip install -r requirements.txt
        echo "Starting Flask app..."
        python3 app.py
    else
        echo "❌ Python 3 not found. Please install Python 3."
    fi
}

# Function to run with Docker
run_docker() {
    echo "🐳 Running with Docker..."
    if command_exists docker; then
        docker build -t side-channel-attack .
        docker run -p 5000:5000 side-channel-attack
    else
        echo "❌ Docker not found. Please install Docker."
    fi
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1. 🚂 Deploy to Railway (Recommended)"
echo "2. 🔮 Deploy to Heroku"
echo "3. 🏠 Run locally"
echo "4. 🐳 Run with Docker"
echo "5. 📖 Show deployment guide"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_heroku
        ;;
    3)
        run_local
        ;;
    4)
        run_docker
        ;;
    5)
        echo "📖 Opening deployment guide..."
        if command_exists cat; then
            cat DEPLOYMENT.md
        else
            echo "Please read DEPLOYMENT.md for detailed instructions."
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "✅ Script completed!"
