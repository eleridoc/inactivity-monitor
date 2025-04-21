#!/bin/bash

APP_NAME="inactivity-monitor"
TARGET_DIR="/opt/$APP_NAME"
SERVICE_NAME="$APP_NAME.service"
SERVICE_FILE_PATH="deployment/systemd/$SERVICE_NAME"

echo "🔁 Deploying $APP_NAME to $TARGET_DIR..."

# Exclusions (à adapter si besoin)
EXCLUDES=(
  --exclude '.git'
  --exclude '.vscode'
  --exclude '*.code-workspace'
  --exclude 'deployment'
  --exclude 'venv'
  --exclude 'Makefile'
  --exclude '__pycache__'
  --exclude '*.pyc'
  --exclude 'deploy.sh'
  --exclude '*.md'
)

# Stop the service if it's running
echo "⛔ Stopping systemd service (if running)..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# Rsync project to /opt
sudo rsync -a --delete "${EXCLUDES[@]}" . "$TARGET_DIR/"

# Ensure scripts are executable
sudo chmod +x "$TARGET_DIR/scripts/install_venv.sh"
sudo chmod +x "$TARGET_DIR/scripts/restart.sh"
sudo chmod +x "$TARGET_DIR/scripts/control_service_helper.py"
sudo chmod +x "$TARGET_DIR/scripts/save_config_helper.py"
sudo chmod +x "$TARGET_DIR/scripts/read_password_helper.py"
sudo chmod +x "$TARGET_DIR/scripts/save_settings_helper.py"

sudo cp ./deployment/inactivity-monitor.desktop /usr/share/applications/
sudo chmod +x /usr/share/applications/inactivity-monitor.desktop

sudo cp ./assets/icons/icon-16.png /usr/share/icons/hicolor/16x16/apps/inactivity-monitor.png
sudo cp ./assets/icons/icon-32.png /usr/share/icons/hicolor/32x32/apps/inactivity-monitor.png
sudo cp ./assets/icons/icon-48.png /usr/share/icons/hicolor/48x48/apps/inactivity-monitor.png
sudo cp ./assets/icons/icon-64.png /usr/share/icons/hicolor/64x64/apps/inactivity-monitor.png
sudo cp ./assets/icons/icon-128.png /usr/share/icons/hicolor/128x128/apps/inactivity-monitor.png
sudo cp ./assets/icons/icon-256.png /usr/share/icons/hicolor/256x256/apps/inactivity-monitor.png


gtk-update-icon-cache
update-desktop-database

# Deploy systemd service file if exists
if [ -f "$SERVICE_FILE_PATH" ]; then
    echo "🛠️  Installing systemd service file..."
    sudo cp "$SERVICE_FILE_PATH" /etc/systemd/system/
    sudo systemctl daemon-reload
else
    echo "⚠️  Service file not found: $SERVICE_FILE_PATH"
fi

echo "🚀 $APP_NAME successfully deployed to $TARGET_DIR"