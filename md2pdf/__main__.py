"""
Copyright (c) 2024 Travis L. Seymour, PhD

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import typer
import markdown
import pdfkit
from pygments.formatters import HtmlFormatter
from pathlib import Path

app = typer.Typer(help="Markdown to PDF Converter")


@app.command()
def convert(
    input_file: Path = typer.Argument(..., exists=True, help="Path to the Markdown file"),
    output_pdf: Path = typer.Argument("output.pdf", help="Path to the output PDF file"),
    save_html: bool = typer.Option(False, "--save-html", help="Save intermediate HTML file"),
    theme: str = typer.Option(
        "monokai",
        help="Pygments theme for syntax highlighting. Options are "
             "['default', 'monokai', 'manni', 'vim', 'friendly', 'native', 'github']",
    ),
):
    """
    Convert a Markdown file to a PDF with syntax-highlighted code blocks.
    """
    # Read the Markdown file
    with open(input_file, "r") as md_file:
        md_content = md_file.read()

    # Convert Markdown to HTML with syntax highlighting
    html_content = markdown.markdown(md_content, extensions=["fenced_code", "codehilite"])

    # Add a CSS style for syntax highlighting using the chosen theme
    css_style = HtmlFormatter(style=theme).get_style_defs(".codehilite")
    html_with_css = f"<style>{css_style}</style>\n{html_content}"

    # Save HTML to a file if requested
    if save_html:
        html_file = input_file.with_suffix(".html")
        with open(html_file, "w") as html_out:
            html_out.write(html_with_css)
        typer.echo(f"Intermediate HTML saved to: {html_file}")

    # Convert HTML to PDF
    pdfkit.from_string(html_with_css, str(output_pdf))
    typer.echo(f"PDF generated: {output_pdf}")


if __name__ == "__main__":
    app()
