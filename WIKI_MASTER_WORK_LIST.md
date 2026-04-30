# Lustre Wiki — Master Work List

This is the prioritized, actionable work list for the wiki modernization project.
It combines the Phase 1 audit and Phase 2 gap analysis into a single plan
organized by topic area, in priority order.

**Legend:**
- **REVISE** — Update existing page with verified content
- **MERGE** — Consolidate redundant pages into a canonical page
- **CULL** — Remove redirect stubs, empty pages, or irrelevant content
- **CREATE** — Write a new wiki page (verified against manual + code)

---

## 0. Getting Started & Introductory Content (TOP PRIORITY)

*The wiki's biggest gap. There is currently NO coherent path for a new Lustre
administrator. Lustre_101 is just links to decade-old slides. How_To is an
unsorted link dump mixing beginner and advanced topics. Main_Page doesn't
guide newcomers. A new admin has no front door.*

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_Getting_Started.txt | The front door. "You're new to Lustre. Here's where to start." Ordered reading list linking to architecture, quick start, sizing, and deployment pattern pages. Replaces the broken promise of Lustre_101. |
| Lustre_Quick_Start_Guide.txt | End-to-end tutorial: set up a minimal 3-node Lustre filesystem (1 combined MGS/MDS + 1 OSS + 1 client) on VMs or bare metal. Real commands, real output, real verification. Modern OS (EL8/9, Rocky, Alma). |
| Lustre_Architecture_for_Admins.txt | Visual, conceptual overview for operators. What is an MDT/OST/MGS, how do RPCs flow, what is LNet, what are the failure domains, what breaks and what recovers. Bridges Introduction_to_Lustre to operational reality. |
| Lustre_Hardware_Sizing_Guide.txt | Worked sizing examples: "I have X users, Y TB — here's how to size MDTs, OSTs, and network." Decision trees for RAID config, SSD vs HDD, NVMe for MDT. |
| Lustre_Deployment_Patterns.txt | Common reference architectures: small (1 MDS + 2 OSS), medium (HA pair + 8 OSS), large (DNE + 100 OSS). What to co-locate, what to separate, when to add MDTs. |
| Lustre_Common_Mistakes.txt | Collected from community experience: wrong LNet config, striping too wide, not backing up MDT, writeconf destroying pool info, running client on server, port 988 blocked, etc. |

### REVISE
| Page | Issues |
|------|--------|
| Lustre_101.txt | Currently just links to 2015-2016 ORNL slides. Should either be rewritten as true introductory content or replaced by a redirect to Lustre_Getting_Started. |
| How_To.txt | Unsorted link dump mixing beginner and advanced topics. Needs reorganization with skill-level indicators and current/deprecated labels. |
| Main_Page.txt | Portal page that doesn't guide newcomers. Needs a prominent "New to Lustre? Start here" section linking to the Getting Started path. |

---

## 1. Installation & Setup

*First thing new users encounter. Several key pages are stuck in CentOS 7 / RHEL 5 era.*

### REVISE
| Page | Issues |
|------|--------|
| Installing_the_Lustre_Software.txt | YUM repos reference el7 only; needs el8/el9 coverage |
| KVM_Quick_Start_Guide.txt | Uses CentOS 7 as primary target (EOL) |
| Create_a_Virtual_HPC_Storage_Cluster_with_Vagrant.txt | Fedora 25, VirtualBox 5.1, CentOS 7, Vagrant 1.9.4 |
| Virtualization.txt | Missing link to Lustre_with_Virtualbox_install |
| Configuring_the_Lustre_File_System.txt | 2009 content; obsolete modprobe.conf, broken URLs |
| Operating_System_Configuration_Guidelines_For_Lustre.txt | RHEL 7 only; needs RHEL 8/9, modern kernel naming |
| Lustre_with_ZFS_Install.txt | Targets CentOS 7, stale SPL references |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| Building_and_Installing_Lustre_from_Source_Code.txt | Compiling_Lustre.txt | Self-labeled "extremely out of date" |
| Building_Lustre_Code.txt | Compiling_Lustre.txt | 2009 content, fully covered |
| Compiling.txt | Compiling_Lustre.txt | Unfinished guide, empty stubs |
| Installing_Lustre_from_Downloaded_RPMs.txt | Installing_the_Lustre_Software.txt | 2010, Oracle refs |
| Lustre_Clients_Overview.txt | Introduction_to_Lustre.txt | 15-line subset |

