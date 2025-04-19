# --------------------------------------------------------------------
# 📁 STATE MANAGEMENT: Track user activity timestamps on disk
# --------------------------------------------------------------------
# This module handles saving and loading runtime state information
# for the Inactivity Monitor. It stores key activity timestamps such
# as the last login and the last keyboard/mouse interaction.
# The state is persisted across reboots using a JSON file.
# --------------------------------------------------------------------

import os
import json
from core.paths import STATE_PATH


def ensure_state_dir():
    """
    Ensure the directory for the state file exists.
    Creates the parent directory of STATE_PATH if it does not already exist.
    """
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)


def load_state():
    """
    Load the application's persistent state from disk.

    Returns:
        dict: A dictionary containing the last login and input timestamps.
              If the file is missing or unreadable, default values are returned.
    """
    ensure_state_dir()

    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass  # Fall back to default if loading fails

    return {
        "last_login_timestamp": 0,
        "last_input_timestamp": 0,
    }


def save_state(state: dict):
    """
    Save the current application state to disk.

    Args:
        state (dict): Dictionary containing 'last_login_timestamp' and 'last_input_timestamp'.
    """
    ensure_state_dir()

    with open(STATE_PATH, "w") as f:
        json.dump(state, f)
