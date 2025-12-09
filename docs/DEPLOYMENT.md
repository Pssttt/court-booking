# Deployment Guide

## Local Development

```bash
./start.sh
```

## VPS Deployment (DigitalOcean, Linode, AWS)

### 1. Setup Server

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Clone repository
git clone https://github.com/Pssttt/court-booking
cd court-booking
```

### 2. Setup Application

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 4. Setup Systemd Service

Create `/etc/systemd/system/court-booking.service`:

```ini
[Unit]
Description=Court Booking WebApp
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/court-booking
Environment="PATH=/opt/court-booking/venv/bin"
ExecStart=/opt/court-booking/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start court-booking
sudo systemctl enable court-booking
```

## Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
docker build -t court-booking .
docker run -p 8000:8000 court-booking
```

### With Docker Compose

```yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
```

## Heroku Deployment

### 1. Create Procfile

```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### 2. Deploy

```bash
heroku login
heroku create court-booking
git push heroku main
heroku open
```

## Railway Deployment

1. Connect GitHub repository
2. Set Python version to 3.11
3. Deploy automatically

## Environment Variables

For sensitive data, use environment variables:

Create `.env`:
Refer to `.env.example`

Update `config/settings.py`:

```python
from os import getenv

BOOKING_DATA = {
    "phone": getenv("PHONE", "default_value"),
    "email": getenv("EMAIL", "default_value"),
    # ...
}
```

## SSL/HTTPS

### With Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name court-booking.com;

    ssl_certificate /etc/letsencrypt/live/court-booking.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/court-booking.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Let's Encrypt Certificate

```bash
sudo certbot certonly --standalone -d court-booking.example.com
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Systemd
sudo journalctl -u court-booking -f

# Docker
docker logs <container-id> -f
```

### Performance Monitoring

Add to `main.py`:

```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Backup & Maintenance

### Backup Configuration

```bash
cp config/settings.py config/settings.backup.py
```

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Monitor Submissions

Check logs for submission errors:

```bash
grep "✅\|❌" app.log
```

## Troubleshooting

### Port Already in Use

```bash
lsof -i :8000
kill -9 <PID>
```

### Out of Memory

Reduce worker count:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app
```

### Slow Submissions

Check network:

```bash
ping docs.google.com
```

Monitor request time in logs.

### Application Won't Start

Check Python version:

```bash
python3 --version  # Should be 3.9+
```

Check dependencies:

```bash
pip list
```
