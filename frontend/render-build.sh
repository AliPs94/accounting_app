#!/usr/bin/env bash
# Build script for Render.com frontend deployment

set -e  # Exit on error

echo "========================================="
echo "Starting Render Build for Frontend"
echo "========================================="

# Check Node version
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "NODE_VERSION env var: ${NODE_VERSION:-not set}"

# Verify Node version is at least 20
NODE_MAJOR_VERSION=$(node --version | cut -d'.' -f1 | sed 's/v//')
echo "Detected Node major version: $NODE_MAJOR_VERSION"

if [ "$NODE_MAJOR_VERSION" -lt 20 ]; then
    echo "ERROR: Node version must be 20 or higher!"
    echo "Current version: $(node --version)"
    echo "Vite 7.x requires Node.js 20.19+ or 22.12+"
    echo "Please set NODE_VERSION=20.19.0 in environment variables"
    exit 1
fi

echo "✓ Node version is compatible"
echo "========================================="

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application (skip type checking for production)
echo "Building application..."
npm run build-only

echo "========================================="
echo "✓ Build completed successfully!"
echo "========================================="

