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
#
# Pandoc version:
#   Only chapters whose XML is newer than their text are reconverted, so
#   every run must use the same pandoc release or the corpus ends up
#   mixing renderings (table layout, spacing, and escaping all vary
#   between releases).  The corpus is rendered with pandoc 2.9.2.1; this
#   script refuses to run with any other version.  Point PANDOC at a
#   matching binary if the system pandoc differs, e.g. the static build:
#     https://github.com/jgm/pandoc/releases/download/2.9.2.1/pandoc-2.9.2.1-linux-amd64.tar.gz
#     PANDOC=~/.local/opt/pandoc-2.9.2.1/bin/pandoc ./convert_manual_to_text.sh
#   To move to a new release, update EXPECTED_PANDOC_VERSION and
#   reconvert every chapter (delete PROCESSED_DIR/*.txt first).

set -euo pipefail

EXPECTED_PANDOC_VERSION="2.9.2.1"
PANDOC="${PANDOC:-pandoc}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAW_DIR="${1:-${SCRIPT_DIR}/../raw/manual/src/lustre-manual}"
PROCESSED_DIR="${2:-${SCRIPT_DIR}/../processed/manual/txt}"

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

if ! command -v "$PANDOC" &>/dev/null; then
    echo "Error: pandoc not found: $PANDOC" >&2
    echo "  Install pandoc ${EXPECTED_PANDOC_VERSION} and/or set PANDOC (see header of $0)." >&2
    exit 1
fi

pandoc_version="$("$PANDOC" --version | head -n1 | awk '{print $2}')"
if [[ "$pandoc_version" != "$EXPECTED_PANDOC_VERSION" ]]; then
    echo "Error: $PANDOC is version ${pandoc_version}; the corpus is rendered with ${EXPECTED_PANDOC_VERSION}." >&2
    echo "  Set PANDOC to a ${EXPECTED_PANDOC_VERSION} binary (see header of $0)." >&2
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

    if "$PANDOC" -f docbook -t plain --wrap=auto --columns=80 "$xml_file" -o "$outfile" 2>/dev/null; then
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
