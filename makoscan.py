import gi
import pyshark
import os
from threading import Thread, Event
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import time


class PacketCaptureApp(Gtk.Window):
    def __init__(self):
       super().__init__(title="Packet Capture Tool")
       self.set_border_width(10)
       self.set_default_size(400, 400)

       # Main layout
       self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
       self.add(self.grid)

       # Interface Selection
       self.interface_label = Gtk.Label(label="Select Interface:")
       self.grid.attach(self.interface_label, 0, 0, 1, 1)

       self.interface_combo = Gtk.ComboBoxText()
       self._populate_interfaces()
       self.grid.attach(self.interface_combo, 1, 0, 1, 1)

       # Filter Selection
       self.filter_label = Gtk.Label(label="Select Filter:")
       self.grid.attach(self.filter_label, 0, 1, 1, 1)

       self.filter_combo = Gtk.ComboBoxText()
       self.filter_combo.append_text("None")
       self.filter_combo.append_text("TCP")
       self.filter_combo.append_text("HTTP")
       self.filter_combo.append_text("port 80")
       self.filter_combo.set_active(0)  # Default to 'None'
       self.grid.attach(self.filter_combo, 1, 1, 1, 1)

       # Packet Limit
       self.limit_label = Gtk.Label(label="Packet Limit:")
       self.grid.attach(self.limit_label, 0, 2, 1, 1)

       self.limit_entry = Gtk.Entry()
       self.limit_entry.set_placeholder_text("Enter max packets")
       self.grid.attach(self.limit_entry, 1, 2, 1, 1)

       # Time Limit
       self.time_label = Gtk.Label(label="Time Limit (seconds):")
       self.grid.attach(self.time_label, 0, 3, 1, 1)

       self.time_entry = Gtk.Entry()
       self.time_entry.set_placeholder_text("Enter time in seconds")
       self.grid.attach(self.time_entry, 1, 3, 1, 1)

       # Start Scan Button
       self.start_button = Gtk.Button(label="Start Scanning")
       self.start_button.connect("clicked", self.start_scanning)
       self.grid.attach(self.start_button, 0, 4, 2, 1)

       # Packet Counter
       self.packet_counter = Gtk.Label(label="Packets Captured: 0")
       self.grid.attach(self.packet_counter, 0, 5, 2, 1)

       # Internal State
       self.capture_thread = None
       self.is_capturing = False
       self.stop_event = Event()  # Used to stop the capture thread

    def _populate_interfaces(self):
        """Populate available network interfaces."""
        try:
            interfaces = os.listdir('/sys/class/net')
            for iface in interfaces:
                self.interface_combo.append_text(iface)
            self.interface_combo.set_active(0)  # Default to the first interface
        except Exception as e:
            print(f"Error fetching interfaces: {e}")

    def start_scanning(self, button):
       """Start packet capture."""
       interface = self.interface_combo.get_active_text()
       filter_text = self.filter_combo.get_active_text()
       packet_limit = self.limit_entry.get_text()
       time_limit = self.time_entry.get_text()

       if not interface:
           self._append_output("Invalid input. Select an interface.")
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

       self.capture_thread = Thread(target=self.capture_packets, args=(interface, filter_text, packet_limit, time_limit))
       self.capture_thread.start()

    def capture_packets(self, interface, filter_text, packet_limit, time_limit):
       """Perform packet capture using PyShark with capture filters and time limits."""
       pcap_file = "capture.pcap"
       try:
           self._append_output(f"Starting capture on {interface} with filter '{filter_text}'...")
           # Use a capture filter if specified
           capture_filter = None if filter_text == "None" else filter_text.lower()

           # Create a PyShark LiveCapture object
           capture = pyshark.LiveCapture(interface=interface, output_file=pcap_file, bpf_filter=capture_filter)

           packet_count = 0
           start_time = time.time()  # Record the start time

           for packet in capture.sniff_continuously():
               # Check time limit
               elapsed_time = time.time() - start_time
               if self.stop_event.is_set() or (time_limit and elapsed_time >= time_limit) or (packet_limit and packet_count >= packet_limit):
                   break

               packet_count += 1
               GLib.idle_add(self.packet_counter.set_text, f"Packets Captured: {packet_count}")

           capture.close()

           self._append_output(f"Capture complete. File saved as {pcap_file}.")

       except Exception as e:
           self._append_output(f"Error during capture: {e}")
       finally:
           self.is_capturing = False
           GLib.idle_add(self.start_button.set_sensitive, True)

    def _append_output(self, text):
        """Append text to the output field."""
        print(text)


if __name__ == "__main__":
    app = PacketCaptureApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
