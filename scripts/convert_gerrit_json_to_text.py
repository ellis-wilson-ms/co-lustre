#!/usr/bin/env python3
"""
convert_gerrit_json_to_text.py — Convert Gerrit JSON exports to plain text + TSV index.

Reads downloaded Gerrit change JSON files, converts each to a clean
plain-text file, and maintains a TSV index.

Only processes files whose JSON source is newer than the existing text
file (or where no text file exists yet).

Usage:
    ./convert_gerrit_json_to_text.py [RAW_DIR [PROCESSED_DIR]]

    RAW_DIR       defaults to ../raw/gerrit       (relative to this script).
    PROCESSED_DIR defaults to ../processed/gerrit  (relative to this script).

    Expects JSON files at RAW_DIR/json/<NUMBER>.json
    Writes  text files to PROCESSED_DIR/txt/<NUMBER>.txt       (filtered)
    Writes  text files to PROCESSED_DIR/txt_full/<NUMBER>.txt  (unfiltered)
    Writes  index to     PROCESSED_DIR/index.tsv
"""

import json
import os
import re
import sys
from pathlib import Path


def safe_str(value) -> str:
    """Convert a value to a clean string, handling None."""
    if value is None:
        return ""
    return str(value).strip()


def account_name(acct: dict | None) -> str:
    """Extract a display name from a Gerrit account dict."""
    if not acct:
        return "unknown"
    return acct.get("name") or acct.get("username") or acct.get("email", "unknown")


def format_labels(labels: dict) -> list[str]:
    """Format label/vote summary from Gerrit labels dict."""
    lines = []
    for label_name, label_info in sorted(labels.items()):
        votes = []
        for reviewer in label_info.get("all", []):
            value = reviewer.get("value")
            if value and value != 0:
                name = account_name(reviewer)
                sign = "+" if value > 0 else ""
                votes.append(f"{name}: {sign}{value}")
        # Also check top-level approved/rejected/recommended/disliked
        if label_info.get("approved"):
            name = account_name(label_info["approved"])
            if not any(name in v for v in votes):
                votes.append(f"{name}: approved")
        if label_info.get("rejected"):
            name = account_name(label_info["rejected"])
            if not any(name in v for v in votes):
                votes.append(f"{name}: rejected")

        if votes:
            lines.append(f"  {label_name}: {'; '.join(votes)}")
        else:
            lines.append(f"  {label_name}: (no votes)")
    return lines


def format_reviewers(reviewers: dict) -> list[str]:
    """Format reviewer lists."""
    lines = []
    for role, people in sorted(reviewers.items()):
        names = []
        for person in people:
            # Skip service accounts in reviewer list for readability
            tags = person.get("tags", [])
            if "SERVICE_USER" in tags:
                continue
            names.append(account_name(person))
        if names:
            lines.append(f"  {role}: {', '.join(names)}")
    return lines


def format_messages(messages: list[dict], include_bot_messages: bool = False) -> list[str]:
    """Format change messages (review comments, patch set uploads, etc.).

    By default, filters out repetitive bot messages (Maloo test results,
    checkpatch, gerrit janitor) to keep the text focused on human review
    content.  Set include_bot_messages=True to include everything.
    """
    BOT_USERNAMES = {
        "jenkins", "maloo", "hpdd-checkpatch", "lgerritjanitor",
        "smatchreview", "autotest",
    }

    lines = []
    for msg in messages:
        author = msg.get("author", {})
        username = author.get("username", "")
        name = account_name(author)
        date = safe_str(msg.get("date", ""))
        body = safe_str(msg.get("message", ""))
        tag = msg.get("tag", "")

        if not body:
            continue

        # Filter bot messages unless requested
        if not include_bot_messages and username in BOT_USERNAMES:
            # Keep short bot messages (< 200 chars) that indicate
            # important state changes (build success/failure, vote)
            if len(body) > 200:
                continue

        lines.append("")
        lines.append(f"--- Message ({name}, {date}) ---")
        lines.append(body)

    return lines


