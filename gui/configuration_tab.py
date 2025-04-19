# --------------------------------------------------------------------
# 🛠️ CONFIGURATION TAB: UI for managing inactivity timeout and SMTP
# --------------------------------------------------------------------
# This module defines the ConfigurationTab class, which builds the UI
# for editing and saving the inactivity timeout and email alert settings.
# It allows testing the SMTP configuration and provides form validation.
# --------------------------------------------------------------------

from gi.repository import Gtk
from email_validator import EmailNotValidError
from core.config_manager import load_config, save_config, validate_config
from core.email_utils import (
    validate_email_address,
    validate_recipient_list,
    send_test_email,
)
from core.utils import get_threshold_info


class ConfigurationTab(Gtk.Grid):
    """
    This class represents the 'Configuration' tab of the application.
    It allows the user to configure inactivity timeout and email settings.
    """

    def __init__(self, main_window):
        """
        Initialize the Configuration tab layout and load existing config.

        Args:
            main_window (Gtk.Window): Reference to the main window for logging.
        """
        super().__init__(column_spacing=10, row_spacing=10, margin=10)
        self.main_window = main_window  # Access to main log() method
        self.build_ui()
        self.load_config()

    def build_ui(self):
        """
        Build and organize all the UI widgets on the configuration tab.
        """
        row = 0

        # === Inactivity timeout field ===
        self.timeout_entry = Gtk.Entry()
        self.timeout_entry.connect("changed", self.display_threshold_info)
        self.attach(Gtk.Label(label="Inactivity delay (minutes):"), 0, row, 1, 1)
        self.attach(self.timeout_entry, 1, row, 1, 1)
        row += 1

        # === Human-readable version of timeout ===
        self.timeout_info_label = Gtk.Label(label="")
        self.attach(self.timeout_info_label, 1, row, 1, 1)
        row += 1

        # === Recipients input ===
        self.email_entry = Gtk.Entry()
        self.attach(Gtk.Label(label="Recipients (comma-separated):"), 0, row, 1, 1)
        self.attach(self.email_entry, 1, row, 1, 1)
        row += 1

        # === Email subject ===
        self.subject_entry = Gtk.Entry()
        self.attach(Gtk.Label(label="Email subject:"), 0, row, 1, 1)
        self.attach(self.subject_entry, 1, row, 1, 1)
        row += 1

        # === Email content textarea ===
        self.message_buffer = Gtk.TextBuffer()
        message_view = Gtk.TextView(buffer=self.message_buffer)
        message_view.set_wrap_mode(Gtk.WrapMode.WORD)
        message_view.set_size_request(300, 100)

        message_frame = Gtk.Frame()
        message_frame.set_shadow_type(Gtk.ShadowType.IN)
        message_frame.add(message_view)

        self.attach(Gtk.Label(label="Email message:"), 0, row, 1, 1)
        self.attach(message_frame, 1, row, 1, 1)
        row += 1

        # === Separator ===
        separator_01 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator_01.set_margin_top(10)
        separator_01.set_margin_bottom(10)
        separator_01.set_hexpand(True)
        separator_01.set_halign(Gtk.Align.FILL)
        self.attach(separator_01, 0, row, 2, 1)
        row += 1

        # === SMTP configuration inputs ===
        self.smtp_host_entry = Gtk.Entry()
        self.attach(Gtk.Label(label="SMTP host:"), 0, row, 1, 1)
        self.attach(self.smtp_host_entry, 1, row, 1, 1)
        row += 1

        self.smtp_port_entry = Gtk.Entry()
        self.attach(Gtk.Label(label="SMTP port:"), 0, row, 1, 1)
        self.attach(self.smtp_port_entry, 1, row, 1, 1)
        row += 1

        self.smtp_user_entry = Gtk.Entry()
        self.attach(Gtk.Label(label="SMTP username:"), 0, row, 1, 1)
        self.attach(self.smtp_user_entry, 1, row, 1, 1)
        row += 1

        self.smtp_pass_entry = Gtk.Entry()
        self.smtp_pass_entry.set_visibility(False)
        self.attach(Gtk.Label(label="SMTP password:"), 0, row, 1, 1)
        self.attach(self.smtp_pass_entry, 1, row, 1, 1)
        row += 1

        # === Bottom separator ===
        separator_bottom = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.attach(separator_bottom, 0, row, 2, 1)
        row += 1

        # === Test button for SMTP ===
        self.test_smtp_button = Gtk.Button(label="Test SMTP conf")
        self.test_smtp_button.connect("clicked", self.on_test_smtp_clicked)
        self.attach(self.test_smtp_button, 0, row, 1, 1)

        # === Save button for the full configuration ===
        save_button = Gtk.Button(label="Save configuration")
        save_button.connect("clicked", self.on_save_clicked)
        self.attach(save_button, 1, row, 1, 1)

    def load_config(self):
        """
        Load configuration from disk and populate form fields.
        """

        self.main_window.log("Loading configuration.")

        config = load_config()
        if not config:
            self.main_window.log("No configuration found.")
            return

        try:
            self.timeout_entry.set_text(str(config.get("timeout_minutes", "")))
            self.email_entry.set_text(", ".join(config["email"].get("to", [])))
            self.subject_entry.set_text(config.get("subject", ""))
            self.message_buffer.set_text(config.get("message", ""))
            self.smtp_host_entry.set_text(config["email"].get("smtp_server", ""))
            self.smtp_port_entry.set_text(str(config["email"].get("smtp_port", "")))
            self.smtp_user_entry.set_text(config["email"].get("smtp_user", ""))
            self.smtp_pass_entry.set_text(config["email"].get("smtp_pass", ""))

            self.main_window.log("Configuration loaded successfully.")

        except Exception as e:
            self.main_window.log("Error loading configuration.", e)

    def on_save_clicked(self, button):
        """
        Validate and save the current form values to the configuration file.
        """
        try:
            timeout = self.timeout_entry.get_text().strip()
            recipients = self.email_entry.get_text().strip()
            subject = self.subject_entry.get_text().strip()
            smtp_host = self.smtp_host_entry.get_text().strip()
            smtp_port = self.smtp_port_entry.get_text().strip()
            smtp_user = self.smtp_user_entry.get_text().strip()
            smtp_pass = self.smtp_pass_entry.get_text().strip()

            # Get message from text buffer
            start_iter = self.message_buffer.get_start_iter()
            end_iter = self.message_buffer.get_end_iter()
            message = self.message_buffer.get_text(start_iter, end_iter, True).strip()

            # Validate required fields
            if not all(
                [
                    timeout,
                    recipients,
                    subject,
                    smtp_host,
                    smtp_port,
                    smtp_user,
                    smtp_pass,
                    message,
                ]
            ):
                self.main_window.log(
                    "All fields are required. Please fill in all fields."
                )
                return

            # Validate types
            try:
                timeout_minutes = int(timeout)
            except ValueError:
                self.main_window.log("Inactivity timeout must be a number.")
                return

            try:
                smtp_port_int = int(smtp_port)
            except ValueError:
                self.main_window.log("SMTP port must be a number.")
                return

            # Validate email addresses
            try:
                valid_emails = validate_recipient_list(recipients)
            except EmailNotValidError as e:
                self.main_window.log(f"Invalid recipient email: {e}")
                return

            try:
                validate_email_address(smtp_user)
            except EmailNotValidError as e:
                self.main_window.log(f"Invalid SMTP username: {e}")
                return

            # Assemble config dictionary
            config = {
                "timeout_minutes": timeout_minutes,
                "email": {
                    "to": valid_emails,
                    "smtp_server": smtp_host,
                    "smtp_port": smtp_port_int,
                    "smtp_user": smtp_user,
                    "smtp_pass": smtp_pass,
                },
                "subject": subject,
                "message": message,
            }

            validate_config(config)
            save_config(config)
            self.main_window.log("Configuration saved successfully.")

        except Exception as e:
            self.main_window.log("Error saving configuration.", e)

    def display_threshold_info(self, widget):
        """
        Display a human-readable string representing the inactivity duration.
        """
        try:
            minutes = int(self.timeout_entry.get_text().strip())
            to_display = get_threshold_info(minutes)
            self.timeout_info_label.set_text(to_display)
        except ValueError:
            self.timeout_info_label.set_text("")

    def on_test_smtp_clicked(self, button):
        """
        Attempt to send a test email using the current SMTP configuration.
        """
        self.test_smtp_button.set_sensitive(False)
        config = load_config()
        self.main_window.log(
            "An email will be sent to the SMTP address, or the address defined for monitoring."
        )
        result = send_test_email(config)
        self.main_window.log(result)
        self.test_smtp_button.set_sensitive(True)
