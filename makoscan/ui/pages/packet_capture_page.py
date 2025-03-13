import gi
import os
from threading import Thread, Event
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from core.capture import capture_packets

class PacketCapturePage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_name("packet_capture")
        self.stop_event = Event()
        self.is_capturing = False

        title = Gtk.Label(label="Packet Capture")
        title.set_markup("<b>Packet Capture</b>")

        self.interface_combo = Gtk.ComboBoxText()
        self._populate_interfaces()

        self.filter_combo = Gtk.ComboBoxText()
        self.filter_combo.append_text("None")
        self.filter_combo.append_text("TCP")
        self.filter_combo.append_text("HTTP")
        self.filter_combo.append_text("port 80")
        self.filter_combo.set_active(0)

        self.limit_entry = Gtk.Entry()
        self.limit_entry.set_placeholder_text("Enter max packets")

        self.time_entry = Gtk.Entry()
        self.time_entry.set_placeholder_text("Enter time in seconds")

        self.start_button = Gtk.Button(label="Start Scanning")
        self.start_button.connect("clicked", self.start_scanning)

        self.stop_button = Gtk.Button(label="Stop Scanning")
        self.stop_button.connect("clicked", self.stop_scanning)
        GLib.idle_add(self.stop_button.set_visible, False)

        self.packet_counter = Gtk.Label(label="Packets Captured: 0")

        self.pack_start(title, False, False, 0)
        self.pack_start(self.interface_combo, False, False, 0)
        self.pack_start(self.filter_combo, False, False, 0)
        self.pack_start(self.limit_entry, False, False, 0)
        self.pack_start(self.time_entry, False, False, 0)
        self.pack_start(self.start_button, False, False, 0)
        self.pack_start(self.stop_button, False, False, 0)
        self.pack_start(self.packet_counter, False, False, 0)

    def _populate_interfaces(self):
        try:
            interfaces = os.listdir('/sys/class/net')
            for iface in interfaces:
                self.interface_combo.append_text(iface)
            self.interface_combo.set_active(0)
        except Exception as e:
            print(f"Error fetching interfaces: {e}")

    def start_scanning(self, button):
        """Start packet capture."""
        interface = self.interface_combo.get_active_text()
        filter_text = self.filter_combo.get_active_text()
        packet_limit = self.limit_entry.get_text()
        time_limit = self.time_entry.get_text()

        if not interface:
            print("Invalid input. Select an interface.")
            return

        if packet_limit.isdigit():
            packet_limit = int(packet_limit)
        else:
            packet_limit = None  # No limit if not provided

        if time_limit.isdigit():
            time_limit = int(time_limit)
        else:
            time_limit = None  # No limit if not provided

        self.is_capturing = True
        self.stop_event.clear()
        self.start_button.set_sensitive(False)

        GLib.idle_add(self.start_button.set_visible, False)
        GLib.idle_add(self.stop_button.set_visible, True)

        self.capture_thread = Thread(
            target=capture_packets,
            args=(
                interface,
                filter_text,
                packet_limit,
                time_limit,
                self.stop_event,
                self.update_packet_counter,
                self.on_capture_complete
            )
        )
        self.capture_thread.start()

    def stop_scanning(self, button):
        """Stop the packet capture process."""
        self.stop_event.set()

    def update_packet_counter(self, count):
        """Update the packet counter label."""
        GLib.idle_add(self.packet_counter.set_text, f"Packets Captured: {count}")

    def on_capture_complete(self):
        """Callback for when capture is complete."""
        GLib.idle_add(self.start_button.set_visible, True)
        GLib.idle_add(self.stop_button.set_visible, False)
        GLib.idle_add(self.start_button.set_sensitive, True)
        self.is_capturing = False
