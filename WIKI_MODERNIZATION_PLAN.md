# Lustre Wiki Modernization Plan

## Project Goals

Modernize the Lustre community wiki so that it is **accurate**, **well-organized**,
and **genuinely useful** as a companion to the Lustre Operations Manual. The wiki
is not a copy of the manual — it is a longer-form, more flexible space for deep
dives, how-tos, community knowledge, and supplementary guides that extend the
formal documentation.

### Guiding Principles

- **Do not guess.** Every factual claim in a revised or new page must be verified
  against the Lustre Manual, Lustre source code, or JIRA issues.
- **Do not rewrite for the sake of rewriting.** Historical pages (conferences,
  meeting minutes, old changelogs, past specs) should be left alone unless they
  contain factually incorrect operational guidance that someone might follow today.
- **Do not duplicate the manual.** Where the wiki covers the same ground, it
  should add value: deeper explanations, worked examples, troubleshooting tips,
  community experience, or context the manual omits.
- **Verify against primary sources.** Cross-referencing means reading the
  manual and source code to ensure wiki content is correct — not mechanically
  adding links everywhere. Link to the manual only when it is genuinely
  worthwhile for the reader.
- **JIRA is a last resort.** The JIRA database contains a mix of ancient and
  current content and is not a reliable general reference. Only consult JIRA
  when investigating a specific bug, confirming whether an issue was fixed, or
  tracing the history of a particular change. Do not treat it as a routine
  source of truth.

---

## Phase 1 — Audit & Classification

**Goal:** Review every wiki page and classify it into one of several action
categories. Produce a master inventory spreadsheet/table.

### Step 1.1 — Categorize every wiki page by topic area

Assign each of the ~359 wiki pages to one (or more) of the following topic areas:

| Topic Area | Description |
|---|---|
| **Installation & Setup** | Building, installing, configuring Lustre from scratch |
| **LNet / Networking** | LNet configuration, multi-rail, routers, InfiniBand, self-test |
| **Storage Backends (ZFS/ldiskfs)** | ZFS tuning, ldiskfs, OSD internals, storage design |
| **Striping & Layouts** | File striping, PFL, DoM, layout enhancements |
| **High Availability & Failover** | Pacemaker, DRBD, failover configuration |
| **Monitoring & Performance** | Monitoring tools, statistics, tuning, benchmarks |
| **Administration & Operations** | Day-to-day ops: mounting, quotas, pools, labels, upgrades |
| **Troubleshooting & Debugging** | Debugging procedures, evictions, error handling, LFSCK |
| **Security** | Shared secret key, nodemap, GSS, Kerberos |
| **HSM & Tiering** | HSM, Robinhood, policy engines |
| **Testing** | Test suites, test descriptions, testing how-tos |
| **Development & Contributing** | Coding style, Gerrit, patch submission, code review |
| **Architecture & Design Docs** | HLDs, scope statements, solution architectures |
| **Conferences & Events** | LUG, Developer Days, workshops, meeting minutes |
| **Changelogs & Releases** | Version changelogs, release information |
| **Meta / Organizational** | Wiki migration, categorization, terms of service, infrastructure |
| **Deprecated / Obsolete** | Pages about removed features (e.g., LibLustre) or dead projects |

### Step 1.2 — Classify each page by action needed

For each page, assign one of these action labels:

| Action | Meaning |
|---|---|
| **PRESERVE** | Historical/archival page (conference, meeting minutes, changelog, old spec). Leave as-is. |
| **REVISE** | Page covers a relevant, current topic but has stale, incorrect, or incomplete content. Needs updating. |
| **MERGE** | Page is redundant with another page on the same topic. Content should be consolidated. |
| **CULL** | Page is irrelevant, overly vendor-specific (e.g., Intel Manager for Lustre marketing), or adds no value. Mark for removal or archival. |
| **KEEP** | Page is current, accurate, and useful. No changes needed (or only trivial fixes). |

