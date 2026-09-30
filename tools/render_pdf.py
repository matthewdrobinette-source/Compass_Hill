"""Render Compass_Hill_Master_Plan.md to HTML and PDF.

Usage:  python3 tools/render_pdf.py
Needs:  pip install markdown; Node with Playwright and a Chromium build
        (set CHROMIUM_PATH if it is not at /opt/pw-browsers/chromium).
"""

import html
import os
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Compass_Hill_Master_Plan.md"
OUT_HTML = ROOT / "build" / "Compass_Hill_Master_Plan.html"
OUT_PDF = ROOT / "Compass_Hill_Master_Plan.pdf"

# Usable width inside a <pre>, in points (letter page, 0.55in margins, padding).
PRE_WIDTH_PT = 510
MONO_ADVANCE = 0.602  # DejaVu Sans Mono glyph width per 1pt of font size
MAX_PRE_PT = 8.5

CSS = """
@page { size: Letter; margin: 0.6in 0.55in 0.7in 0.55in; }
:root { --ink:#1d1d1b; --muted:#5b5b57; --rule:#cfcac0; --accent:#2f5d50; --wash:#f6f4ef; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Bitstream Charter", "DejaVu Serif", Georgia, serif; font-size: 10.2pt;
       line-height: 1.42; color: var(--ink); background: #fff; margin: 0; }
h1 { font-size: 20pt; line-height: 1.15; margin: 0 0 6pt; color: var(--accent); }
h2 { font-size: 14pt; margin: 18pt 0 6pt; color: var(--accent); break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p { margin: 5pt 0; }
ul, ol { margin: 4pt 0 6pt; padding-left: 18pt; }
li { margin: 1.5pt 0; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 14pt 0; }
strong { color: #000; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9pt;
        line-height: 1.3; break-inside: auto; }
tr { break-inside: avoid; }
th { text-align: left; font-weight: bold; border-bottom: 1.2px solid var(--ink); padding: 3pt 6pt 3pt 0; }
td { border-bottom: 1px solid var(--rule); padding: 3pt 6pt 3pt 0; vertical-align: top; }
td.nw { white-space: nowrap; }
pre { background: var(--wash); border: 1px solid var(--rule); border-radius: 4pt; padding: 7pt 8pt;
      font-family: "DejaVu Sans Mono", "Liberation Mono", monospace; line-height: 1.25;
      white-space: pre; overflow: hidden; break-inside: avoid; margin: 6pt 0 8pt; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 0.9em; }
a { color: var(--accent); text-decoration: none; }
"""


def fit_pre_blocks(body: str) -> str:
    def repl(m):
        inner = m.group(2)
        text = html.unescape(re.sub(r"<[^>]+>", "", inner))
        longest = max((len(line) for line in text.split("\n")), default=1)
        size = min(MAX_PRE_PT, PRE_WIDTH_PT / (MONO_ADVANCE * max(longest, 1)))
        return f'<pre style="font-size:{size:.2f}pt">{m.group(1)}{inner}</pre>'

    return re.sub(r"<pre>(<code[^>]*>)?(.*?)</pre>", repl, body, flags=re.S)


def keep_short_cells_whole(body: str) -> str:
    """Stop short values such as "$0.35–0.6M" from wrapping in narrow columns."""

    def repl(m):
        text = re.sub(r"<[^>]+>", "", m.group(2))
        if len(html.unescape(text)) <= 14:
            return f'<td class="nw"{m.group(1)}>{m.group(2)}</td>'
        return m.group(0)

    return re.sub(r"<td([^>]*)>(.*?)</td>", repl, body, flags=re.S)


def build_html() -> str:
    md = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    body = fit_pre_blocks(body)
    body = keep_short_cells_whole(body)
    title = "Compass Hill Estate — Master Property Plan"
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    )


def main() -> int:
    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    script = ROOT / "tools" / "html_to_pdf.js"
    env = dict(os.environ)
    env.setdefault("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
    subprocess.run(["node", str(script), str(OUT_HTML), str(OUT_PDF)], check=True, env=env)
    print(f"wrote {OUT_PDF.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
