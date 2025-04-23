# --------------------------------------------------------------------
# ⚙️ SETTINGS MANAGEMENT: Load, validate, and save app user options
# --------------------------------------------------------------------
# This module handles:
# - Loading user-defined options from /etc/inactivity-monitor/settings.json
# - Validating optional fields (e.g. custom monitoring sender email)
# - Saving settings with elevated privileges via a helper script
# --------------------------------------------------------------------
from gi.repository import GLib
import os
import json
import tempfile
import subprocess
from core.paths import SETTINGS_PATH
from core.email_utils import validate_email_address
from email_validator import EmailNotValidError

# Default settings used if no file is found or keys are missing
DEFAULT_SETTINGS = {
    "enable_logs": False,
    "send_monitoring_on_start": False,
    "monitoring_sender": "",
    "monitoring_at_30": False,
    "monitoring_at_60": False,
    "monitoring_at_90": False,
    "startup_error": False,
    "weekly_monitoring_enabled": False,
    "weekly_monitoring_day": 0,
    "weekly_monitoring_hour": 12,
}


def load_settings():
    """
    Load user settings from disk or return default values if file is missing.

    Returns:
        dict: Complete settings dictionary with defaults merged in.
    """
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_SETTINGS.copy()

    with open(SETTINGS_PATH, "r") as f:
        data = json.load(f)

    return {**DEFAULT_SETTINGS, **data}  # Merge user-defined with defaults


def validate_settings(settings: dict):
    """
    Validate the structure and content of the user settings.

    This ensures the optional monitoring email (monitoring_sender)
    is either empty or a valid email address.

    Args:
        settings (dict): The settings dictionary to validate.

    Raises:
        ValueError: If the monitoring_sender is not a valid email address.
    """
    email = settings.get("monitoring_sender", "").strip()

    if email:  # Only validate if not empty
        try:
            validate_email_address(email)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid monitoring sender email: {e}")


def save_settings_with_privileges(settings: dict, main_window=None):
    """
    Save the settings dictionary to disk using elevated privileges (via pkexec).

    Args:
        settings (dict): The settings to persist in the settings file.
        main_window (Gtk.Window, optional): If provided, logs will be printed to this GUI window.

    Raises:
        RuntimeError: If the helper script fails to save the settings.
    """
    try:
        # Create temporary JSON file to pass to privileged helper
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            json.dump(settings, tmp, indent=4)
            tmp_path = tmp.name

        # Path to helper script that runs with privileges
        helper_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "scripts", "save_settings_helper.py"
            )
        )

        result = subprocess.run(
            ["pkexec", "python3", helper_path, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Forward output to GUI logs
        # if main_window:
        #     if result.stdout:
        #         for line in result.stdout.strip().splitlines():
        #             GLib.idle_add(main_window.log, line)
        #     if result.stderr:
        #         for line in result.stderr.strip().splitlines():
        #             GLib.idle_add(main_window.log, line)

        # Raise if command failed
        if result.returncode != 0:
            raise RuntimeError(f"Failed to save settings: {result.stderr.strip()}")

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
