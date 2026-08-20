#!/usr/bin/env python3
"""
make_social_previews.py - build the 1280x640 social preview card for each repo.

WHY THIS MATTERS MORE THAN IT LOOKS LIKE IT DOES
    The social preview is what renders when a repo is shared on LinkedIn, Slack,
    or anywhere with link unfurling, and it is the image that appears in the
    LinkedIn Featured section. With no preview set, GitHub generates a mostly
    grey card. For someone applying to jobs, that grey card is the thumbnail a
    recruiter sees.

    The one rule that matters: the project name has to be legible at thumbnail
    size. Everything else is secondary.

USAGE
    python3 scripts/make_social_previews.py --out assets/social/
    python3 scripts/make_social_previews.py --out assets/social/ --png

Upload each one at Settings -> General -> Social preview on the matching repo.
"""

import argparse
import os

W, H = 1280, 640

# Dark canvas, because it reads well against both LinkedIn's white feed and
# Slack's dark mode, and because a light card on a light feed disappears.
BG = "#0d1117"
FG = "#e6edf3"
MUTED = "#9198a1"
RULE = "#30363d"

CARDS = [
    {
        "file": "aws-anomaly-soar",
        "kicker": "CLOUD DETECTION AND RESPONSE",
        "title": "aws-anomaly-soar",
        "sub": "Behavioural anomaly detection on CloudTrail with a human-gated containment playbook",
        "accent": "#f0883e",
        "stats": [("6", "step SOAR playbook"),
                  ("~$5-7", "per month to run"),
                  ("100%", "Terraform managed")],
        "chips": ["Step Functions", "DynamoDB baselines", "ATT&CK for Cloud", "D3FEND"],
    },
    {
        "file": "llm-sectest",
        "kicker": "OWASP TOP 10 FOR LLM APPLICATIONS 2025",
        "title": "llm-sectest",
        "sub": "Attack battery with a programmatic oracle per test, so a finding is proven rather than eyeballed",
        "accent": "#3fb950",
        "stats": [("5 of 6", "exploitable before"),
                  ("0 of 6", "exploitable after"),
                  ("$0", "all inference local")],
        "chips": ["Prompt injection", "Output handling", "Prompt leakage", "pytest"],
    },
    {
        "file": "dns-tunnel-vuln-mgmt",
        "kicker": "VULNERABILITY MANAGEMENT LIFECYCLE",
        "title": "dns-tunnel-vuln-mgmt",
        "sub": "Covert DNS C2 found by red team, scored, remediated in depth, and verified by retest",
        "accent": "#58a6ff",
        "stats": [("7.6", "CVSS 4.0, High"),
                  ("4", "layered controls"),
                  ("5", "VM isolated lab")],
        "chips": ["Suricata", "BIND9 RPZ", "Wazuh on ARM64", "NIST SP 800-40r4"],
    },
]

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def build(c):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c["title"])}: {esc(c["sub"])}">']
    o.append(f'<title>{esc(c["title"])}</title>')
    o.append(f"<style>text{{font-family:{FONT}}}</style>")
    o.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # Accent spine on the left edge. Gives the card an identity at thumbnail
    # size, where the body text has already stopped being readable.
    o.append(f'<rect x="0" y="0" width="14" height="{H}" fill="{c["accent"]}"/>')

    x = 82
    o.append(f'<text x="{x}" y="118" fill="{c["accent"]}" font-size="21" '
             f'font-weight="700" letter-spacing="2.6">{esc(c["kicker"])}</text>')

    # The title is the only element that has to survive thumbnail scaling.
    o.append(f'<text x="{x}" y="212" fill="{FG}" font-size="70" '
             f'font-weight="700">{esc(c["title"])}</text>')

    o.append(f'<text x="{x}" y="268" fill="{MUTED}" font-size="26">'
             f'{esc(c["sub"][:78])}</text>')
    if len(c["sub"]) > 78:
        cut = c["sub"][:78].rfind(" ")
        o[-1] = (f'<text x="{x}" y="268" fill="{MUTED}" font-size="26">'
                 f'{esc(c["sub"][:cut])}</text>')
        o.append(f'<text x="{x}" y="304" fill="{MUTED}" font-size="26">'
                 f'{esc(c["sub"][cut + 1:])}</text>')

    o.append(f'<line x1="{x}" y1="354" x2="{W - 82}" y2="354" stroke="{RULE}" stroke-width="2"/>')

    # Numbers, because a number is what a reader repeats to a hiring manager.
    for i, (num, label) in enumerate(c["stats"]):
        sx = x + i * 340
        o.append(f'<text x="{sx}" y="432" fill="{FG}" font-size="52" '
                 f'font-weight="700">{esc(num)}</text>')
        o.append(f'<text x="{sx}" y="466" fill="{MUTED}" font-size="21">{esc(label)}</text>')

    cx = x
    for chip in c["chips"]:
        cw = int(len(chip) * 11.6) + 38
        o.append(f'<rect x="{cx}" y="528" width="{cw}" height="42" rx="21" '
                 f'fill="none" stroke="{RULE}" stroke-width="2"/>')
        o.append(f'<text x="{cx + 17}" y="555" fill="{MUTED}" font-size="19">{esc(chip)}</text>')
        cx += cw + 14

    o.append(f'<text x="{W - 82}" y="118" fill="{MUTED}" font-size="21" '
             f'text-anchor="end">github.com/adamalizeerj</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/social/")
    ap.add_argument("--png", action="store_true",
                    help="also write PNG, which GitHub's uploader prefers")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    for c in CARDS:
        svg_path = os.path.join(args.out, f"{c['file']}-social.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(build(c))
        print(f"wrote {svg_path}")
        if args.png:
            try:
                import cairosvg
            except ImportError:
                print("  (install cairosvg for PNG output)")
                continue
            png_path = os.path.join(args.out, f"{c['file']}-social.png")
            cairosvg.svg2png(url=svg_path, write_to=png_path,
                             output_width=W, output_height=H)
            print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
