# --------------------------------------------------------------------
# 🛠️ SERVICE TAB: Displays and manages systemd service + log viewer
# --------------------------------------------------------------------
# This tab includes:
# - Real-time status of the background service
# - Last login and user activity times
# - A panel for live log display (tail -like)
# - Controls to start/stop/restart the systemd service
# --------------------------------------------------------------------

from gi.repository import Gtk, GLib
from core.paths import LOG_PATH
import os
import subprocess
from core.state import load_state
from core.config_manager import load_config
from core.utils import format_timestamp, get_threshold_info
from core.service_utils import run_service_command


class ServiceTab(Gtk.Grid):
    """
    Represents the 'Service' tab in the GTK UI.
    Provides user information, service controls, and service log display.
    """

    def __init__(self, main_window):
        """
        Initialize the tab and schedule automatic updates every 3 seconds.
        """
        super().__init__(column_spacing=10, row_spacing=10, margin=10)
        self.main_window = main_window
        self.service_info_labels = {}
        self.build_ui()
        GLib.timeout_add(3000, self.check_and_display_service_info)
        self.load_service_log()

    def build_ui(self):
        """
        Create and lay out all UI components in the service tab.
        """
        row = 0

        # === Informational rows (service info + timestamps) ===
        self.info_listbox = Gtk.ListBox()
        self.info_listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        def add_info_row(key, label_text, value_text="Checking…"):
            """
            Add a key-value info line to the listbox.
            """
            list_row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=label_text, xalign=0)
            value_label = Gtk.Label(label=value_text, xalign=1)
            value_label.set_selectable(True)

            hbox.pack_start(label, True, True, 0)
            hbox.pack_end(value_label, False, False, 0)
            list_row.add(hbox)

            self.info_listbox.add(list_row)
            self.service_info_labels[key] = value_label

        for key, text in [
            ("status", "Service status:"),
            ("last_login", "Last login:"),
            ("last_input", "Last activity:"),
            ("threshold_reached", "Threshold reached?"),
            ("threshold", "Threshold:"),
            ("30_percent_monitoring", "30% mail sent?"),
            ("60_percent_monitoring", "60% mail sent?"),
            ("90_percent_monitoring", "90% mail sent?"),
        ]:
            add_info_row(key, text)

        self.attach(self.info_listbox, 0, row, 3, 1)
        self.info_listbox.show_all()
        row += 1

        # === First separator ===
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(5)
        separator.set_margin_bottom(5)
        separator.set_hexpand(True)
        separator.set_halign(Gtk.Align.FILL)
        self.attach(separator, 0, row, 3, 1)
        row += 1

        # === Service control buttons ===
        self.restart_button = Gtk.Button(label="Restart Service")
        self.start_button = Gtk.Button(label="Start Service")
        self.stop_button = Gtk.Button(label="Stop Service")

        self.restart_button.connect(
            "clicked", lambda b: self.on_restart_button_clicked("restart")
        )
        self.start_button.connect(
            "clicked", lambda b: self.on_start_button_clicked("start")
        )
        self.stop_button.connect(
            "clicked", lambda b: self.on_stop_button_clicked("stop")
        )

        self.attach(self.start_button, 0, row, 1, 1)
        self.attach(self.stop_button, 1, row, 1, 1)
        self.attach(self.restart_button, 2, row, 1, 1)
        row += 1

        # === Second separator before log section ===
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator2.set_margin_top(5)
        separator2.set_margin_bottom(5)
        separator2.set_hexpand(True)
        separator2.set_halign(Gtk.Align.FILL)
        self.attach(separator2, 0, row, 3, 1)
        row += 1

        # === Refresh button for service logs ===
        self.refresh_button = Gtk.Button(label="Refresh service log")
        self.refresh_button.connect("clicked", lambda b: self.load_service_log())
        self.attach(self.refresh_button, 0, row, 1, 1)
        row += 1

        # === Service log display ===
        self.service_log_buffer = Gtk.TextBuffer()
        self.service_log_view = Gtk.TextView(buffer=self.service_log_buffer)
        self.service_log_view.set_editable(False)
        self.service_log_view.set_cursor_visible(False)
        self.service_log_view.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.set_min_content_width(300)
        scrolled.add(self.service_log_view)

        frame = Gtk.Frame(label="Service log:")
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.add(scrolled)

        self.attach(frame, 0, row, 3, 1)

    def check_and_display_service_info(self):
        """
        Refresh service information and update UI values.
        """
        state = load_state()
        config = load_config()
        self.check_and_display_service_status()
        self.check_and_display_activity_time(state)

        if not config:
            for key in [
                "threshold",
                "30_percent_monitoring",
                "60_percent_monitoring",
                "90_percent_monitoring",
            ]:
                self.service_info_labels[key].set_text("⚠️ No configuration found.")
        else:
            minutes = int(str(config.get("timeout_minutes", "0")).strip())
            threshold_to_display = get_threshold_info(minutes)
            self.service_info_labels["threshold"].set_text(threshold_to_display)

        return True  # Ensure timeout continues

    def check_and_display_activity_time(self, state):
        """
        Display last login and last activity from the saved state.
        """
        last_login_timestamp = state["last_login_timestamp"]
        last_input_timestamp = state["last_input_timestamp"]

        self.service_info_labels["last_login"].set_text(
            format_timestamp(last_login_timestamp)
            if last_login_timestamp > 0
            else "⚠️ unknown"
        )
        self.service_info_labels["last_input"].set_text(
            format_timestamp(last_input_timestamp)
            if last_input_timestamp > 0
            else "⚠️ unknown"
        )

    def check_and_display_service_status(self):
        """
        Call systemctl to detect service status and update UI + button states.
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "inactivity-monitor"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            status = result.stdout.strip()

            if status == "active":
                self.service_info_labels["status"].set_text("🟢 Service is running")
                self.start_button.set_sensitive(False)
                self.stop_button.set_sensitive(True)
                self.restart_button.set_sensitive(True)
            elif status == "inactive":
                self.service_info_labels["status"].set_text("🔴 Service is inactive")
                self.start_button.set_sensitive(True)
                self.stop_button.set_sensitive(False)
                self.restart_button.set_sensitive(True)
            else:
                self.service_info_labels["status"].set_text(
                    f"⚠️ Service status: {status}"
                )
                self.start_button.set_sensitive(True)
                self.stop_button.set_sensitive(False)
                self.restart_button.set_sensitive(False)

        except Exception:
            self.service_info_labels["status"].set_text(
                "❌ Unable to check service status"
            )
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)
            self.restart_button.set_sensitive(False)

    def on_restart_button_clicked(self, widget):
        """Callback for restarting the service."""
        self.main_window.log("👤 You asked to restart the service.")
        try:
            output = run_service_command("restart")
            self.main_window.log(output or "✅ Service restarted.")
        except Exception as e:
            self.main_window.log("❌ Failed to restart the service.", e)

        self.check_and_display_service_info()

    def on_start_button_clicked(self, widget):
        """Callback for starting the service."""
        self.main_window.log("👤 You asked to start the service.")
        try:
            output = run_service_command("start")
            self.main_window.log(output or "✅ Service started.")
        except Exception as e:
            self.main_window.log("❌ Failed to start the service.", e)

        self.check_and_display_service_info()

    def on_stop_button_clicked(self, widget):
        """You asked to stop the service."""
        self.main_window.log("👤 You asked to stop the service.")
        try:
            output = run_service_command("stop")
            self.main_window.log(output or "✅ Service stopped.")
        except Exception as e:
            self.main_window.log("❌ Failed to stop the service.", e)

        self.check_and_display_service_info()

    def load_service_log(self, lines=100):
        """
        Load the last N lines of the service log file into the log viewer.
        """

        self.main_window.log("⏳ Loading service logs.")

        try:
            if not os.path.exists(LOG_PATH):
                self.service_log_buffer.set_text("service.log not found.")
                return True

            with open(LOG_PATH, "r") as f:
                content = f.readlines()[-lines:]

            self.service_log_buffer.set_text("".join(content))
            GLib.idle_add(self.scroll_service_log_to_bottom)
            self.main_window.log("✅ Service log loading complete.")

        except Exception as e:
            self.service_log_buffer.set_text(f"Error reading service.log:\n{str(e)}")
            self.main_window.log("⚠️ Service log loading complete whith error:", e)

        return True

    def scroll_service_log_to_bottom(self):
        """
        Scrolls the service log viewer to the bottom.
        """
        end_iter = self.service_log_buffer.get_end_iter()
        self.service_log_view.scroll_to_iter(end_iter, 0.0, True, 0.0, 1.0)
