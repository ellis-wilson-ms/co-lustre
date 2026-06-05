#!/usr/bin/env bash
#
# update_corpus.sh — One-command update of the processed Lustre corpus.
#
# Runs the whole pipeline in order, with no per-script arguments, so it can
# be invoked by hand or from cron:
#
#   1. fetch new/changed JIRA issues   (download_jira_incremental.py)
#   2. fetch new/changed Gerrit changes (download_gerrit_json.py, incremental)
#   3. convert JIRA  XML  -> processed/jira
#   4. convert Gerrit JSON -> processed/gerrit
#   5. convert manual DocBook -> processed/manual   (needs pandoc)
#   6. convert wiki  XML  -> processed/wiki
#
# DoS-safety: a flock(1) single-instance lock means a second invocation (e.g.
# an overlapping cron fire) exits immediately instead of doubling load on the
# shared JIRA/Gerrit servers.  The fetchers themselves are sequential and
# rate-limited.
#
# By default this script does NOT commit or push — it only updates the working
# tree and prints a summary of what changed.  Pass --commit to opt in to an
# automatic commit of the refreshed corpus (raw/ + processed/) on the current
# branch; even with --commit it NEVER pushes.
#
# Usage:
#   ./update_corpus.sh [--dry-run] [--commit] [--push] [--max-issues N]
#                      [--skip-jira] [--skip-gerrit]
#
#   --dry-run        Acquire the lock and run the JIRA preflight only; fetch
#                    nothing and run no converters.  Confirms wiring + that the
#                    JIRA search endpoint answers unauthenticated.
#   --commit         After the update, git-add raw/ and processed/ and commit
#                    them on the current branch ("Update Corpus <date>").  Skips
#                    a commit that would only bump the .last_update markers.
#                    Off by default.
#   --push           After committing, push the current branch to its tracking
#                    remote.  Requires --commit.  Errors if the branch has no
#                    upstream configured.  Never force-pushes.
#   --max-issues N   Cap JIRA issues fetched (passed through; for smoke tests).
#   --skip-jira      Skip the JIRA fetch (still runs the JIRA converter).
#   --skip-gerrit    Skip the Gerrit fetch (still runs the Gerrit converter).
#   -h, --help       Show this help.
#
# Cron example (logs OUTSIDE the repo so they never dirty git):
#   17 4 * * *  /path/to/co-lustre/scripts/update_corpus.sh \
#                 >> "$HOME/co-lustre-logs/update_corpus_$(date +\%Y\%m\%d).log" 2>&1

set -uo pipefail   # NOT -e: one failing converter must not abort the rest.

# ── helpers ──────────────────────────────────────────────────────────────

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

usage() { sed -n '2,/^set -uo/{/^set -uo/d;s/^# \{0,1\}//;p}' "$0"; }

FAILURES=0

# run_step DESCRIPTION CMD [ARGS...] — run a step, log it, count failures,
# and KEEP GOING on error.
run_step() {
    local desc="$1"; shift
    log "▶ ${desc}"
    if "$@"; then
        log "✓ ${desc}"
    else
        local rc=$?
        log "✗ ${desc} (exit ${rc})"
        FAILURES=$((FAILURES + 1))
    fi
}

# auto_commit — opt-in (--commit): stage ONLY the corpus output dirs and commit
# them on the current branch, mirroring the maintainer's "Update Corpus <date>"
# message convention.  It NEVER pushes, NEVER stages anything outside raw/ +
# processed/ (so unrelated working-tree edits are left alone), and skips a
# commit that would only bump the .last_update run markers (so a no-op cron run
# does not litter history).  It commits even when an earlier step failed —
# logging loudly — because each fetcher advances its own marker only on success,
# so a failed step leaves that source stale-but-consistent rather than corrupt,
# and the non-zero exit at the end still surfaces the failure to cron/monitoring.
auto_commit() {
    if ! git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
        log "✗ --commit: ${REPO_ROOT} is not a git repository; skipping commit."
        return 1
    fi

    # Stage only what the pipeline produces — never sweep in unrelated edits.
    local paths=()
    [[ -d "${REPO_ROOT}/raw" ]]       && paths+=(raw)
    [[ -d "${REPO_ROOT}/processed" ]] && paths+=(processed)
    if [[ ${#paths[@]} -eq 0 ]]; then
        log "--commit: no raw/ or processed/ directory to stage; nothing to commit."
        return 0
    fi
    git -C "$REPO_ROOT" add -- "${paths[@]}"

    if git -C "$REPO_ROOT" diff --cached --quiet -- "${paths[@]}"; then
        log "--commit: no corpus changes to commit."
        return 0
    fi

    # If the ONLY staged changes are the run markers, don't make a no-op commit.
    local nonmarker
    nonmarker="$(git -C "$REPO_ROOT" diff --cached --name-only -- "${paths[@]}" \
        | grep -vxF -e 'raw/jira/.last_update' -e 'raw/gerrit/json/.last_update' \
        | wc -l | tr -d ' ')"
    if [[ "$nonmarker" -eq 0 ]]; then
        log "--commit: only .last_update markers changed; skipping no-op commit."
        git -C "$REPO_ROOT" reset -q -- "${paths[@]}"   # leave markers in the working tree
        return 0
    fi

    if [[ "$FAILURES" -gt 0 ]]; then
        log "--commit: WARNING — committing despite ${FAILURES} failed step(s); affected sources stay stale until the next successful run."
    fi

    local n branch
    n="$(git -C "$REPO_ROOT" diff --cached --name-only -- "${paths[@]}" | wc -l | tr -d ' ')"
    branch="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
    if git -C "$REPO_ROOT" commit -q -m "Update Corpus $(date '+%Y-%m-%d')"; then
        log "✓ --commit: committed ${n} path(s) on '${branch}'."
    else
        log "✗ --commit: git commit failed."
        FAILURES=$((FAILURES + 1))
    fi
}

auto_push() {
    local branch remote
    branch="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
    remote="$(git -C "$REPO_ROOT" config --get "branch.${branch}.remote" 2>/dev/null)"
    if [[ -z "$remote" ]]; then
        log "✗ --push: branch '${branch}' has no upstream configured; skipping push."
        FAILURES=$((FAILURES + 1))
        return 1
    fi
    if git -C "$REPO_ROOT" push -q "$remote" "${branch}"; then
        log "✓ --push: pushed '${branch}' to '${remote}'."
    else
        local rc=$?
        log "✗ --push: git push failed (exit ${rc})."
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# ── arguments ────────────────────────────────────────────────────────────

DRY_RUN=false
SKIP_JIRA=false
SKIP_GERRIT=false
MAX_ISSUES=""
COMMIT=false
PUSH=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)     DRY_RUN=true ;;
        --commit)      COMMIT=true ;;
        --push)        PUSH=true ;;
        --skip-jira)   SKIP_JIRA=true ;;
        --skip-gerrit) SKIP_GERRIT=true ;;
        --max-issues)  MAX_ISSUES="${2:?--max-issues needs a value}"; shift ;;
        --max-issues=*) MAX_ISSUES="${1#*=}" ;;
        -h|--help)     usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

