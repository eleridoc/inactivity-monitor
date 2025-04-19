# --------------------------------------------------------------------
# 🖱️ INPUT MONITORING: Detect last user activity using xprintidle
# --------------------------------------------------------------------

import subprocess
from shutil import which
from datetime import datetime, timedelta
import logging


def is_xprintidle_available():
    """
    Check if the 'xprintidle' utility is available on the system.

    Returns:
        bool: True if xprintidle is found in PATH, False otherwise.
    """
    return which("xprintidle") is not None


def get_last_input_time():
    """
    Estimate the last user input (keyboard/mouse) using xprintidle.

    This function queries the idle time (in milliseconds) since the last
    user interaction, then subtracts that duration from the current time.

    Returns:
        datetime | None: Timestamp of the last input, or None on error.
    """
    if not is_xprintidle_available():
        logging.info("xprintidle not found. Idle time won't be checked.")
        return None

    try:
        # Run xprintidle to get idle time in milliseconds
        result = subprocess.run(["xprintidle"], capture_output=True, text=True)
        output = result.stdout.strip()

        if not output.isdigit():
            raise ValueError(f"xprintidle returned invalid output: '{output}'")

        idle_ms = int(output)
        # Subtract idle time from now to get last input time
        return datetime.now() - timedelta(milliseconds=idle_ms)

    except Exception as e:
        logging.warning(f"xprintidle error: {e}")
        return None
