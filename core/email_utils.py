# --------------------------------------------------------------------
# 📧 EMAIL UTILITIES: Validation and SMTP messaging helpers
# --------------------------------------------------------------------
# This module provides:
# - Email validation (single address or comma-separated list)
# - Generic and test email sending via SMTP
# - Placeholders for monitoring-related notification functions
# --------------------------------------------------------------------

from email_validator import validate_email, EmailNotValidError
import smtplib
import logging
from email.message import EmailMessage


def validate_email_address(email: str) -> str:
    """
    Validate a single email address and return its normalized form.

    Args:
        email (str): Raw email address to validate.

    Returns:
        str: Normalized and validated email address.

    Raises:
        EmailNotValidError: If the email is invalid.
    """
    result = validate_email(email)
    return result.email


def validate_recipient_list(recipient_str: str) -> list:
    """
    Validate and normalize a comma-separated list of email addresses.

    Args:
        recipient_str (str): Comma-separated string of email addresses.

    Returns:
        list: List of validated and normalized email addresses.

    Raises:
        EmailNotValidError: If no valid addresses are provided.
    """
    recipients = [e.strip() for e in recipient_str.split(",") if e.strip()]
    if not recipients:
        raise EmailNotValidError("No recipient email provided.")
    return [validate_email_address(e) for e in recipients]


# Placeholder notification methods (to be implemented later)


def send_weekly_email(config, settings, state):
    """Send notification each week."""
    logging.info("send_weekly_email")


def send_start_reached_email(config, settings, state):
    """Send notification when monitoring threshold is initially reached."""
    logging.info("send_start_reached_email")


def send_start_disabled_email(config, settings, state):
    """Send notification if monitoring is disabled."""
    logging.info("send_start_disabled_email")


def send_start_email(config, settings, state):
    """Send monitoring start email."""
    logging.info("send_start_email")


def send_threshold_30_email(config, settings, state):
    """Send monitoring email at 30% of timeout threshold."""
    logging.info("send_threshold_30_email")


def send_threshold_60_email(config, settings, state):
    """Send monitoring email at 60% of timeout threshold."""
    logging.info("send_threshold_60_email")


def send_threshold_90_email(config, settings, state):
    """Send monitoring email at 90% of timeout threshold."""
    logging.info("send_threshold_90_email")


def send_alert_to_recipient(config, settings, state):
    """Send emergency alert to predefined recipients."""
    logging.info("send_alert_to_recipient")


def send_alert_to_monitoring(config, settings, state):
    """Send emergency alert to monitoring address."""
    logging.info("send_alert_to_monitoring")


def send_test_email(config, settings):
    """
    Send a test email using the SMTP configuration and monitoring settings.

    Args:
        config (dict): Main application config (SMTP credentials, etc.).
        settings (dict): Optional settings (may contain alternate recipient).

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        if not config:
            raise ValueError("No configuration found.")
        smtp_conf = config["email"]

        # Use monitoring_sender if defined
        email_to = smtp_conf["smtp_user"]
        if settings and settings.get("monitoring_sender"):
            email_to = settings["monitoring_sender"]

        send_email(
            config,
            smtp_conf["smtp_user"],
            email_to,
            "[Inactivity Monitor][Test email]",
            "This is a test email sent from the Inactivity Monitor configuration panel.",
        )
        return True
    except Exception as e:
        return False


def send_email(config, email_from, email_to, email_subject, email_content):
    """
    Send an email using the configured SMTP server.

    Args:
        config (dict): Contains SMTP server, port, credentials.
        email_from (str): Email sender address.
        email_to (str): Email recipient address.
        email_subject (str): Subject line.
        email_content (str): Plain text message body.

    Returns:
        bool: True if email sent successfully, False otherwise.
    """
    try:
        if not config:
            raise ValueError("No configuration found.")

        smtp_conf = config["email"]

        # Compose email
        msg = EmailMessage()
        msg["Subject"] = email_subject
        msg["From"] = email_from
        msg["To"] = email_to
        msg.set_content(email_content)

        # Send via SMTP
        with smtplib.SMTP(
            smtp_conf["smtp_server"], smtp_conf["smtp_port"], timeout=10
        ) as server:
            server.starttls()  # Enable TLS
            server.login(smtp_conf["smtp_user"], smtp_conf["smtp_pass"])  # Auth
            server.send_message(msg)  # Send

        return True

    except Exception as e:
        return False
