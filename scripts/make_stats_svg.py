#!/usr/bin/env python3
"""
make_stats_svg.py - generate a self-hosted profile card as a static SVG.

The usual move is to embed a third-party stats card. That costs three things:
the image is rendered on demand by someone else's service and can fail under
rate limiting at exactly the wrong moment, the visual appears on a very large
share of profiles so it reads as a template rather than as effort, and the
metrics it reports (raw commit and star counts) are the exact class of number
that the purchased-reputation market has devalued.

This writes an SVG you commit to your own repo. It always renders, costs no
external request when someone views your profile, looks like yours, and reports
signals a bot farm does not bother to fake: how many of your repositories are
described, licensed, tagged, and documented.

Usage:
    python3 make_stats_svg.py octocat --out assets/
    python3 make_stats_svg.py octocat --out assets/ --theme dark
    python3 make_stats_svg.py octocat --out assets/ --deep       # +README/CI checks
    python3 make_stats_svg.py octocat --dump-json data.json      # cache the data
    python3 make_stats_svg.py --from-json data.json --out assets/

Auth is optional but recommended (60 requests/hour unauthenticated):
    export GITHUB_TOKEN=ghp_...

Then embed it, theme-aware, with real alt text:

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/profile-card-dark.svg">
      <img alt="Profile summary: 24 public repositories, primarily Python and Go"
           src="assets/profile-card-light.svg">
    </picture>

Regenerate on a schedule so it never becomes a lie - see
assets/workflows/profile-card.yml.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com"
UA = "make-stats-svg/1.0"

# Approximate GitHub linguist colours for the languages most likely to show up.
# Anything unlisted falls back through the palette below, so the card still
# renders sensibly for languages this dict has never heard of.
LANG_COLOURS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Go": "#00ADD8", "Rust": "#dea584", "Java": "#b07219", "C": "#555555",
    "C++": "#f34b7d", "C#": "#178600", "Ruby": "#701516", "PHP": "#4F5D95",
    "Swift": "#F05138", "Kotlin": "#A97BFF", "Shell": "#89e051",
    "HTML": "#e34c26", "CSS": "#563d7c", "Vue": "#41b883", "Dart": "#00B4AB",
    "Scala": "#c22d40", "Elixir": "#6e4a7e", "Haskell": "#5e5086",
    "Lua": "#000080", "R": "#198CE7", "Julia": "#a270ba", "Perl": "#0298c3",
    "PowerShell": "#012456", "HCL": "#844FBA", "Dockerfile": "#384d54",
    "Makefile": "#427819", "Jupyter Notebook": "#DA5B0B", "Zig": "#ec915c",
    "Nix": "#7e7eff", "Assembly": "#6E4C13", "Solidity": "#AA6746",
}
FALLBACK_PALETTE = ["#6e7781", "#8250df", "#1f883d", "#bf3989", "#9a6700", "#0969da"]

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#1f2328",
        "text": "#1f2328", "muted": "#59636e", "rule": "#d1d9e0",
        "track": "#eaeef2", "accent": "#0969da",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#e6edf3",
        "text": "#e6edf3", "muted": "#9198a1", "rule": "#21262d",
        "track": "#21262d", "accent": "#4493f8",
    },
}


def api_get(path, token=None):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", UA)
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "not_found"
        if e.code in (403, 429) and e.headers.get("X-RateLimit-Remaining") == "0":
            return None, "rate_limited"
        return None, f"http_{e.code}"
    except Exception as e:
        return None, f"error: {e}"


def count_recent(repos, days=90):
    """Repositories pushed to within the window.

    Replaces the star count as a headline number. Stars measure audience;
    this measures whether the work is alive, which is the signal a reviewer
    is actually reading for on a portfolio account.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    n = 0
    for r in repos:
        ts = r.get("pushed_at")
        if not ts:
            continue
        try:
            when = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if when >= cutoff:
            n += 1
    return n


