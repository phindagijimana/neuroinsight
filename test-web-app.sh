#!/bin/bash

# NeuroInsight Web App - Quick Test Script
# Run this on your Mac

echo "======================================"
echo "  NeuroInsight Web App Test"
echo "======================================"
echo ""

# Check if in correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: docker-compose.yml not found"
    echo "Please run this script from the hippo directory"
    exit 1
fi

echo "✓ Found docker-compose.yml"
echo ""

# Check Docker is running
echo "Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check current branch
echo "Checking Git branch..."
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

if [ "$BRANCH" != "web-app" ]; then
    echo "WARNING: You're on '$BRANCH' branch"
    echo "Recommended: git checkout web-app"
    echo ""
fi

# Create .env file if it doesn't exist
echo "Checking environment file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ Created .env file"
    else
        echo "ERROR: .env.example not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi
echo ""

# Start services
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "======================================"
echo "  Service Status"
echo "======================================"
docker-compose ps

echo ""
echo "======================================"
echo "  Testing URLs"
echo "======================================"

# Test backend
echo ""
echo "Testing backend API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend API is responding (http://localhost:8000)"
else
    echo "✗ Backend API not responding"
fi

# Test frontend
echo ""
echo "Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend is responding (http://localhost:3000)"
else
    echo "✗ Frontend not responding"
fi

echo ""
echo "======================================"
echo "  Ready!"
echo "======================================"
echo ""
echo "Open in your browser:"
echo "  http://localhost:3000"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""

# Open browser
echo "Opening browser..."
open http://localhost:3000

