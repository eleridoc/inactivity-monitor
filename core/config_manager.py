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
from email_validator import validate_email, EmailNotValidError
from core.email_utils import validate_email_address
from core.paths import CONFIG_PATH
from core.crypto_utils import encrypt_password, decrypt_password


def load_config():
    """
    Load the application configuration from disk (CONFIG_PATH).
    Decrypt the SMTP password if it exists.

    Returns:
        dict or None: Configuration data with decrypted password,
                      or None if the file does not exist.

    Raises:
        ValueError: If password decryption fails.
    """
    if not os.path.exists(CONFIG_PATH):
        return None

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    # Decrypt the SMTP password if present
    try:
        encrypted_password = data["email"].get("smtp_pass")
        if encrypted_password:
            data["email"]["smtp_pass"] = decrypt_password(encrypted_password)
    except Exception as e:
        raise ValueError(f"Failed to decrypt password: {e}")

    return data


def save_config(data):
    """
    Save the configuration to disk, encrypting the SMTP password first.

    Args:
        data (dict): The configuration dictionary to persist.

    This function creates the target directory if it doesn't exist.
    """
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Encrypt password before saving to disk
    if "smtp_pass" in data["email"]:
        plain_password = data["email"]["smtp_pass"]
        data["email"]["smtp_pass"] = encrypt_password(plain_password)

    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


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
    required_fields = ["timeout_minutes", "email", "message"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")

    # Nested email fields
    email_cfg = data["email"]
    email_fields = ["to", "smtp_server", "smtp_port", "smtp_user", "smtp_pass"]
    for field in email_fields:
        if field not in email_cfg or not email_cfg[field]:
            raise ValueError(f"Missing email field: {field}")

    # Check data types
    if not isinstance(data["timeout_minutes"], int):
        raise ValueError("timeout_minutes must be an integer")
    if not isinstance(email_cfg["smtp_port"], int):
        raise ValueError("smtp_port must be an integer")

    # Validate sender email
    validate_email_address(email_cfg["smtp_user"])

    # Validate all recipients
    for addr in email_cfg["to"]:
        validate_email_address(addr)

    return True
