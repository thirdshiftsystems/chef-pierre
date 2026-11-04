#!/usr/bin/env python3
"""Extract a recipe's ingredients + method from a source page.

Packages the approach verified to work for the household's two primary
sources: cooking.nytimes.com (plain curl with a browser UA returns the recipe
text in the HTML) and Cloudflare-fronted sites like eatingwell.com (curl is
403-blocked, so this prints the browser_navigate route instead).

Usage:
    python3 extract_recipe_text.py <url>

Notes:
  - The anchors below are the sites' section headings; extend ANCHORS per site.
  - If output is thin or empty, fall back to the manual routes in SKILL.md
    (browser_navigate + read_file on the cached snapshot file).
  - Do not invent quantities when extraction fails; ask the user to paste.
"""
import html
import re
import subprocess
import sys

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126 Safari/537.36"
)
ANCHORS = ["Yield:", "Ingredients", "Preparation", "Directions"]
WINDOW_BEFORE = 2500
WINDOW_AFTER = 4000


def fetch(url: str, out: str = "/tmp/recipe_page.html") -> str:
    subprocess.run(
        ["curl", "-sL", "-A", UA, "--max-time", "30", url, "-o", out],
        check=False,
    )
    with open(out, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def to_text(fragment: str) -> str:
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", fragment))
    return re.sub(r"\n\s*\n+", "\n", txt).strip()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    url = sys.argv[1]
    page = fetch(url)

    if "Just a moment" in page or "Enable JavaScript" in page or len(page) < 5000:
        print("BLOCKED (Cloudflare/JS interstitial). Use browser_navigate:")
        print(f"  browser_navigate({url!r})")
        print("  then read_file the cache/web/browser-snapshot-*.txt path it prints.")
        return 1

    printed = 0
    for anchor in ANCHORS:
        idx = page.find(anchor)
        if idx < 0:
            continue
        print(f"\n===== {anchor} =====")
        print(to_text(page[max(0, idx - WINDOW_BEFORE): idx + WINDOW_AFTER]))
        printed += 1

    if not printed:
        print("No anchors matched — page shape changed or content is JS-only.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
