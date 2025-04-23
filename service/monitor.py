# --------------------------------------------------------------------
# 🧠 MONITORING LOOP: Core background logic for user inactivity checks
# --------------------------------------------------------------------
# This script is executed by the systemd service. It:
# - Loads the configuration and settings
# - Monitors keyboard/mouse activity and user logins
# - Sends notification emails at various inactivity thresholds
# - Stops when maximum inactivity duration is exceeded
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
from core.settings_manager import load_settings
from core.email_utils import (
    send_weekly_email,
    send_start_reached_email,
    send_start_disabled_email,
    send_start_email,
    send_threshold_30_email,
    send_threshold_60_email,
    send_threshold_90_email,
    send_alert_to_recipient,
    send_alert_to_monitoring,
)

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Configure logging for the background service
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    """
    Main loop to monitor user inactivity.

    Periodically checks last login and input timestamps, evaluates thresholds,
    and sends emails or stops the service if needed.
    """

    logging.info("########## Starting service #########")

    # Log diagnostic environment values
    logging.info(f"📡 DISPLAY={os.environ.get('DISPLAY', '<not set>')}")
    logging.info(f"📡 XAUTHORITY={os.environ.get('XAUTHORITY', '<not set>')}")
    logging.info("📡 Run Inactivity Monitor.")

    # Load settings from disk
    settings = load_settings()
    send_monitoring_on_start = settings["send_monitoring_on_start"]
    monitoring_at_30 = settings["monitoring_at_30"]
    monitoring_at_60 = settings["monitoring_at_60"]
    monitoring_at_90 = settings["monitoring_at_90"]
    monitoring_weekly_enabled = settings["monitoring_weekly_enabled"]
    monitoring_weekly_day = settings["monitoring_weekly_day"]
    monitoring_weekly_hour = settings["monitoring_weekly_hour"]

    # Load state flags and previous timestamps
    state = load_state()
    if not state:
        logging.error("🔴 No state found. Aborting monitor.")
        return

    threshold_reached = state["threshold_reached"]
    service_disabled = state["service_disabled"]

    # Load configuration and validate it
    config = load_config(True)
    if not config:
        logging.error("🔴 No configuration found. Aborting monitor.")
        return

    try:
        validate_config(config)
    except Exception as e:
        logging.error(f"🔴 Invalid configuration: {e}")
        return

    # Handle initial state (e.g., if service is disabled or already expired)
    if threshold_reached:
        logging.info("☠️ Service started but threshold already reached.")
        if send_monitoring_on_start:
            send_start_reached_email(config, settings, state)
        else:
            logging.info("🔒 Monitoring email for service startup is disabled.")

        return

    if service_disabled:
        logging.info("Service started but is disabled.")
        if send_monitoring_on_start:
            send_start_disabled_email(config, settings, state)
        else:
            logging.info("🔒 Monitoring email for service startup is disabled.")
        return

    logging.info("🟢 Service started and is active.")
    if send_monitoring_on_start:
        send_start_email(config, settings, state)
    else:
        logging.info("🔒 Monitoring email for service startup is disabled.")

    # Default threshold (30 days in minutes)
    threshold = config.get("timeout_minutes", 4320)

    # Loop forever (until threshold is hit or service stopped)
    while True:
        try:
            logging.info("------------- Loop tick -------------")

            now = datetime.now()
            now_timestamp = now.timestamp()

            state_for_loop = load_state()
            state_updated_with_time = manage_activity_time(state_for_loop, now)

            last_activity_timestamp = max(
                state_updated_with_time["last_input_timestamp"],
                state_updated_with_time["last_login_timestamp"],
            )

            if monitoring_weekly_enabled:

                now_day = now.strftime("%A")
                now_hour = now.hour
                now_date = now.date()

                logging.info(
                    f"📅 [Weekly monitoring] monitoring_weekly_day : {monitoring_weekly_day}"
                )
                logging.info(
                    f"📅 [Weekly monitoring] monitoring_weekly_hour : {monitoring_weekly_hour}"
                )
                logging.info(f"📅 [Weekly monitoring] now_day : {now_day}")
                logging.info(f"📅 [Weekly monitoring] now_hour : {now_hour}")
                logging.info(f"📅 [Weekly monitoring] now_date : {now_date}")

                last_sent_ts = state_updated_with_time.get(
                    "last_weekly_monitoring_sent", 0
                )

                logging.info(f"📅 [Weekly monitoring] last_sent_ts : {last_sent_ts}")

                last_sent_date = (
                    datetime.fromtimestamp(last_sent_ts).date()
                    if last_sent_ts > 0
                    else None
                )

                logging.info(
                    f"📅 [Weekly monitoring] last_sent_date : {last_sent_date}"
                )

                # Conditions to send the email
                should_send = (
                    now_day == monitoring_weekly_day
                    and now_hour >= monitoring_weekly_hour
                    and last_sent_date != now_date
                )

                logging.info(f"📅 [Weekly monitoring] should_send : {should_send}")

                if should_send:
                    try:
                        logging.info(
                            "📬 [Weekly monitoring] Weekly monitoring email is due."
                        )
                        send_weekly_email(config, settings)
                        state_updated_with_time["last_weekly_monitoring_sent"] = (
                            now_timestamp
                        )
                        logging.info(
                            "✅ [Weekly monitoring] Weekly monitoring email sent."
                        )
                    except Exception as e:
                        logging.error(
                            f"❌ [Weekly monitoring] Failed to send weekly monitoring email: {e}"
                        )
                else:
                    logging.info(
                        "📅 [Weekly monitoring] Weekly monitoring not due yet or already sent today."
                    )
            else:
                logging.info(
                    "📅 [Weekly monitoring] Weekly monitoring setting disabled."
                )

            if last_activity_timestamp > 0:
                diff_ts_seconds = now_timestamp - last_activity_timestamp
                diff_ts_minutes = diff_ts_seconds / 60
                logging.info(f"🕒 Inactivity (m): {diff_ts_minutes}")

                # === 30% Threshold
                if monitoring_at_30:
                    threshold__30 = threshold * 0.3
                    if diff_ts_minutes >= threshold__30:
                        logging.info("📊 30% threshold reached.")
                        if not state_updated_with_time.get("monitoring_at_30"):
                            send_threshold_30_email(config, settings, state_for_loop)
                            state_updated_with_time["monitoring_at_30"] = True
                        else:
                            logging.info("📊 30% email already sent.")
                    else:
                        logging.info("📊 Below the 30% threshold.")
                        state_updated_with_time["monitoring_at_30"] = False
                else:
                    logging.info("📊 30% threshold email disabled.")

                # === 60% Threshold
                if monitoring_at_60:
                    threshold__60 = threshold * 0.6
                    if diff_ts_minutes >= threshold__60:
                        logging.info("📊 60% threshold reached.")
                        if not state_updated_with_time.get("monitoring_at_60"):
                            send_threshold_60_email(config, settings, state_for_loop)
                            state_updated_with_time["monitoring_at_60"] = True
                        else:
                            logging.info("📊 60% email already sent.")
                    else:
                        logging.info("📊 Below the 60% threshold.")
                        state_updated_with_time["monitoring_at_60"] = False
                else:
                    logging.info("📊 60% threshold email disabled.")

                # === 90% Threshold
                if monitoring_at_90:
                    threshold__90 = threshold * 0.9
                    if diff_ts_minutes >= threshold__90:
                        logging.info("📊 90% threshold reached.")
                        if not state_updated_with_time.get("monitoring_at_90"):
                            send_threshold_90_email(config, settings, state_for_loop)
                            state_updated_with_time["monitoring_at_90"] = True
                        else:
                            logging.info("📊 90% email already sent.")
                    else:
                        logging.info("📊 Below the 90% threshold.")
                        state_updated_with_time["monitoring_at_90"] = False
                else:
                    logging.info("📊 90% threshold email disabled.")

                # === Final threshold
                logging.info(f"🧪 Threshold check: {diff_ts_minutes} > {threshold} ?")
                if diff_ts_minutes >= threshold:
                    logging.warning("☠️ Inactivity threshold reached!")

                    send_alert_to_recipient(config, settings, state_for_loop)
                    send_alert_to_monitoring(config, settings, state_for_loop)

                    state_updated_with_time["threshold_reached"] = True
                else:
                    logging.info("🟢 Final threshold NOT reached")
            else:
                logging.info("⚠️ No usable activity timestamps found")

            # Save the state
            save_state(state_updated_with_time)

            if state_updated_with_time.get("threshold_reached"):
                logging.warning("☠️ STOP Inactivity Monitor because threshold reached")
                # TODO: Stop the service programmatically here
                break

            logging.info("-------------------------------------")
            time.sleep(30)

        except Exception as e:
            logging.exception("Unexpected error in monitor loop")
            # TODO: Notify via email on loop failure


# Entry point
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in monitor:")
        raise
