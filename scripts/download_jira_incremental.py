#!/usr/bin/env python3
"""
download_jira_incremental.py — Incrementally download/refresh JIRA issues as XML.

Keeps the local raw/jira/xml/<PROJECT>/<KEY>.xml corpus current WITHOUT
re-fetching all ~20k issues and without hammering the shared JIRA server.

Unlike download_jira_xml.sh (which brute-forces an ID range and skips any
issue already on disk — so changed issues are never refreshed), this script:

  * uses JIRA's search-XML view with a JQL "updated >= <date>" query to find
    issues that are NEW *or have CHANGED* since the last run, then writes only
    those — refreshing stale ones (an issue that has since closed gets updated).
  * is polite: a single search request usually returns every changed issue, so
    there are effectively zero per-issue calls; everything is sequential with a
    0.5s delay and exponential backoff on 429/5xx (mirrors download_gerrit_json.py).

A timestamp marker at raw/jira/.last_update tracks the last successful run.
It is advanced to the run-start date ONLY on success; a one-day query overlap
means an issue updated mid-run is never lost (re-fetching is an idempotent
file overwrite).

If the search-XML endpoint is unavailable (e.g. it requires authentication on
this server), the script degrades to a bounded upward ID probe that discovers
NEW issues only (it cannot refresh changed ones) and stops after a run of misses.

Usage:
    # Incremental refresh (auto-detects marker; the normal cron/manual case):
    ./download_jira_incremental.py

    # Preflight + print the plan without fetching anything:
    ./download_jira_incremental.py --dry-run

    # Smoke test: fetch at most N issues:
    ./download_jira_incremental.py --max-issues 5

    # Ignore the marker and look back from a bootstrap date:
    ./download_jira_incremental.py --full --bootstrap-date 2026-04-01

Defaults:
    Jira dir = ../raw/jira  (relative to this script); marker + xml/ live here.
"""

# Defer annotation evaluation so the `X | None` type hints below also work on
# Python 3.9 (the system default on some hosts), not just 3.10+.
from __future__ import annotations

import argparse
import http.client
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

JIRA_URL = "https://jira.whamcloud.com"
PROJECTS = ["LU", "LUDOC"]

# Polite-to-the-server knobs (same ethos as download_gerrit_json.py).
RATE_LIMIT_DELAY = 0.5  # seconds between requests / pages
MAX_RETRIES = 5
RETRY_BACKOFF = [5, 15, 30, 60, 120]  # seconds between retries
TEMP_MAX = 100  # issues per search page
MAX_SEARCH_PAGES = 1000  # runaway backstop (>50k issues; far above the corpus)

MARKER_FILE = ".last_update"
PROBE_MISS_LIMIT = 20  # consecutive misses before a probe gives up (fallback)
BOOTSTRAP_LOOKBACK_DAYS = 30  # used when no marker exists and no date given


# ── logging (matches download_gerrit_json.py) ────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts}  {msg}", flush=True)


# ── HTTP with retry/backoff (mirrors gerrit_api_get) ─────────────────────