### CULL
| Page | Reason |
|------|--------|
| Preparing_to_Install_Lustre.txt | 2010, RHEL 5.4, all dead URLs |
| Getting_Started.txt | Single-sentence placeholder, never written |
| Debian_Install.txt | Debian Etch/Lenny, kernel 2.6.18 |
| Patchless_Client.txt | Lustre 1.6.0 era; all modern clients are patchless |
| Using_Xen_with_Lustre.txt | 2009 Xen/RHEL5, Xen obsolete in HPC |

---

## 2. Administration & Operations

*Day-to-day ops — some critical pages are dangerously outdated.*

### REVISE
| Page | Issues |
|------|--------|
| Upgrading_to_a_New_Version_of_Lustre.txt | **CRITICAL** — only covers Lustre 1.6→1.8. Needs complete rewrite for 2.x upgrades |
| Managing_Free_Space.txt | 2009; /proc paths (now /sys), tagged NeedsReview |
| Working_with_File_System_Labels.txt | 2009; fsname limits need verification |
| Creating_and_Managing_OST_Pools.txt | 2010; obsolete 1.6/1.8 compat notes |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_File_System_Expansion.txt | Adding MDTs/OSTs: step-by-step with pre/post checks and space-rebalancing |
| Lustre_OST_MDT_Removal.txt | Deactivating, removing, and restoring MDTs/OSTs safely |
| Lustre_Configuration_Log_Management.txt | writeconf, replace_nids, clear_conf — worked examples to prevent data loss |
| Lustre_Upgrade_Checklist.txt | Practical checklist for 2.x upgrades with rollback guidance |
| Lustre_Backup_Strategies.txt | File-level vs device-level vs lustre_rsync — decision tree |
| Lustre_Rsync_Replication.txt | lustre_rsync deployment guide with changelog user management |
| Lustre_Day_to_Day_Operations.txt | Quick-reference cheat sheet: startup/shutdown, mount/unmount sequences |
| Lustre_Striping_Best_Practices.txt | When/how to stripe, matching I/O patterns, HPC vs small-files examples |
| Lustre_Quota_Administration.txt | Worked examples for user/group quotas, default quotas, grace period tuning |
| Lustre_Project_Quotas.txt | Project quotas: per-directory assignment, version interop, practical examples |
| Lustre_OST_Pool_Management.txt | Pool creation/management, tiered storage, rack-aware placement |

### CULL
| Page | Reason |
|------|--------|
| Managing_OSTs.txt | Pure link page, no original content |
| Lustre_System_Configuration_Utilities.txt | 2010, all dead links, covered by manual |

---

## 3. Storage Backends — ZFS/ldiskfs

*Critical topic area with scattered, stale content. ZFS tunables pages reference removed parameters.*

### REVISE
| Page | Issues |
|------|--------|
| ZFS_Tunables_for_Lustre_Metadata_Servers_(MDS).txt | References removed zfs_vdev_scheduler, defunct SPL man page, only 4 tunables |
| ZFS_Tunables_for_Lustre_Object_Storage_Servers_(OSS).txt | Same issues as MDS tunables |
| ZFS_System_Design.txt | DRAID section "to be continued" — never completed |
| ZFS_OSD.txt | References completed features as future work |
| ZFS_OSD_Hardware_Considerations.txt | Recommends Intel Xeon E5 26xx (2-3 gen old) |
| ZFS_Versions_in_Official_Lustre_Releases.txt | Missing releases after mid-2023 |
| ZFS_JBOD_Monitoring.txt | 2016; outdated scripts, no modern monitoring integration |
| ZFS_MDT_ENOSPC_Recovery.txt | "As of 2.10" — needs version-gating update |
| Introduction_to_Lustre_Object_Storage_Devices_(OSDs).txt | DRAID listed as "(future)" — has since landed |
| Configuring_RAID_for_Disk_Arrays.txt | RHEL 4/5, broken URLs, needs full rewrite for modern OS |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| ZFS_recordsize_Property.txt | ZFS_OSD_Storage_Basics.txt | 10 lines, covered elsewhere |
| Optimizing_Performance_of_SSDs_and_Advanced_Format_Drives.txt | ZFS_OSD_Storage_Basics.txt | Short ashift-only page |

