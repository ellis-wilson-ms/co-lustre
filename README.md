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
│   ├── code/lustre-release/    # Lustre source code (v2.17.52, GPL-2.0)
│   ├── jira/                   # Plaintext JIRA issues + TSV index
│   │   ├── index.tsv           # Tab-separated index (key, status, priority, type, …)
│   │   └── txt/
│   │       ├── LU/             # ~19,947 issue files (LU-1 through LU-19947)
│   │       └── LUDOC/          # ~558 documentation issue files
│   ├── manual/txt/             # 45+ plaintext manual chapters
│   ├── wiki/txt/               # 1,000+ plaintext wiki pages
│   └── wiki_in_wikitext/txt/   # Wiki pages in original wikitext markup
└── scripts/                    # Data collection and conversion utilities
```

## Data Sources

| Source | Origin | Raw Format | Processed Format |
|--------|--------|------------|------------------|
| **JIRA Issues** | [jira.whamcloud.com](https://jira.whamcloud.com/) | XML | Plaintext + TSV index |
| **Official Manual** | Lustre documentation (DocBook) | DocBook XML | Plaintext |
| **Wiki** | [wiki.lustre.org](https://wiki.lustre.org/) | MediaWiki XML | Plaintext |
| **Source Code** | [git.whamcloud.com](https://git.whamcloud.com/fs/lustre-release.git) | — | As-is (v2.17.52) |

## Scripts

### `download_jira_xml.sh`

Downloads JIRA issues as XML from Whamcloud's JIRA server using parallel `curl` requests.

```bash
# Usage: download_jira_xml.sh <PROJECT> <MIN_ID> <MAX_ID>
./scripts/download_jira_xml.sh LU 1 19947
./scripts/download_jira_xml.sh LUDOC 1 558
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

- **Python 3**
- **[pandoc](https://pandoc.org/)** — required for manual conversion (`apt install pandoc` / `brew install pandoc`)
- **curl** — used by the JIRA download script

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
