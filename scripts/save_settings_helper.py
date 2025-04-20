# --------------------------------------------------------------------
# 💾 SAVE SETTINGS HELPER: Save /etc settings with privilege + restart
# --------------------------------------------------------------------
# This helper script is invoked with elevated privileges (via pkexec)
# to safely save user settings in /etc/inactivity-monitor/settings.json.
# After saving, it automatically restarts the background service.
# --------------------------------------------------------------------

#!/usr/bin/env python3

import os
import sys
import json

# Add project root to sys.path to allow imports from core/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.paths import SETTINGS_PATH
from core.service_utils import run_service_command


def main():
    """
    Main function executed by pkexec to store settings and restart the service.

    Expects a single argument: the path to a temporary JSON file containing the settings.

    Raises:
        SystemExit(1): If any error occurs during the save or restart process.
    """
    try:
        # Validate input argument
        if len(sys.argv) != 2:
            print("Usage: save_settings_helper.py <temp_file_path>")
            sys.exit(1)

        file_path = sys.argv[1]
        print(f"📄 Reading settings from: {file_path}")

        # Read the settings from the temporary JSON file
        with open(file_path, "r") as f:
            settings = json.load(f)

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)

        # Write the settings to the final location
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)

        print("🔄 Now restart the service.")

        # Attempt to restart the systemd service
        try:
            output = run_service_command("restart")
            print(output or "✅ Service restarted.")
        except Exception as e:
            print("❌ Failed to restart the service.", e)

    except Exception as e:
        print(f"❌ Error saving settings: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