### CULL
| Page | Reason |
|------|--------|
| ZFSjbodMonitoring.txt | Redirect |
| Zfs_system_design.txt | Redirect |
| Architecture_-_ZFS_for_Lustre.txt | Redirect |

---

## 4. LNet / Networking

*Complex, often misconfigured. Multi-Rail page is still a placeholder despite feature shipping in 2017.*

### REVISE
| Page | Issues |
|------|--------|
| Multi-Rail_LNet.txt | **CRITICAL** — still a project-planning placeholder. Feature shipped in Lustre 2.10 (2017). Needs complete rewrite as operational documentation |
| Dynamic_LNet_Configuration_and_lnetctl.txt | Treats Lustre 2.7 DLC as "new" |
| Static_LNet_Configuration.txt | Should note DLC is now preferred method |
| Starting_and_Stopping_LNet.txt | Refers to lnetctl as new, RHEL 7 era |
| LNet_Router_Config_Guide.txt | Intel OPA refs (legacy/EOL), needs health/sensitivity features |
| Lustre_Resiliency__Understanding_Lustre_Message_Loss_and_Tuning_for_Resiliency.txt | Cray-specific, needs generalization |
| Infiniband_Configuration_Howto.txt | 2.8/2.9 patches, stale URLs, FMR/PMR outdated |
| Optimizing_o2iblnd_Performance.txt | Heavily Intel OPA-focused (EOL hardware) |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| Dynamic_LNET_Configuration.txt | Dynamic_LNet_Configuration_and_lnetctl.txt | Stub with JIRA link only |
| LNET_Router.txt | LNet_Router_Config_Guide.txt | Stub with dead links |

### CULL
| Page | Reason |
|------|--------|
| LNet_Router_Config_Guide2.txt | Redirect |
| LNet_Router_Config_Guide_(HPDD_Link).txt | Two-sentence pointer |
| Multi-rail_lnet.txt | One-line redirect |

---

## 5. Troubleshooting & Debugging

*High-value reference material, but all debugging pages have 2010-era dead links.*

### REVISE
| Page | Issues |
|------|--------|
| Lustre_Debugging_Procedures.txt | 2010; dead LustreManual20_HTML URLs, /proc paths |
| Lustre_Debugging_for_Developers.txt | 2011; LWT tracing may be removed, dead links |
| Diagnostic_and_Debugging_Tools.txt | 2010; stale tool refs (Sun VirtualBox, VMware Server 2.0) |
| Handling_File_System_Errors.txt | 2010; dead links, should reference current LFSCK |
| Wireshark.txt | Only LUG 2013 ref; needs current plugin status |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_Client_Eviction_Guide.txt | Causes of eviction, practical debugging steps, timeout tuning, remediation |
| Lustre_Recovery_Overview.txt | Unified overview: VBR, commit-on-share, metadata replay, imperative recovery |

### CULL
| Page | Reason |
|------|--------|
| Debugging_Lustre.txt | Empty TOC stub |
| Understanding_Lustre_Evictions.txt | Single-line redirect |

---

## 6. Striping & Layouts (PFL/DoM/FLR)

*Modern features with generally good design docs but gaps in operational guidance.*

### REVISE
| Page | Issues |
|------|--------|
| (No pages need revision — design docs are current) | |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_FLR_Operations.txt | lfs mirror create/extend/split/resync/verify how-to. When FLR vs RAID, resync automation. |
| Lustre_DoM_Operations.txt | Data on MDT practical guide: sizing impact, workload characterization, migration. |

