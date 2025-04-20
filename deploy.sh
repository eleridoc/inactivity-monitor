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
sudo chmod +x "$TARGET_DIR/scripts/encrypt_password_helper.py"

# Deploy systemd service file if exists
if [ -f "$SERVICE_FILE_PATH" ]; then
    echo "🛠️  Installing systemd service file..."
    sudo cp "$SERVICE_FILE_PATH" /etc/systemd/system/
    sudo systemctl daemon-reload
else
    echo "⚠️  Service file not found: $SERVICE_FILE_PATH"
fi

echo "🚀 $APP_NAME successfully deployed to $TARGET_DIR"