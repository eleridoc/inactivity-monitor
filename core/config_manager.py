# --------------------------------------------------------------------
# ⚙️ CONFIGURATION MANAGEMENT: Load, validate, and save app settings
# --------------------------------------------------------------------
# This module handles:
# - Loading and decrypting the application's configuration
# - Encrypting and saving sensitive fields (SMTP password)
# - Validating the required fields and data types
# --------------------------------------------------------------------

import os
import json
import subprocess
import tempfile
from core.email_utils import validate_email_address
from core.paths import CONFIG_PATH


def load_config(with_password_decryption=False):
    """
    Load the application configuration from disk (CONFIG_PATH).

    If `with_password_decryption` is True, the SMTP password will be decrypted
    using a privileged helper script. Otherwise, the password field will be returned
    as an empty string to avoid unnecessary elevation prompts.

    Args:
        with_password_decryption (bool): Whether to decrypt the SMTP password (default: False).

    Returns:
        dict or None: Configuration data, possibly with decrypted password,
                      or None if the configuration file does not exist.

    Raises:
        ValueError: If password decryption fails.
    """
    if not os.path.exists(CONFIG_PATH):
        return None

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    if with_password_decryption:
        try:
            path = os.path.join(
                os.path.dirname(__file__), "..", "scripts", "read_password_helper.py"
            )
            result = subprocess.run(
                ["pkexec", "python3", path],
                capture_output=True,
                text=True,
                check=True,
            )
            data["email"]["smtp_pass"] = result.stdout.strip()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {e}")
    else:
        # Hide password in UI unless explicitly requested
        data["email"]["smtp_pass"] = ""

    return data


def validate_config(data):
    """
    Validate the structure and content of the configuration data.

    This includes checking for required fields, correct data types,
    and valid email formats for sender and recipients.

    Args:
        data (dict): The configuration to validate.

    Raises:
        ValueError: If a required field is missing or invalid.

    Returns:
        bool: True if validation passes.
    """
    # Top-level required fields
    required_fields = ["timeout_minutes", "email", "message", "subject"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")

    # Email-related required subfields
    email_cfg = data["email"]
    email_fields = ["to", "smtp_server", "smtp_port", "smtp_user"]
    for field in email_fields:
        if field not in email_cfg or not email_cfg[field]:
            raise ValueError(f"Missing email field: {field}")

    # Type validation
    if not isinstance(data["timeout_minutes"], int):
        raise ValueError("timeout_minutes must be an integer")
    if not isinstance(email_cfg["smtp_port"], int):
        raise ValueError("smtp_port must be an integer")

    # Validate sender and recipient email addresses
    validate_email_address(email_cfg["smtp_user"])
    for addr in email_cfg["to"]:
        validate_email_address(addr)

    return True


def save_config_with_privileges(data, main_window):
    """
    Save the configuration using a privileged helper script (via pkexec).

    This function:
    - Serializes the config into a temporary file
    - Calls a helper script with `pkexec` to save it securely
    - Automatically deletes the temporary file afterward

    Args:
        data (dict): The configuration dictionary to save.
        main_window (Gtk.Window): Reference to UI to send logs (if needed)

    Raises:
        RuntimeError: If saving fails or the helper script encounters an error.
    """
    try:
        # Write configuration to a temporary file
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            json.dump(data, tmp, indent=4)
            tmp_path = tmp.name

        helper_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "save_config_helper.py"
        )
        helper_path = os.path.abspath(helper_path)

        # Run privileged helper
        result = subprocess.run(
            ["pkexec", "python3", helper_path, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Optionally log output
        # main_window.log(f"Stdout: {result.stdout}")
        # main_window.log(f"Stderr: {result.stderr}")

        if result.returncode != 0:
            raise RuntimeError(f"Failed to save config: {result.stderr.strip()}")

    finally:
        # Cleanup temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
