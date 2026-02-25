#!/bin/bash

# FlintBloom Startup Script

set -e

echo "🌟 Starting FlintBloom..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
    echo "   Then run this script again"
    exit 1
fi

# Load environment variables
source .env

echo "📦 Database type: $DB_TYPE"

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker Compose..."

    # Start services
    docker-compose up -d

    echo ""
    echo "✅ FlintBloom is starting..."
    echo ""
    echo "📊 Services:"
    echo "   - API: http://localhost:8000"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - Health: http://localhost:8000/health"
    echo ""
    echo "🔍 Check logs with: docker-compose logs -f backend"
    echo "🛑 Stop with: docker-compose down"

elif command -v python3 &> /dev/null; then
    echo "🐍 Using Python directly..."

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "📦 Installing dependencies..."
    cd backend
    pip install -r requirements.txt

    # Run application
    echo "🚀 Starting application..."
    python -m app.main

else
    echo "❌ Neither Docker nor Python3 found!"
    echo "   Please install Docker or Python 3.11+"
    exit 1
fi
