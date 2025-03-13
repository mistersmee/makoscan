import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class StartPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_name("start")

        title = Gtk.Label(label="MAKKOscan")
        title.set_markup("<b><big>MAKKOscan</big></b>")
        desc = Gtk.Label(label="A network packet capture and analysis tool.")
        start_button = Gtk.Button(label="Start")
        start_button.connect("clicked", self.on_start_clicked)

        self.pack_start(title, False, False, 0)
        self.pack_start(desc, False, False, 0)
        self.pack_start(start_button, False, False, 0)

    def on_start_clicked(self, button):
        # Connect to the parent window's next_page method
        parent = self.get_parent()
        while parent and not isinstance(parent, Gtk.Window):
            parent = parent.get_parent()

        if parent:
            parent.next_page(button)
