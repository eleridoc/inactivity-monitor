# --------------------------------------------------------------------
# ⚙️ SETTINGS TAB: UI for user-defined options (logging, monitoring)
# --------------------------------------------------------------------
# This module defines the GTK tab for configuring optional features
# like logging, monitoring thresholds, and sender override.
# It handles loading, validating, and saving settings securely.
# --------------------------------------------------------------------

from gi.repository import Gtk, GLib
import threading
from core.settings_manager import (
    load_settings,
    save_settings_with_privileges,
    validate_settings,
)
from core.email_utils import validate_email_address
from email_validator import EmailNotValidError
import calendar


class SettingsTab(Gtk.Grid):
    """
    Represents the 'Settings' tab for optional behaviors and preferences.

    Includes toggles for logging, monitoring thresholds, and a custom sender address.
    """

    def __init__(self, main_window):
        """
        Initialize the tab and load stored settings.

        Args:
            main_window (Gtk.Window): Reference to the main window for logging.
        """
        super().__init__(column_spacing=10, row_spacing=10, margin=10)
        self.main_window = main_window
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        """Build and layout all widgets on the settings tab."""
        row = 0

        # === Enable logs checkbox ===
        self.logs_checkbox = Gtk.CheckButton(label="Enable logs")
        self.attach(self.logs_checkbox, 0, row, 2, 1)
        row += 1

        # === Separator: logs -> sender override ===
        separator_01 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator_01.set_margin_top(5)
        separator_01.set_margin_bottom(5)
        separator_01.set_hexpand(True)
        separator_01.set_halign(Gtk.Align.FILL)
        self.attach(separator_01, 0, row, 2, 1)
        row += 1

        # === Sender override input field ===
        self.monitoring_sender_entry = Gtk.Entry()
        self.attach(
            Gtk.Label(label="Monitoring sender override (optional):"), 0, row, 1, 1
        )
        self.attach(self.monitoring_sender_entry, 1, row, 1, 1)
        row += 1

        # === Separator: sender -> monitoring logic ===
        separator_02 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator_02.set_margin_top(5)
        separator_02.set_margin_bottom(5)
        separator_02.set_hexpand(True)
        separator_02.set_halign(Gtk.Align.FILL)
        self.attach(separator_02, 0, row, 2, 1)
        row += 1

        # === Send monitoring email on service start ===
        self.start_monitoring_checkbox = Gtk.CheckButton(
            label="Send monitoring email on service start"
        )
        self.attach(self.start_monitoring_checkbox, 0, row, 2, 1)
        row += 1

        # === Threshold monitoring checkboxes ===
        self.at_30_checkbox = Gtk.CheckButton(
            label="Send monitoring email at 30% of timeout"
        )
        self.attach(self.at_30_checkbox, 0, row, 2, 1)
        row += 1

        self.at_60_checkbox = Gtk.CheckButton(
            label="Send monitoring email at 60% of timeout"
        )
        self.attach(self.at_60_checkbox, 0, row, 2, 1)
        row += 1

        self.at_90_checkbox = Gtk.CheckButton(
            label="Send monitoring email at 90% of timeout"
        )
        self.attach(self.at_90_checkbox, 0, row, 2, 1)
        row += 1

        # === Separator: sender -> monitoring logic ===
        separator_03 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator_03.set_margin_top(5)
        separator_03.set_margin_bottom(5)
        separator_03.set_hexpand(True)
        separator_03.set_halign(Gtk.Align.FILL)
        self.attach(separator_03, 0, row, 2, 1)
        row += 1

        # === Weekly monitoring ===
        self.weekly_checkbox = Gtk.CheckButton(label="Send monitoring email weekly")
        self.attach(self.weekly_checkbox, 0, row, 2, 1)
        row += 1

        # Day of week selector
        self.weekday_combo = Gtk.ComboBoxText()
        for i in range(7):
            self.weekday_combo.append_text(calendar.day_name[i])
        self.weekday_combo.set_active(0)
        self.attach(Gtk.Label(label="Day of the week:"), 0, row, 1, 1)
        self.attach(self.weekday_combo, 1, row, 1, 1)
        row += 1

        # Time selector
        self.hour_spin = Gtk.SpinButton()
        self.hour_spin.set_range(0, 23)
        self.hour_spin.set_increments(1, 1)
        self.hour_spin.set_numeric(True)

        self.attach(Gtk.Label(label="Hour of the day:"), 0, row, 1, 1)
        self.attach(self.hour_spin, 1, row, 1, 1)
        row += 1

        # === Separator: sender -> monitoring logic ===
        separator_04 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator_04.set_margin_top(5)
        separator_04.set_margin_bottom(5)
        separator_04.set_hexpand(True)
        separator_04.set_halign(Gtk.Align.FILL)
        self.attach(separator_04, 0, row, 2, 1)
        row += 1

        # === Save button ===
        save_button = Gtk.Button(label="Save options")
        save_button.connect("clicked", self.on_save_clicked)
        self.attach(save_button, 0, row, 2, 1)

    def load_settings(self):
        """
        Load settings from disk and apply values to the widgets.
        """
        settings = load_settings()

        self.logs_checkbox.set_active(settings.get("enable_logs", False))
        self.start_monitoring_checkbox.set_active(
            settings.get("send_monitoring_on_start", False)
        )
        self.monitoring_sender_entry.set_text(settings.get("monitoring_sender", ""))
        self.at_30_checkbox.set_active(settings.get("monitoring_at_30", False))
        self.at_60_checkbox.set_active(settings.get("monitoring_at_60", False))
        self.at_90_checkbox.set_active(settings.get("monitoring_at_90", False))

        self.weekly_checkbox.set_active(
            settings.get("monitoring_weekly_enabled", False)
        )
        self.weekday_combo.set_active(settings.get("monitoring_weekly_day", 0))
        self.hour_spin.set_value(settings.get("monitoring_weekly_hour", 12))

        self.main_window.log("⚙️ Settings loaded.")

    def on_save_clicked(self, button):
        """
        Save settings after validating input fields.
        Prevents privilege elevation if validation fails.
        """

        self.main_window.log("-------------------------------------------")
        self.main_window.log("👤 You have requested to save the settings.")

        try:
            settings = self.build_setting()  # May raise validation errors
        except Exception as e:
            self.main_window.log("❌ Invalid settings. Please fix errors.", e)
            return

        def worker():
            try:
                save_settings_with_privileges(settings, self.main_window)
                GLib.idle_add(self.main_window.log, "✅ Settings saved successfully.")
            except Exception as e:
                GLib.idle_add(self.main_window.log, "❌ Failed to save settings.", e)

        threading.Thread(target=worker, daemon=True).start()

    def build_setting(self):
        """
        Collect and validate settings from form widgets.

        Returns:
            dict: The complete settings object.

        Raises:
            ValueError: If validation fails (e.g. invalid sender email).
        """
        settings = {
            "enable_logs": self.logs_checkbox.get_active(),
            "send_monitoring_on_start": self.start_monitoring_checkbox.get_active(),
            "monitoring_sender": self.monitoring_sender_entry.get_text().strip(),
            "monitoring_at_30": self.at_30_checkbox.get_active(),
            "monitoring_at_60": self.at_60_checkbox.get_active(),
            "monitoring_at_90": self.at_90_checkbox.get_active(),
            "monitoring_weekly_enabled": self.weekly_checkbox.get_active(),
            "monitoring_weekly_day": self.weekday_combo.get_active(),
            "monitoring_weekly_hour": int(self.hour_spin.get_value()),
        }

        validate_settings(settings)

        return settings
