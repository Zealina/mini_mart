#!/usr/bin/env bash
#
# setup_vps.sh — Provision a fresh Ubuntu/Debian VPS for the cexpressminimart app
#
# What it does:
#   1. Installs Python3 + pip, Node.js + npm, Nginx
#   2. Installs your pip requirements (in a venv) and npm dependencies
#   3. Runs `npm run build` and moves the build output to /var/www/cexpressminimart
#   4. Creates /var/www/cexpressminimart-uploads
#   5. chowns both dirs so Nginx (www-data) can serve/write to them
#   6. Copies your repo's nginx config into sites-available, enables it, tests it
#   7. Sets up Gunicorn (WSGI) to run the Flask app as a systemd service
#
# Usage:
#   1. Edit the CONFIG block below to match your setup
#   2. chmod +x setup_vps.sh
#   3. sudo ./setup_vps.sh
#
set -euo pipefail

# ============================== CONFIG ==============================
# Path to your project repo on the server (already git-cloned there)
REPO_DIR="/home/$(logname)/mini_mart"

# Where the built frontend should live (served by nginx)
WEB_ROOT="/var/www/cexpressminimart"

# Uploads directory
UPLOADS_DIR="/var/www/cexpressminimart-uploads"

# Frontend build output dir relative to REPO_DIR (vite default is "dist")
BUILD_DIR="dist"

# Path (relative to REPO_DIR) to your requirements.txt
REQUIREMENTS_FILE="requirements.txt"

# Path (relative to REPO_DIR) to your nginx config file in the repo
NGINX_CONF_SRC="deploy/nginx.conf"
NGINX_SITE_NAME="cexpressminimart"

# Python venv location
VENV_DIR="$REPO_DIR/venv"

# Flask/WSGI entrypoint, in the form module:variable (e.g. app:app or wsgi:app)
WSGI_ENTRYPOINT="wsgi:app"

# Gunicorn bind address (match whatever your nginx conf proxies to)
GUNICORN_BIND="127.0.0.1:8000"

# systemd service name for gunicorn
SERVICE_NAME="cexpressminimart"

# User/group nginx runs as (usually www-data on Debian/Ubuntu)
WEB_USER="www-data"
WEB_GROUP="www-data"
# ======================================================================

if [[ $EUID -ne 0 ]]; then
  echo "Please run this script with sudo." >&2
  exit 1
fi

echo "==> Updating package lists"
apt-get update -y

echo "==> Installing Python3, pip, venv"
apt-get install -y python3 python3-pip python3-venv

echo "==> Installing Node.js + npm (via NodeSource, Node 20.x)"
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
else
  echo "Node.js already installed: $(node -v)"
fi

echo "==> Installing Vite globally (in case it's not a project devDependency)"
npm install -g vite

echo "==> Installing Nginx"
apt-get install -y nginx

# ------------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------------
echo "==> Setting up Python virtual environment"
cd "$REPO_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$REPO_DIR/$REQUIREMENTS_FILE"
pip install gunicorn
deactivate

# ------------------------------------------------------------------
# Node dependencies + build
# ------------------------------------------------------------------
echo "==> Installing npm dependencies"
cd "$REPO_DIR"
npm install

echo "==> Building frontend with npm run build"
npm run build

echo "==> Moving build output to $WEB_ROOT"
mkdir -p "$WEB_ROOT"
rm -rf "${WEB_ROOT:?}"/*
cp -r "$REPO_DIR/$BUILD_DIR/"* "$WEB_ROOT/"

# ------------------------------------------------------------------
# Uploads directory
# ------------------------------------------------------------------
echo "==> Creating uploads directory at $UPLOADS_DIR"
mkdir -p "$UPLOADS_DIR"

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
echo "==> Setting ownership/permissions for nginx access"
chown -R "$WEB_USER:$WEB_GROUP" "$WEB_ROOT"
chown -R "$WEB_USER:$WEB_GROUP" "$UPLOADS_DIR"
chmod -R 755 "$WEB_ROOT"
chmod -R 775 "$UPLOADS_DIR"

# ------------------------------------------------------------------
# Nginx config
# ------------------------------------------------------------------
echo "==> Installing nginx config"
if [[ ! -f "$REPO_DIR/$NGINX_CONF_SRC" ]]; then
  echo "ERROR: nginx config not found at $REPO_DIR/$NGINX_CONF_SRC" >&2
  exit 1
fi

cp "$REPO_DIR/$NGINX_CONF_SRC" "/etc/nginx/sites-available/$NGINX_SITE_NAME"
ln -sf "/etc/nginx/sites-available/$NGINX_SITE_NAME" "/etc/nginx/sites-enabled/$NGINX_SITE_NAME"

echo "==> Testing nginx config"
nginx -t

echo "==> Restarting nginx"
systemctl restart nginx
systemctl enable nginx

# ------------------------------------------------------------------
# Gunicorn / WSGI systemd service
# ------------------------------------------------------------------
echo "==> Creating systemd service for Gunicorn (Flask WSGI)"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Gunicorn instance to serve ${SERVICE_NAME}
After=network.target

[Service]
User=${WEB_USER}
Group=${WEB_GROUP}
WorkingDirectory=${REPO_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind ${GUNICORN_BIND} ${WSGI_ENTRYPOINT}
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "==> Enabling and starting Gunicorn service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "==> Done!"
echo "    Frontend served from: $WEB_ROOT"
echo "    Uploads dir:          $UPLOADS_DIR"
echo "    Gunicorn service:     systemctl status $SERVICE_NAME"
echo "    Nginx site:           /etc/nginx/sites-available/$NGINX_SITE_NAME"
