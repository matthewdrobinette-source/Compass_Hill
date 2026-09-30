# Compass Hill

Master property plan for the Compass Hill Estate in southwest Ohio.

| File | What it is |
|---|---|
| [`Compass_Hill_Master_Plan.md`](Compass_Hill_Master_Plan.md) | The plan (Revision B). This is the source of truth. |
| [`Compass_Hill_Master_Plan.pdf`](Compass_Hill_Master_Plan.pdf) | Printable copy, rendered from the Markdown. |
| [`tools/floorplans.py`](tools/floorplans.py) | Draws the house plans on one 120-ft grid (1 character = 1 ft), so the stair and elevator core stays stacked on every level. |
| [`tools/render_pdf.py`](tools/render_pdf.py) | Renders the Markdown to PDF through headless Chromium. |

To rebuild after editing:

```sh
python3 tools/floorplans.py        # if rooms changed; paste the output into section 7
pip install markdown
python3 tools/render_pdf.py        # needs Node + Playwright + Chromium
```
