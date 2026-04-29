#!/usr/bin/env bash
#
# download_jira_xml.sh — Download JIRA issues as XML files.
#
# Downloads <PROJECT>-<MIN>..<PROJECT>-<MAX> from the Whamcloud JIRA
# server into the specified output directory.  Skips issues that have
# already been downloaded (safe to re-run / resume).
#
# Runs up to PARALLEL (default 4) downloads concurrently.
#
# Usage:
#   ./download_jira_xml.sh PROJECT MIN MAX [OUTPUT_DIR]
#
# Examples:
#   ./download_jira_xml.sh LU     1 19947
#   ./download_jira_xml.sh LUDOC  1 464
#   ./download_jira_xml.sh LU     1 19947 /tmp/jira_xml
#
# Defaults:
#   OUTPUT_DIR = ../raw/jira/xml  (relative to this script's location)

set -euo pipefail

PARALLEL=4

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 PROJECT MIN MAX [OUTPUT_DIR]" >&2
    echo "  e.g. $0 LU 1 19947" >&2
    exit 1
fi

PROJECT="$1"
MIN="$2"
MAX="$3"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${4:-${SCRIPT_DIR}/../raw/jira/xml}"

BASE_URL="https://jira.whamcloud.com/si/jira.issueviews:issue-xml"

# ── helpers ──────────────────────────────────────────────────────────

log()  { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

download_issue() {
    local key="$1"
    local outfile="${OUTPUT_DIR}/${PROJECT}/${key}.xml"

    if [[ -f "$outfile" ]]; then
        return 0   # already downloaded
    fi

    local url="${BASE_URL}/${key}/${key}.xml"
    local http_code
    http_code=$(curl -s -o "$outfile" -w '%{http_code}' "$url")

    if [[ "$http_code" == "200" ]]; then
        log "OK   ${key}"
    else
        rm -f "$outfile"
        log "SKIP ${key}  (HTTP ${http_code})"
    fi
}

# ── main ─────────────────────────────────────────────────────────────

mkdir -p "${OUTPUT_DIR}/${PROJECT}"

log "Output directory: ${OUTPUT_DIR}"
log "Downloading ${PROJECT}-${MIN}..${PROJECT}-${MAX}  (${PARALLEL} parallel)"
log "Existing files will be skipped."
echo ""

RUNNING=0

for (( i=MIN; i<=MAX; i++ )); do
    download_issue "${PROJECT}-${i}" &
    (( ++RUNNING ))

    if (( RUNNING >= PARALLEL )); then
        wait -n   # wait for any one child to finish
        (( --RUNNING ))
    fi
done

wait  # wait for remaining jobs
log "Done."