### CULL
| Page | Reason |
|------|--------|
| Pfl2-lfs-setstripe.1.txt | Draft man page; real man pages ship with source |
| Layout_Enhancement.txt | Redirect stub |
| Lock_ahead.txt | Stub with dead links |
| DNE_Phase_IIb.txt | Stub with dead opensfs.org links |

---

## 7. High Availability & Failover

*Complex setup. All Pacemaker pages reference RHEL 6/7 (both EOL).*

### REVISE
| Page | Issues |
|------|--------|
| Creating_a_Framework_for_High_Availability_with_Pacemaker.txt | RHEL 6/7 (EOL); needs RHEL 8/9 and Corosync v3 |
| Creating_Pacemaker_Resources_for_Lustre_Storage_Services.txt | Lustre 2.10 era agents; RA availability may have changed |
| Lustre_Server_Fault_Isolation_with_Pacemaker_Node_Fencing.txt | RHEL 6 refs; fence agents need updating for Redfish |
| Managing_Lustre_with_the_ZFS_backend_as_a_High_Availability_Service.txt | Title misleading (covers both backends) |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| Configuring_Lustre_for_Failover.txt | Creating_a_Framework_for_High_Availability_with_Pacemaker.txt | 2010 stub |
| Managing_Lustre_as_a_High_Availability_Service.txt | (already a redirect — just cull) | |

### CULL
| Page | Reason |
|------|--------|
| Managing_Lustre_as_a_High_Availability_Service.txt | Redirect stub |
| DRBD_and_Lustre.txt | Unverified benchmarks, no practical guidance |

---

## 8. Monitoring & Performance

*Monitoring guide is good but needs modernization. ZFS tunables are stale.*

### REVISE
| Page | Issues |
|------|--------|
| Lustre_Tuning.txt | 2019; references 1.4.7-era params, needs modern NVMe/large-memory guidance |
| Lustre_Monitoring_and_Statistics_Guide.txt | 2023; needs 2.15+ parameter paths |
| Integrated_Manager_for_Lustre.txt | 2018; repo may be archived, needs status update |
| Server_Side_Advise_and_Hinting.txt | Sparse stub; feature exists since 2.9 but no usage docs |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_Health_Checks.txt | How to know if your Lustre filesystem is healthy: lctl params, lfs df, target status |
| Lustre_IO_Monitoring.txt | Deep-dive on rpc_stats, brw_stats, llite.*.stats — interpretation and worked examples |
| Lustre_NRS_Configuration.txt | Network Request Scheduler policies: FIFO, CRR-N, ORR, TRR, TBF, Delay |
| Lustre_Service_Thread_Tuning.txt | OSS/MDS thread counts, CPT binding, IRQ affinity |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| InfluxDB.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Sparse hub, incomplete |
| MDT_metrics.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Raw key tables |
| OST_metrics.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Raw key tables |

### CULL
| Page | Reason |
|------|--------|
| Lustre_Monitoring_and_Statistiscs_Guide.txt | Typo-fix redirect |
| Monitoring.txt | Category redirect |
| University_of_Wisconsin_Check_MK_Graphite_Graphios_Setup_Guide.txt | Redirect |
| University_of_Wisconsin_Setup_Guide.txt | Blanked page |
| Crawler_script.txt | Raw undocumented script with site-specific IPs |

---

## 9. Security

*Growing importance. Wiki coverage is thin — missing encryption, SELinux, modern SSK.*

### REVISE
| Page | Issues |
|------|--------|
| Setting_up_Lustre_Security.txt | Extremely thin — only ACLs/root squash. Missing SSK, nodemaps, encryption, SELinux |
| Shared_Secret_Key_Authentication_And_Encryption.txt | Dead opensfs/hpdd links; needs current setup instructions |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_Client_Encryption.txt | fscrypt-based encryption: key management, access semantics, limitations, performance |
| Lustre_Kerberos_SSK_Authentication.txt | Step-by-step SSK and Kerberos setup guide |
| Lustre_Multi_Tenancy.txt | End-to-end tenant isolation with nodemaps and filesets |

---

## 10. HSM & Tiering

### REVISE
| Page | Issues |
|------|--------|
| Robinhood_Policy_Engine.txt | 2016; should note v3/v4 status and successors (LiPE) |

