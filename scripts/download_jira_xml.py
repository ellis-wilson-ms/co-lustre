#!/usr/bin/env python3
"""
download_jira_xml.py — Download JIRA issues as XML files.

Fetches issues from the Whamcloud JIRA server and saves one XML file per
issue under OUTPUT_DIR/<PROJECT>/<KEY>.xml.

Two modes:

  range   Download <PROJECT>-<MIN>..<PROJECT>-<MAX>, skipping issues that
          already exist locally.  Use for the initial download.

  update  Incremental refresh.  Queries JIRA for every issue in the
          project updated since the last successful update (a per-project
          marker file), then downloads each one that is new or has
          changed since its local copy was downloaded.  This picks up
          both newly created issues and edits to existing ones (status,
          resolution, comments, ...).

          Without a marker, the oldest local XML file's modification
          time is used as the starting point, since every local copy is
          at least that fresh.

Downloads are written atomically and validated, so a failed request,
error page, or interstitial never replaces a good local copy.

Usage:
    ./download_jira_xml.py range LU 1 19947
    ./download_jira_xml.py update LU LUDOC
    ./download_jira_xml.py update LU --dry-run       # show what would change
    ./download_jira_xml.py update LU --since 2026-03-01

Defaults:
    OUTPUT_DIR = ../raw/jira/xml  (relative to this script)
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

JIRA_URL = "https://jira.whamcloud.com"
XML_URL = JIRA_URL + "/si/jira.issueviews:issue-xml/{key}/{key}.xml"
SEARCH_URL = JIRA_URL + "/rest/api/2/search"
SEARCH_PAGE_SIZE = 1000  # server-side maximum
PARALLEL = 4
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 15, 30]  # seconds
TIMEOUT = 60
USER_AGENT = "co-lustre-corpus/1.0 (+https://github.com/ellis-wilson-ms/co-lustre)"
MARKER_FILE = ".last_update"
# JQL dates are interpreted in the server's time zone; query from a day
# earlier than the marker so time zone differences cannot skip updates.
SINCE_MARGIN = timedelta(days=1)


def log(msg: str) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {msg}", flush=True)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    # JIRA answers requests for nonexistent issues with a redirect to an
    # HTML page; surface the 3xx status instead of following it.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def http_get(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with _opener.open(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


def download_issue(key: str, project_dir: Path, overwrite: bool) -> str:
    """Download one issue. Returns 'ok', 'exists', 'missing', or 'failed'."""
    outfile = project_dir / f"{key}.xml"
    if outfile.exists() and not overwrite:
        return "exists"

    url = XML_URL.format(key=key)
    for attempt in range(MAX_RETRIES + 1):
        try:
            status, body = http_get(url)
        except (urllib.error.URLError, OSError) as e:
            status, body = 0, str(e).encode()

        if status == 200 and b"<rss" in body[:4096]:
            fd, tmp = tempfile.mkstemp(dir=project_dir, prefix=f".{key}.", suffix=".tmp")
            with os.fdopen(fd, "wb") as f:
                f.write(body)
            os.replace(tmp, outfile)
            log(f"OK    {key}")
            return "ok"
        if (300 <= status < 400 or status in (403, 404)) and not overwrite:
            # Deleted, moved, or restricted issue in a range scan.
            log(f"SKIP  {key}  (HTTP {status})")
            return "missing"
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF[attempt])

    log(f"FAIL  {key}  (HTTP {status})")
    return "failed"


def run_downloads(keys: list[str], project_dir: Path, overwrite: bool, parallel: int) -> dict:
    project_dir.mkdir(parents=True, exist_ok=True)
    counts = {"ok": 0, "exists": 0, "missing": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        for result in pool.map(lambda k: download_issue(k, project_dir, overwrite), keys):
            counts[result] += 1
    return counts


def search_updated(project: str, since_date: str) -> list[tuple[str, datetime]]:
    """Return (key, updated) for every issue in project updated on/after since_date."""
    jql = f'project = "{project}" AND updated >= "{since_date}" ORDER BY key ASC'
    results = []
    start = 0
    while True:
        params = urllib.parse.urlencode({
            "jql": jql,
            "fields": "updated",
            "startAt": start,
            "maxResults": SEARCH_PAGE_SIZE,
        })
        status, body = http_get(f"{SEARCH_URL}?{params}")
        if status != 200:
            raise RuntimeError(f"JIRA search failed (HTTP {status}) for: {jql}")
        data = json.loads(body)
        for issue in data["issues"]:
            updated = datetime.strptime(issue["fields"]["updated"], "%Y-%m-%dT%H:%M:%S.%f%z")
            results.append((issue["key"], updated))
        start += len(data["issues"])
        if not data["issues"] or start >= data["total"]:
            return results


def read_marker(project_dir: Path) -> datetime | None:
    marker = project_dir / MARKER_FILE
    if marker.exists():
        return datetime.fromisoformat(marker.read_text().strip())
    return None


def oldest_local_mtime(project_dir: Path) -> datetime | None:
    mtimes = [p.stat().st_mtime for p in project_dir.glob("*.xml")]
    if not mtimes:
        return None
    return datetime.fromtimestamp(min(mtimes), tz=timezone.utc)


def is_stale(path: Path, updated: datetime) -> bool:
    if not path.exists():
        return True
    return updated.timestamp() > path.stat().st_mtime


def cmd_range(args) -> int:
    project_dir = args.output / args.project
    keys = [f"{args.project}-{i}" for i in range(args.min, args.max + 1)]
    log(f"Output directory: {project_dir}")
    log(f"Downloading {keys[0]}..{keys[-1]}  ({args.parallel} parallel); existing files are skipped")
    counts = run_downloads(keys, project_dir, overwrite=False, parallel=args.parallel)
    log(f"Done: {counts['ok']} downloaded, {counts['exists']} already present, "
        f"{counts['missing']} not found, {counts['failed']} failed.")
    return 1 if counts["failed"] else 0


def update_project(project: str, args) -> bool:
    project_dir = args.output / project

    if args.since:
        since = datetime.fromisoformat(args.since)
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        source = "--since"
    elif (since := read_marker(project_dir)) is not None:
        source = MARKER_FILE
    elif (since := oldest_local_mtime(project_dir)) is not None:
        source = "oldest local file"
    else:
        log(f"{project}: no local issues and no marker; run 'range' mode first.")
        return False

    since_date = (since - SINCE_MARGIN).strftime("%Y-%m-%d")
    query_started = datetime.now(timezone.utc)
    log(f"{project}: querying issues updated since {since_date} "
        f"(from {source}: {since.isoformat(timespec='seconds')})")
    updated = search_updated(project, since_date)

    stale = [key for key, ts in updated if is_stale(project_dir / f"{key}.xml", ts)]
    new = sum(1 for key in stale if not (project_dir / f"{key}.xml").exists())
    log(f"{project}: {len(updated)} updated upstream; {len(stale)} need download "
        f"({new} new, {len(stale) - new} changed)")

    if args.dry_run:
        for key in stale[:20]:
            print(f"    {key}")
        if len(stale) > 20:
            print(f"    ... and {len(stale) - 20} more")
        return True

    counts = run_downloads(stale, project_dir, overwrite=True, parallel=args.parallel)
    log(f"{project}: {counts['ok']} downloaded, {counts['failed']} failed")
    if counts["failed"]:
        log(f"{project}: marker not advanced; re-run to retry failures.")
        return False

    (project_dir / MARKER_FILE).write_text(query_started.isoformat(timespec="seconds") + "\n")
    return True


def cmd_update(args) -> int:
    log(f"Output directory: {args.output}")
    ok = True
    for project in args.projects:
        ok = update_project(project, args) and ok
    return 0 if ok else 1


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Download Whamcloud JIRA issues as XML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1],
    )
    parser.add_argument("--output", type=Path, default=script_dir.parent / "raw" / "jira" / "xml",
                        help="XML output directory (default: ../raw/jira/xml)")
    parser.add_argument("--parallel", type=int, default=PARALLEL,
                        help=f"concurrent downloads (default: {PARALLEL})")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_range = sub.add_parser("range", help="download a key range, skipping existing files")
    p_range.add_argument("project")
    p_range.add_argument("min", type=int)
    p_range.add_argument("max", type=int)
    p_range.set_defaults(func=cmd_range)

    p_update = sub.add_parser("update", help="download new and changed issues")
    p_update.add_argument("projects", nargs="+", metavar="PROJECT")
    p_update.add_argument("--since", help="override start date (YYYY-MM-DD or ISO 8601)")
    p_update.add_argument("--dry-run", action="store_true",
                          help="report what would be downloaded without downloading")
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
