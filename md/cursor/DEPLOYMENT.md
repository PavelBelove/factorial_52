# Deployment Guide - Factorial 52!

## Server Setup (176.120.21.138)

### Prerequisites
- Ubuntu/Debian server
- Python 3.11+
- Git
- Domain: factorial.agints.ru → 176.120.21.138

### Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx

# Create app user (optional, for security)
sudo useradd -m -s /bin/bash plexmem
sudo su - plexmem

# Clone repository
cd ~
git clone git@github.com:PavelBelove/factorial_52.git plexmem
cd plexmem

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Create .env file
cp .env.example .env
nano .env
```

Update `.env` with production values:
```env
OPENROUTER_API_KEY=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
TELEGRAM_BOT_TOKEN=6602937806:AAFqIbi_sEkpHKJuWBkWLIAJY4Qf9l6Cyqc
DEBUG=False
LOG_LEVEL=INFO
```

### SSL Certificate (Let's Encrypt)

```bash
# Setup Nginx for domain
sudo nano /etc/nginx/sites-available/factorial
```

Nginx config:
```nginx
server {
    server_name factorial.agints.ru;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/factorial /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d factorial.agints.ru
```

### Systemd Service

Create `/etc/systemd/system/plexmem-api.service`:
```ini
[Unit]
Description=PlexMem API Service
After=network.target

[Service]
Type=simple
User=plexmem
WorkingDirectory=/home/plexmem/plexmem
Environment="PATH=/home/plexmem/plexmem/venv/bin"
ExecStart=/home/plexmem/plexmem/venv/bin/python run_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/plexmem-bot.service`:
```ini
[Unit]
Description=PlexMem Telegram Bot
After=network.target plexmem-api.service

[Service]
Type=simple
User=plexmem
WorkingDirectory=/home/plexmem/plexmem
Environment="PATH=/home/plexmem/plexmem/venv/bin"
ExecStart=/home/plexmem/plexmem/venv/bin/python run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable plexmem-api plexmem-bot
sudo systemctl start plexmem-api plexmem-bot

# Check status
sudo systemctl status plexmem-api
sudo systemctl status plexmem-bot

# View logs
sudo journalctl -u plexmem-api -f
sudo journalctl -u plexmem-bot -f
```

### Database Migration

```bash
# First time setup - run migrations
source venv/bin/activate
python scripts/add_translator_fields.py
python scripts/add_needs_summarization.py
```

### Updates

```bash
# Pull latest changes
cd ~/plexmem
git pull origin main

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart plexmem-api
sudo systemctl restart plexmem-bot
```

### Monitoring

```bash
# API logs
tail -f logs/api.log

# Bot logs
tail -f logs/bot.log

# Agent debug logs (if DEBUG=True)
ls -la logs/agents/
```

### Backup

```bash
# Backup database
cp data/plexmem.db data/plexmem.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup script (add to crontab)
0 3 * * * cd /home/plexmem/plexmem && cp data/plexmem.db data/backups/plexmem.db.$(date +\%Y\%m\%d)
```

### Security Notes

- ✅ VPN (Amnesia) already configured on server - don't touch
- ✅ .env file contains secrets - never commit to git
- ✅ Use systemd services for auto-restart
- ✅ SSL certificate auto-renewal via certbot
- ✅ Logs rotation configured

### Troubleshooting

**Port 8000 already in use:**
```bash
sudo fuser -k 8000/tcp
sudo systemctl restart plexmem-api
```

**Database locked:**
```bash
# Check for zombie processes
ps aux | grep python
# Kill if needed
sudo systemctl restart plexmem-api plexmem-bot
```

**SSL certificate issues:**
```bash
sudo certbot renew --dry-run
sudo certbot renew
```

### DNS Configuration

Verify DNS at registrar:
- A record: `@` → `176.120.21.138`
- CNAME: `factorial` → `agints.ru`

Check propagation:
```bash
dig factorial.agints.ru
nslookup factorial.agints.ru
```

