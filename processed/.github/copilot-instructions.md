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
5. **gerrit/** — Code review history. Search when you have a lead
   from another source, when other sources have come up empty, or
   when looking for unlanded work. See gerrit section for details.

## Directory Contents

### jira/

JIRA bug tracker issues from projects LU and LUDOC.

- **index.tsv** — **Always search the index before reading individual
  files.** Tab-separated index of all issues. Columns:
  `key, status, resolution, priority, type, assignee, summary`.
  Grep or filter this file to find relevant issue keys, then read only
  those specific files. Common patterns:
  - `grep -i "pcc" jira/index.tsv` — find all PCC-related issues
  - `awk -F'\t' '$2=="Open"' jira/index.tsv` — list all open issues
  - `grep -i "lnet.*timeout" jira/index.tsv` — keyword search
  Do not scan `txt/` directories directly unless the index search
  yields nothing.
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

#### Viewing Gerrit changes via the code repo

The `code/lustre-release/` repo also has a `gerrit` remote pointing at
`https://review.whamcloud.com/fs/lustre-release`. This allows viewing
the actual code diff for any Gerrit change without additional API calls.

**Merged changes** — The commit SHA is already in the local history
(it came in via the GitHub mirror). The SHA is stored in each Gerrit
JSON file under `revisions.<sha>`. To see the diff:
```
cd code/lustre-release
git show <sha>               # full diff + commit message
git diff --stat <sha>^..<sha>  # file list with line counts
git show <sha> -- path/to/file.c  # diff for a single file
```

**Open or abandoned changes** — These live on special `refs/changes/*`
refs that are not fetched by default. To make them available locally,
do a one-time bulk fetch:
```
cd code/lustre-release
git fetch gerrit 'refs/changes/*:refs/changes/*'
```
After that, every patch set is available locally. The ref for a
specific patch set is in the Gerrit JSON (`revisions.<sha>.ref`,
e.g. `refs/changes/79/64079/37`). To view it:
```
git show FETCH_HEAD           # if you just fetched one ref
git log -1 refs/changes/79/64079/37  # specific patch set
git diff refs/changes/79/64079/37^..refs/changes/79/64079/37  # diff
```

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

### gerrit/

Gerrit code review data from review.whamcloud.com (project
fs/lustre-release). Change reviews spanning 2012 to present.

- **index.tsv** — **Always search the index before reading individual
  files.** Tab-separated index of all changes. Columns:
  `number, status, branch, owner, patch_set, insertions, deletions, subject`.
  Grep or filter this file to narrow down to specific change numbers,
  then read only those files from `txt/`. Common patterns:
  - `grep -i "pcc" gerrit/index.tsv` — find changes by subject keyword
  - `awk -F'\t' '$2=="NEW"' gerrit/index.tsv | grep -i "ec"` — open
    changes related to EC (erasure coding)
  - `awk -F'\t' '$2=="MERGED" && $4=="Patrick Farrell"' gerrit/index.tsv`
    — merged changes by a specific author
  Do not grep across `txt/` or `txt_full/` without first narrowing
  through the index.
- **txt/** — One plain-text file per change (e.g., `5200.txt`). Contains
  metadata, labels, reviewers, commit message, and human review
  commentary. Verbose automated bot messages (Maloo test logs,
  checkpatch warnings, jenkins build details) are filtered to short
  status summaries.
- **txt_full/** — Same as `txt/` but with **all** messages unfiltered,
  including full bot output (test suite listings, build logs, style
  warnings). Files are ~4x larger on average.

#### When to search gerrit

Gerrit is #5 in the search order. Do not reach for it as a first
resort. Search gerrit when:

1. **You have a specific lead from another source.** A JIRA issue
   references a Gerrit change number, a commit message mentions a
   Change-Id, or a wiki page links to a review. Look up the change
   number in the index or read the file directly.
2. **Other sources have come up empty.** You have searched jira/,
   code/, manual/, and wiki/ and still cannot find the answer. Gerrit
   review discussions often contain design rationale, workarounds, and
   context not captured elsewhere.
3. **You are hunting for unlanded code/changes.** For example: "What
   PCC fixes exist that haven't been merged?" Filter `index.tsv` for
   `status=NEW` or `status=ABANDONED` and grep subjects for keywords.

#### Which gerrit directory to use

- **Default to `txt/`** for all searches. The filtered version contains
  all human review commentary and concise bot status summaries.
- **Use `txt_full/` only** when you know the exact change number AND
  you specifically need to see full automated commentary (e.g., the
  complete Maloo test results, jenkins build output, or checkpatch
  warnings for a particular patch set).

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
- **Unlanded patch search:** Filter `gerrit/index.tsv` for `NEW` status
  changes matching a keyword, then read matching `gerrit/txt/*.txt`
  files. Only resort to this after checking jira/ and code/.
- **Gerrit change lookup (known number):** Read
  `gerrit/txt/<number>.txt` directly. Use `gerrit/txt_full/<number>.txt`
  only if you need full bot output for that specific change.
