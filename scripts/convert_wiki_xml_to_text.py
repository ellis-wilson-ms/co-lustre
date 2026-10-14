#!/usr/bin/env python3
"""
convert_wiki_xml_to_text.py — Split and convert Lustre wiki XML export.

Takes the full MediaWiki XML export (full_xml_download.xml) and:
  1. Splits it into individual XML files in wiki/xml/<Title>.xml
  2. Converts each page to clean plaintext in wiki/txt/<Title>.txt

The wikitext markup is stripped to produce readable, greppable text.
It also writes the original markup to wiki_in_wikitext/txt/<Title>.txt.

wiki_in_wikitext/ is where local page edits are made before they are
uploaded to the wiki.  Before writing anything, this script lists every
local wikitext page whose content would be replaced by the export and
requires interactive confirmation.  It refuses to run non-interactively
if any local page would change.

Usage:
    python3 convert_wiki_xml_to_text.py [RAW_DIR [PROCESSED_DIR]]

    RAW_DIR       defaults to ../raw/wiki       (relative to this script).
    PROCESSED_DIR defaults to ../processed/wiki  (relative to this script).
"""

import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


# MediaWiki namespace
MW_NS = "{http://www.mediawiki.org/xml/export-0.11/}"


def sanitize_filename(title: str) -> str:
    """Convert a wiki page title to a safe filename."""
    name = title.replace(' ', '_')
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(ch, '_')
    return name


