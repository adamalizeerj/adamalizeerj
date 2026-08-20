#!/usr/bin/env python3
"""
make_buttons.py - generate the contact buttons as self-hosted SVGs.

The usual move is shields.io. That puts a third-party image request in the most
valuable position on the profile, which means the top of the page can render as
a broken image if that service is slow, rate limiting, or down. It also looks
like every other profile.

These are committed to the repository instead. They render instantly, cannot
fail, and are readable in both GitHub themes by construction: a solid fill with
white text needs no light and dark variant.

Usage:
    python3 scripts/make_buttons.py --out assets/
"""

import argparse
import os

# Fills chosen to stay legible against both the light (#ffffff) and dark
# (#0d1117) GitHub canvases. All text is white, so contrast is a property of
# the pill rather than of the page.
BUTTONS = [
    {"file": "btn-linkedin.svg", "label": "LinkedIn",
     "sub": "in/aalizeerj", "fill": "#0A66C2", "icon": "linkedin"},
    {"file": "btn-email.svg", "label": "Email",
     "sub": "adamalizeerj@gmail.com", "fill": "#3d444d", "icon": "mail"},
    {"file": "btn-resume.svg", "label": "Resume",
     "sub": "PDF", "fill": "#1f6feb", "icon": "doc"},
]

ICONS = {
    # 16x16 paths, drawn in white, kept simple so they stay crisp at this size.
    "linkedin": ('<path fill="#fff" d="M3.4 5.6h2.5V14H3.4V5.6zm1.25-4a1.45 1.45 0 1 1 0 '
                 '2.9 1.45 1.45 0 0 1 0-2.9zM7.6 5.6h2.4v1.15h.03c.34-.62 1.16-1.28 '
                 '2.38-1.28 2.54 0 3.01 1.6 3.01 3.7V14h-2.5v-3.83c0-.91-.02-2.09-1.29-2.09-1.3 '
                 '0-1.5 1-1.5 2.02V14H7.6V5.6z"/>'),
    "mail": ('<path fill="#fff" d="M1.6 3.6h12.8c.44 0 .8.36.8.8v7.2c0 .44-.36.8-.8.8H1.6a.8.8 0 '
             '0 1-.8-.8V4.4c0-.44.36-.8.8-.8zm.6 1.9v6h11.6v-6L8 9.2 2.2 5.5zm.5-.7L8 8.1l5.3-3.3z"/>'),
    "doc": ('<path fill="#fff" d="M4 1.6h5.2L13 5.4V14a.8.8 0 0 1-.8.8H4a.8.8 0 0 1-.8-.8V2.4c0-.44.36-.8.8-.8zm5 1.2v2.6h2.6zM5.2 8h5.6v1.2H5.2zm0 2.6h5.6v1.2H5.2z"/>'),
}

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="28" \
viewBox="0 0 {w} 28" role="img" aria-label="{aria}">
<title>{aria}</title>
<rect x="0" y="0" width="{w}" height="28" rx="6" fill="{fill}"/>
<g transform="translate(9, 6)">{icon}</g>
<text x="31" y="18.5" fill="#ffffff" font-size="12.5" font-weight="600"
 textLength="{tl}" lengthAdjust="spacingAndGlyphs"
 font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">{label}</text>
</svg>
"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def build(b):
    """One short word per pill.

    An earlier version rendered a second line of detail inside the pill and it
    overflowed, because the rendered width of a string depends on the font the
    viewer actually has. The fix is to carry the detail in the title and the
    aria-label, where it costs no pixels, and to pin the visible label with
    textLength so it fits the box on any font stack.
    """
    tl = round(len(b["label"]) * 7.6, 1)
    width = int(31 + tl + 13)
    aria = f'{b["label"]}: {b["sub"]}'
    return TEMPLATE.format(w=width, fill=b["fill"], icon=ICONS[b["icon"]],
                           label=esc(b["label"]), tl=tl, aria=esc(aria))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for b in BUTTONS:
        path = os.path.join(args.out, b["file"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(b))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