def parse_change(json_path: Path) -> dict | None:
    """Parse a single Gerrit change JSON file and return a dict of fields."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    number = data.get("_number")
    if number is None:
        return None

    # Extract commit message from current revision
    commit_message = ""
    revisions = data.get("revisions", {})
    for rev_hash, rev_info in revisions.items():
        commit_obj = rev_info.get("commit", {})
        commit_message = commit_obj.get("message", "")
        break  # only one key in CURRENT_REVISION mode

    info = {
        "number": number,
        "change_id": safe_str(data.get("change_id")),
        "project": safe_str(data.get("project")),
        "branch": safe_str(data.get("branch")),
        "topic": safe_str(data.get("topic")),
        "hashtags": data.get("hashtags", []),
        "subject": safe_str(data.get("subject")),
        "status": safe_str(data.get("status")),
        "owner": account_name(data.get("owner")),
        "created": safe_str(data.get("created")),
        "updated": safe_str(data.get("updated")),
        "submit_type": safe_str(data.get("submit_type")),
        "insertions": data.get("insertions", 0),
        "deletions": data.get("deletions", 0),
        "total_comment_count": data.get("total_comment_count", 0),
        "unresolved_comment_count": data.get("unresolved_comment_count", 0),
        "current_revision_number": data.get("current_revision_number", 0),
        "commit_message": commit_message,
        "labels": data.get("labels", {}),
        "reviewers": data.get("reviewers", {}),
        "messages": data.get("messages", []),
    }

    return info


def format_text(info: dict, include_bot_messages: bool = False) -> str:
    """Render the parsed change dict as clean plain text."""
    lines = []
    number = info["number"]

    lines.append(f"Change:     {number}")
    lines.append(f"Subject:    {info['subject']}")
    lines.append(f"Link:       {GERRIT_URL}/c/{info['project']}/+/{number}")
    lines.append(f"Change-Id:  {info['change_id']}")
    lines.append(f"Project:    {info['project']}")
    lines.append(f"Branch:     {info['branch']}")
    lines.append(f"Status:     {info['status']}")
    lines.append(f"Owner:      {info['owner']}")
    lines.append(f"Created:    {info['created']}")
    lines.append(f"Updated:    {info['updated']}")
    lines.append(f"Patch Set:  {info['current_revision_number']}")
    lines.append(f"Insertions: +{info['insertions']}")
    lines.append(f"Deletions:  -{info['deletions']}")
    lines.append(f"Comments:   {info['total_comment_count']} "
                 f"({info['unresolved_comment_count']} unresolved)")

    if info["topic"]:
        lines.append(f"Topic:      {info['topic']}")
    if info["hashtags"]:
        lines.append(f"Hashtags:   {', '.join(info['hashtags'])}")

    # Labels / votes
    if info["labels"]:
        lines.append("")
        lines.append("--- Labels ---")
        lines.extend(format_labels(info["labels"]))

    # Reviewers
    if info["reviewers"]:
        reviewer_lines = format_reviewers(info["reviewers"])
        if reviewer_lines:
            lines.append("")
            lines.append("--- Reviewers ---")
            lines.extend(reviewer_lines)

    # Commit message
    if info["commit_message"]:
        lines.append("")
        lines.append("--- Commit Message ---")
        lines.append(info["commit_message"].strip())

    # Messages (review history)
    if info["messages"]:
        msg_lines = format_messages(
            info["messages"],
            include_bot_messages=include_bot_messages,
        )
        if msg_lines:
            lines.append("")
            lines.append("--- Review History ---")
            lines.extend(msg_lines)

    lines.append("")  # trailing newline
    return "\n".join(lines)


GERRIT_URL_CONST = "https://review.whamcloud.com"


def needs_conversion(json_path: Path, txt_path: Path) -> bool:
    """Return True if the text file is missing or older than the JSON."""
    if not txt_path.exists():
        return True
    return json_path.stat().st_mtime > txt_path.stat().st_mtime


def main():
    script_dir = Path(__file__).resolve().parent
    raw_dir = (
        Path(sys.argv[1]) if len(sys.argv) > 1
        else script_dir.parent / "raw" / "gerrit"
    )
    processed_dir = (
        Path(sys.argv[2]) if len(sys.argv) > 2
        else script_dir.parent / "processed" / "gerrit"
    )

    json_root = raw_dir / "json"
    txt_root = processed_dir / "txt"
    txt_full_root = processed_dir / "txt_full"
    index_path = processed_dir / "index.tsv"

    if not json_root.is_dir():
        print(f"Error: JSON directory not found: {json_root}", file=sys.stderr)
        sys.exit(1)

    # Collect all JSON files (skip marker file)
    json_files = sorted(
        p for p in json_root.glob("*.json")
        if p.stem.isdigit()
    )
    if not json_files:
        print("No JSON files found.")
        return

    converted = 0
    skipped = 0
    failed = 0
    index_rows = []

    for json_path in json_files:
        stem = json_path.stem  # e.g. 5200
        txt_path = txt_root / f"{stem}.txt"
        txt_full_path = txt_full_root / f"{stem}.txt"

        if (not needs_conversion(json_path, txt_path)
                and not needs_conversion(json_path, txt_full_path)):
            # Still need to read for index, but don't rewrite text
            info = parse_change(json_path)
            if info:
                index_rows.append(info)
            skipped += 1
            continue

        info = parse_change(json_path)
        if info is None:
            print(f"FAIL  {stem}  (parse error)")
            failed += 1
            continue

        # Filtered version (bot messages >200 chars dropped)
        txt_root.mkdir(parents=True, exist_ok=True)
        txt_path.write_text(format_text(info), encoding="utf-8")

        # Full version (all messages, no filtering)
        txt_full_root.mkdir(parents=True, exist_ok=True)
        txt_full_path.write_text(
            format_text(info, include_bot_messages=True), encoding="utf-8"
        )

        index_rows.append(info)
        converted += 1
        if converted % 500 == 0:
            print(f"  ... {converted} converted so far")

    # Write the TSV index (always regenerated fully for consistency)
    processed_dir.mkdir(parents=True, exist_ok=True)
    TSV_HEADER = (
        "number\tstatus\tbranch\towner\tpatch_set\t"
        "insertions\tdeletions\tsubject"
    )
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(TSV_HEADER + "\n")
        for info in sorted(index_rows, key=lambda r: r["number"]):
            row = "\t".join([
                str(info["number"]),
                info["status"],
                info["branch"],
                info["owner"],
                str(info["current_revision_number"]),
                str(info["insertions"]),
                str(info["deletions"]),
                info["subject"],
            ])
            f.write(row + "\n")

    print(f"\nDone: {converted} converted, {skipped} up-to-date, {failed} failed.")
    print(f"Index: {index_path}  ({len(index_rows)} changes)")


# Used by format_text
GERRIT_URL = GERRIT_URL_CONST

if __name__ == "__main__":
    main()