### Step 1.3 — Identify duplicate / near-duplicate page clusters

Several pages appear to cover the same ground. Examples spotted on first pass:

- `FAQ.txt` / `Frequently_Asked_Questions.txt` / `Frequently_Asked_Questions_(Old_Wiki).txt`
- `How_To.txt` / `How_Tos.txt` / `HowTo.txt`
- `Compiling.txt` / `Compiling_Lustre.txt` / `Building_Lustre_Code.txt` / `Building_and_Installing_Lustre_from_Source_Code.txt`
- `ZFSjbodMonitoring.txt` / `ZFS_JBOD_Monitoring.txt`
- `Zfs_system_design.txt` / `ZFS_System_Design.txt`
- `LNet_Router_Config_Guide.txt` / `LNet_Router_Config_Guide2.txt` / `LNet_Router_Config_Guide_(HPDD_Link).txt`
- `Lustre_Monitoring_and_Statistics_Guide.txt` / `Lustre_Monitoring_and_Statistiscs_Guide.txt` (typo duplicate)
- `Multi-Rail_LNet.txt` / `Multi-rail_lnet.txt`
- `Lustre_Internals.txt` / `Lustre_Internals_(Old).txt` / `Understanding_Lustre_Internals.txt`
- `Dynamic_LNET_Configuration.txt` / `Dynamic_LNet_Configuration_and_lnetctl.txt`
- `Simple_Gerrit_Builder_Howto.txt` / `SimpleGerritBuilderHowto.txt`
- `Test_Descriptions.txt` / `TestDescriptions.txt`

These clusters need to be resolved — typically by merging the best content
into one canonical page.

### Deliverable

A single table (TSV or Markdown) with columns:
`filename | topic_area | action | merge_target | notes`

---

## Phase 2 — Gap Analysis (Wiki vs. Manual)

**Goal:** Identify topics well-covered by the manual that have no corresponding
wiki deep-dive, and topics where the wiki could add significant value beyond
what the manual provides.

### Step 2.1 — Map manual chapters to existing wiki pages

For each of the 47 manual chapters, list which wiki pages (if any) cover the
same or related material. Flag chapters where:

- The wiki has **no coverage** and a deep-dive would add value.
- The wiki has coverage but it **contradicts** the manual.
- The wiki has coverage that is **stale** relative to the manual.

### Step 2.2 — Identify missing wiki pages

Based on the gap analysis, propose new wiki pages that would genuinely help
the community. These are NOT copies of manual chapters — they are deeper
treatments, worked examples, or practical guides. Potential candidates:

- Modern LNet multi-rail configuration cookbook (with real-world examples)
- ZFS tuning guide consolidated from the scattered ZFS pages
- Quota administration deep-dive and troubleshooting
- Modern client mount options reference and tuning
- DNE (Distributed Namespace) practical guide
- Lustre on cloud / container environments guide
- Encryption at rest / in transit guide (if supported in current Lustre)
- PCC (Persistent Client Cache) practical guide
- Modern upgrade procedures (2.14 → 2.15 → 2.16+)

### Deliverable

A table: `manual_chapter | wiki_pages_covering | gap_type | proposed_action`

---

## Phase 3 — Produce the Master Work List

**Goal:** Combine Phase 1 and Phase 2 outputs into a single, prioritized work
list organized by topic area.

### Step 3.1 — Build the work list

For each topic area, list:

1. **Pages to REVISE** (with specific notes on what needs fixing)
2. **Page clusters to MERGE** (which pages, into what target)
3. **Pages to CULL** (with justification)
4. **New pages to CREATE** (with scope description)

### Step 3.2 — Prioritize by impact

Order topic areas by how much user-facing impact the work will have:

1. Installation & Setup (first thing new users hit)
2. Administration & Operations (daily use)
3. Storage Backends — ZFS/ldiskfs (critical and currently scattered)
4. LNet / Networking (complex, often misconfigured)
5. Troubleshooting & Debugging (high-value reference)
6. Striping & Layouts (PFL/DoM — modern features, poor docs)
7. High Availability & Failover (complex setup)
8. Monitoring & Performance (tuning guides)
9. Security (growing importance)
10. HSM & Tiering
11. Testing (developer audience)
12. Development & Contributing (developer audience)
13. Meta / Organizational (low priority, housekeeping)
14. Conferences & Events (PRESERVE — no work needed)
15. Changelogs & Releases (PRESERVE — no work needed)
16. Architecture & Design Docs (PRESERVE — no work needed unless misleading)
17. Deprecated / Obsolete (CULL or label clearly)

### Deliverable

The master work list, organized by topic area, ready for execution.

---

## Phase 4 — Execute Revisions by Topic Area

**Goal:** For each topic area (in priority order), research and produce the
actual wiki page content.

### Workflow per topic area

For each topic area:

1. **Read the relevant manual chapters** in `manual/txt/` to establish the
   authoritative baseline.
2. **Read the existing wiki pages** for that topic to understand current state.
3. **Grep the Lustre source code** in `code/lustre-release/` to verify
   commands, parameters, proc entries, module options, and default values.
4. **Write or revise the wiki page(s)** in `wiki/txt/` (plain text) and
   `wiki_in_wikitext/txt/` (MediaWiki markup) simultaneously.
5. **(If needed) Check JIRA** — only for specific bugs, confirming whether an
   issue was fixed, or tracing the history of a particular change. Do not
   routinely scan JIRA for every topic.
6. **Link sparingly:** Add links to the manual or other wiki pages only when
   genuinely useful to the reader — not as a mechanical exercise.

### Quality checks per page

- [ ] All `lctl` commands verified against current source
- [ ] All proc/sys paths verified against current source
- [ ] All module parameters verified against current source
- [ ] All default values verified against current source
- [ ] No contradiction with the Lustre Manual
- [ ] No vendor-specific or product-specific content unless clearly labeled
- [ ] Links to manual or other wiki pages included only where genuinely useful

### Deliverable

Revised/new wiki page files in both `wiki/txt/` and `wiki_in_wikitext/txt/`.

---

## Phase 5 — Cleanup & Final Review

**Goal:** Handle merges, culling, and a final consistency pass.

### Step 5.1 — Execute merges

For each MERGE cluster identified in Phase 1:

1. Determine the canonical page name.
2. Consolidate all unique content into the canonical page.
3. Replace the redundant pages with a redirect notice or remove them.

### Step 5.2 — Execute culls

For each CULL page:

1. Verify the page truly has no ongoing value.
2. Either remove the file or add a clear deprecation notice at the top.

### Step 5.3 — Final consistency review

- Verify any cross-references between wiki pages are valid.
- Verify any references to manual chapters are accurate.
- Spot-check a sample of revised pages against the source code one more time.

### Deliverable

Clean, consistent wiki with no orphaned links, no redundant pages, and no
vendor-specific marketing content.

---

## Summary of Phases

| Phase | Description | Depends On |
|---|---|---|
| **1** | Audit & Classification — review all 359 pages | — |
| **2** | Gap Analysis — wiki vs. manual | Phase 1 |
| **3** | Master Work List — prioritized by topic | Phases 1 & 2 |
| **4** | Execute Revisions — topic by topic | Phase 3 |
| **5** | Cleanup & Final Review | Phase 4 |

---

## Notes

- Phases 1–3 are planning phases. No wiki content is modified.
- Phase 4 is the bulk of the work. Each topic area is a self-contained unit
  of work that can be reviewed independently.
- The user (Rick) will review and approve the plan after Phase 3 before any
  content modifications begin.
- All content changes will be verified against primary sources (manual, code,
  JIRA). No guessing.
