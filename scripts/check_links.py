#!/usr/bin/env python3
"""
check_links.py - verify every link in a Markdown file still resolves.

A dead link on a profile README is the cheapest available way to look careless,
and it happens by drift rather than by mistake: a repo gets renamed, a file moves,
a service shuts down. Nobody re-reads their own profile. This does.

Usage:
    python3 scripts/check_links.py README.md
    python3 scripts/check_links.py README.md --skip linkedin.com --skip x.com

Exit code 1 if any link is dead, otherwise 0.

Notes:
  - mailto: and anchor-only links are skipped, there is nothing to request.
  - Relative paths are checked against the filesystem, not the network, so they
    work before the branch is pushed.
  - LinkedIn is skipped by default. It serves 999 or 403 to unauthenticated
    clients, so a failure there is a bot check rather than a broken link.
"""

import argparse
import os
import re
import sys
import urllib.error
import urllib.request

# Markdown inline links plus HTML src/href attributes.
MD_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_ATTR = re.compile(r"(?:href|src|srcset)\s*=\s*[\"']([^\"']+)[\"']")

DEFAULT_SKIP = ["linkedin.com"]
UA = "Mozilla/5.0 (compatible; profile-link-check/1.0)"
TIMEOUT = 25


HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)


def strip_non_rendering(text):
    """Drop what GitHub will not turn into a clickable link.

    Commented-out blocks and fenced code samples routinely hold placeholder URLs.
    Checking them produces failures for links that were never live in the first
    place, which trains you to ignore the checker.
    """
    text = HTML_COMMENT.sub("", text)
    return FENCED_CODE.sub("", text)


def extract(text):
    text = strip_non_rendering(text)
    found = []
    for pattern in (MD_LINK, HTML_ATTR):
        for m in pattern.finditer(text):
            url = m.group(1).strip()
            if url:
                found.append(url)
    # Preserve order, drop duplicates.
    seen, out = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def check_remote(url):
    """HEAD first, fall back to GET. Some hosts reject HEAD outright."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return True, r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return False, e.code
        except Exception as e:
            if method == "HEAD":
                continue
            return False, type(e).__name__
    return False, "unreachable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--skip", action="append", default=[],
                    help="substring of URLs to skip, repeatable")
    args = ap.parse_args()

    skip = DEFAULT_SKIP + args.skip
    base = os.path.dirname(os.path.abspath(args.path)) or "."
    text = open(args.path, encoding="utf-8").read()

    dead = []
    print(f"checking links in {args.path}\n")

    for url in extract(text):
        if url.startswith("#") or url.startswith("mailto:") or url.startswith("data:"):
            print(f"  SKIP  {url[:80]}")
            continue
        if any(s in url for s in skip):
            print(f"  SKIP  {url}   (skip list)")
            continue

        if url.startswith("http://") or url.startswith("https://"):
            ok, detail = check_remote(url)
            print(f"  {'OK  ' if ok else 'DEAD'}  {url}   [{detail}]")
            if not ok:
                dead.append((url, detail))
        else:
            target = os.path.normpath(os.path.join(base, url.split("#")[0]))
            ok = os.path.exists(target)
            print(f"  {'OK  ' if ok else 'DEAD'}  {url}   [local]")
            if not ok:
                dead.append((url, "missing file"))

    print()
    if dead:
        print(f"{len(dead)} dead link(s):")
        for url, detail in dead:
            print(f"  {url}  ->  {detail}")
        return 1
    print("all links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
