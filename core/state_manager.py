# --------------------------------------------------------------------
# 📁 STATE MANAGEMENT: Track user activity timestamps and flags
# --------------------------------------------------------------------
# This module manages persistent runtime state for the Inactivity Monitor.
# It stores:
# - Last login timestamp
# - Last user input timestamp
# - Monitoring flags (threshold reached, service disabled, etc.)
# --------------------------------------------------------------------

import os
import json
from core.paths import STATE_PATH

# Default structure including activity timestamps and monitoring flags
DEFAULT_STATE = {
    "last_login_timestamp": 0,
    "last_input_timestamp": 0,
    "threshold_reached": False,
    "monitoring_30_reached": False,
    "monitoring_60_reached": False,
    "monitoring_90_reached": False,
    "service_disabled": False,
    "last_weekly_monitoring_timestamp": 0,
}


def ensure_state_dir():
    """Ensure the state directory exists on disk."""
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)


def load_state():
    """
    Load persistent state from disk, including activity timestamps and flags.

    Returns:
        dict: Merged state with defaults if missing keys.
    """
    ensure_state_dir()

    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r") as f:
                data = json.load(f)
                return {**DEFAULT_STATE, **data}  # merge with defaults
        except Exception:
            pass  # fall back if corrupted

    return DEFAULT_STATE.copy()


def save_state(state: dict):
    """
    Save the current state to disk.

    Args:
        state (dict): Dictionary containing timestamps and monitoring flags.
    """
    ensure_state_dir()
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=4)


def reset_monitoring_flags():
    """
    Reset all monitoring flags to False (useful when restarting the service).
    """
    state = load_state()
    for flag in [
        "threshold_reached",
        "monitoring_30_reached",
        "monitoring_60_reached",
        "monitoring_90_reached",
        "service_disabled",
    ]:
        state[flag] = False
    save_state(state)
