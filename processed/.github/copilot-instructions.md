# Lustre Public Dataset — Processed Reference Data

This workspace contains processed, AI-searchable versions of four
primary Lustre documentation sources. All content is plain text or
source code — no binary formats.

## Recommended Search Order

When investigating a Lustre issue (crash, error, configuration question):

1. **jira/** — Search the index first, then read matching issue files.
   Most bugs, stack traces, and error messages are documented here with
   resolution status.
2. **code/** — Grep the source for function names, error strings, or
   proc parameters to understand current behavior.
3. **manual/** — Authoritative operational procedures, configuration
   options, and tuning guidance.
4. **wiki/** — Community knowledge: architecture deep-dives, howtos,
   meeting notes, and supplementary guides.

## Directory Contents

### jira/

JIRA bug tracker issues from projects LU and LUDOC.

- **index.tsv** — **Start here.** Tab-separated index of ~19,800 issues.
  Columns: `key, status, resolution, priority, type, assignee, summary`.
  Use this to quickly find issues by keyword, check status, or filter by
  resolution before reading full issue files.
- **txt/LU/** — One plain-text file per LU issue (e.g., `LU-9962.txt`).
- **txt/LUDOC/** — One plain-text file per LUDOC issue.

Each issue file has a structured header (Key, Summary, Status, Resolution,
Priority, Assignee, Reporter, dates, links) followed by the full description
and all comments in chronological order.

### code/

Lustre source code (lustre-release repository).

- **lustre-release/** — Full source tree. Use grep/find directly.
  Key subdirectories: `lustre/ofd/`, `lustre/ldlm/`, `lustre/llite/`,
  `lustre/mdt/`, `lustre/obdclass/`, `lustre/ptlrpc/`, `lnet/`.

#### Important: lustre-release is a separate git repo

`code/lustre-release/` is a git clone of
`https://github.com/lustre/lustre-release.git`. It is **not** part of
the dataset repository and must **never** be committed to the dataset's
git history.

**On session start**, before using the source code:

1. If `code/lustre-release/` does not exist, clone it:
   ```
   git clone https://github.com/lustre/lustre-release.git code/lustre-release
   ```
2. If it already exists, pull the latest:
   ```
   cd code/lustre-release && git checkout master && git pull
   ```
3. If the user specifies a Lustre version (e.g. "2.15"), check out the
   corresponding branch. The naming convention is `b<major>_<minor>`:
   - 2.15 → `b2_15`
   - 2.12 → `b2_12`
   - 1.8  → `b1_8`
   ```
   cd processed/code/lustre-release && git checkout b2_15 && git pull origin b2_15
   ```
   If no version is specified, stay on `master`.

### manual/

Lustre Operations Manual, converted from DocBook XML to plain text.

- **txt/** — 47 chapter files (e.g., `ConfiguringStorage.txt`,
  `LustreTuning.txt`, `ManagingStripingFreeSpace.txt`).
  Chapter names are self-descriptive.

### wiki/

Lustre Wiki pages (plaintext — **use this directory** for searching,
reading, and answering questions about wiki content).

- **txt/** — 359 plain-text files, one per wiki page (e.g.,
  `ZFS.txt`, `Configuring_Lustre_File_Striping.txt`).
  Each file has a metadata header (Title, URL, Page ID, Last Updated,
  Last Editor) followed by the page content with markup stripped for
  easy reading and grepping.

**NEVER edit files in `wiki/txt/`.** These are auto-generated
plain-text extracts. The editing workflow is:

1. Edit the MediaWiki source in `wiki_in_wikitext/txt/`.
2. The user uploads the wikitext to the wiki.
3. Pages are downloaded as XML, then reformatted into both XML and
   the plain-text files in `wiki/txt/`.

### wiki_in_wikitext/

Lustre Wiki pages in original MediaWiki markup. **This is the
directory to edit** when creating or modifying wiki page content.

- **txt/** — Same pages as `wiki/txt/`, but the content section
  preserves the original MediaWiki wikitext markup (templates, links,
  tables, headings, categories, etc.).

**Workflow for wiki edits:**
- **Read** wiki content from `wiki/txt/` (plain text, easier to search).
- **Write/edit** wiki content in `wiki_in_wikitext/txt/` (MediaWiki markup).
- New pages should be created in `wiki_in_wikitext/txt/` only.

## Search Strategies

- **Stack trace lookup:** Extract function names from the trace, grep
  `jira/index.tsv` for keywords, then read matching `jira/txt/LU/*.txt`
  files. Also grep `code/lustre-release/` for the function to see
  current implementation.
- **Configuration questions:** Check `manual/txt/` first (authoritative),
  then `wiki/txt/` for community guides.
- **"Is this bug fixed?":** Search `jira/index.tsv` — the `status` and
  `resolution` columns immediately tell you. Read the issue file for
  details on the fix and any linked patches.
- **Error message lookup:** Grep across all directories:
  `grep -rl "error string" jira/txt/ manual/txt/ wiki/txt/`
