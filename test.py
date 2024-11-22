import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import google.generativeai as genai
import os

file = open('apikey.txt', 'r')

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK Application")

        # Create a vertical box layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Create a button
        self.button = Gtk.Button(label="Click Me")
        vbox.pack_start(self.button, True, True, 0)

        # Create a text view for output
        self.text_view = Gtk.TextView()
        vbox.pack_start(self.text_view, True, True, 0)

        # Connect the button's clicked signal to a handler
        self.button.connect("clicked", self.on_button_clicked)

    def on_button_clicked(self, button):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("The opposite of hot is")

        # Update the text view
        buffer = self.text_view.get_buffer()
        buffer.set_text(response.text)

def main():
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
