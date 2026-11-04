#!/usr/bin/env python3
"""Bulk-load a shopping list into the household Kroger cart.

Usage:
    python3 bulk_load_cart.py            # DRY RUN - prints picks, writes nothing
    python3 bulk_load_cart.py --commit   # actually adds every matched pick

Phase 1 is mandatory: read every [PICK] line and fix the search terms until the
matched descriptions are the products you actually mean. Keyword search returns
nonsense often (see the SKILL.md pitfalls). Never invent a productId - every add
uses an ID the search API returned.
"""
import json
import os
import re
import subprocess
import sys

KROGER = os.environ.get("KROGER_SCRIPT", os.path.expanduser("~/.hermes/scripts/kroger/kroger.py"))

# (search term, qty, aisle group)
ITEMS = [
    # put the real list here
]

STOP = {"the", "a", "of", "and", "with", "for"}


def tokens(s):
    return [t for t in re.findall(r"[a-z0-9']+", s.lower()) if t not in STOP]


def search(term):
    p = subprocess.run(["python3", KROGER, "search", term, "--json"],
                       capture_output=True, text=True, timeout=90)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout or "")[:200]
    try:
        return json.loads(p.stdout), None
    except Exception as e:
        return None, f"json parse: {e} :: {p.stdout[:200]}"


def score(desc, term):
    dt = set(tokens(desc))
    qt = tokens(term)
    if not qt:
        return 0.0
    hit = sum(1 for t in qt if any(t in d or d in t for d in dt))
    return hit / len(qt)


def pick(term):
    results, err = search(term)
    if err or not results:
        return None, err or "no results"
    scored = sorted(((score(r.get("description", ""), term), i, r)
                     for i, r in enumerate(results)),
                    key=lambda x: (-x[0], x[1]))
    best = scored[0]
    if best[0] < 0.5:
        return None, f"no confident match (best {best[0]:.2f}: {best[2].get('description')})"
    return best[2], None


def add(product_id, qty):
    p = subprocess.run(["python3", KROGER, "add", "--product-id", str(product_id),
                        "--qty", str(qty)], capture_output=True, text=True, timeout=90)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def main():
    commit = "--commit" in sys.argv
    picks, failures = [], []
    for term, qty, group in ITEMS:
        prod, err = pick(term)
        if err:
            failures.append((group, term, err))
            continue
        picks.append((group, term, qty, prod))
        print(f"[PICK] {group:14s} | {term:38s} | qty {qty} | {prod.get('productId')} | "
              f"{prod.get('description')} | {prod.get('size')} | ${prod.get('price')}")
    print(f"\n=== {len(picks)} matched, {len(failures)} unmatched ===")
    for g, t, e in failures:
        print(f"[MISS] {g:14s} | {t:38s} | {e}")

    if not commit:
        print("\nDRY RUN - nothing written to the cart.")
        return

    print("\n=== COMMITTING TO CART ===")
    ok = 0
    for group, term, qty, prod in picks:
        good, msg = add(prod.get("productId"), qty)
        if good:
            ok += 1
            print(f"[ADDED] {term} x{qty} -> {prod.get('productId')}")
        else:
            print(f"[FAILED] {term} -> {msg[:160]}")
    print(f"\n=== cart: {ok}/{len(picks)} items added ===")


if __name__ == "__main__":
    main()
