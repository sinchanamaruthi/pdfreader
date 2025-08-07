#!/bin/bash

# Financial Stock Assistant Startup Script

echo "🚀 Starting Financial Stock Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🎯 Launching Streamlit application..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

echo "✅ Application should be running at http://localhost:8501"