### CREATE
| Proposed Page | Scope |
|---------------|-------|
| Lustre_HSM_Setup.txt | End-to-end HSM deployment: coordinator, copytool, archive backends, request monitoring |
| Lustre_HSM_Policy_Automation.txt | Policy engine integration, changelog-driven automation, file state management |

---

## 11. Testing

*Mostly in good shape thanks to recent 2024-2025 updates.*

### REVISE
| Page | Issues |
|------|--------|
| Acceptance_Small_(acc-sm)_Testing_on_Lustre.txt | Test lists reference b1_6/b1_8/HEAD circa 2010 |
| Testing_HOWTO.txt | 2018; CentOS 7.1, old Whamcloud URLs |
| Test_Descriptions.txt | 2020; suite status may have changed |
| Test_Groups_for_Patch_Testing.txt | 2021; test group composition likely changed |
| POSIX_Compliance_Testing.txt | 2016; gcc 2.96/3.x toolchains, broken URLs |

### CULL
| Page | Reason |
|------|--------|
| TestDescriptions.txt | CamelCase redirect |

---

## 12. Development & Contributing

*Core pages are well-maintained. Some stale satellite pages.*

### REVISE
| Page | Issues |
|------|--------|
| Development.txt | Some stale opensfs URLs |
| Submitting_Changes.txt | 2020; some dead URLs |
| Simple_Gerrit_Builder_Howto.txt | 2019; stale links |
| Subsystem_Map.txt | 2008; code paths very outdated |
| Finding_a_Project.txt | References Bugzilla |
| Reporting_Bugs.txt | One Bugzilla reference |
| Logging_API.txt | 2009; llog API very outdated |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| Contribute.txt | Development.txt | Stale duplicate |
| Lustre_Style_Guide_Includes.txt | Lustre_Coding_Style_Guidelines.txt | 16 lines |
| Signed-off-by.txt | Commit_Comments.txt | Short DCO text |
| Lustre_Internals.txt | Understanding_Lustre_Internals.txt | Stub |

### CULL
| Page | Reason |
|------|--------|
| Lustre_Coding_Guidelines.txt | Redirect |
| SimpleGerritBuilderHowto.txt | Redirect |
| Upstream_contributing.txt | Redirect |

---

## 13. Meta / Organizational

*Low priority — housekeeping.*

### REVISE
| Page | Issues |
|------|--------|
| GetInvolved_Get_Involved.txt | Dead links to Bull, Juelich, SourceForge |
| Mailing_Lists_and_IRC.txt | Title says IRC but content has Slack |
| How_To.txt | Some linked pages may be stale |
| Download.txt | 2016; sparse, outdated |

### MERGE
| Page | Into | Notes |
|------|------|-------|
| Frequently_Asked_Questions_(Old_Wiki).txt | Frequently_Asked_Questions.txt | Old wiki FAQ |
| Lustre_Software_Releases.txt | Lustre_Release_Information.txt | Stale duplicate |

### CULL
| Page | Reason |
|------|--------|
| Communication.txt | Redirect |
| FAQ.txt | Redirect |
| HowTo.txt | Redirect |
| How_Tos.txt | Redirect |
| Lustre_Wiki.txt | Redirect |
| Learn_Learn.txt | Oracle/Sun dead content |
| Terms_of_Service.txt | Placeholder since 2015 |
| Test_page.txt | Blanked in 2022 |
| Lustre_Internals_(Old).txt | Redirect |
| Lustre_Internals_Documentation_Update.txt | Stale TODO |
| Understanding_Lustre_Internals_TESTS.txt | Blanked |
| Intel_Manager_for_Lustre.txt | Redirect |
| Intel_Web-Based_Training.txt | Dead Intel links |
| Metadata_Writeback_Cache.txt | Empty stub since 2019 |
| File_Level_Replication_Phase_1.txt | Redirect |
| Trash_Can_Undelete.txt | Redirect |
| Past_Events.txt | Dead redirect |

---

## 14-17. No Work Required

These topic areas require no wiki modifications:

