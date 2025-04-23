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


def get_formatted_log_message(message: str) -> str:
    """
    Format a log message with a timestamp.

    Args:
        message (str): Message to log.

    Returns:
        str: Formatted string with timestamp.
    """
    now = datetime.now().strftime("%H:%M:%S")
    return f"[{now}] {message}"


def build_log_entry(message: str, exception: Exception = None) -> str:
    """
    Build a full log entry string with timestamp and optional exception trace.
    This also logs the same messages to the system logging.

    Args:
        message (str): The message to log.
        exception (Exception, optional): An exception to include.

    Returns:
        str: Full block to insert into the GUI log.
    """
    log_lines = [get_formatted_log_message(message)]
    logging.info(message)

    if exception:
        trace = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        log_lines.extend(line.rstrip() for line in trace)
        for line in trace:
            logging.info(line.strip())

    return "\n".join(log_lines) + "\n"


def log_to_gui_buffer(log_buffer, log_view, message: str, exception: Exception = None):
    """
    Insert a log message (with optional exception) into the GTK text buffer and scroll down.

    Args:
        log_buffer (Gtk.TextBuffer): The text buffer used for logging.
        log_view (Gtk.TextView): The view displaying the buffer.
        message (str): The message to display.
        exception (Exception, optional): An optional exception to include.
    """
    full_text = build_log_entry(message, exception)
    end_iter = log_buffer.get_end_iter()
    log_buffer.insert(end_iter, full_text)

    # Create a mark and scroll to it reliably
    mark = log_buffer.create_mark(None, log_buffer.get_end_iter(), False)
    log_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)


def log_info(enable_logs, *args):
    """
    Log a message using logging.info() only if logging is enabled.

    This helper allows conditional logging depending on a user-defined
    flag such as 'enable_logs' in the settings. Useful in services or
    background tasks where verbosity is optional.

    Args:
        enable_logs (bool): Whether logging is enabled.
        *args: Parts of the message to concatenate and log. Each arg is
               converted to a string and joined with spaces.

    Example:
        log_info(True, "Service started with PID:", 1234)
    """
    if enable_logs:
        message = " ".join(str(arg) for arg in args)
        logging.info(message)
