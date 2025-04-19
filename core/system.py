# --------------------------------------------------------------------
# 🧑‍💻 SYSTEM MONITORING: Detect system login state and last login time
# --------------------------------------------------------------------
# This module provides functions to check whether a user is currently
# logged in, and to retrieve the timestamp of the most recent login.
# It uses the `psutil` library for system-level user session information.
# --------------------------------------------------------------------

import psutil
from datetime import datetime


def is_user_logged_in():
    """
    Check if any user is currently logged into the system.

    Returns:
        bool: True if at least one user session is active, False otherwise.
    """
    return bool(psutil.users())


def get_last_login_time():
    """
    Retrieve the timestamp of the most recent user login.

    Returns:
        datetime | None: The datetime of the last login, or None if no users are logged in.

    Note:
        - Only the first user from psutil.users() is considered.
        - Useful for determining when a user session was last established.
    """
    users = psutil.users()
    if not users:
        return None

    # Convert the 'started' timestamp to a datetime object
    return datetime.fromtimestamp(users[0].started)
