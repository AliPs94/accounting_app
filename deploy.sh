#!/bin/bash

# Deployment script for Accounting System
# Usage: ./deploy.sh

echo "🚀 Starting deployment..."

# Step 1: Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Step 2: Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Step 3: Install/Update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 4: Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Step 5: Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Step 6: Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages

# Step 7: Build frontend
echo "⚛️  Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Step 8: Restart services
echo "🔄 Restarting services..."
sudo systemctl restart accounting
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Your site should be live at your domain"