if $PUSH && ! $COMMIT; then
    echo "Error: --push requires --commit" >&2; usage >&2; exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# The fetch/convert scripts use Python 3.10+ syntax, but a bare `python3`
# (especially under cron's minimal PATH) may resolve to an older interpreter.
# Pick the first candidate that is >= 3.10; override with CO_LUSTRE_PYTHON.
pick_python() {
    local cand
    for cand in "${CO_LUSTRE_PYTHON:-}" python3 python3.13 python3.12 python3.11 python3.10; do
        [[ -z "$cand" ]] && continue
        if command -v "$cand" >/dev/null 2>&1 \
           && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
            command -v "$cand"
            return 0
        fi
    done
    return 1
}

# ── single-instance lock (the #1 DoS guard) ──────────────────────────────
# Held for the whole run; released automatically when fd 9 closes on exit,
# so a crash never leaves a stale lock.  Lives outside the repo.

LOCKFILE="${TMPDIR:-/tmp}/co-lustre-update_corpus.lock"
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    log "Another update_corpus run is in progress (${LOCKFILE}) — exiting."
    exit 0
fi

# ── run ──────────────────────────────────────────────────────────────────

log "=== co-lustre corpus update starting ==="
log "Repo: ${REPO_ROOT}"
$DRY_RUN && log "Mode: DRY RUN (preflight only, no fetch, no converters)"

if ! PYTHON="$(pick_python)"; then
    log "ERROR: no Python >= 3.10 found (required by the fetch/convert scripts)."
    log "       Install one or set CO_LUSTRE_PYTHON=/path/to/python3.1x"
    exit 1
fi
log "Python: ${PYTHON} ($("$PYTHON" --version 2>&1))"

# 1. JIRA fetch (incremental: new + changed issues).
if $SKIP_JIRA; then
    log "Skipping JIRA fetch (--skip-jira)"
else
    jira_args=()
    $DRY_RUN && jira_args+=(--dry-run)
    [[ -n "$MAX_ISSUES" ]] && jira_args+=(--max-issues "$MAX_ISSUES")
    run_step "JIRA fetch" "$PYTHON" "${SCRIPT_DIR}/download_jira_incremental.py" "${jira_args[@]}"
fi

# 2. Gerrit fetch (incremental by default via its own .last_update marker).
if $DRY_RUN; then
    log "Skipping Gerrit fetch (dry run)"
elif $SKIP_GERRIT; then
    log "Skipping Gerrit fetch (--skip-gerrit)"
else
    run_step "Gerrit fetch" "$PYTHON" "${SCRIPT_DIR}/download_gerrit_json.py"
fi

# 3-6. Converters (local, incremental, idempotent). Skipped in a dry run.
if $DRY_RUN; then
    log "Skipping converters (dry run)"
else
    run_step "Convert JIRA"   "$PYTHON" "${SCRIPT_DIR}/convert_jira_xml_to_text.py"
    run_step "Convert Gerrit" "$PYTHON" "${SCRIPT_DIR}/convert_gerrit_json_to_text.py"

    if command -v pandoc >/dev/null 2>&1; then
        run_step "Convert manual" bash "${SCRIPT_DIR}/convert_manual_to_text.sh"
    else
        log "✗ Convert manual — pandoc not installed; skipping (install: apt-get install pandoc)"
        FAILURES=$((FAILURES + 1))
    fi

    run_step "Convert wiki"   "$PYTHON" "${SCRIPT_DIR}/convert_wiki_xml_to_text.py"
fi

# ── summary ──────────────────────────────────────────────────────────────

if git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    changed="$(git -C "$REPO_ROOT" status --short | wc -l | tr -d ' ')"
    log "Working tree: ${changed} changed path(s)."
    log "  (raw/jira/.last_update and raw/gerrit/json/.last_update change every successful run — expected)"

    if $DRY_RUN; then
        ($COMMIT || $PUSH) && log "  (--commit/--push ignored in --dry-run: nothing was fetched or converted)"
    elif $COMMIT; then
        auto_commit
        $PUSH && auto_push
    else
        log "  (NOT committed — review & commit yourself, or pass --commit)"
    fi
fi

if [[ "$FAILURES" -gt 0 ]]; then
    log "=== Done with ${FAILURES} failed step(s) ==="
    exit 1
fi
log "=== Done: all steps succeeded ==="
exit 0
