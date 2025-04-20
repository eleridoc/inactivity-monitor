#!/usr/bin/env python3

# --------------------------------------------------------------------
# 💾 CONFIG SAVE HELPER: Save config file with encryption + privileges
# --------------------------------------------------------------------
# This script is designed to be run with `pkexec` to write the configuration
# to the system-level CONFIG_PATH with appropriate permissions.
# It:
# - Reads JSON input (stdin or file path)
# - Encrypts the SMTP password if provided
# - Reuses the existing encrypted password if the input is blank
# - Writes the final JSON config to the secure path
# --------------------------------------------------------------------

import os
import sys
import json

# Add project root to sys.path to allow local imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.paths import CONFIG_PATH
from core.crypto_utils import encrypt_password


def main():
    """
    Read configuration JSON from stdin or a file path, encrypt password if needed,
    and write the updated configuration to CONFIG_PATH with elevated privileges.

    This function is meant to be called by pkexec and ensures proper handling
    of sensitive password encryption and config persistence.
    """
    try:
        # Determine the source of the JSON input
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            print(f"📄 Reading data from file: {file_path}")
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            print("📥 Reading data from stdin...")
            data = json.load(sys.stdin)

        print("✅ JSON data successfully read")

        # Ensure target directory exists
        target_dir = os.path.dirname(CONFIG_PATH)
        print(f"📁 Ensuring directory exists: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)

        # Load existing password from config to preserve it if input is blank
        existing_password = None
        if os.path.exists(CONFIG_PATH):
            print(f"📂 Existing config found at {CONFIG_PATH}")
            with open(CONFIG_PATH, "r") as f:
                existing = json.load(f)
                existing_password = existing["email"].get("smtp_pass", None)
        else:
            print("⚠️ No existing config found")

        # Handle the password logic
        if "smtp_pass" in data["email"]:
            plain_password = data["email"]["smtp_pass"].strip()
            if plain_password == "":
                print("🔐 Empty password field — reusing previous encrypted password")
                if existing_password:
                    data["email"]["smtp_pass"] = existing_password
                else:
                    raise ValueError("No previous password found to reuse.")
            else:
                print("🔐 Encrypting new password...")
                data["email"]["smtp_pass"] = encrypt_password(plain_password)
        else:
            print("❌ smtp_pass not found in data")

        # Save final config
        print(f"💾 Saving config to {CONFIG_PATH}...")
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)

        print("✅ Config saved successfully")

    except Exception as e:
        print(f"❌ Error during save: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
