#!/bin/bash

# Build script for DigitalOcean App Platform

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies and build frontend
echo "📦 Installing Node.js dependencies..."
cd /workspace && npm install

echo "🔨 Building frontend..."
npm run build

echo "✅ Build completed successfully!" 