# Deployment Guide - Accounting System

## 🚀 Pre-Deployment Checklist

### 1. Security Settings

#### ✅ Update `accounting_project/settings.py`:

```python
# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update allowed hosts with your domain
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-server-ip']

# CORS settings - Update with your frontend domain
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

CORS_ALLOW_ALL_ORIGINS = False  # MUST be False in production!

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. Database Configuration

#### For PostgreSQL (Recommended):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'accounting_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### 3. Static Files Configuration

Add to `settings.py`:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4. Requirements File

Update `requirements.txt` to include production packages:

```
Django==5.2.6
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
python-decouple==3.8
psycopg2-binary==2.9.9  # For PostgreSQL
gunicorn==21.2.0  # WSGI server
whitenoise==6.6.0  # For serving static files
```

### 5. Environment Variables

Create a `.env` file (DO NOT commit to git):

```env
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 6. Frontend Build

```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

---

## 📦 Deployment Options

### Option A: Traditional VPS (DigitalOcean, Linode, AWS EC2)

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, PostgreSQL, Nginx
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx -y
```

#### 2. Setup PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE accounting_db;
CREATE USER accounting_user WITH PASSWORD 'your-password';
ALTER ROLE accounting_user SET client_encoding TO 'utf8';
ALTER ROLE accounting_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE accounting_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO accounting_user;
\q
```

#### 3. Setup Application

```bash
# Clone your repository
cd /var/www/
git clone your-repo-url accounting

# Create virtual environment
cd accounting
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py setup_default_accounts

# Compile translations
python manage.py compilemessages
```

#### 4. Setup Gunicorn

Create `/etc/systemd/system/accounting.service`:

```ini
[Unit]
Description=Accounting System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/accounting
Environment="PATH=/var/www/accounting/venv/bin"
ExecStart=/var/www/accounting/venv/bin/gunicorn --workers 3 --bind unix:/var/www/accounting/accounting.sock accounting_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl start accounting
sudo systemctl enable accounting
```

#### 5. Setup Nginx

Create `/etc/nginx/sites-available/accounting`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/accounting/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/accounting/media/;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://unix:/var/www/accounting/accounting.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        proxy_pass http://unix:/var/www/accounting/accounting.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        root /var/www/accounting/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/accounting /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### Option B: Heroku

#### 1. Create `Procfile`:

```
web: gunicorn accounting_project.wsgi --log-file -
```

#### 2. Create `runtime.txt`:

```
python-3.12.0
```

#### 3. Update `settings.py` for Heroku:

```python
import dj_database_url

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 4. Deploy:

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py setup_default_accounts
```

---

### Option C: Docker

#### `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages

EXPOSE 8000

CMD ["gunicorn", "accounting_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=accounting_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your-password

  web:
    build: .
    command: gunicorn accounting_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

## 🔒 Security Best Practices

1. **Never commit sensitive data** - Use `.gitignore`:
```
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
media/
venv/
node_modules/
frontend/dist/
```

2. **Use environment variables** for all secrets

3. **Keep dependencies updated**:
```bash
pip list --outdated
npm outdated
```

4. **Setup monitoring** - Use services like:
   - Sentry for error tracking
   - New Relic for performance monitoring
   - CloudWatch for AWS deployments

5. **Regular backups** of database:
```bash
pg_dump accounting_db > backup_$(date +%Y%m%d).sql
```

6. **Enable firewall**:
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

---

## 📝 Post-Deployment Tasks

1. ✅ Test all API endpoints
2. ✅ Test frontend functionality
3. ✅ Verify Arabic translations work
4. ✅ Test user authentication
5. ✅ Create initial admin user
6. ✅ Setup default accounts
7. ✅ Configure email settings (if needed)
8. ✅ Setup backups
9. ✅ Configure monitoring
10. ✅ Test voucher creation and reports

---

## 🆘 Troubleshooting

### Static files not loading:
```bash
python manage.py collectstatic --noinput
sudo systemctl restart accounting
sudo systemctl restart nginx
```

### Database connection issues:
```bash
sudo -u postgres psql
\c accounting_db
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO accounting_user;
```

### Permission issues:
```bash
sudo chown -R www-data:www-data /var/www/accounting
sudo chmod -R 755 /var/www/accounting
```

---

## 📞 Support

For issues during deployment, check:
- Django logs: `/var/log/accounting/`
- Nginx logs: `/var/log/nginx/`
- System logs: `sudo journalctl -u accounting`

