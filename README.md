# co-lustre

A comprehensive text corpus of [Lustre](http://lustre.org) filesystem documentation, JIRA issues, and source code — converted to searchable plaintext for analysis, reference, and retrieval.

Lustre is an open-source, distributed parallel file system designed for large-scale HPC environments. This repository collects and normalizes data from multiple Lustre knowledge sources into a single, grepable dataset.

> **For most users, the `processed/` directory is all you need.** The corpus is maintained by [Ellis Wilson](https://github.com/ellis-wilson-ms) and kept relatively up-to-date with respect to the upstream data sources. The `scripts/` and `raw/` directories are included only for transparency — they document how the data is collected and normalized, but are not required for day-to-day use.

## Repository Structure

```
co-lustre/
├── raw/                        # Original source data (XML, DocBook, MediaWiki)
│   ├── jira/xml/               # Raw JIRA issue XML exports (LU, LUDOC projects)
│   ├── manual/src/             # DocBook XML source for the official Lustre manual
│   └── wiki/                   # Full MediaWiki XML export of the Lustre wiki
│       ├── full_xml_download.xml
│       └── page-list.txt
├── processed/                  # Cleaned plaintext output
│   ├── code/lustre-release/    # Lustre source code (GPL-2.0)
│   ├── jira/                   # Plaintext JIRA issues + TSV index
│   │   ├── index.tsv           # Tab-separated index (key, status, priority, type, …)
│   │   └── txt/
│   │       ├── LU/             # Lustre bug/feature issues
│   │       └── LUDOC/          # Lustre documentation issues
│   ├── manual/txt/             # Plaintext manual chapters
│   ├── wiki/txt/               # Plaintext wiki pages
│   └── wiki_in_wikitext/txt/   # Wiki pages in original wikitext markup
└── scripts/                    # Data collection and conversion utilities
```

## Data Sources

| Source | Origin | Raw Format | Processed Format |
|--------|--------|------------|------------------|
| **JIRA Issues** | [jira.whamcloud.com](https://jira.whamcloud.com/) | XML | Plaintext + TSV index |
| **Official Manual** | Lustre documentation (DocBook) | DocBook XML | Plaintext |
| **Wiki** | [wiki.lustre.org](https://wiki.lustre.org/) | MediaWiki XML | Plaintext |
| **Source Code** | [git.whamcloud.com](https://git.whamcloud.com/fs/lustre-release.git) | — | As-is |

## Scripts

### `update_corpus.sh` — one-command update (recommended)

Refreshes the entire corpus end to end with **no arguments**, so it can be run
by hand or from cron. It fetches new/changed JIRA issues and Gerrit changes,
then re-runs every converter, in the correct order:

```bash
./scripts/update_corpus.sh                  # full update (leaves changes in the working tree)
./scripts/update_corpus.sh --commit         # full update, then commit raw/ + processed/
./scripts/update_corpus.sh --commit --push  # same as ^ but also pushes updates
./scripts/update_corpus.sh --dry-run        # verify wiring + JIRA endpoint, fetch nothing
./scripts/update_corpus.sh --max-issues 5   # cap JIRA fetch (smoke test)
./scripts/update_corpus.sh --skip-jira      # also: --skip-gerrit
```

- **DoS-safe by design.** A `flock` single-instance lock means a second
  invocation (e.g. an overlapping cron fire) exits immediately instead of
  doubling load on the shared servers. The fetchers are sequential and
  rate-limited (0.5 s between requests, exponential backoff on 429/5xx).
- **Does not commit by default.** It updates the working tree and prints a
  summary of what changed — review and commit yourself. Pass `--commit` to opt
  in to an automatic `git commit` of `raw/` + `processed/` on the current branch
  (message `Update Corpus <date>`. It stages only those two directories, skips a
  commit that would merely bump the `.last_update` markers, optionally pushes
  with `--push`.
- **Picks a suitable Python automatically** (the scripts need 3.10+; override
  with `CO_LUSTRE_PYTHON=/path/to/python3.x` if needed).

Cron example (logs kept *outside* the repo so they never dirty git):

```cron
17 4 * * *  /path/to/co-lustre/scripts/update_corpus.sh >> "$HOME/co-lustre-logs/update_corpus_$(date +\%Y\%m\%d).log" 2>&1
```

### `download_jira_incremental.py`

Polite, incremental JIRA fetcher used by `update_corpus.sh`. Uses JIRA's
search-XML view with a JQL `updated >= <date>` query to fetch issues that are
**new *or have changed*** since the last run (unlike `download_jira_xml.sh`,
which only ever adds new issues and never refreshes existing ones). A marker at
`raw/jira/.last_update` tracks the last successful run and is advanced only on
success, with a one-day query overlap so nothing is missed.

```bash
./scripts/download_jira_incremental.py            # incremental refresh
./scripts/download_jira_incremental.py --dry-run  # preflight + print plan only
./scripts/download_jira_incremental.py --full --bootstrap-date 2026-04-01
```

If the search endpoint is ever unavailable, it falls back to a bounded
upward-ID probe that discovers new issues only.

### `download_jira_xml.sh`

Downloads JIRA issues as XML from Whamcloud's JIRA server using parallel `curl` requests.

```bash
# Usage: download_jira_xml.sh <PROJECT> <MIN_ID> <MAX_ID>
./scripts/download_jira_xml.sh LU 1 <MAX_LU_ID>
./scripts/download_jira_xml.sh LUDOC 1 <MAX_LUDOC_ID>
```

### `convert_jira_xml_to_text.py`

Converts raw JIRA XML to structured plaintext. Strips HTML, extracts metadata (status, priority, assignee, dates, comments), and generates a TSV index.

```bash
./scripts/convert_jira_xml_to_text.py raw/jira processed/jira
```

### `convert_manual_to_text.sh`

Converts DocBook XML manual chapters to plaintext using `pandoc`.

```bash
./scripts/convert_manual_to_text.sh raw/manual/src/lustre-manual processed/manual/txt
```

### `convert_wiki_xml_to_text.py`

Splits a full MediaWiki XML export into individual pages and converts each to plaintext, stripping wikitext markup and templates.

```bash
./scripts/convert_wiki_xml_to_text.py raw/wiki processed/wiki
```

## Prerequisites

- **Python 3.10+** (the fetch/convert scripts use 3.10+ syntax; `update_corpus.sh`
  auto-selects a suitable interpreter, or set `CO_LUSTRE_PYTHON`)
- **[pandoc](https://pandoc.org/)** — required for manual conversion (`apt install pandoc` / `brew install pandoc`)
- **curl** — used by the JIRA download script
- **flock** — used by `update_corpus.sh` for its single-instance lock (standard on Linux)

## Processed Data Format

### JIRA Issues

Each issue is a plaintext file containing structured fields:

```
Key: LU-12345
Summary: Example issue title
Status: Closed
Priority: Major
Type: Bug
Assignee: developer@example.com
...
Description:
  <issue description text>

Comments:
  [2024-01-15 author@example.com]
  <comment text>
```

The `index.tsv` provides a tab-separated overview of all issues with columns: `key`, `status`, `resolution`, `priority`, `type`, `assignee`, `summary`.

### Manual

Each chapter is a standalone plaintext file named after its topic (e.g., `ConfiguringLNet.txt`, `LustreTuning.txt`, `LustreDebugging.txt`).

### Wiki

Each wiki page is a plaintext file named after the page title (e.g., `Compiling_Lustre.txt`). A parallel `wiki_in_wikitext/` directory preserves the original wikitext markup before stripping.

## License

- **Lustre source code**: GPL-2.0 (see [processed/code/lustre-release/COPYING](processed/code/lustre-release/COPYING))
- **Documentation and JIRA data**: Sourced from the Lustre project's public resources
