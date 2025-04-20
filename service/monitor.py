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
from core.state_manager import load_state, save_state

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

    # Load state
    state = load_state()
    if not state:
        logging.error("No state found. Aborting monitor.")
        return

    threshold_reached = state["threshold_reached"]
    service_disabled = state["service_disabled"]

    if threshold_reached:
        # Todo : send monitoring email, started but threshold reached (if send_monitoring_on_start activated)
        logging.info(
            "Threshold reached, send email to monitoring (if send_monitoring_on_start activated) and stop Inactivity Monitor."
        )
        return

    if service_disabled:
        # Todo : send monitoring email, started but service disabled (if send_monitoring_on_start activated)
        logging.info(
            "Service disabled, send email to monitoring (if send_monitoring_on_start activated) and stop Inactivity Monitor."
        )
        return

    # Load and validate configuration
    config = load_config(True)
    if not config:
        # Todo : send monitoring email, started but error (if send_monitoring_on_start activated)

        logging.error("No configuration found. Aborting monitor.")
        return

    try:
        validate_config(config)
    except Exception as e:

        # Todo : send monitoring email, started but error (if send_monitoring_on_start activated)

        logging.error(f"Invalid configuration: {e}")
        return

    # Default inactivity threshold (in minutes): 30 days
    threshold = config.get("timeout_minutes", 4320)

    while True:
        try:
            logging.info("------------- Loop tick -------------")

            now = datetime.now()
            now_timestamp = now.timestamp()

            # Load previous state from disk
            state_for_loop = load_state()

            # Fetch updated activity timestamps
            state_updated_with_time = manage_activity_time(state_for_loop, now)

            last_activity_timestamp = max(
                state_updated_with_time["last_input_timestamp"],
                state_updated_with_time["last_login_timestamp"],
            )

            if last_activity_timestamp > 0:
                diff_ts_seconds = now_timestamp - last_activity_timestamp
                logging.info(f"🕒 Inactivity (s): {diff_ts_seconds}")

                if diff_ts_seconds >= 0:
                    diff_ts_minutes = diff_ts_seconds / 60
                    logging.info(f"🕒 Inactivity (m): {diff_ts_minutes}")

                    threshold__30 = threshold * 0.3
                    threshold__60 = threshold * 0.6
                    threshold__90 = threshold * 0.9

                    if diff_ts_minutes >= threshold__30:
                        logging.info("30% threshold reached.")
                        if state_updated_with_time["monitoring_at_30"] is not True:
                            # Todo : send monitoring email, 30% threshold reached. (if monitoring_at_30 activated)
                            logging.info(
                                "30% threshold reached, send email to monitoring"
                            )
                            state_updated_with_time["monitoring_at_30"] = True
                        else:
                            logging.info("30% threshold reached, email already sent.")
                    else:
                        logging.info("30% threshold NOT reached.")
                        state_updated_with_time["monitoring_at_30"] = False

                    if diff_ts_minutes >= threshold__60:
                        logging.info("60% threshold reached.")
                        if state_updated_with_time["monitoring_at_60"] is not True:
                            # Todo : send monitoring email, 60% threshold reached. (if monitoring_at_60 activated)
                            logging.info(
                                "60% threshold reached, send email to monitoring"
                            )
                            state_updated_with_time["monitoring_at_60"] = True
                        else:
                            logging.info("60% threshold reached, email already sent.")
                    else:
                        logging.info("60% threshold NOT reached.")
                        state_updated_with_time["monitoring_at_60"] = False

                    if diff_ts_minutes >= threshold__90:
                        logging.info("90% threshold reached.")
                        if state_updated_with_time["monitoring_at_90"] is not True:
                            # Todo : send monitoring email, 90% threshold reached. (if monitoring_at_90 activated)
                            logging.info(
                                "90% threshold reached, send email to monitoring"
                            )
                            state_updated_with_time["monitoring_at_90"] = True
                        else:
                            logging.info("90% threshold reached, email already sent.")
                    else:
                        logging.info("90% threshold NOT reached.")
                        state_updated_with_time["monitoring_at_90"] = False

                    logging.info(
                        f"🧪 Threshold check: {diff_ts_minutes} > {threshold} ?"
                    )

                    if diff_ts_minutes >= threshold:
                        logging.warning(
                            "⏰ Inactivity threshold reached! (TODO: send email)"
                        )
                        # Todo : send monitoring email, threshold reached.
                        # Todo : send email to recipients, threshold reached.
                        state_updated_with_time["threshold_reached"] = True
                    else:
                        logging.info("✅ Threshold NOT reached")
                else:
                    logging.info("🌀 Time anomaly: future activity?")
            else:
                logging.info("⚠️ No usable activity timestamps available")

            # 💾 Save the updated state to disk
            save_state(state_updated_with_time)

            if state_updated_with_time["threshold_reached"]:
                logging.warning("☠️ STOP Inactivity Monitor because threshold reached")
                # todo stop the service !!!

            logging.info("-------------------------------------")
            time.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logging.exception("Unexpected error in monitor loop")
            # Todo : send monitoring email, because of erro in Loop tick


# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in monitor:")
        raise
