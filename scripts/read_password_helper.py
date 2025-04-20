#!/usr/bin/env python3

# --------------------------------------------------------------------
# 🔐 PASSWORD HELPER: Decrypt SMTP password with elevated privileges
# --------------------------------------------------------------------
# This script is intended to be run with pkexec and used by the GTK UI.
# It securely reads the SMTP password from the config file, decrypts it,
# and returns it via stdout for display or editing in the GUI.
# --------------------------------------------------------------------

import sys
import os

# Add project root to sys.path to allow local imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import json
from core.paths import CONFIG_PATH
from core.crypto_utils import decrypt_password

try:
    # Load the configuration file
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    # Get the encrypted password
    encrypted = config["email"]["smtp_pass"]

    if encrypted:
        # Decrypt and print the password to stdout
        decrypted = decrypt_password(encrypted)
        print(decrypted)
    else:
        # If no password is stored, output empty string
        print("")
except Exception as e:
    """
    Handle decryption errors (e.g., permission denied, missing file).
    Prints the error and exits with non-zero status.
    """
    print(f"ERROR: {e}")
    exit(1)
