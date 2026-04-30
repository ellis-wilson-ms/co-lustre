#!/usr/bin/env python3
"""
download_gerrit_json.py — Download Gerrit changes as JSON files.

Fetches all changes for fs/lustre-release from review.whamcloud.com
via the REST API.  Saves one JSON file per change in the output
directory.

Supports incremental updates: on subsequent runs, only changes updated
since the last successful download are fetched (based on a stored
timestamp marker).

Usage:
    # Full initial download (all changes, paginated):
    ./download_gerrit_json.py

    # Incremental update (only recently modified changes):
    ./download_gerrit_json.py --update

    # Force full re-download:
    ./download_gerrit_json.py --full

    # Custom output directory:
    ./download_gerrit_json.py --output /tmp/gerrit_json

Defaults:
    OUTPUT_DIR = ../raw/gerrit/json  (relative to this script)
"""

import argparse
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GERRIT_URL = "https://review.whamcloud.com"
PROJECT = "fs/lustre-release"
BATCH_SIZE = 100  # keep responses manageable (full messages can be huge)
PARALLEL_NONE = 1  # sequential fetches (polite to the server)
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

# Options to request from Gerrit — gives us the data we need without
# pulling enormous diff content.
QUERY_OPTIONS = [
    "CURRENT_REVISION",
    "CURRENT_COMMIT",
    "DETAILED_ACCOUNTS",
    "MESSAGES",
    "DETAILED_LABELS",
]

MARKER_FILE = ".last_update"
MAX_RETRIES = 5
RETRY_BACKOFF = [5, 15, 30, 60, 120]  # seconds between retries


def gerrit_api_get(endpoint: str, params: dict | None = None) -> str:
    """Make a GET request to the Gerrit REST API, return the raw body.

    Retries on transient network errors (timeouts, incomplete reads,
    connection resets) with exponential backoff.
    """
    url = f"{GERRIT_URL}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = resp.read().decode("utf-8")
            break  # success
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                log(f"  HTTP {e.code}, retrying in {wait}s "
                    f"(attempt {attempt + 1}/{MAX_RETRIES}) ...")
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code} for {url}", file=sys.stderr)
            raise
        except (urllib.error.URLError, ConnectionError, OSError,
                http.client.IncompleteRead) as e:
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                log(f"  Network error: {e}, retrying in {wait}s "
                    f"(attempt {attempt + 1}/{MAX_RETRIES}) ...")
                time.sleep(wait)
                continue
            print(f"  Network error for {url}: {e}", file=sys.stderr)
            raise

    # Gerrit prefixes JSON responses with )]}' to prevent XSSI
    if body.startswith(")]}'"):
        body = body[4:].lstrip("\n")
    return body


def query_changes(query: str, start: int = 0) -> list[dict]:
    """Query changes from Gerrit, returning the parsed JSON list."""
    params = {
        "q": query,
        "n": str(BATCH_SIZE),
        "S": str(start),
        "o": QUERY_OPTIONS,
    }
    body = gerrit_api_get("/changes/", params)
    return json.loads(body)


def fetch_and_save_all_changes(query: str, output_dir: Path) -> int:
    """Paginate through all changes, saving each batch immediately.

    Returns the total number of changes saved.
    """
    total = 0
    start = 0
    latest_updated = None

    while True:
        log(f"Fetching changes {start}..{start + BATCH_SIZE} ...")
        batch = query_changes(query, start=start)

        if not batch:
            break

        # Save each change immediately
        for change in batch:
            save_change(change, output_dir)
            updated = change.get("updated", "")
            if updated and (latest_updated is None or updated > latest_updated):
                latest_updated = updated

        # Update marker after each batch so we can resume
        if latest_updated:
            write_marker(output_dir, latest_updated)

        total += len(batch)
        log(f"  got {len(batch)} changes, saved (total: {total})")

        # Check if there are more results
        if batch[-1].get("_more_changes"):
            start += len(batch)
            time.sleep(RATE_LIMIT_DELAY)
        else:
            break

    if latest_updated:
        log(f"Final marker: {latest_updated}")

    return total


def save_change(change: dict, output_dir: Path) -> None:
    """Save a single change as a JSON file."""
    number = change.get("_number")
    if number is None:
        return
    outfile = output_dir / f"{number}.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(change, f, indent=2, ensure_ascii=False)


def read_marker(output_dir: Path) -> str | None:
    """Read the last-update marker timestamp, or None if not present."""
    marker = output_dir / MARKER_FILE
    if marker.is_file():
        return marker.read_text().strip()
    return None


def write_marker(output_dir: Path, timestamp: str) -> None:
    """Write the last-update marker."""
    marker = output_dir / MARKER_FILE
    marker.write_text(timestamp + "\n")


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts}  {msg}", flush=True)


def compute_latest_updated(changes: list[dict]) -> str | None:
    """Find the most recent 'updated' timestamp across all changes."""
    latest = None
    for c in changes:
        updated = c.get("updated", "")
        if updated and (latest is None or updated > latest):
            latest = updated
    return latest


def main():
    parser = argparse.ArgumentParser(
        description="Download Gerrit changes as JSON files."
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory for JSON files "
             "(default: ../raw/gerrit/json relative to script)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--update", "-u",
        action="store_true",
        help="Incremental update: only fetch changes updated since last run",
    )
    mode.add_argument(
        "--full", "-f",
        action="store_true",
        help="Force a full download of all changes",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    output_dir = Path(args.output) if args.output else (
        script_dir.parent / "raw" / "gerrit" / "json"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine query
    base_query = f"project:{PROJECT}"

    if args.update:
        marker = read_marker(output_dir)
        if marker:
            # Gerrit 'after' uses date format YYYY-MM-DD or full timestamp.
            # Trim to date for safety (server timezone quirks).
            after_date = marker[:10]  # YYYY-MM-DD
            query = f"{base_query} after:{after_date}"
            log(f"Incremental update: changes after {after_date}")
        else:
            log("No marker file found — falling back to full download.")
            query = base_query
    else:
        query = base_query
        if not args.full:
            # Default: auto-detect — if marker exists, do incremental
            marker = read_marker(output_dir)
            if marker:
                after_date = marker[:10]
                query = f"{base_query} after:{after_date}"
                log(f"Auto-detected previous run. Incremental: after {after_date}")
                log("  (use --full to force complete re-download)")
            else:
                log("No previous run detected — full download.")

    log(f"Query: {query}")
    log(f"Output: {output_dir}")

    total = fetch_and_save_all_changes(query, output_dir)

    if total == 0:
        log("No changes found.")
    else:
        log(f"Done: {total} changes saved to {output_dir}")


if __name__ == "__main__":
    main()
