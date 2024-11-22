import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Multi-Screen GTK App")

        # Create a stack to hold multiple pages
        stack = Gtk.Stack()
        self.add(stack)

        # Create the first page
        self.page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button1 = Gtk.Button(label="Click Me 1")
        text_view1 = Gtk.TextView()
        self.page1.pack_start(button1, True, True, 0)
        self.page1.pack_start(text_view1, True, True, 0)
        button1.connect("clicked", self.on_button_clicked, text_view1)

        # Create the second page
        self.page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button2 = Gtk.Button(label="Click Me 2")
        text_view2 = Gtk.TextView()
        self.page2.pack_start(button2, True, True, 0)
        self.page2.pack_start(text_view2, True, True, 0)
        button2.connect("clicked", self.on_button_clicked, text_view2)

        # Add both pages to the stack
        stack.add_titled(self.page1, "page1", "Page 1")
        stack.add_titled(self.page2, "page2", "Page 2")

        # Add the "Next Page" button to the first page
        next_button1 = Gtk.Button(label="Next Page")
        next_button1.connect("clicked", self.on_next_button_clicked, stack)
        self.page1.pack_start(next_button1, True, True, 0)

    def on_button_clicked(self, button, text_view):
        buffer = text_view.get_buffer()
        buffer.set_text("Button clicked! This is the output.")

    def on_next_button_clicked(self, button, stack):
        stack.set_visible_child(self.page2)

if __name__ == "__main__":
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