- **Conferences & Events** (~37 pages) — All PRESERVE
- **Changelogs & Releases** (~57 pages) — All PRESERVE/KEEP except redirect stubs already listed
- **Architecture & Design Docs** (~30 pages) — All PRESERVE/KEEP (LFSCK, PFL, FLR, etc.)
- **Deprecated / Obsolete** — Handled via CULL entries above

---

## Summary — Work Items by Type

| Type | Count | Description |
|------|-------|-------------|
| REVISE | 55 | Update stale content, verify against manual + code |
| MERGE | 19 | Consolidate redundant pages |
| CULL | 51 | Remove redirect stubs, empty pages, dead content |
| CREATE | 30 | New wiki pages filling gaps |
| **Total** | **155** | |

---

### New Pages to Create (30)

The original 7 proposed pages were scoped too broadly. Each would have been
massive. These have been split into focused, manageable pages, and significant
new introductory content has been added to address the wiki's complete lack
of a new-user on-ramp.

#### Getting Started & Introductory (6 pages — HIGHEST PRIORITY)

These pages do not exist in any form on the wiki today. A new Lustre
administrator currently has no coherent path from "what is this?" to
"I have a working filesystem."

| # | Proposed Page | Scope |
|---|---------------|-------|
| 1 | **Lustre_Getting_Started.txt** | The front door. "You're new. Read these pages in this order." Links to the learning path below. Replaces the broken promise of Lustre_101 and the unsorted How_To page. |
| 2 | **Lustre_Quick_Start_Guide.txt** | End-to-end tutorial: set up a minimal 3-node Lustre filesystem (1 MGS/MDS + 1 OSS + 1 client) on VMs or bare metal. Actual commands, actual output, actual verification. Modern OS (EL8/9). |
| 3 | **Lustre_Architecture_for_Admins.txt** | Visual, conceptual overview aimed at operators (not developers). What is an MDT/OST/MGS, how do RPCs flow, what are the failure domains. Bridges Introduction_to_Lustre (which is dev-focused) to operational reality. |
| 4 | **Lustre_Hardware_Sizing_Guide.txt** | Worked sizing examples: "I have X users, Y TB — here's how to size MDTs, OSTs, and network." Decision trees for RAID config, SSD vs HDD, NVMe for MDT. From manual's SettingUpLustreSystem chapter but with practical examples. |
| 5 | **Lustre_Deployment_Patterns.txt** | Common reference architectures: small (1 MDS + 2 OSS), medium (HA pair + 8 OSS), large (DNE + 100 OSS). What to co-locate, what to separate, when to add MDTs. |
| 6 | **Lustre_Common_Mistakes.txt** | Collected from community experience: wrong LNet config, striping too wide for small files, not backing up MDT, writeconf destroying pool info, running client on server node, port 988 blocked, etc. |

#### Administration & Operations (8 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 7 | **Lustre_File_System_Expansion.txt** | Adding MDTs and OSTs: step-by-step with pre/post checks and space-rebalancing guidance. From LustreMaintenance. |
| 8 | **Lustre_OST_MDT_Removal.txt** | Deactivating, removing, and restoring MDTs and OSTs. High-stakes operation that needs clear, safe procedures. From LustreMaintenance. |
| 9 | **Lustre_Configuration_Log_Management.txt** | writeconf, replace_nids, clear_conf — destructive commands that need worked examples to prevent data loss. From LustreMaintenance. |
| 10 | **Lustre_Upgrade_Checklist.txt** | Practical checklist for 2.x upgrades: pre-upgrade validation, rolling upgrade steps, optional feature enablement, rollback guidance. From UpgradingLustre. |
| 11 | **Lustre_Backup_Strategies.txt** | Overview: file-level vs. device-level vs. lustre_rsync. When to use what. MDT backup importance. From BackupAndRestore. |
| 12 | **Lustre_Rsync_Replication.txt** | lustre_rsync deployment guide: changelog user management, multi-MDT considerations, error recovery. From BackupAndRestore. |
| 13 | **Lustre_Day_to_Day_Operations.txt** | Quick-reference cheat sheet: startup/shutdown order, mount/unmount sequences, common gotchas (mount-by-label with multipath, noauto + HA). From LustreOperations. |
| 14 | **Lustre_Striping_Best_Practices.txt** | When to stripe, how wide, matching I/O patterns. Worked examples for HPC sequential vs. many-small-files workloads. Strategy guidance the manual doesn't provide. |

