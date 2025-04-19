# --------------------------------------------------------------------
# 📧 EMAIL UTILITIES: Validation and SMTP test
# --------------------------------------------------------------------

from email_validator import validate_email, EmailNotValidError
import smtplib
from email.message import EmailMessage


def validate_email_address(email: str) -> str:
    """
    Validate a single email address and return its normalized form.

    Args:
        email (str): Raw email address.

    Returns:
        str: Validated and normalized email address.

    Raises:
        EmailNotValidError: If the email is invalid.
    """
    result = validate_email(email)
    return result.email


def validate_recipient_list(recipient_str: str) -> list:
    """
    Validate and normalize a comma-separated list of email addresses.

    Args:
        recipient_str (str): Comma-separated string of emails.

    Returns:
        list: List of validated and normalized email addresses.

    Raises:
        EmailNotValidError: If no valid addresses are provided.
    """
    recipients = [e.strip() for e in recipient_str.split(",") if e.strip()]
    if not recipients:
        raise EmailNotValidError("No recipient email provided.")
    return [validate_email_address(e) for e in recipients]


def send_test_email(config):
    """
    Send a test email using the SMTP settings from the provided configuration.

    Args:
        config (dict): Application configuration containing SMTP credentials.

    Returns:
        str: Success or error message.
    """
    try:
        if not config:
            raise ValueError("No configuration found.")

        smtp_conf = config["email"]

        # Create test message
        msg = EmailMessage()
        msg["Subject"] = "SMTP Test - Inactivity Monitor"
        msg["From"] = smtp_conf["smtp_user"]
        msg["To"] = smtp_conf["smtp_user"]
        msg.set_content(
            "This is a test email sent from the Inactivity Monitor configuration panel."
        )

        # Connect and send email
        with smtplib.SMTP(
            smtp_conf["smtp_server"], smtp_conf["smtp_port"], timeout=10
        ) as server:
            server.starttls()  # Secure connection using TLS
            server.login(smtp_conf["smtp_user"], smtp_conf["smtp_pass"])  # Authenticate
            server.send_message(msg)  # Send message

        return "✅ Test email sent successfully."

    except Exception as e:
        # Return formatted error message for GUI display
        return f"❌ Failed to send test email. Error: {str(e)}"
