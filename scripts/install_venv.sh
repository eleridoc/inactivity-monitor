#!/bin/bash

# Define application and virtual environment directories
APP_DIR="/opt/inactivity-monitor"
VENV_DIR="$APP_DIR/venv"

echo "🔧 (Re)creating virtual environment in $VENV_DIR"

# Remove existing virtual environment (if any)
sudo rm -rf "$VENV_DIR"

# Create a new virtual environment with access to system packages
sudo python3 -m venv "$VENV_DIR" --system-site-packages

# Upgrade pip and install required Python packages
sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# 🔐 Encryption key generation (if it doesn't already exist)
KEY_PATH="/etc/inactivity-monitor/key.key"
if [ ! -f "$KEY_PATH" ]; then
	echo "🔑 Generating encryption key at $KEY_PATH..."
	# Run Python inline command to generate and save the encryption key
	sudo "$VENV_DIR/bin/python" -c "from core.crypto_utils import generate_key; generate_key()"
	echo "✅ Key generated."
else
  echo "🔐 Key already exists at $KEY_PATH"
fi

echo "✅ Venv ready in $VENV_DIR"
