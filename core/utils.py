# --------------------------------------------------------------------
# 🧮 UTILITY FUNCTIONS: Timestamp formatting & human-readable durations
# --------------------------------------------------------------------
# This module contains helper functions used to:
# - Convert timestamps into readable strings
# - Convert an inactivity threshold (in minutes) into days/hours/minutes
# --------------------------------------------------------------------

from datetime import datetime
import logging
import traceback


def format_timestamp(ts):
    """
    Convert a UNIX timestamp to a human-readable string.

    Args:
        ts (int or float): The timestamp to format.

    Returns:
        str: A string in the format 'YYYY-MM-DD HH:MM:SS' or '—' if invalid.
    """
    if not ts:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def get_threshold_info(minutes):
    """
    Convert a number of minutes into a human-readable duration.

    Args:
        minutes (int): Total number of minutes.

    Returns:
        str: A string like '1 day(s), 3 hour(s), 15 minute(s)'.
             Returns an empty string on invalid input.
    """
    try:
        days, rem_minutes = divmod(minutes, 1440)  # 1440 minutes = 1 day
        hours, minutes = divmod(rem_minutes, 60)

        parts = []
        if days:
            parts.append(f"{days} day(s)")
        if hours:
            parts.append(f"{hours} hour(s)")
        if minutes or not parts:
            parts.append(f"{minutes} minute(s)")

        return ", ".join(parts)
    except ValueError:
        return ""


def get_formated_log_message(message: str):
    now = datetime.now().strftime("%H:%M:%S")
    formated_message = f"[{now}] {message}"
    return formated_message


def build_log_entry(message: str, exception: Exception = None) -> str:
    """
    Build a full log entry string with timestamp and optional exception trace.

    This also writes the same data to the logging system.

    Args:
        message (str): The message to log.
        exception (Exception, optional): An exception to include.

    Returns:
        str: Full log text block (with timestamp) to be inserted in GUI.
    """

    log_lines = [get_formated_log_message(message)]

    logging.info(message)

    if exception:
        trace = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        log_lines.extend(line.rstrip() for line in trace)
        for line in trace:
            logging.info(line.strip())

    return "".join(log_lines) + "\n"
