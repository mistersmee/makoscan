import gi
import os
import pyshark
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class PcapToPlaintextPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_name("pcap_plaintext")

        title = Gtk.Label(label="PCAP to Plaintext Converter")
        title.set_markup("<b>PCAP to Plaintext</b>")

        self.translate_button = Gtk.Button(label="Translate PCAP")
        self.translate_button.connect("clicked", self.translate_pcap)

        self.translation_status = Gtk.Label(label="No translation performed yet.")

        self.pack_start(title, False, False, 0)
        self.pack_start(self.translate_button, False, False, 0)
        self.pack_start(self.translation_status, False, False, 0)

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
