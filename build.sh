#!/bin/bash
set -e

echo "🚀 Starting Heroku build process..."

# Navigate to frontend directory
cd frontend

echo "📦 Installing frontend dependencies with yarn..."
yarn install --production=false

echo "🏗️ Building React application..."
yarn build

echo "✅ Build completed successfully!"

# Verify build
if [ -d "build" ]; then
    echo "✅ Build directory exists"
    echo "📁 Build contents:"
    ls -la build/
    
    if [ -f "build/index.html" ]; then
        echo "✅ index.html found"
    else
        echo "❌ index.html missing!"
        exit 1
    fi
    
    if [ -d "build/static" ]; then
        echo "✅ static directory found"
        echo "📁 Static contents:"
        ls -la build/static/
    else
        echo "❌ static directory missing!"
        exit 1
    fi
else
    echo "❌ Build directory not created!"
    exit 1
fi

echo "🎉 Frontend build successful!"