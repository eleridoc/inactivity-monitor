# --------------------------------------------------------------------
# 🧠 MONITORING LOOP: Core background logic for user inactivity checks
# --------------------------------------------------------------------
# This script is executed by the systemd service. It:
# - Loads the configuration file
# - Periodically checks for last user login and input activity
# - Calculates inactivity duration
# - Logs warnings when the threshold is exceeded
# --------------------------------------------------------------------

import time
import logging
import os
import sys
from datetime import datetime

# Add root project path to sys.path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paths import LOG_PATH
from core.config_manager import load_config, validate_config
from core.activity_manager import manage_activity_time

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Configure global logger for this script
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    """
    Main loop to monitor system inactivity and log alerts if the timeout is reached.
    It runs continuously with a fixed sleep interval.
    """
    # Diagnostic: log environment context
    logging.info(f"DISPLAY={os.environ.get('DISPLAY', '<not set>')}")
    logging.info(f"XAUTHORITY={os.environ.get('XAUTHORITY', '<not set>')}")
    logging.info("📡 Inactivity Monitor started.")

    # Load and validate configuration
    config = load_config(True)
    if not config:
        logging.error("No configuration found. Aborting monitor.")
        return

    try:
        validate_config(config)
    except Exception as e:
        logging.error(f"Invalid configuration: {e}")
        return

    # Default inactivity threshold (in minutes): 30 days
    threshold = config.get("timeout_minutes", 4320)

    while True:
        try:
            logging.info("------------- Loop tick -------------")

            now = datetime.now()
            now_timestamp = now.timestamp()

            # Fetch updated activity timestamps
            state = manage_activity_time()

            last_activity_timestamp = max(
                state["last_input_timestamp"], state["last_login_timestamp"]
            )

            if last_activity_timestamp > 0:
                diff_ts_seconds = now_timestamp - last_activity_timestamp
                logging.info(f"🕒 Inactivity (s): {diff_ts_seconds}")

                if diff_ts_seconds >= 0:
                    diff_ts_minutes = diff_ts_seconds / 60
                    logging.info(f"🕒 Inactivity (m): {diff_ts_minutes}")
                    logging.info(
                        f"🧪 Threshold check: {diff_ts_minutes} > {threshold} ?"
                    )

                    if diff_ts_minutes >= threshold:
                        logging.warning(
                            "⏰ Inactivity threshold reached! (TODO: send email)"
                        )
                    else:
                        logging.info("✅ Threshold NOT reached")
                else:
                    logging.info("🌀 Time anomaly: future activity?")
            else:
                logging.info("⚠️ No usable activity timestamps available")

            logging.info("-------------------------------------")
            time.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logging.exception("Unexpected error in monitor loop")


# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in monitor:")
        raise
