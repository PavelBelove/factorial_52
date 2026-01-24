#!/bin/bash

# Initial server setup script for Factorial 52!
# Run this ONCE on fresh server as root

set -e

echo "🎲 Factorial 52! - Initial Server Setup"
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo bash setup_server.sh)"
    exit 1
fi

# Server info
SERVER_IP="176.120.21.138"
DOMAIN="factorial.agints.ru"
APP_USER="plexmem"
APP_DIR="/home/$APP_USER/plexmem"

echo "📋 Configuration:"
echo "  Server IP: $SERVER_IP"
echo "  Domain: $DOMAIN"
echo "  App User: $APP_USER"
echo "  App Directory: $APP_DIR"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    curl \
    sqlite3

# Create app user (if doesn't exist)
if id "$APP_USER" &>/dev/null; then
    echo "✓ User $APP_USER already exists"
else
    echo "👤 Creating user $APP_USER..."
    useradd -m -s /bin/bash $APP_USER
    echo "✓ User created"
fi

# Setup SSH key for GitHub (as app user)
echo "🔑 Setting up SSH key for GitHub..."
su - $APP_USER << 'EOF'
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -C "plexmem@factorial.agints.ru" -f ~/.ssh/id_rsa -N ""
    echo "✓ SSH key generated"
    echo "📋 Add this public key to GitHub:"
    echo "   https://github.com/settings/keys"
    echo ""
    cat ~/.ssh/id_rsa.pub
    echo ""
    read -p "Press Enter after adding key to GitHub..."
else
    echo "✓ SSH key already exists"
fi
EOF

# Clone repository
echo "📥 Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "✓ Directory already exists"
    cd $APP_DIR
    su - $APP_USER -c "cd $APP_DIR && git pull origin main"
else
    su - $APP_USER -c "git clone git@github.com:PavelBelove/factorial_52.git $APP_DIR"
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
su - $APP_USER << EOF
cd $APP_DIR
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Setup .env file
echo "⚙️  Setting up .env file..."
if [ ! -f "$APP_DIR/.env" ]; then
    su - $APP_USER -c "cp $APP_DIR/.env.example $APP_DIR/.env"
    echo "⚠️  IMPORTANT: Edit $APP_DIR/.env with production credentials!"
    echo "   OPENROUTER_API_KEY=..."
    echo "   TELEGRAM_BOT_TOKEN=..."
    read -p "Press Enter after editing .env file..."
else
    echo "✓ .env file already exists"
fi

# Create directories
echo "📁 Creating directories..."
su - $APP_USER -c "mkdir -p $APP_DIR/data $APP_DIR/logs $APP_DIR/logs/agents"

# Install systemd services
echo "⚙️  Installing systemd services..."
cp $APP_DIR/systemd/plexmem-api.service /etc/systemd/system/
cp $APP_DIR/systemd/plexmem-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable plexmem-api plexmem-bot
echo "✓ Services installed"

# Setup Nginx
echo "🌐 Setting up Nginx..."
cp $APP_DIR/systemd/nginx-factorial.conf /etc/nginx/sites-available/factorial
ln -sf /etc/nginx/sites-available/factorial /etc/nginx/sites-enabled/factorial
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t
systemctl reload nginx
echo "✓ Nginx configured"

# Setup SSL certificate
echo "🔒 Setting up SSL certificate..."
echo "⚠️  Make sure DNS is configured:"
echo "   A record: @ → $SERVER_IP"
echo "   CNAME: factorial → agints.ru"
read -p "DNS configured? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@agints.ru
    echo "✓ SSL certificate installed"
else
    echo "⚠️  Skipping SSL setup. Run manually later:"
    echo "   sudo certbot --nginx -d $DOMAIN"
fi

# Run database migrations
echo "💾 Running database migrations..."
su - $APP_USER << EOF
cd $APP_DIR
source venv/bin/activate
python scripts/add_translator_fields.py
python scripts/add_needs_summarization.py
EOF

# Start services
echo "🚀 Starting services..."
systemctl start plexmem-api
systemctl start plexmem-bot

sleep 3

# Check status
if systemctl is-active --quiet plexmem-api && systemctl is-active --quiet plexmem-bot; then
    echo "✅ All services running!"
else
    echo "⚠️  Some services failed to start. Check status:"
    systemctl status plexmem-api --no-pager
    systemctl status plexmem-bot --no-pager
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Useful commands:"
echo "  sudo systemctl status plexmem-api plexmem-bot"
echo "  sudo journalctl -u plexmem-api -f"
echo "  sudo journalctl -u plexmem-bot -f"
echo "  tail -f $APP_DIR/logs/api.log"
echo ""
echo "🔄 To update:"
echo "  cd $APP_DIR && ./deploy.sh"
echo ""
echo "🌐 Access:"
echo "  API: https://$DOMAIN/"
echo "  Health: https://$DOMAIN/health"
echo "  Bot: Telegram @factorial_52_bot"

