#!/bin/bash

# Define the systemd service name
SERVICE_NAME="inactivity-monitor"


echo "🔄 (Re)starting systemd service: $SERVICE_NAME"

# Reload systemd to ensure it sees any recent service file changes
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable "$SERVICE_NAME"

# Stop the service if it's already running (ignore errors)
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# Start the service
sudo systemctl start "$SERVICE_NAME"

# Wait briefly before checking status (give the service time to start)
sleep 1.5

echo
echo "📡 Service status:"
# Show a short status summary for the service
sudo systemctl status "$SERVICE_NAME" --no-pager --lines=5

echo
echo "✅ Service started and checked successfully."
