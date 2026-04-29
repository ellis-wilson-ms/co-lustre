#!/usr/bin/env python3
"""
convert_jira_xml_to_text.py — Convert JIRA XML exports to plain text + TSV index.

Walks the xml/ tree for downloaded JIRA XML files, converts each to a
clean plain-text file under txt/<PROJECT>/, and maintains a TSV index
at jira/index.tsv.

Only processes files whose XML source is newer than the existing text
file (or where no text file exists yet).

Usage:
    ./convert_jira_xml_to_text.py [RAW_DIR [PROCESSED_DIR]]

    RAW_DIR       defaults to ../raw/jira       (relative to this script).
    PROCESSED_DIR defaults to ../processed/jira  (relative to this script).

    Expects XML files at RAW_DIR/xml/<PROJECT>/<KEY>.xml
    Writes  text files to PROCESSED_DIR/txt/<PROJECT>/<KEY>.txt
    Writes  index to     PROCESSED_DIR/index.tsv
"""

import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def strip_html(text: str) -> str:
    """Unescape HTML entities and strip HTML tags, producing readable text."""
    if not text:
        return ""
    # Unescape HTML entities (may be double-encoded in JIRA XML)
    text = html.unescape(text)
    text = html.unescape(text)  # second pass for double-encoding
    # Replace <br/> and <br> with newlines before stripping tags
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    # Replace </p> and </li> with newline to preserve paragraph breaks
    text = re.sub(r"</(?:p|li|div|tr)>", "\n", text, flags=re.IGNORECASE)
    # Strip all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse runs of blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_or_empty(element, tag: str) -> str:
    """Get the text content of a child element, or '' if missing."""
    child = element.find(tag)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def parse_issue(xml_path: Path) -> dict | None:
    """Parse a single JIRA XML file and return a dict of fields."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return None

    root = tree.getroot()
    item = root.find(".//item")
    if item is None:
        return None

    # --- core fields ---
    key = text_or_empty(item, "key")
    if not key:
        return None

    info = {
        "key": key,
        "summary": text_or_empty(item, "summary"),
        "link": text_or_empty(item, "link"),
        "type": text_or_empty(item, "type"),
        "priority": text_or_empty(item, "priority"),
        "status": text_or_empty(item, "status"),
        "resolution": text_or_empty(item, "resolution"),
        "assignee": text_or_empty(item, "assignee"),
        "reporter": text_or_empty(item, "reporter"),
        "created": text_or_empty(item, "created"),
        "updated": text_or_empty(item, "updated"),
        "resolved": text_or_empty(item, "resolved"),
        "description": strip_html(text_or_empty(item, "description")),
        "environment": strip_html(text_or_empty(item, "environment")),
    }

    # --- labels ---
    labels_el = item.find("labels")
    if labels_el is not None:
        info["labels"] = [l.text for l in labels_el.findall("label") if l.text]
    else:
        info["labels"] = []

    # --- issue links ---
    links = []
    for linktype in item.findall(".//issuelinktype"):
        link_name = text_or_empty(linktype, "name")
        for direction_tag in ("outwardlinks", "inwardlinks"):
            direction = linktype.find(direction_tag)
            if direction is None:
                continue
            desc = direction.get("description", direction_tag)
            for issuelink in direction.findall("issuelink"):
                linked_key = text_or_empty(issuelink, "issuekey")
                if linked_key:
                    links.append(f"{link_name}: {desc} {linked_key}")
    info["links"] = links

    # --- comments (preserve chronological order) ---
    comments = []
    for c in item.findall(".//comment"):
        author = c.get("author", "unknown")
        created = c.get("created", "")
        body = strip_html(c.text or "")
        comments.append({"author": author, "created": created, "body": body})
    info["comments"] = comments

    # --- attachments ---
    attachments = []
    for a in item.findall(".//attachment"):
        attachments.append(a.get("name", ""))
    info["attachments"] = [a for a in attachments if a]

    return info


def format_text(info: dict) -> str:
    """Render the parsed issue dict as clean plain text."""
    lines = []

    lines.append(f"Key:        {info['key']}")
    lines.append(f"Summary:    {info['summary']}")
    lines.append(f"Link:       {info['link']}")
    lines.append(f"Type:       {info['type']}")
    lines.append(f"Priority:   {info['priority']}")
    lines.append(f"Status:     {info['status']}")
    lines.append(f"Resolution: {info['resolution']}")
    lines.append(f"Assignee:   {info['assignee']}")
    lines.append(f"Reporter:   {info['reporter']}")
    lines.append(f"Created:    {info['created']}")
    lines.append(f"Updated:    {info['updated']}")
    if info["resolved"]:
        lines.append(f"Resolved:   {info['resolved']}")
    if info["labels"]:
        lines.append(f"Labels:     {', '.join(info['labels'])}")
    if info["links"]:
        lines.append(f"Links:      {'; '.join(info['links'])}")
    if info["attachments"]:
        lines.append(f"Attachments: {', '.join(info['attachments'])}")

    if info["environment"]:
        lines.append("")
        lines.append("--- Environment ---")
        lines.append(info["environment"])

    if info["description"]:
        lines.append("")
        lines.append("--- Description ---")
        lines.append(info["description"])

    for c in info["comments"]:
        lines.append("")
        lines.append(f"--- Comment ({c['author']}, {c['created']}) ---")
        lines.append(c["body"])

    lines.append("")  # trailing newline
    return "\n".join(lines)


def needs_conversion(xml_path: Path, txt_path: Path) -> bool:
    """Return True if the text file is missing or older than the XML."""
    if not txt_path.exists():
        return True
    return xml_path.stat().st_mtime > txt_path.stat().st_mtime


def main():
    script_dir = Path(__file__).resolve().parent
    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir.parent / "raw" / "jira"
    processed_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else script_dir.parent / "processed" / "jira"

    xml_root = raw_dir / "xml"
    txt_root = processed_dir / "txt"
    index_path = processed_dir / "index.tsv"

    if not xml_root.is_dir():
        print(f"Error: XML directory not found: {xml_root}", file=sys.stderr)
        sys.exit(1)

    # Collect all XML files across all project subdirectories
    xml_files = sorted(xml_root.rglob("*.xml"))
    if not xml_files:
        print("No XML files found.")
        return

    converted = 0
    skipped = 0
    failed = 0
    index_rows = []

    for xml_path in xml_files:
        # Derive project from parent dir name (e.g. xml/LU/LU-9962.xml -> LU)
        project = xml_path.parent.name
        stem = xml_path.stem  # e.g. LU-9962
        txt_dir = txt_root / project
        txt_path = txt_dir / f"{stem}.txt"

        if not needs_conversion(xml_path, txt_path):
            # Still need to read for index, but don't rewrite text
            info = parse_issue(xml_path)
            if info:
                index_rows.append(info)
            skipped += 1
            continue

        info = parse_issue(xml_path)
        if info is None:
            print(f"FAIL  {stem}  (parse error)")
            failed += 1
            continue

        txt_dir.mkdir(parents=True, exist_ok=True)
        txt_path.write_text(format_text(info), encoding="utf-8")
        index_rows.append(info)
        converted += 1
        print(f"OK    {stem}")

    # Write the TSV index (always regenerated fully for consistency)
    TSV_HEADER = "key\tstatus\tresolution\tpriority\ttype\tassignee\tsummary"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(TSV_HEADER + "\n")
        for info in sorted(index_rows, key=lambda r: r["key"]):
            row = "\t".join([
                info["key"],
                info["status"],
                info["resolution"],
                info["priority"],
                info["type"],
                info["assignee"],
                info["summary"],
            ])
            f.write(row + "\n")

    print(f"\nDone: {converted} converted, {skipped} up-to-date, {failed} failed.")
    print(f"Index: {index_path}  ({len(index_rows)} issues)")


if __name__ == "__main__":
    main()
