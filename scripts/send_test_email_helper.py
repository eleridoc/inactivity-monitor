#!/usr/bin/env python3

# --------------------------------------------------------------------
# 📧 TEST EMAIL SCRIPT: Sends a test email using loaded configuration
# --------------------------------------------------------------------
# This script:
# - Loads the application's main configuration and settings
# - Sends a test email to verify SMTP functionality
# - Designed to be called from the UI or CLI using elevated privileges
# --------------------------------------------------------------------

import os
import sys
import json
import smtplib

# Add project root to sys.path to allow core module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.config_manager import load_config
from core.settings_manager import load_settings
from core.email_utils import send_test_email


def main():
    """
    Load config and settings, then send a test email using the SMTP credentials.

    The script prints a success or failure message to stdout/stderr
    and returns an appropriate exit code (0 for success, 1 for failure).
    """
    try:
        # Load config with SMTP password decryption
        config = load_config(True)
        settings = load_settings()

        # Attempt to send the test email
        result = send_test_email(config, settings)

        if result:
            print("✅ Test email sent successfully.")
        else:
            print("❌ Failed to send test email.")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to send test email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