def collect(username, token, deep=False, max_deep=10):
    user, err = api_get(f"/users/{username}", token)
    if err == "rate_limited":
        raise SystemExit("GitHub API rate limit reached. Set GITHUB_TOKEN and retry.")
    if err or not user:
        raise SystemExit(f"Could not fetch user '{username}' ({err}).")

    repos, err = api_get(
        f"/users/{username}/repos?per_page=100&sort=pushed&direction=desc", token)
    if err or repos is None:
        repos = []

    owned = [r for r in repos if not r.get("fork") and not r.get("archived")]

    langs = {}
    for r in owned:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1

    data = {
        "username": username,
        "name": user.get("name") or username,
        "bio": user.get("bio") or "",
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "owned": len(owned),
        "forked": sum(1 for r in repos if r.get("fork")),
        "stars": sum(r.get("stargazers_count", 0) for r in owned),
        "active_90d": count_recent(owned, days=90),
        "described": sum(1 for r in owned if r.get("description")),
        "licensed": sum(1 for r in owned
                        if (r.get("license") or {}).get("spdx_id") not in (None, "NOASSERTION")),
        "tagged": sum(1 for r in owned if len(r.get("topics") or []) >= 3),
        "with_demo": sum(1 for r in owned if r.get("homepage")),
        "languages": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "deep": False,
    }

    if deep:
        documented = ci = 0
        for r in owned[:max_deep]:
            rd, e = api_get(f"/repos/{username}/{r['name']}/readme", token)
            if not e and rd and rd.get("size", 0) > 800:
                documented += 1
            wf, e2 = api_get(
                f"/repos/{username}/{r['name']}/contents/.github/workflows", token)
            if not e2 and isinstance(wf, list) and wf:
                ci += 1
        data.update({"deep": True, "deep_sample": min(len(owned), max_deep),
                     "documented": documented, "ci": ci})
    return data


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def truncate(s, n):
    s = str(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "\u2026"


def lang_colour(name, i):
    return LANG_COLOURS.get(name, FALLBACK_PALETTE[i % len(FALLBACK_PALETTE)])


def render(data, theme_name):
    t = THEMES[theme_name]
    W, PAD = 820, 28
    langs = list(data["languages"].items())[:6]
    total = sum(c for _, c in langs) or 1
    owned = max(data["owned"], 1)

    stats = [
        (f"{data['owned']}", "public repos"),
        (f"{data.get('active_90d', 0)}", "pushed in 90 days"),
        (f"{len(data['languages'])}", "languages"),
    ]
    quality = [
        (data["described"], owned, "described"),
        (data["licensed"], owned, "licensed"),
        (data["tagged"], owned, "tagged"),
        (data["with_demo"], owned, "with demo"),
    ]
    if data.get("deep"):
        s = max(data.get("deep_sample", 1), 1)
        quality = [(data.get("documented", 0), s, "documented"),
                   (data.get("ci", 0), s, "with CI")] + quality[:2]

    H = 262 if langs else 214
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(data["name"])} GitHub summary">')
    a(f'<title>{esc(data["name"])}: {data["owned"]} public repositories, '
      f'{esc(", ".join(k for k, _ in langs[:3])) or "no languages detected"}</title>')
    a('<style>'
      'text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}'
      '.h{font-size:19px;font-weight:600}.sub{font-size:12.5px}'
      '.n{font-size:26px;font-weight:600}.l{font-size:11.5px}'
      '.k{font-size:12.5px}.f{font-size:10.5px}'
      '</style>')
    a(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
      f'fill="{t["bg"]}" stroke="{t["border"]}"/>')

    # header. The handle is right-aligned rather than positioned after the name,
    # because estimating rendered text width from character count overlaps on
    # anything longer than a short name.
    a(f'<text class="h" x="{PAD}" y="38" fill="{t["title"]}">'
      f'{esc(truncate(data["name"], 34))}</text>')
    a(f'<text class="sub" x="{W-PAD}" y="38" text-anchor="end" fill="{t["muted"]}">'
      f'@{esc(data["username"])}</text>')
    if data.get("bio"):
        a(f'<text class="sub" x="{PAD}" y="59" fill="{t["muted"]}">'
          f'{esc(truncate(data["bio"], 92))}</text>')
    a(f'<line x1="{PAD}" y1="74" x2="{W-PAD}" y2="74" stroke="{t["rule"]}"/>')

    # headline counts
    for i, (num, label) in enumerate(stats):
        x = PAD + i * 132
        a(f'<text class="n" x="{x}" y="112" fill="{t["title"]}">{esc(num)}</text>')
        a(f'<text class="l" x="{x}" y="130" fill="{t["muted"]}">{esc(label)}</text>')

    # quality ratios: the part a purchased-reputation account does not bother with
    qx = PAD + 3 * 132 + 14
    a(f'<text class="l" x="{qx}" y="90" fill="{t["muted"]}">'
      f'REPOSITORY HYGIENE</text>')
    for i, (got, of, label) in enumerate(quality):
        col, row = i % 2, i // 2
        x, y = qx + col * 148, 112 + row * 26
        pct = got / of if of else 0
        a(f'<text class="k" x="{x}" y="{y}" fill="{t["text"]}">'
          f'{got}/{of}</text>')
        a(f'<text class="l" x="{x + 42}" y="{y}" fill="{t["muted"]}">{esc(label)}</text>')
        a(f'<rect x="{x}" y="{y + 5}" width="120" height="3" rx="1.5" fill="{t["track"]}"/>')
        a(f'<rect x="{x}" y="{y + 5}" width="{max(round(120 * pct), 1)}" height="3" '
          f'rx="1.5" fill="{t["accent"]}"/>')

    # language bar
    if langs:
        a(f'<text class="l" x="{PAD}" y="185" fill="{t["muted"]}">'
          f'LANGUAGES BY REPOSITORY</text>')
        bar_w, x = W - 2 * PAD, PAD
        a(f'<rect x="{PAD}" y="196" width="{bar_w}" height="9" rx="4.5" fill="{t["track"]}"/>')
        for i, (name, count) in enumerate(langs):
            seg = max(round(bar_w * count / total), 3)
            if x + seg > PAD + bar_w:
                seg = PAD + bar_w - x
            if seg <= 0:
                break
            a(f'<rect x="{x}" y="196" width="{seg}" height="9" '
              f'fill="{lang_colour(name, i)}"><title>{esc(name)}: {count} repos</title></rect>')
            x += seg
        lx = PAD
        for i, (name, count) in enumerate(langs):
            a(f'<circle cx="{lx + 4}" cy="{224}" r="4" fill="{lang_colour(name, i)}"/>')
            a(f'<text class="l" x="{lx + 15}" y="228" fill="{t["text"]}">'
              f'{esc(name)} <tspan fill="{t["muted"]}">{count}</tspan></text>')
            lx += 30 + int(len(name) * 6.9) + len(str(count)) * 7

    a(f'<text class="f" x="{PAD}" y="{H - 14}" fill="{t["muted"]}">'
      f'Generated {esc(data["generated"])} from the GitHub REST API. '
      f'Counts cover public, non-archived repositories owned by this account.</text>')
    a('</svg>')
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description="Generate a self-hosted profile card SVG.")
    ap.add_argument("username", nargs="?", help="GitHub username")
    ap.add_argument("--out", default=".", help="output directory (default: .)")
    ap.add_argument("--theme", default="both", choices=["light", "dark", "both"])
    ap.add_argument("--name", default="profile-card", help="output filename stem")
    ap.add_argument("--deep", action="store_true",
                    help="also check README size and CI presence (more API calls)")
    ap.add_argument("--dump-json", help="write the collected data to this path")
    ap.add_argument("--from-json", help="render from a saved data file, no network")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            data = json.load(f)
    else:
        if not args.username:
            ap.error("username is required unless --from-json is given")
        data = collect(args.username, args.token, deep=args.deep)

    if args.dump_json:
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {args.dump_json}")

    os.makedirs(args.out, exist_ok=True)
    themes = ["light", "dark"] if args.theme == "both" else [args.theme]
    for th in themes:
        path = os.path.join(args.out, f"{args.name}-{th}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(data, th))
        print(f"wrote {path}")

    if len(themes) == 2:
        print("\nEmbed with real alt text so it survives dark mode and screen readers:\n")
        print("<picture>")
        print(f'  <source media="(prefers-color-scheme: dark)" '
              f'srcset="{args.name}-dark.svg">')
        print(f'  <img alt="Profile summary: {data["owned"]} public repositories, '
              f'primarily {", ".join(list(data["languages"])[:2]) or "unlisted"}" '
              f'src="{args.name}-light.svg">')
        print("</picture>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
