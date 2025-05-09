# --------------------------------------------------------------------
# 📁 PATH DEFINITIONS: Centralized file paths for config, logs, state
# --------------------------------------------------------------------

import os

# Path to the main configuration file (JSON)
CONFIG_PATH = "/etc/inactivity-monitor/config.json"

# Path to the main log file used by the background service
LOG_PATH = "/var/log/inactivity-monitor/service.log"

# Path to the file storing the application's persistent state (timestamps, etc.)
STATE_PATH = "/var/lib/inactivity-monitor/state.json"

# Path to the file storing the encryption key used for password encryption
KEY_PATH = "/etc/inactivity-monitor/key.key"

# Path to the gui log file used by the gui
GUI_LOG_PATH = os.path.expanduser("~/.config/inactivity-monitor/gui.log")

# Path to the settings file (JSON)
SETTINGS_PATH = "/etc/inactivity-monitor/settings.json"
