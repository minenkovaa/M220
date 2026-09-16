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


def empty_link_label(node) -> str | None:
    if node.tag.lower() != "a":
        return None
    if node.get("aria-label") is not None:
        return None
    if node.text_content().strip():
        return None
    title = (node.get("title") or "").strip()
    if title:
        return title
    href = (node.get("href") or "").strip()
    if href:
        return f"Link to {href}"
    return None


def image_alt_text(node) -> str | None:
    if node.tag.lower() != "img":
        return None
    if node.get("alt") is not None:
        return None
    title = (node.get("title") or "").strip()
    if title:
        return title
    src = (node.get("src") or "").strip()
    if src:
        name = Path(src).stem.replace("-", " ")
        if name:
            return name
    return "Image"


def add_labels_to_html(path: Path) -> None:
    tree = html.parse(str(path))
    for node in tree.xpath(".//*"):
        if should_label(node):
            if node.get("aria-label") is None:
                text = label_text(node)
                if text:
                    node.set("aria-label", text)
            continue

        if node.tag.lower() == "a":
            label = empty_link_label(node)
            if label:
                node.set("aria-label", label)
            continue

        if node.tag.lower() == "img":
            alt = image_alt_text(node)
            if alt:
                node.set("alt", alt)

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
