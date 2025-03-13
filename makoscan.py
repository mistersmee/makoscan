import gi
import google.generativeai as genai
import os
import pyshark
import sys
import time
from threading import Thread, Event

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class MAKKOscan(Gtk.Window):
    def __init__(self):
        super().__init__(title="MAKKOscan")
        self.set_border_width(10)
        self.set_default_size(500, 300)

        self.stop_event = Event()
        self.current_page = 0
        self.pages = [
            self.build_start_page(),
            self.build_packet_capture_page(),
            self.build_pcap_to_plaintext_page(),
            self.build_llm_analysis_page()
        ]

        self.stack = Gtk.Stack()
        for page in self.pages:
            self.stack.add_named(page, page.get_name())

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.pack_start(self.stack, True, True, 0)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.next_page)
        self.next_button.set_sensitive(False)  # Initially disabled on the first page
        self.quit_button = Gtk.Button(label="Quit")
        self.quit_button.connect("clicked", self.quit_app)

        self.back_button = Gtk.Button(label="Back")
        self.back_button.connect("clicked", self.prev_page)
        self.back_button.set_sensitive(False)  # Initially disabled on the first page

        self.button_box.pack_start(self.back_button, False, False, 0)
        self.button_box.pack_end(self.quit_button, False, False, 0)
        self.button_box.pack_end(self.next_button, False, False, 0)

        self.main_box.pack_end(self.button_box, False, False, 0)
        self.add(self.main_box)
        self.show_all()

    def build_start_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_name("start")

        title = Gtk.Label(label="MAKKOscan")
        title.set_markup("<b><big>MAKKOscan</big></b>")
        desc = Gtk.Label(label="A network packet capture and analysis tool.")
        start_button = Gtk.Button(label="Start")
        start_button.connect("clicked", self.next_page)

        box.pack_start(title, False, False, 0)
        box.pack_start(desc, False, False, 0)
        box.pack_start(start_button, False, False, 0)

        return box

    def build_packet_capture_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_name("packet_capture")

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

        box.pack_start(title, False, False, 0)
        box.pack_start(self.interface_combo, False, False, 0)
        box.pack_start(self.filter_combo, False, False, 0)
        box.pack_start(self.limit_entry, False, False, 0)
        box.pack_start(self.time_entry, False, False, 0)
        box.pack_start(self.start_button, False, False, 0)
        box.pack_start(self.stop_button, False, False, 0)
        box.pack_start(self.packet_counter, False, False, 0)

        return box

    def build_pcap_to_plaintext_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_name("pcap_plaintext")

        title = Gtk.Label(label="PCAP to Plaintext Converter")
        title.set_markup("<b>PCAP to Plaintext</b>")
        self.translate_button = Gtk.Button(label="Translate PCAP")
        self.translate_button.connect("clicked", self.translate_pcap)
        self.translation_status = Gtk.Label(label="No translation performed yet.")

        box.pack_start(title, False, False, 0)
        box.pack_start(self.translate_button, False, False, 0)
        box.pack_start(self.translation_status, False, False, 0)

        return box

    def build_llm_analysis_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_name("llm_analysis")

        title = Gtk.Label(label="LLM Analysis")
        title.set_markup("<b>LLM Analysis</b>")
        self.analyze_button = Gtk.Button(label="Analyze with LLM")
        self.analyze_button.connect("clicked", self.analyse_llm)
        self.analysis_output_buffer = Gtk.TextBuffer()
        self.analysis_output_view = Gtk.TextView(buffer=self.analysis_output_buffer)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.analysis_output_view)

        box.pack_start(title, False, False, 0)
        box.pack_start(self.analyze_button, False, False, 0)
        box.pack_start(scrolled_window, True, True, 0)

        return box

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

    def _populate_interfaces(self):
        try:
            interfaces = os.listdir('/sys/class/net')
            for iface in interfaces:
                self.interface_combo.append_text(iface)
            self.interface_combo.set_active(0)
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

       GLib.idle_add(self.start_button.set_visible, False)
       GLib.idle_add(self.stop_button.set_visible, True)

       self.capture_thread = Thread(target=self.capture_packets, args=(interface, filter_text, packet_limit, time_limit))
       self.capture_thread.start()

    def stop_scanning(self, button):
        """Stop the packet capture process."""
        self.stop_event.set()
        # Show Start Button and Hide Stop Button
        self.start_button.set_visible(True)
        self.stop_button.set_visible(False)

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

           GLib.idle_add(self.start_button.set_visible, True)
           GLib.idle_add(self.stop_button.set_visible, False)

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
        """Send the translated text file to a local Hugging Face model."""
        txt_file = "capture.txt"


        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        if not os.path.exists(txt_file):
            self.analysis_output_buffer.set_text("No translated text file found.")
            return

        try:
            with open(txt_file, "r") as f:
                text_data = f.read()

            model = genai.GenerativeModel('gemini-2.0-flash')

            # Define a structured prompt
            custom_prompt = (
                "Analyze the following network traffic log and provide insights into potential threats, "
                "malicious patterns, or suspicious activity. Summarize key observations and include relevant "
                "protocol details. Provide a conclusion on whether the traffic seems benign or risky:\n\n"
                f"{text_data}"
            )

            response_text = model.generate_content(custom_prompt)

            # Display response in GUI
            self.analysis_output_buffer.set_text(response_text.text)
        except Exception as e:
            self.analysis_output_buffer.set_text(f"Error during analysis: {e}")


if __name__ == "__main__":
    app = MAKKOscan()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
