import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.window import MAKKOscan

if __name__ == "__main__":
    app = MAKKOscan()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
