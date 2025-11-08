#!/bin/bash

# Simple HTTP server for DoIt frontend
echo "🚀 Starting DoIt Frontend Server..."
echo "📍 Server will be available at: http://localhost:8080"
echo "📍 Landing page: http://localhost:8080/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8080
