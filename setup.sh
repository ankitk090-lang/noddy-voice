#!/bin/bash

# Noddy AI Assistant - Quick Setup Script

echo "🚀 Starting Noddy AI Setup..."

# 1. Clone the repository (Assuming you will push this to a repo)
# echo "📦 Cloning repository..."
# git clone <YOUR_REPO_URL>
# cd Noddy_Redesign

# 2. Backend Setup
echo "🐍 Setting up Backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

source venv/bin/activate
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt
pip install "numpy<2" # Fix for ChromaDB compatibility

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: backend/.env file is missing!"
    echo "Please create it using .env.example as a template."
    cp .env.example .env
fi

# 3. Frontend Setup
echo "⚛️  Setting up Frontend..."
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install

# Check for .env
if [ ! -f ".env" ]; then
    echo "Creating frontend .env..."
    cp .env.example .env
fi

echo "🎉 Setup Complete!"
echo ""
echo "To run the project:"
echo "1. Terminal 1 (Backend): cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Terminal 2 (Frontend): cd frontend && npm run dev"
