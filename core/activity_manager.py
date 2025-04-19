# --------------------------------------------------------------------
# 📊 ACTIVITY TRACKING: Update login and input timestamps in state file
# --------------------------------------------------------------------
# This module provides a single function `manage_activity_time` that:
# - Reads the current login time and idle time
# - Compares them with previously saved timestamps
# - Updates the state file if more recent activity is detected
# --------------------------------------------------------------------

import logging
import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import load_state, save_state
from core.system import is_user_logged_in, get_last_login_time
from core.input import get_last_input_time


def manage_activity_time():
    """
    Update the state file with the most recent login or input activity timestamps.

    This function:
    - Reads the latest login time using psutil.
    - Checks the last user input (keyboard/mouse) time using xprintidle.
    - Compares with previously saved timestamps.
    - Updates the state file if more recent values are found.

    Returns:
        dict: Updated state containing 'last_login_timestamp' and 'last_input_timestamp'.
    """
    now = datetime.now()

    # Get current login and idle times
    last_login = get_last_login_time()
    last_idle = get_last_input_time()

    # Load previous state from disk
    state = load_state()
    last_login_timestamp = state["last_login_timestamp"]
    last_input_timestamp = state["last_input_timestamp"]

    logging.info(f"Now: {now}")
    logging.info(f"last_login: {last_login}")
    logging.info(f"last_idle: {last_idle}")

    # ⏱️ Update login timestamp if it's newer than previously saved
    if last_login is not None:
        login_ts = int(last_login.timestamp())
        if login_ts > last_login_timestamp:
            logging.info(f"🆕 New login timestamp: {login_ts}")
            state["last_login_timestamp"] = login_ts

    # ⌨️🖱️ Update input timestamp only if a user is currently logged in
    if is_user_logged_in():
        logging.info("✅ User is logged in. Checking input activity...")
        if last_idle is not None:
            idle_ts = int(last_idle.timestamp())
            if idle_ts > last_input_timestamp:
                logging.info(f"🆕 New input timestamp: {idle_ts}")
                state["last_input_timestamp"] = idle_ts
    else:
        # Log why input time isn't used if no user is logged in
        if last_idle is not None:
            logging.info(
                "👤 User is logged out. Input time exists but will not be used."
            )
        else:
            logging.info("👤 User is logged out. No input time available.")

    # 💾 Save the updated state to disk
    save_state(state)

    # Log final timestamps
    logging.info(f"new_last_login_timestamp: {state['last_login_timestamp']}")
    logging.info(f"new_last_input_timestamp: {state['last_input_timestamp']}")

    return state
