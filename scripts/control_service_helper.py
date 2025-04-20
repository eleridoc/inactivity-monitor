#!/usr/bin/env python3

# --------------------------------------------------------------------
# ⚙️ SERVICE CONTROL HELPER: Run systemctl commands via pkexec
# --------------------------------------------------------------------
# This script is used to start, stop, or restart the background systemd
# service 'inactivity-monitor' with elevated privileges (via pkexec).
# It is designed to be called from the GTK UI for safe privilege escalation.
# --------------------------------------------------------------------

import sys
import subprocess
import os

# Add project root to sys.path to allow local imports if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Validate number of arguments
if len(sys.argv) != 2:
    print("Usage: control_service_helper.py <start|stop|restart>")
    sys.exit(1)

command = sys.argv[1]
service = "inactivity-monitor"

# Validate the command argument
if command not in ["start", "stop", "restart"]:
    print("Invalid command. Use start, stop, or restart.")
    sys.exit(1)

try:
    """
    Run the appropriate systemctl command.
    If successful, display a confirmation message.
    """
    subprocess.run(["systemctl", command, service], check=True)
    print(f"✅ Service '{service}' {command}ed successfully.")
except subprocess.CalledProcessError as e:
    """
    Handle failure when the systemctl command returns a non-zero status.
    """
    print(f"❌ Failed to {command} service: {e}")
    sys.exit(1)