#### Monitoring & Performance (4 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 15 | **Lustre_Health_Checks.txt** | "How do I know my Lustre filesystem is healthy?" Integrating lctl parameters, lfs df, target status checks, and external monitoring setup. |
| 16 | **Lustre_IO_Monitoring.txt** | Deep-dive on rpc_stats, brw_stats, llite.*.stats — what each field means, how to interpret, worked examples. From LustreProc. |
| 17 | **Lustre_NRS_Configuration.txt** | Network Request Scheduler policies (FIFO, CRR-N, ORR, TRR, TBF, Delay). The NRS section alone is ~800 lines in the manual. Needs dedicated coverage with policy selection guidance. |
| 18 | **Lustre_Service_Thread_Tuning.txt** | OSS/MDS thread counts, CPT binding, IRQ affinity. Standalone tuning page from LustreTuning. |

#### Security (3 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 19 | **Lustre_Client_Encryption.txt** | fscrypt-based client-side encryption: key management, access semantics, limitations, performance impact. New feature needing practical docs. |
| 20 | **Lustre_Kerberos_SSK_Authentication.txt** | Step-by-step SSK and Kerberos setup guide. Combines ManagingSecurity + LustreSharedSecretKey content. |
| 21 | **Lustre_Multi_Tenancy.txt** | End-to-end tenant isolation with nodemaps and filesets: UID/GID mapping, root squash, subdirectory mounts, multiple filesets (2.17+). |

#### Quota (3 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 22 | **Lustre_Quota_Administration.txt** | Worked examples for user/group quotas, default quotas, grace period tuning. Real-world "multi-department HPC center" workflow. |
| 23 | **Lustre_Project_Quotas.txt** | Project quotas: per-directory assignment via lfs project, version interop, practical examples. Enough for a standalone page. |
| 24 | **Lustre_OST_Pool_Management.txt** | OST pool creation/management, use cases (tiered storage, rack-aware placement, FLR fault domains). Currently scattered across multiple pages. |

#### HSM (2 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 25 | **Lustre_HSM_Setup.txt** | End-to-end HSM deployment walkthrough: coordinator, copytool, archive backends, request monitoring. |
| 26 | **Lustre_HSM_Policy_Automation.txt** | Policy engine integration, changelog-driven automation, file state management. |

#### Recovery & Troubleshooting (2 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 27 | **Lustre_Client_Eviction_Guide.txt** | Causes of eviction, practical debugging steps, timeout tuning, remediation. The #1 troubleshooting topic for admins. |
| 28 | **Lustre_Recovery_Overview.txt** | Unified overview of recovery mechanisms: VBR, commit-on-share, metadata replay, imperative recovery. Architectural understanding in one place. |

#### Striping & Layouts (2 pages)

| # | Proposed Page | Scope |
|---|---------------|-------|
| 29 | **Lustre_FLR_Operations.txt** | lfs mirror create/extend/split/resync/verify how-to. When to use FLR vs RAID, resync automation, monitoring mirror state. |
| 30 | **Lustre_DoM_Operations.txt** | Data on MDT practical guide: MDT sizing impact, workload characterization, monitoring DoM usage, migrating files to/from DoM. |

---

## Execution Order

Work proceeds by topic area in the priority order above (1-13). Within each
topic area, the order is: CULL → MERGE → REVISE → CREATE.

- **CULLs first** — remove noise so we can see clearly
- **MERGEs next** — consolidate before revising
- **REVISEs** — update stale content, verified against manual + code
- **CREATEs last** — write new pages from scratch with verified content

**Exception:** The 6 Getting Started pages (items 1-6) should be created
FIRST, before any other topic area work begins. They are the highest-impact
gap and benefit from being written before the existing pages are revised
(so the new pages can link to the revised content as it becomes available).

Each topic area is a self-contained unit of work that can be reviewed
independently before moving to the next.
