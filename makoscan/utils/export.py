import os
import subprocess

def export_to_pdf_file(result_text):
    """
    Export analysis results to a PDF file.

    Args:
        result_text (str): The text to export

    Returns:
        bool: True if export successful, False otherwise
    """
    markdown_file = "analysis.md"
    pdf_file = "analysis.pdf"

    try:
        with open(markdown_file, "w") as md_file:
            md_file.write("# LLM Analysis Result\n\n")
            md_file.write(result_text)

        # Convert Markdown to PDF using Pandoc
        subprocess.run(["pandoc", "-t", "html", "-o", pdf_file, markdown_file], check=True)
        return True
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        return False
