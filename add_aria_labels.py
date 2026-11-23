#!/usr/bin/env python3
"""Apply basic accessibility improvements to generated HTML."""

from __future__ import annotations

from pathlib import Path
import argparse

from lxml import html

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def tag_name(node) -> str:
    tag = node.tag
    return tag.lower() if isinstance(tag, str) else ""


def label_text(node) -> str:
    text = "".join(node.itertext())
    return " ".join(text.split())


def should_label(node) -> bool:
    return tag_name(node) in HEADING_TAGS


def empty_link_label(node) -> str | None:
    if tag_name(node) != "a":
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
    if tag_name(node) != "img":
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
    parser = html.HTMLParser(encoding="utf-8")
    tree = html.parse(str(path), parser=parser)
    root = tree.getroot()

    html_node = root if tag_name(root) == "html" else root.find(".//html")
    if html_node is not None and not html_node.get("lang"):
        html_node.set("lang", "en")

    body = root if tag_name(root) == "body" else root.find(".//body")
    if body is not None:
        main = root.xpath(".//*[translate(@role, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='main'] | .//main")
        target = main[0] if main else body
        target_id = target.get("id")
        if not target_id:
            target_id = "main-content"
            target.set("id", target_id)

        head = root.find(".//head")
        if head is not None:
            style = head.find(".//style[@data-accessibility='skip-link']")
            if style is None:
                style = html.Element("style", {"data-accessibility": "skip-link"})
                style.text = (
                    ".skip-link{position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden}"
                    ".skip-link:focus{left:1em;top:1em;width:auto;height:auto;z-index:10000;padding:.5em 1em;"
                    "background:#fff;color:#000;border:2px solid #000}"
                )
                head.append(style)

        skip = body.xpath("./a[contains(concat(' ', normalize-space(@class), ' '), ' skip-link ')]")
        if not skip:
            skip_link = html.Element("a", {"href": f"#{target_id}", "class": "skip-link"})
            skip_link.text = "Skip to main content"
            body.insert(0, skip_link)

    for table in tree.xpath(".//table"):
        for row_index, row in enumerate(table.xpath("./thead/tr | ./tbody/tr | ./tr")[:1]):
            for header in row.xpath("./th | ./td"):
                header.tag = "th"
                header.set("scope", "col")
        for header in table.xpath(".//thead//th | .//tr/th"):
            if not header.get("scope"):
                header.set("scope", "col")

    for node in tree.xpath(".//*"):
        if should_label(node):
            if node.get("aria-label") is not None:
                del node.attrib["aria-label"]
            continue

        if tag_name(node) == "a":
            label = empty_link_label(node)
            if label:
                node.set("aria-label", label)
            continue

        if tag_name(node) == "img":
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
