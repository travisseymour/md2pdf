"""
Copyright (c) 2024-2026 Travis L. Seymour, PhD

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

from pathlib import Path
from typing import Optional

import markdown
import pdfkit
import typer
from pygments.formatters import HtmlFormatter

app = typer.Typer(help="Markdown to PDF Converter")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""

TABLE_CSS = """
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ccc;
    padding: 8px 12px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #fafafa;
}
"""


@app.command()
def convert(
    input_file: Path = typer.Argument(..., exists=True, help="Path to the Markdown file"),
    output_pdf: Optional[Path] = typer.Argument(None, help="Path to the output PDF file (default: <input>.pdf)"),
    save_html: bool = typer.Option(False, "--save-html", help="Save intermediate HTML file"),
    theme: str = typer.Option(
        "monokai",
        help="Pygments theme for syntax highlighting. Options are "
        "['default', 'monokai', 'manni', 'vim', 'friendly', 'native', 'github']",
    ),
    margin: Optional[float] = typer.Option(None, "--margin", help="Page margins in inches (e.g. 0.75)"),
    font_scale: Optional[int] = typer.Option(None, "--font-scale", help="Font size as a percentage of the default (e.g. 120 for 20%% larger)"),
):
    """
    Convert a Markdown file to a PDF with syntax-highlighted code blocks.
    """
    if output_pdf is None:
        output_pdf = input_file.with_suffix(".pdf")

    # Read the Markdown file
    with open(input_file, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()

    # Convert Markdown to HTML with syntax highlighting and table support
    html_content = markdown.markdown(md_content, extensions=["fenced_code", "codehilite", "tables"])

    # Build CSS: syntax highlighting theme + table styling
    highlight_css = HtmlFormatter(style=theme).get_style_defs(".codehilite")
    font_css = f"body {{ font-size: {font_scale}%; }}\n" if font_scale is not None else ""
    css = f"{highlight_css}\n{TABLE_CSS}\n{font_css}"

    # Wrap in a proper HTML document with UTF-8 charset
    html_doc = HTML_TEMPLATE.format(css=css, body=html_content)

    # Save HTML to a file if requested
    if save_html:
        html_file = input_file.with_suffix(".html")
        with open(html_file, "w", encoding="utf-8") as html_out:
            html_out.write(html_doc)
        typer.echo(f"Intermediate HTML saved to: {html_file}")

    # Convert HTML to PDF
    options = {}
    if margin is not None:
        margin_str = f"{margin}in"
        options["margin-top"] = margin_str
        options["margin-bottom"] = margin_str
        options["margin-left"] = margin_str
        options["margin-right"] = margin_str
    pdfkit.from_string(html_doc, str(output_pdf), options=options or None)
    typer.echo(f"PDF generated: {output_pdf}")


if __name__ == "__main__":
    app()
