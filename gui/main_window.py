# --------------------------------------------------------------------
# 🪟 MAIN WINDOW: Initializes the GTK interface with notebook tabs
# --------------------------------------------------------------------
# This module defines the main application window, including:
# - A GTK notebook with two tabs: Service and Configuration.
# - A persistent logging area at the bottom of the window.
# - A method to log messages from anywhere in the GUI.
# --------------------------------------------------------------------

import gi

gi.require_version("Gtk", "3.0")
import os
import logging
from core.paths import GUI_LOG_PATH

# Setup GUI logger
os.makedirs(os.path.dirname(GUI_LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=GUI_LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from gi.repository import Gtk
import traceback
from datetime import datetime
from gui.service_tab import ServiceTab
from gui.configuration_tab import ConfigurationTab
from core.utils import build_log_entry


from core.version import __version__


class MainWindow(Gtk.Window):
    """
    The main window of the application that holds the notebook tabs
    and a shared logging area at the bottom of the UI.
    """

    def __init__(self):
        """
        Initialize the main window and build the full interface.
        """
        super().__init__(title="Inactivity Monitor")

        self.build_ui()

    def build_ui(self):
        """
        Build the full interface: notebook with tabs and logging panel.
        """
        self.set_border_width(20)
        self.set_default_size(600, 500)

        # === Log view must be created early so tabs can use it ===
        self.log_buffer = Gtk.TextBuffer()

        self.log(f"📝 Start Inactivity Monitor GUI [ version: { __version__ } ]")

        # === Main vertical layout ===
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        # === Notebook for tabs ===
        notebook = Gtk.Notebook()
        main_box.pack_start(notebook, True, True, 0)

        # === Tab 1: Service ===
        self.service_tab = ServiceTab(self)
        notebook.append_page(self.service_tab, Gtk.Label(label="Service"))

        # === Tab 2: Configuration ===
        self.configuration_tab = ConfigurationTab(self)
        notebook.append_page(self.configuration_tab, Gtk.Label(label="Configuration"))

        # === Log viewer (bottom panel) ===
        log_view = Gtk.TextView(buffer=self.log_buffer)
        log_view.set_editable(False)
        log_view.set_cursor_visible(False)
        log_view.set_wrap_mode(Gtk.WrapMode.WORD)

        log_scrolled = Gtk.ScrolledWindow()
        log_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        log_scrolled.set_min_content_height(100)
        log_scrolled.set_min_content_width(300)
        log_scrolled.add(log_view)

        log_frame = Gtk.Frame(label="Gui log:")
        log_frame.set_shadow_type(Gtk.ShadowType.IN)
        log_frame.add(log_scrolled)

        main_box.pack_start(log_frame, False, False, 0)

    def log(self, message, exception=None):
        """
        Append a message to the GUI log view and system log.

        Args:
            message (str): The message to log.
            exception (Exception, optional): An exception to include.
        """
        full_text = build_log_entry(message, exception)
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, full_text)


def launch_gui():
    """
    Launch the GTK application and start the event loop.
    """
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
