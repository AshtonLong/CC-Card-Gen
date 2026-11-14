#!/usr/bin/env python3
"""Validate card JSON files written by the card-writing subagents.

Usage: python validate_cards.py <cards_dir or file.json>... [--source-dir DIR] [--depth full|exam|cram]

Errors (exit code 1): invalid JSON, missing/broken cloze syntax, nested clozes, HTML tags,
braces in "extra", bad tags, bad "yield", figure references to missing files/pages.
Warnings: long cards, >3 deletions, near-duplicate cards (within and across files),
yield levels that don't belong in the chosen depth.
"""
import argparse
import collections
import difflib
import json
import os
import re
import sys

CLOZE = re.compile(r"\{\{c(\d+)::(.*?)\}\}", re.S)
HTML = re.compile(r"<\s*/?\s*(b|i|u|br|div|span|p|sub|sup|img|font|li|ul|ol)\b", re.I)
YIELDS = {"high", "medium", "low"}
ALLOWED = {"full": YIELDS, "exam": {"high", "medium"}, "cram": {"high"}}


def answer_text(t):
    return CLOZE.sub(lambda m: m.group(2).split("::")[0], t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--source-dir", help="folder with the original lecture files (checks figure refs)")
    ap.add_argument("--depth", choices=sorted(ALLOWED), default=None)
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".json"))
        else:
            files.append(p)

    page_counts = {}
    errors, warnings, everything = [], [], []
    for path in files:
        name = os.path.basename(path)
        try:
            cards = json.load(open(path, encoding="utf-8"))
            assert isinstance(cards, list)
        except Exception as e:
            errors.append(f"{name}: not a JSON array of cards ({e})")
            continue
        ycount, figs = collections.Counter(), 0
        for i, c in enumerate(cards):
            key = f"{name}#{i}"
            t = c.get("text", "") if isinstance(c, dict) else ""
            clozes = CLOZE.findall(t)
            if not clozes:
                errors.append(f"{key}: no {{{{cN::...}}}} cloze")
            if t.count("{{") != len(clozes) or t.count("}}") != len(clozes):
                errors.append(f"{key}: stray '{{{{' or '}}}}' (put a space between closing braces in math)")
            for _, body in clozes:
                if "{{" in body:
                    errors.append(f"{key}: nested cloze")
                if not body.split("::")[0].strip():
                    errors.append(f"{key}: empty cloze")
            if len({n for n, _ in clozes}) > 3:
                warnings.append(f"{key}: more than 3 cloze numbers")
            if t.count("\\(") != t.count("\\)"):
                errors.append(f"{key}: unbalanced MathJax \\( \\)")
            extra = c.get("extra", "") or ""
            if HTML.search(t + extra):
                errors.append(f"{key}: HTML tag (use plain text)")
            if "{{" in extra or "}}" in extra:
                errors.append(f"{key}: '{{{{' or '}}}}' in extra")
            tags = c.get("tags") or []
            if not tags or any((not isinstance(x, str)) or " " in x for x in tags):
                errors.append(f"{key}: tags must be a non-empty list of strings without spaces")
            y = c.get("yield")
            if y not in YIELDS:
                errors.append(f"{key}: yield must be high/medium/low, got {y!r}")
            else:
                ycount[y] += 1
                if args.depth and y not in ALLOWED[args.depth]:
                    warnings.append(f"{key}: yield={y} doesn't belong in depth={args.depth}")
            fig = c.get("figure")
            if fig:
                figs += 1
                fname, page = fig.get("file") or fig.get("pdf"), fig.get("page")
                if args.source_dir and fname:
                    fpath = os.path.join(args.source_dir, fname)
                    if not os.path.exists(fpath):
                        errors.append(f"{key}: figure file not found: {fname}")
                    elif fname.lower().endswith(".pdf"):
                        if fpath not in page_counts:
                            import pymupdf
                            with pymupdf.open(fpath) as d:
                                page_counts[fpath] = d.page_count
                        if not isinstance(page, int) or not 1 <= page <= page_counts[fpath]:
                            errors.append(f"{key}: figure page {page!r} out of range")
            words = len(answer_text(t).split())
            if words > 45:
                warnings.append(f"{key}: long card ({words} words)")
            everything.append((key, re.sub(r"\W+", " ", answer_text(t)).lower().strip()))
        print(f"{name}: {len(cards)} cards, yield={dict(ycount)}, figures={figs}")

    for a in range(len(everything)):
        ka, ta = everything[a]
        for b in range(a + 1, len(everything)):
            kb, tb = everything[b]
            m = difflib.SequenceMatcher(None, ta, tb)
            if m.real_quick_ratio() > 0.85 and m.quick_ratio() > 0.85 and m.ratio() > 0.85:
                warnings.append(f"near-duplicate: {ka} ~ {kb}: {ta[:70]!r}")

    print(f"\nTOTAL {len(everything)} cards in {len(files)} files")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
