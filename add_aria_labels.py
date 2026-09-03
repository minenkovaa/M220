#!/usr/bin/env python3
"""Add aria-label attributes to generated HTML headings and title labels."""

from __future__ import annotations

from pathlib import Path
import argparse

from lxml import html

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
TITLE_CLASSES = {"title", "subtitle", "heading"}


def label_text(node) -> str:
    text = "".join(node.itertext())
    return " ".join(text.split())


def should_label(node) -> bool:
    tag = node.tag.lower() if hasattr(node.tag, "lower") else str(node.tag).lower()
    classes = set((node.get("class") or "").split())
    return tag in HEADING_TAGS or bool(classes & TITLE_CLASSES)


def add_labels_to_html(path: Path) -> None:
    tree = html.parse(str(path))
    for node in tree.xpath(".//*"):
        if not should_label(node):
            continue
        if node.get("aria-label") is not None:
            continue
        text = label_text(node)
        if text:
            node.set("aria-label", text)
    with path.open("wb") as f:
        tree.write(f, encoding="utf-8", method="html")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="HTML files or directories to process")
    args = parser.parse_args()

    for raw in args.paths:
        target = Path(raw)
        if target.is_dir():
            for html_file in sorted(target.rglob("*.html")):
                add_labels_to_html(html_file)
        elif target.suffix.lower() == ".html":
            add_labels_to_html(target)
        else:
            raise SystemExit(f"Unsupported target: {target}")


if __name__ == "__main__":
    main()