def strip_wikitext(text: str) -> str:
    """Convert wikitext markup to readable plaintext."""
    if not text:
        return ""

    # Handle redirects
    if text.strip().startswith("#REDIRECT"):
        return text.strip()

    s = text

    # Remove HTML comments
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL)

    # Convert HTML entities
    s = html.unescape(s)

    # Strip <ref>...</ref> and <ref ... />
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<ref[^/]*/\s*>", "", s, flags=re.IGNORECASE)

    # Convert <br/>, <br>, <br /> to newlines
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)

    # Strip common HTML tags but keep content
    s = re.sub(r"</?(?:div|span|p|small|big|center|blockquote|sup|sub|u|s|strike|nowiki|code|tt|var|pre|syntaxhighlight|source)[^>]*>", "", s, flags=re.IGNORECASE)

    # Bold and italic
    s = re.sub(r"'{2,3}", "", s)

    # Wiki links: [[Page|display]] -> display, [[Page]] -> Page
    s = re.sub(r"\[\[[^\]]*\|([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)

    # External links: [http://url display] -> display (http://url)
    s = re.sub(r"\[(\S+)\s+([^\]]+)\]", r"\2 (\1)", s)
    # Bare external links: [http://url] -> http://url
    s = re.sub(r"\[(\S+)\]", r"\1", s)

    # Templates — remove simple ones, keep content of others
    # {{note|text}} -> text
    s = re.sub(r"\{\{[Nn]ote\|([^}]+)\}\}", r"Note: \1", s)
    # {{warning|text}} -> text
    s = re.sub(r"\{\{[Ww]arning\|([^}]+)\}\}", r"Warning: \1", s)
    # Remove remaining templates (may be multi-line)
    s = re.sub(r"\{\{[^}]*\}\}", "", s, flags=re.DOTALL)

    # Wiki tables — convert to readable format
    # Table start/end
    s = re.sub(r"^\{\|.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"^\|\}.*$", "", s, flags=re.MULTILINE)
    # Table row separator
    s = re.sub(r"^\|-.*$", "", s, flags=re.MULTILINE)
    # Header cells: ! text -> text
    s = re.sub(r"^!\s*", "", s, flags=re.MULTILINE)
    # Table cells: | text -> text
    s = re.sub(r"^\|\s*", "", s, flags=re.MULTILINE)

    # Headings: == Title == -> Title
    s = re.sub(r"^(={1,6})\s*(.*?)\s*\1\s*$", r"\2", s, flags=re.MULTILINE)

    # Bullet/numbered lists: preserve but clean up
    s = re.sub(r"^(\*+)", lambda m: "  " * (len(m.group(1)) - 1) + "- ", s, flags=re.MULTILINE)
    s = re.sub(r"^(#+)", lambda m: "  " * (len(m.group(1)) - 1) + "- ", s, flags=re.MULTILINE)
    # Definition lists
    s = re.sub(r"^;(.+)$", r"\1", s, flags=re.MULTILINE)
    s = re.sub(r"^:+\s*", "  ", s, flags=re.MULTILINE)

    # Categories
    s = re.sub(r"\[\[Category:[^\]]*\]\]", "", s, flags=re.IGNORECASE)

    # File/Image links
    s = re.sub(r"\[\[(?:File|Image):[^\]]*\]\]", "", s, flags=re.IGNORECASE)

    # Magic words
    s = re.sub(r"__[A-Z]+__", "", s)

    # Collapse excessive blank lines
    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


def build_page(page_el):
    """Extract a page's metadata and render its plaintext and wikitext files.

    Returns None for pages without a title.
    """
    title_el = page_el.find(f"{MW_NS}title")
    if title_el is None or not title_el.text:
        return None
    title = title_el.text
    safe_name = sanitize_filename(title)

    page_id_el = page_el.find(f"{MW_NS}id")
    revision = page_el.find(f"{MW_NS}revision")

    timestamp = ""
    contributor = ""
    wikitext = ""
    comment = ""

    if revision is not None:
        ts_el = revision.find(f"{MW_NS}timestamp")
        timestamp = ts_el.text if ts_el is not None and ts_el.text else ""

        contrib_el = revision.find(f"{MW_NS}contributor")
        if contrib_el is not None:
            uname_el = contrib_el.find(f"{MW_NS}username")
            contributor = uname_el.text if uname_el is not None and uname_el.text else ""

        text_el = revision.find(f"{MW_NS}text")
        wikitext = text_el.text if text_el is not None and text_el.text else ""

        comment_el = revision.find(f"{MW_NS}comment")
        comment = comment_el.text if comment_el is not None and comment_el.text else ""

    header = []
    header.append(f"Title:        {title}")
    header.append(f"URL:          https://wiki.lustre.org/{safe_name.replace(' ', '_')}")
    if page_id_el is not None and page_id_el.text:
        header.append(f"Page ID:      {page_id_el.text}")
    header.append(f"Last Updated: {timestamp}")
    header.append(f"Last Editor:  {contributor}")
    if comment:
        header.append(f"Edit Comment: {comment}")
    header.append("")

    plaintext = "\n".join(header + ["--- Content ---", strip_wikitext(wikitext), ""])
    markup = "\n".join(header + ["--- Content (MediaWiki markup) ---", wikitext, ""])

    return {
        "title": title,
        "safe_name": safe_name,
        "plaintext": plaintext,
        "wikitext": markup,
    }


def read_header_field(path: Path, field: str) -> str:
    """Return a 'Field: value' header value from a page file, or ''."""
    prefix = f"{field}:"
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("---"):
                    break
                if line.startswith(prefix):
                    return line[len(prefix):].strip()
    except OSError:
        pass
    return ""


def confirm_wikitext_overwrite(built_pages, wikitext_dir: Path):
    """List local wikitext pages the export would replace and require confirmation.

    Exits the program unless the user explicitly confirms.
    """
    changed = []
    for page in built_pages:
        path = wikitext_dir / f"{page['safe_name']}.txt"
        if path.exists() and path.read_text(encoding="utf-8") != page["wikitext"]:
            changed.append(path)

    export_names = {f"{p['safe_name']}.txt" for p in built_pages}
    local_only = sorted(p for p in wikitext_dir.glob("*.txt") if p.name not in export_names)

    if local_only:
        print(f"{len(local_only)} local wikitext page(s) are not in this export and "
              f"will be left untouched (no plaintext will be generated for them):")
        for path in local_only:
            print(f"    {path.name}")
        print()

    if not changed:
        print("No existing wikitext pages differ from the export; nothing local will be overwritten.\n")
        return

    print("=" * 78)
    print(f"WARNING: {len(changed)} page(s) in {wikitext_dir}")
    print("differ from the export and will be OVERWRITTEN with the exported version.")
    print("Any local edits not yet uploaded to the wiki will be lost.")
    print("=" * 78)
    for path in sorted(changed):
        editor = read_header_field(path, "Last Editor") or "?"
        updated = read_header_field(path, "Last Updated") or "?"
        print(f"    {path.name:<70}  {updated}  {editor}")
    print()
    print("Commit wiki_in_wikitext/ first so the overwritten content can be recovered with git.")

    if not sys.stdin.isatty():
        sys.stdout.flush()
        print("Refusing to overwrite without interactive confirmation (stdin is not a terminal).",
              file=sys.stderr)
        sys.exit(1)

    try:
        answer = input(f"Type 'overwrite' to replace these {len(changed)} page(s), anything else to abort: ")
    except EOFError:
        answer = ""
    if answer.strip() != "overwrite":
        print("Aborted; no files were written.")
        sys.exit(1)
    print()


def process_full_export(raw_dir: Path, processed_dir: Path):
    """Parse the full export and write individual XML + text files."""
    full_xml = raw_dir / "full_xml_download.xml"
    xml_dir = raw_dir / "xml"
    txt_dir = processed_dir / "txt"
    wikitext_dir = processed_dir.parent / "wiki_in_wikitext" / "txt"

    if not full_xml.exists():
        print(f"Error: {full_xml} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {full_xml} ...")
    tree = ET.parse(full_xml)
    root = tree.getroot()

    # Extract the siteinfo for re-wrapping individual XML files
    siteinfo = root.find(f"{MW_NS}siteinfo")
    mediawiki_attribs = dict(root.attrib)

    pages = root.findall(f"{MW_NS}page")
    print(f"Found {len(pages)} pages.\n")

    built = []
    for page_el in pages:
        page = build_page(page_el)
        if page is not None:
            built.append((page_el, page))

    if wikitext_dir.is_dir():
        confirm_wikitext_overwrite([page for _, page in built], wikitext_dir)

    xml_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    wikitext_dir.mkdir(parents=True, exist_ok=True)

    split_count = 0
    convert_count = 0

    for page_el, page in built:
        title = page["title"]
        safe_name = page["safe_name"]

        # --- Write individual XML ---
        xml_path = xml_dir / f"{safe_name}.xml"
        # Build a standalone mediawiki XML doc for this page
        new_root = ET.Element("mediawiki", mediawiki_attribs)
        if siteinfo is not None:
            new_root.append(siteinfo)
        new_root.append(page_el)

        ind_tree = ET.ElementTree(new_root)
        ET.indent(ind_tree, space="  ")
        ind_tree.write(str(xml_path), encoding="unicode", xml_declaration=True)
        split_count += 1

        (txt_dir / f"{safe_name}.txt").write_text(page["plaintext"], encoding="utf-8")
        (wikitext_dir / f"{safe_name}.txt").write_text(page["wikitext"], encoding="utf-8")

        convert_count += 1
        print(f"OK  {title}")

    print(f"\nDone: {split_count} XML files, {convert_count} text files, {convert_count} wikitext files.")
    print(f"XML:      {xml_dir}")
    print(f"TXT:      {txt_dir}")
    print(f"Wikitext: {wikitext_dir}")


def main():
    script_dir = Path(__file__).resolve().parent
    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir.parent / "raw" / "wiki"
    processed_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else script_dir.parent / "processed" / "wiki"
    process_full_export(raw_dir, processed_dir)


if __name__ == "__main__":
    main()
