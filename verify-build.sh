#!/bin/bash
set -e

echo "🔍 Post-build verification..."

# Check if build directory exists
if [ ! -d "frontend/build" ]; then
    echo "❌ CRITICAL: frontend/build directory missing!"
    echo "📋 Current directory contents:"
    ls -la
    echo "📋 Frontend directory contents:"
    ls -la frontend/ || echo "Frontend directory not found"
    exit 1
fi

echo "✅ Build directory exists"

# Check essential files
if [ ! -f "frontend/build/index.html" ]; then
    echo "❌ CRITICAL: index.html missing!"
    exit 1
fi

if [ ! -d "frontend/build/static" ]; then
    echo "❌ CRITICAL: static directory missing!"
    exit 1
fi

# Check for JS files
js_count=$(find frontend/build/static -name "*.js" | wc -l)
if [ "$js_count" -eq 0 ]; then
    echo "❌ CRITICAL: No JavaScript files found!"
    exit 1
fi

echo "✅ Found $js_count JavaScript file(s)"

# Check file sizes (ensure files aren't empty)
index_size=$(wc -c < "frontend/build/index.html")
if [ "$index_size" -lt 100 ]; then
    echo "❌ CRITICAL: index.html too small ($index_size bytes)"
    exit 1
fi

echo "✅ index.html size: $index_size bytes"

echo "🎉 Post-build verification successful!"
echo "📋 Build summary:"
echo "   - Build directory: ✅"
echo "   - index.html: ✅ ($index_size bytes)"  
echo "   - Static files: ✅"
echo "   - JavaScript files: ✅ ($js_count files)"