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
| **Official Manual** | [review.whamcloud.com/doc/manual](https://review.whamcloud.com/doc/manual) (DocBook) | DocBook XML | Plaintext |
| **Wiki** | [wiki.lustre.org](https://wiki.lustre.org/) | MediaWiki XML | Plaintext |
| **Source Code** | [git.whamcloud.com](https://git.whamcloud.com/fs/lustre-release.git) | — | As-is |

## Scripts

### `download_jira_xml.py`

Downloads JIRA issues as XML from Whamcloud's JIRA server. `range` mode fetches a key range for the initial download, skipping issues already present. `update` mode is the routine refresh: it asks JIRA for every issue updated since the last run and re-downloads any that are new or have changed (status, resolution, comments, …), tracking progress in `raw/jira/xml/<PROJECT>/.last_update`.

```bash
./scripts/download_jira_xml.py range LU 1 <MAX_LU_ID>     # initial download
./scripts/download_jira_xml.py update LU LUDOC --dry-run  # preview a refresh
./scripts/download_jira_xml.py update LU LUDOC            # refresh new + changed issues
```

### `convert_jira_xml_to_text.py`

Converts raw JIRA XML to structured plaintext. Strips HTML, extracts metadata (status, priority, assignee, dates, comments), and generates a TSV index. Only XML files newer than their text file are reconverted; the index is always rebuilt.

```bash
./scripts/convert_jira_xml_to_text.py raw/jira processed/jira
```

### `convert_manual_to_text.sh`

Converts DocBook XML manual chapters to plaintext using `pandoc`. The manual source in `raw/manual/src/lustre-manual` tracks Gerrit (`https://review.whamcloud.com/doc/manual`), which is the canonical upstream; the GitHub mirror is no longer updated, and git.whamcloud.com is behind a Cloudflare challenge that blocks scripted clones.

```bash
git -C raw/manual/src/lustre-manual pull
PANDOC=~/.local/opt/pandoc-2.9.2.1/bin/pandoc ./scripts/convert_manual_to_text.sh raw/manual/src/lustre-manual processed/manual/txt
```

### `convert_wiki_xml_to_text.py`

Splits a full MediaWiki XML export into individual pages and converts each to plaintext, stripping wikitext markup and templates. It also rewrites `processed/wiki_in_wikitext/`, where local page edits are made before upload, so it first lists every local page the export would replace and requires typing `overwrite` to continue. Commit `wiki_in_wikitext/` before running it.

```bash
./scripts/convert_wiki_xml_to_text.py raw/wiki processed/wiki
```

## Prerequisites

- **Python 3**
- **[pandoc](https://pandoc.org/) 2.9.2.1** — required for manual conversion. The corpus is rendered with this exact release and `convert_manual_to_text.sh` refuses other versions; if your system pandoc differs, unpack the [static build](https://github.com/jgm/pandoc/releases/tag/2.9.2.1) and set `PANDOC=/path/to/pandoc`.

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
