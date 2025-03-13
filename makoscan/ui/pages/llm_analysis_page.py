import gi
import os
import webbrowser
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from core.analysis import analyze_with_llm
from utils.export import export_to_pdf_file

class LLMAnalysisPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_name("llm_analysis")

        title = Gtk.Label(label="LLM Analysis")
        title.set_markup("<b>LLM Analysis</b>")

        self.analyze_button = Gtk.Button(label="Analyze with LLM")
        self.analyze_button.connect("clicked", self.analyze_llm)

        self.export_button = Gtk.Button(label="Export to PDF")
        self.export_button.connect("clicked", self.export_to_pdf)
        GLib.idle_add(self.export_button.set_visible, False)

        self.open_pdf_button = Gtk.Button(label="Open PDF")
        self.open_pdf_button.connect("clicked", self.open_pdf)
        GLib.idle_add(self.open_pdf_button.set_visible, False)

        self.status_label = Gtk.Label(label="")

        self.analysis_output_buffer = Gtk.TextBuffer()
        self.analysis_output_view = Gtk.TextView(buffer=self.analysis_output_buffer)
        self.analysis_output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.analysis_output_view.set_editable(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.analysis_output_view)

        self.pack_start(title, False, False, 0)
        self.pack_start(self.analyze_button, False, False, 0)
        self.pack_start(scrolled_window, True, True, 0)
        self.pack_start(self.export_button, False, False, 0)
        self.pack_start(self.open_pdf_button, False, False, 0)
        self.pack_start(self.status_label, False, False, 0)

    def analyze_llm(self, button):
        """Analyze the translated text using LLM."""
        try:
            result_text = analyze_with_llm("capture.txt")
            if result_text:
                self.analysis_output_buffer.set_text(result_text)
                # Show export button after analysis is done
                GLib.idle_add(self.export_button.set_visible, True)
            else:
                self.analysis_output_buffer.set_text("No analysis result returned.")
        except Exception as e:
            self.analysis_output_buffer.set_text(f"Error during analysis: {e}")

    def export_to_pdf(self, button):
        """Export analysis results to PDF."""
        start, end = self.analysis_output_buffer.get_bounds()
        result_text = self.analysis_output_buffer.get_text(start, end, True)

        if not result_text.strip():
            GLib.idle_add(self.status_label.set_text, "No analysis result to export.")
            return

        try:
            success = export_to_pdf_file(result_text)
            if success:
                GLib.idle_add(self.status_label.set_text, "Exported to analysis.pdf")
                GLib.idle_add(self.open_pdf_button.set_visible, True)
            else:
                GLib.idle_add(self.status_label.set_text, "Failed to export to PDF")
        except Exception as e:
            GLib.idle_add(self.status_label.set_text, f"Error exporting to PDF: {e}")

    def open_pdf(self, button):
        """Open the exported PDF using the default system viewer."""
        pdf_file = "analysis.pdf"
        if os.path.exists(pdf_file):
            webbrowser.open(pdf_file)  # Open the PDF
        else:
            GLib.idle_add(self.status_label.set_text, "PDF file not found.")