def http_get(url: str, timeout: int = 300) -> tuple[int, bytes]:
    """GET *url*, returning (status_code, body_bytes).

    Retries transient failures (429/5xx, network errors) with exponential
    backoff.  Non-retryable HTTP errors (404/401/403/...) are RETURNED, not
    raised, so callers (the ID probe) can treat them as a miss.
    """
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            url, headers={"Accept": "application/xml, text/xml, */*"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.getcode(), resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                log(f"  HTTP {e.code}, retrying in {wait}s "
                    f"(attempt {attempt + 1}/{MAX_RETRIES}) ...")
                time.sleep(wait)
                continue
            # Non-retryable — hand the code + error body back to the caller.
            try:
                body = e.read()
            except Exception:
                body = b""
            return e.code, body
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
    raise RuntimeError("retry loop exhausted")  # unreachable


# ── XML parsing / validation ─────────────────────────────────────────────

def parse_rss(body: bytes):
    """Return the root <rss> Element if *body* is well-formed issue RSS.

    Returns None for parse errors or non-RSS roots — which is exactly how an
    HTML login/error page (served with HTTP 200) is rejected.
    """
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None
    if root.tag != "rss":
        return None
    return root


def item_key_project(item) -> tuple[str | None, str | None]:
    """Extract (KEY, PROJECT) from an <item>, e.g. ("LU-9", "LU")."""
    key_elem = item.find("key")
    key = key_elem.text.strip() if (key_elem is not None and key_elem.text) else None
    proj_elem = item.find("project")
    project = None
    if proj_elem is not None and proj_elem.get("key"):
        project = proj_elem.get("key")
    elif key and "-" in key:
        project = key.rsplit("-", 1)[0]
    return key, project


# ── file writing ─────────────────────────────────────────────────────────

def write_issue_xml(xml_dir: Path, project: str, key: str, item) -> None:
    """Wrap a single <item> in an <rss><channel> envelope and write it to
    xml_dir/<PROJECT>/<KEY>.xml, matching the per-issue download format so
    convert_jira_xml_to_text.py (which does root.find('.//item')) parses it
    identically.  Written via a temp file + atomic replace.
    """
    proj_dir = xml_dir / project
    proj_dir.mkdir(parents=True, exist_ok=True)

    item.tail = None  # drop any trailing whitespace from the source tree
    rss = ET.Element("rss", {"version": "0.92"})
    channel = ET.SubElement(rss, "channel")
    channel.append(item)
    data = ET.tostring(rss, encoding="utf-8")

    outfile = proj_dir / f"{key}.xml"
    tmp = proj_dir / f"{key}.tmp"  # ends in .tmp → ignored by *.xml globs
    tmp.write_bytes(data)
    tmp.replace(outfile)


def highest_local_id(xml_dir: Path, project: str) -> int:
    """Highest numeric issue ID already on disk for *project* (0 if none)."""
    proj_dir = xml_dir / project
    if not proj_dir.is_dir():
        return 0
    pat = re.compile(rf"^{re.escape(project)}-(\d+)\.xml$")
    hi = 0
    for f in proj_dir.glob(f"{project}-*.xml"):
        m = pat.match(f.name)
        if m:
            hi = max(hi, int(m.group(1)))
    return hi


# ── marker file ──────────────────────────────────────────────────────────

def read_marker(jira_dir: Path) -> str | None:
    marker = jira_dir / MARKER_FILE
    if marker.is_file():
        return marker.read_text().strip()
    return None


def write_marker(jira_dir: Path, value: str) -> None:
    (jira_dir / MARKER_FILE).write_text(value + "\n")


# ── URL builders ─────────────────────────────────────────────────────────

def search_url(jql: str, temp_max: int, start: int = 0) -> str:
    q = urllib.parse.quote(jql, safe="")
    url = (f"{JIRA_URL}/sr/jira.issueviews:searchrequest-xml/temp/"
           f"SearchRequest.xml?jqlQuery={q}&tempMax={temp_max}")
    if start:
        url += f"&pager/start={start}"
    return url


def issue_url(key: str) -> str:
    return f"{JIRA_URL}/si/jira.issueviews:issue-xml/{key}/{key}.xml"


# ── preflight: is the search-XML endpoint usable unauthenticated? ────────

def preflight() -> bool:
    """Issue ONE request that is guaranteed to match issues and verify the
    response is real issue RSS (not an HTML login page).  Picks search vs probe.
    """
    jql = f'project in ({", ".join(PROJECTS)}) ORDER BY updated DESC'
    url = search_url(jql, 1)
    log("Preflight: verifying search-XML endpoint is reachable and unauthenticated ...")
    log(f"  {url}")
    try:
        status, body = http_get(url)
    except Exception as e:
        log(f"  Preflight request failed: {e} — search path unavailable.")
        return False
    if status != 200:
        log(f"  Preflight got HTTP {status} — search path unavailable.")
        return False
    root = parse_rss(body)
    if root is None:
        log("  Preflight response was not valid issue RSS (login/HTML page?) "
            "— search path unavailable.")
        return False
    item = root.find(".//item")
    if item is None or item.find("key") is None:
        log("  Preflight RSS contained no issue items — search path unavailable.")
        return False
    key, _ = item_key_project(item)
    log(f"  Preflight OK — endpoint returned issue {key}. Using search path.")
    return True


# ── primary path: JQL search, split items into per-issue files ───────────

def fetch_via_search(jira_dir: Path, query_date: str, max_issues: int,
                     dry_run: bool) -> int:
    xml_dir = jira_dir / "xml"
    jql = (f'project in ({", ".join(PROJECTS)}) '
           f'AND updated >= "{query_date}" ORDER BY updated ASC')
    log(f"JQL: {jql}")

    if dry_run:
        log(f"[dry-run] search URL (page 1): {search_url(jql, TEMP_MAX)}")
        return 0

    total = 0
    start = 0
    page = 0
    seen: set[str] = set()  # keys written this run — guards against a server
    #                         that ignores pager/start (would loop forever).
    while True:
        page += 1
        if page > MAX_SEARCH_PAGES:
            log(f"  WARNING: hit page cap ({MAX_SEARCH_PAGES}); stopping early. "
                f"Re-run to continue (the marker is not advanced on a cap).")
            return -total  # negative signals "incomplete" to the caller
        url = search_url(jql, TEMP_MAX, start)
        log(f"Fetching search results {start}..{start + TEMP_MAX} ...")
        status, body = http_get(url)
        if status != 200:
            raise RuntimeError(f"search returned HTTP {status}")
        root = parse_rss(body)
        if root is None:
            raise RuntimeError("search response was not valid RSS (login page?)")

        items = root.findall(".//item")
        if not items:
            break

        new_this_page = 0
        for item in items:
            key, project = item_key_project(item)
            if not key or project not in PROJECTS:
                log(f"  skipping item with key={key!r} project={project!r}")
                continue
            if key in seen:
                continue  # already written this run (overlap / stalled paging)
            seen.add(key)
            new_this_page += 1
            write_issue_xml(xml_dir, project, key, item)
            total += 1
            if max_issues and total >= max_issues:
                log(f"  reached --max-issues {max_issues}, stopping")
                return total

        log(f"  got {len(items)} item(s), {new_this_page} new (total: {total})")

        if len(items) < TEMP_MAX:
            break  # short page = last page
        if new_this_page == 0:
            # A full page with zero new keys means pagination is not advancing
            # (e.g. the server ignored pager/start). Stop rather than hammer it.
            log("  WARNING: full page yielded no new issues — pagination not "
                "advancing; stopping to avoid a request loop.")
            break
        start += len(items)
        time.sleep(RATE_LIMIT_DELAY)

    return total


# ── fallback path: bounded upward ID probe (new issues only) ─────────────

def fetch_via_probe(jira_dir: Path, max_issues: int, dry_run: bool) -> int:
    xml_dir = jira_dir / "xml"
    total = 0
    for project in PROJECTS:
        hi = highest_local_id(xml_dir, project)
        log(f"{project}: highest local id = {hi}; probing upward "
            f"(stop after {PROBE_MISS_LIMIT} consecutive misses)")
        if dry_run:
            log(f"[dry-run] would probe {project}-{hi + 1} upward")
            continue

        misses = 0
        n = hi + 1
        while misses < PROBE_MISS_LIMIT:
            key = f"{project}-{n}"
            status, body = http_get(issue_url(key))
            root = parse_rss(body) if status == 200 else None
            item = root.find(".//item") if root is not None else None
            if item is not None and item.find("key") is not None:
                k, proj = item_key_project(item)
                write_issue_xml(xml_dir, proj or project, k or key, item)
                total += 1
                misses = 0
                log(f"  OK   {key}")
                if max_issues and total >= max_issues:
                    log(f"  reached --max-issues {max_issues}, stopping")
                    return total
            else:
                misses += 1
            n += 1
            time.sleep(RATE_LIMIT_DELAY)
    return total


# ── date helpers ─────────────────────────────────────────────────────────

def minus_days(date_str: str, days: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=days)
    return d.strftime("%Y-%m-%d")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Incrementally download/refresh JIRA issues as XML."
    )
    parser.add_argument(
        "--output", "-o",
        help="Base jira dir (default: ../raw/jira relative to script); "
             "the marker and xml/ tree live here.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preflight + print the plan; fetch nothing, write nothing.",
    )
    parser.add_argument(
        "--max-issues", type=int, default=0,
        help="Cap the total number of issues fetched (for smoke tests).",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Ignore the marker; look back from --bootstrap-date instead.",
    )
    parser.add_argument(
        "--bootstrap-date",
        help="Lower-bound date (YYYY-MM-DD) when no marker exists or --full. "
             f"Default: {BOOTSTRAP_LOOKBACK_DAYS} days before today.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    jira_dir = Path(args.output) if args.output else (
        script_dir.parent / "raw" / "jira"
    )
    (jira_dir / "xml").mkdir(parents=True, exist_ok=True)

    run_start = datetime.now().strftime("%Y-%m-%d")

    # Decide the lower-bound date for the query.
    marker = read_marker(jira_dir)
    if args.full or not marker:
        query_date = args.bootstrap_date or minus_days(run_start,
                                                        BOOTSTRAP_LOOKBACK_DAYS)
        why = "--full" if args.full else "no marker found"
        log(f"{why}: looking back from bootstrap date {query_date}")
        if not args.bootstrap_date and not args.full:
            log("  (seed raw/jira/.last_update or pass --bootstrap-date to "
                "control the first-run window)")
    else:
        marker_date = marker[:10]
        try:
            query_date = minus_days(marker_date, 1)  # 1-day overlap
        except ValueError:
            query_date = args.bootstrap_date or minus_days(
                run_start, BOOTSTRAP_LOOKBACK_DAYS)
            log(f"Marker {marker_date!r} unparsable — using {query_date}")
        else:
            log(f"Marker date {marker_date} → query updated >= {query_date} "
                f"(1-day overlap)")

    log(f"Jira dir: {jira_dir}")
    log(f"Run-start marker (written only on success): {run_start}")

    use_search = preflight()

    if args.dry_run:
        log("[dry-run] No issues will be fetched; marker will not advance.")
        if use_search:
            fetch_via_search(jira_dir, query_date, args.max_issues, dry_run=True)
        else:
            fetch_via_probe(jira_dir, args.max_issues, dry_run=True)
        log("[dry-run] Done.")
        return 0

    incomplete = False
    if use_search:
        total = fetch_via_search(jira_dir, query_date, args.max_issues,
                                 dry_run=False)
        if total < 0:  # page-cap backstop tripped
            incomplete = True
            total = -total
    else:
        log("Search path unavailable — falling back to bounded ID probe "
            "(discovers NEW issues only; changed issues are NOT refreshed).")
        total = fetch_via_probe(jira_dir, args.max_issues, dry_run=False)

    # Advance the marker only after a complete, non-truncated run.
    if incomplete:
        log("Run incomplete (page cap) — marker NOT advanced; re-run to continue.")
    elif args.max_issues and total >= args.max_issues:
        log("Reached --max-issues cap (partial run) — marker NOT advanced.")
    else:
        write_marker(jira_dir, run_start)
        log(f"Marker advanced to {run_start}.")

    log(f"Done: {total} issue(s) fetched/refreshed.")
    return 1 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main())
