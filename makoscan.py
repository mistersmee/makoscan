import gi
import pyshark
import os
from threading import Thread, Event

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import time
import google.generativeai as genai


class PacketCaptureApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="MAKKOscan")
        self.set_border_width(10)
        self.set_default_size(400, 400)

        # Create a Stack and StackSwitcher
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)

        # Main layout with StackSwitcher and Stack
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(self.stack_switcher, False, False, 0)
        vbox.pack_start(self.stack, True, True, 0)
        self.add(vbox)

        # Add the first page (Packet Capture)
        self.page1 = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.stack.add_titled(self.page1, "page1", "Packet Capture")

        # Add the second page (PCAP Translation)
        self.page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.stack.add_titled(self.page2, "page2", "PCAP <-> Plaintext")

        # Add the third page (LLM Analysis)
        self.page3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.stack.add_titled(self.page3, "page3", "LLM Analysis")

        self._setup_page1()
        self._setup_page2()
        self._setup_page3()

    def _setup_page1(self):
        """Set up the first page for packet capture."""
        # Interface Selection
        self.interface_label = Gtk.Label(label="Select Interface:")
        self.page1.attach(self.interface_label, 0, 0, 1, 1)

        self.interface_combo = Gtk.ComboBoxText()
        self._populate_interfaces()
        self.page1.attach(self.interface_combo, 1, 0, 1, 1)

        # Filter Selection
        self.filter_label = Gtk.Label(label="Select Filter:")
        self.page1.attach(self.filter_label, 0, 1, 1, 1)

        self.filter_combo = Gtk.ComboBoxText()
        self.filter_combo.append_text("None")
        self.filter_combo.append_text("TCP")
        self.filter_combo.append_text("HTTP")
        self.filter_combo.append_text("port 80")
        self.filter_combo.set_active(0)  # Default to 'None'
        self.page1.attach(self.filter_combo, 1, 1, 1, 1)

        # Packet Limit
        self.limit_label = Gtk.Label(label="Packet Limit:")
        self.page1.attach(self.limit_label, 0, 2, 1, 1)

        self.limit_entry = Gtk.Entry()
        self.limit_entry.set_placeholder_text("Enter max packets")
        self.page1.attach(self.limit_entry, 1, 2, 1, 1)

        # Time Limit
        self.time_label = Gtk.Label(label="Time Limit (seconds):")
        self.page1.attach(self.time_label, 0, 3, 1, 1)

        self.time_entry = Gtk.Entry()
        self.time_entry.set_placeholder_text("Enter time in seconds")
        self.page1.attach(self.time_entry, 1, 3, 1, 1)

        # Start Scan Button
        self.start_button = Gtk.Button(label="Start Scanning")
        self.start_button.connect("clicked", self.start_scanning)
        self.page1.attach(self.start_button, 0, 4, 2, 1)

        # Packet Counter
        self.packet_counter = Gtk.Label(label="Packets Captured: 0")
        self.page1.attach(self.packet_counter, 0, 5, 2, 1)

        # Internal State
        self.capture_thread = None
        self.is_capturing = False
        self.stop_event = Event()

    def _setup_page2(self):
        """Set up the second page for PCAP translation."""
        # Instructions
        instructions = Gtk.Label(label="Translate the captured PCAP file to plaintext.")
        self.page2.pack_start(instructions, False, False, 0)

        # Translate Button
        translate_button = Gtk.Button(label="Translate PCAP")
        translate_button.connect("clicked", self.translate_pcap)
        self.page2.pack_start(translate_button, False, False, 0)

        # Output Label
        self.translation_status = Gtk.Label(label="No translation performed yet.")
        self.page2.pack_start(self.translation_status, False, False, 0)

    def _setup_page3(self):
        """Set up the third page for LLM Analysis."""
        # Instructions
        instructions = Gtk.Label(label="Send plaintext of packet capture file to LLM for analysis.")
        self.page3.pack_start(instructions, False, False, 0)

        # Send button
        send_button = Gtk.Button(label="Analyse with LLM")
        send_button.connect("clicked", self.analyse_llm)
        self.page3.pack_start(send_button, False, False, 0)

        # Output Label


    def _populate_interfaces(self):
        """Populate available network interfaces."""
        try:
            interfaces = os.listdir('/sys/class/net')
            for iface in interfaces:
                self.interface_combo.append_text(iface)
            self.interface_combo.set_active(0)  # Default to the first interface
        except Exception as e:
            print(f"Error fetching interfaces: {e}")

    def translate_pcap(self, button):
       """Translate the PCAP file to plaintext without JSON parsing."""
       pcap_file = "capture.pcap"
       txt_file = "capture.txt"

       try:
           if not os.path.exists(pcap_file):
               self.translation_status.set_text("PCAP file not found.")
               return

           capture = pyshark.FileCapture(pcap_file)

           with open(txt_file, "w") as f:
               for packet in capture:
                   f.write("Packet:\n")
                   # Iterate through layers in each packet
                   for layer in packet:
                       f.write(f"Layer {layer.layer_name}:\n")
                       # Write fields for each layer
                       for field in layer.field_names:
                           try:
                               value = getattr(layer, field, None)
                               if value:
                                   f.write(f"  {field}: {value}\n")
                           except AttributeError:
                               f.write(f"  {field}: (No value available)\n")
                   f.write("\n")  # Add a blank line after each packet

           self.translation_status.set_text(f"Translation complete. Saved as {txt_file}.")
       except Exception as e:
           self.translation_status.set_text(f"Error: {e}")

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

    def analyse_llm(self, button):
        pass

if __name__ == "__main__":
    app = PacketCaptureApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
