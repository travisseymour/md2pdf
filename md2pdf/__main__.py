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

import math
import os
from io import BytesIO
from pathlib import Path
from typing import Annotated

import markdown
import pdfkit
from cyclopts import App, Parameter, validators
from pygments.formatters import HtmlFormatter

app = App(help="Markdown to PDF Converter")

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


# ----------------------------------------------------------------------
# WATERMARK (reportlab + pypdf, adapted from pptxtool.py)
# ----------------------------------------------------------------------


def _try_register_font() -> str:
    """Register a TrueType font for reportlab and return its name."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        ("Liberation Sans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ("DejaVu Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
        ("Arial", "/usr/share/fonts/truetype/msttcorefonts/arial.ttf"),
        ("Arial", "/Library/Fonts/Arial.ttf"),
        ("Arial", "C:\\Windows\\Fonts\\arial.ttf"),
    ]
    for name, path in candidates:
        if name in pdfmetrics.getRegisteredFontNames():
            return name
        try:
            if os.path.isfile(path):
                pdfmetrics.registerFont(TTFont(name, path))
                return name
        except Exception:
            pass
    return "Helvetica"


def _fit_font_size(text: str, font_name: str, page_w: float, page_h: float, theta_rad: float) -> float:
    """Binary-search for the largest font size whose rotated bounding box fits the page."""
    from reportlab.pdfbase import pdfmetrics

    margin = math.hypot(page_w, page_h) * 0.04

    def fits(size: float) -> bool:
        adv = pdfmetrics.stringWidth(text, font_name, size)
        asc, desc = 0.8 * size, -0.2 * size
        try:
            asc = pdfmetrics.getAscent(font_name, size)
            desc = pdfmetrics.getDescent(font_name, size)
        except Exception:
            pass
        text_h = asc - desc
        c, s = abs(math.cos(theta_rad)), abs(math.sin(theta_rad))
        bb_w = adv * c + text_h * s
        bb_h = adv * s + text_h * c
        return bb_w <= (page_w - 2 * margin) and bb_h <= (page_h - 2 * margin)

    lo, hi = 1.0, 4000.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if fits(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _make_watermark_page(page_w: float, page_h: float, text: str, font_name: str) -> bytes:
    """Create a single-page PDF with centered diagonal watermark text."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfgen import canvas

    theta = math.atan2(page_h, page_w)
    size = _fit_font_size(text, font_name, page_w, page_h, theta)

    adv = pdfmetrics.stringWidth(text, font_name, size)
    asc, desc = 0.8 * size, -0.2 * size
    try:
        asc = pdfmetrics.getAscent(font_name, size)
        desc = pdfmetrics.getDescent(font_name, size)
    except Exception:
        pass
    baseline_y = -(asc + desc) / 2.0

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.saveState()
    c.translate(page_w / 2.0, page_h / 2.0)
    c.rotate(math.degrees(theta))
    c.setFillGray(0.7)
    c.setFillAlpha(0.3)
    c.setFont(font_name, size)
    c.drawString(-adv / 2.0, baseline_y, text)
    c.restoreState()
    c.showPage()
    c.save()

    buf.seek(0)
    return buf.getvalue()


def _apply_watermark(pdf_path: Path, text: str) -> None:
    """Overlay diagonal watermark text on every page of an existing PDF."""
    from pypdf import PdfReader, PdfWriter

    font_name = _try_register_font()
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    wm_cache: dict[tuple[float, float], bytes] = {}

    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        if (w, h) not in wm_cache:
            wm_cache[(w, h)] = _make_watermark_page(w, h, text, font_name)

        wm_page = PdfReader(BytesIO(wm_cache[(w, h)])).pages[0]
        page.merge_page(wm_page)
        writer.add_page(page)

    with open(pdf_path, "wb") as f:
        writer.write(f)


# ----------------------------------------------------------------------
# MAIN COMMAND
# ----------------------------------------------------------------------


@app.default
def convert(
    input_file: Annotated[Path, Parameter(validator=validators.Path(exists=True), help="Path to the Markdown file")],
    output_pdf: Annotated[Path | None, Parameter(help="Path to the output PDF file (default: <input>.pdf)")] = None,
    *,
    save_html: Annotated[bool, Parameter(help="Save intermediate HTML file")] = False,
    theme: Annotated[str, Parameter(help="Pygments theme for syntax highlighting. Options are "
        "['default', 'monokai', 'manni', 'vim', 'friendly', 'native', 'github']")] = "monokai",
    margin: Annotated[float | None, Parameter(help="Page margins in inches (e.g. 0.75)")] = None,
    font_scale: Annotated[int | None, Parameter(help="Font size as a percentage of the default (e.g. 120 for 20% larger)")] = None,
    watermark: Annotated[str | None, Parameter(help="Add diagonal watermark text to each page (e.g. 'DRAFT' or 'CONFIDENTIAL')")] = None,
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
        print(f"Intermediate HTML saved to: {html_file}")

    # Convert HTML to PDF
    options = {"enable-local-file-access": ""}
    if margin is not None:
        margin_str = f"{margin}in"
        options["margin-top"] = margin_str
        options["margin-bottom"] = margin_str
        options["margin-left"] = margin_str
        options["margin-right"] = margin_str
    pdfkit.from_string(html_doc, str(output_pdf), options=options)

    # Apply watermark to the generated PDF
    if watermark:
        _apply_watermark(output_pdf, watermark)

    print(f"PDF generated: {output_pdf}")


if __name__ == "__main__":
    app()
