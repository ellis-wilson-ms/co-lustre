#!/usr/bin/env bash
#
# convert_manual_to_text.sh — Convert Lustre manual DocBook XML to plain text.
#
# Converts each chapter-level DocBook XML file to plaintext using pandoc.
# Skips part-level files, index, and supporting files (legal notices, etc.)
# since their content is included in the chapter files.
#
# Usage:
#   ./convert_manual_to_text.sh [RAW_DIR [PROCESSED_DIR]]
#
# Defaults:
#   RAW_DIR       = ../raw/manual/src/lustre-manual  (relative to this script)
#   PROCESSED_DIR = ../processed/manual/txt           (relative to this script)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAW_DIR="${1:-${SCRIPT_DIR}/../raw/manual/src/lustre-manual}"
PROCESSED_DIR="${2:-${SCRIPT_DIR}/../processed/manual/txt}"

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

if ! command -v pandoc &>/dev/null; then
    echo "Error: pandoc is required but not installed." >&2
    echo "  Install with: sudo apt-get install pandoc" >&2
    exit 1
fi

if [[ ! -d "$RAW_DIR" ]]; then
    echo "Error: Source directory not found: $RAW_DIR" >&2
    exit 1
fi

mkdir -p "$PROCESSED_DIR"

# Skip files that are not standalone chapter/section content:
#   - index.xml, ix.xml          (book structure / index markers)
#   - I_*, II_*, III_*, etc.     (part wrappers that just xi:include chapters)
#   - legalnotice*.xml           (legal boilerplate)
#   - Revision.xml              (revision history)
SKIP_PATTERN="^(index|ix|I{1,3}_|IV_|V_|VI_|legalnotice|Revision)"

converted=0
skipped=0
failed=0

for xml_file in "$RAW_DIR"/*.xml; do
    basename="$(basename "$xml_file" .xml)"

    # Skip non-chapter files
    if [[ "$basename" =~ $SKIP_PATTERN ]]; then
        continue
    fi

    outfile="${PROCESSED_DIR}/${basename}.txt"

    # Skip if text file is newer than source
    if [[ -f "$outfile" && "$outfile" -nt "$xml_file" ]]; then
        (( ++skipped ))
        continue
    fi

    if pandoc -f docbook -t plain --wrap=auto --columns=80 "$xml_file" -o "$outfile" 2>/dev/null; then
        log "OK    ${basename}"
        (( ++converted ))
    else
        log "FAIL  ${basename}"
        rm -f "$outfile"
        (( ++failed ))
    fi
done

log "Done: ${converted} converted, ${skipped} up-to-date, ${failed} failed."
log "Output: ${PROCESSED_DIR}"
