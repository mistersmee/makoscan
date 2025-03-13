import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

# Import UI pages
from ui.pages.start_page import StartPage
from ui.pages.packet_capture_page import PacketCapturePage
from ui.pages.pcap_to_plaintext_page import PcapToPlaintextPage
from ui.pages.llm_analysis_page import LLMAnalysisPage

class MAKKOscan(Gtk.Window):
    def __init__(self):
        super().__init__(title="MAKKOscan")
        self.set_border_width(10)
        self.set_default_size(500, 300)

        self.current_page = 0
        self.pages = [
            StartPage(),
            PacketCapturePage(),
            PcapToPlaintextPage(),
            LLMAnalysisPage()
        ]

        self.stack = Gtk.Stack()
        for page in self.pages:
            self.stack.add_named(page, page.get_name())

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.pack_start(self.stack, True, True, 0)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.next_page)
        GLib.idle_add(self.next_button.set_sensitive, False)  # Initially disabled on the first page
        self.quit_button = Gtk.Button(label="Quit")
        self.quit_button.connect("clicked", self.quit_app)

        self.back_button = Gtk.Button(label="Back")
        self.back_button.connect("clicked", self.prev_page)
        GLib.idle_add(self.back_button.set_sensitive, False)  # Initially disabled on the first page

        self.button_box.pack_start(self.back_button, False, False, 0)
        self.button_box.pack_end(self.quit_button, False, False, 0)
        self.button_box.pack_end(self.next_button, False, False, 0)

        self.main_box.pack_end(self.button_box, False, False, 0)
        self.add(self.main_box)

    def next_page(self, widget):
        """Navigate to the next page."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.stack.set_visible_child_name(self.pages[self.current_page].get_name())
            self.update_navigation_buttons()

    def prev_page(self, widget):
        """Navigate to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.set_visible_child_name(self.pages[self.current_page].get_name())
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Update the state of navigation buttons."""
        self.back_button.set_sensitive(self.current_page > 0)
        self.next_button.set_sensitive(self.current_page < len(self.pages) - 1)

    def quit_app(self, widget):
        Gtk.main_quit()
