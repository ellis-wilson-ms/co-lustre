# Lustre Wiki Audit Inventory

## Summary Statistics

| Action | Count | Description |
|--------|-------|-------------|
| PRESERVE | ~95 | Historical/archival — leave as-is |
| KEEP | ~80 | Current and accurate — no changes needed |
| REVISE | ~55 | Relevant topic, stale/incorrect/incomplete content |
| MERGE | ~15 | Redundant — consolidate into canonical page |
| CULL | ~40 | Redirect stubs, empty pages, vendor-specific, no value |

**Total: ~359 pages**

---

## Pages by Action

### CULL — Remove or Archive (No Value)

These pages are redirect stubs, empty placeholders, vendor-specific marketing,
or completely obsolete content with no salvageable value.

| Filename | Topic Area | Notes |
|----------|-----------|-------|
| Past_Events.txt | Conferences & Events | "Moved to Lustre Conferences" — dead redirect |
| Change_Log_1.6.txt | Changelogs & Releases | #REDIRECT stub |
| Change_Log_1.8.txt | Changelogs & Releases | #REDIRECT stub |
| Change_Log_2.0.txt | Changelogs & Releases | #REDIRECT stub |
| Retired_Release_Terminology.txt | Changelogs & Releases | #REDIRECT to Release_Terminology |
| ZFSjbodMonitoring.txt | Meta / Organizational | #REDIRECT CamelCase artifact |
| Zfs_system_design.txt | Meta / Organizational | #REDIRECT capitalization fix |
| Architecture_-_ZFS_for_Lustre.txt | Meta / Organizational | #REDIRECT to ZFS_OSD |
| LNet_Router_Config_Guide2.txt | LNet / Networking | #REDIRECT to LNet_Router_Config_Guide |
| LNet_Router_Config_Guide_(HPDD_Link).txt | LNet / Networking | Two-sentence pointer, no value |
| Multi-rail_lnet.txt | LNet / Networking | One-line redirect |
| Preparing_to_Install_Lustre.txt | Installation & Setup | 2010, RHEL 5.4 content, all dead URLs |
| Getting_Started.txt | Meta / Organizational | Single-sentence placeholder, never written |
| Debian_Install.txt | Installation & Setup | Debian Etch/Lenny, kernel 2.6.18, Lustre 1.x |
| Patchless_Client.txt | Installation & Setup | Lustre 1.6.0 era; all modern clients are patchless |
| Managing_OSTs.txt | Administration & Operations | Pure link page, no original content |
| Managing_Lustre_as_a_High_Availability_Service.txt | HA & Failover | #REDIRECT stub |
| DRBD_and_Lustre.txt | HA & Failover | Unverified, undated benchmarks, no practical guidance |
| Layout_Enhancement.txt | Architecture & Design Docs | #REDIRECT stub |
| DNE_Phase_IIb.txt | Architecture & Design Docs | Stub with dead opensfs.org links only |
| Lock_ahead.txt | Architecture & Design Docs | Stub with dead links and stale email |
| Lustre_Monitoring_and_Statistiscs_Guide.txt | Meta / Organizational | Typo-fix redirect |
| Monitoring.txt | Meta / Organizational | Redirect to Category:Monitoring |
| University_of_Wisconsin_Check_MK_Graphite_Graphios_Setup_Guide.txt | Meta / Organizational | Redirect, UW endorsement rename |
| University_of_Wisconsin_Setup_Guide.txt | Meta / Organizational | Blanked page, zero content |
| TestDescriptions.txt | Meta / Organizational | CamelCase redirect |
| Crawler_script.txt | Monitoring & Performance | Raw undocumented script, site-specific IPs |
| Debugging_Lustre.txt | Troubleshooting & Debugging | Empty TOC stub, 3 bullet links only |
| Understanding_Lustre_Evictions.txt | Troubleshooting & Debugging | Single-line redirect |
| Lustre_Coding_Guidelines.txt | Development & Contributing | #REDIRECT to Lustre_Coding_Style_Guidelines |
| SimpleGerritBuilderHowto.txt | Development & Contributing | CamelCase redirect |
| Upstream_contributing.txt | Development & Contributing | #REDIRECT |
| Communication.txt | Meta / Organizational | #REDIRECT to Mailing_Lists_and_IRC |
| FAQ.txt | Meta / Organizational | #REDIRECT to Frequently_Asked_Questions |
| HowTo.txt | Meta / Organizational | #REDIRECT to How_To |
| How_Tos.txt | Meta / Organizational | #REDIRECT to How_To |
| Learn_Learn.txt | Meta / Organizational | Lustre 1.8/2.0, Oracle/Sun training, all dead |
| Lustre_Wiki.txt | Meta / Organizational | #REDIRECT to Main_Page |
| Terms_of_Service.txt | Meta / Organizational | Placeholder "being developed" since 2015 |
| Test_page.txt | Meta / Organizational | Blanked in 2022, zero content |
| Lustre_Internals_(Old).txt | Deprecated / Obsolete | Redirect |
| Lustre_Internals_Documentation_Update.txt | Meta / Organizational | Stale TODO list from 2018 |
| Understanding_Lustre_Internals_TESTS.txt | Deprecated / Obsolete | Blanked in 2022 |
| Intel_Manager_for_Lustre.txt | Deprecated / Obsolete | Redirect |
| Intel_Web-Based_Training.txt | Meta / Organizational | Dead Intel training links |
| Using_Xen_with_Lustre.txt | Installation & Setup | 2009 Xen/RHEL5, obsolete |
| Lustre_System_Configuration_Utilities.txt | Administration & Operations | 2010 content, all dead links, covered by manual |
| Metadata_Writeback_Cache.txt | Architecture & Design Docs | Empty stub from 2019, never populated |
| File_Level_Replication_Phase_1.txt | Deprecated / Obsolete | Redirect to HLD |
| Trash_Can_Undelete.txt | Deprecated / Obsolete | Redirect to HLD |
| Pfl2-lfs-setstripe.1.txt | Striping & Layouts | Draft man page, stale; real man pages ship with source |

---

### MERGE — Consolidate into Canonical Pages

| Filename | Merge Into | Notes |
|----------|-----------|-------|
| Lustre_Software_Releases.txt | Lustre_Release_Information.txt | Stale duplicate, last updated 2023 |
| LNET_Router.txt | LNet_Router_Config_Guide.txt | Stub with dead links |
| Dynamic_LNET_Configuration.txt | Dynamic_LNet_Configuration_and_lnetctl.txt | Stub with JIRA link only |
| Configuring_Lustre_for_Failover.txt | Creating_a_Framework_for_High_Availability_with_Pacemaker.txt | 2010 stub with just links |
| Building_and_Installing_Lustre_from_Source_Code.txt | Compiling_Lustre.txt | Self-labeled "extremely out of date" |
| Building_Lustre_Code.txt | Compiling_Lustre.txt | 2009 content, fully covered by Compiling_Lustre |
| Compiling.txt | Compiling_Lustre.txt | Unfinished guide, empty stubs |
| Installing_Lustre_from_Downloaded_RPMs.txt | Installing_the_Lustre_Software.txt | 2010 content, Oracle download references |
| Lustre_Clients_Overview.txt | Introduction_to_Lustre.txt | 15-line subset of Introduction |
| ZFS_recordsize_Property.txt | ZFS_OSD_Storage_Basics.txt | 10 lines, covered elsewhere |
| Optimizing_Performance_of_SSDs_and_Advanced_Format_Drives.txt | ZFS_OSD_Storage_Basics.txt | Short ashift-only page |
| InfluxDB.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Sparse hub, incomplete |
| MDT_metrics.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Raw key tables, no context |
| OST_metrics.txt | Lustre_Monitoring_and_Statistics_Guide.txt | Raw key tables, no context |
| Contribute.txt | Development.txt | Stale duplicate |
| Lustre_Style_Guide_Includes.txt | Lustre_Coding_Style_Guidelines.txt | 16 lines on #include ordering |
| Signed-off-by.txt | Commit_Comments.txt | Short DCO text, already referenced |
| Frequently_Asked_Questions_(Old_Wiki).txt | Frequently_Asked_Questions.txt | Old wiki FAQ, outdated |
| Lustre_Internals.txt | Understanding_Lustre_Internals.txt | Stub with dead links |

---

### REVISE — Update Stale/Incorrect Content

#### Storage Backends (ZFS/ldiskfs)

| Filename | Issues |
|----------|--------|
| ZFS_JBOD_Monitoring.txt | 2016; outdated monitoring scripts, no modern integration (Prometheus/Grafana) |
| ZFS_MDT_ENOSPC_Recovery.txt | 2020; says "as of 2.10", LU-8856 may be resolved |
| ZFS_OSD.txt | 2020; references completed features as future work, "ZFS 0.9" version that never shipped |
| ZFS_OSD_Hardware_Considerations.txt | 2025; recommends Intel Xeon E5 26xx (2-3 gen old) |
| ZFS_System_Design.txt | 2018; DRAID section "to be continued" — never completed |
| ZFS_Tunables_for_Lustre_Metadata_Servers_(MDS).txt | 2018; references removed zfs_vdev_scheduler, defunct SPL man page, only 4 tunables |
| ZFS_Tunables_for_Lustre_Object_Storage_Servers_(OSS).txt | 2018; same issues as MDS tunables |
| ZFS_Versions_in_Official_Lustre_Releases.txt | 2023; missing releases after mid-2023 |
| Introduction_to_Lustre_Object_Storage_Devices_(OSDs).txt | 2022; DRAID listed as "(future)" but has since landed |
| Configuring_RAID_for_Disk_Arrays.txt | 2016/2009; RHEL 4/5, broken URLs, needs full rewrite |
| Lustre_with_ZFS_Install.txt | 2025; targets CentOS 7 (EOL), stale SPL references |

#### LNet / Networking

| Filename | Issues |
|----------|--------|
| Dynamic_LNet_Configuration_and_lnetctl.txt | 2017; treats Lustre 2.7 DLC as "new" |
| Static_LNet_Configuration.txt | 2018; should note DLC is now preferred |
| Starting_and_Stopping_LNet.txt | Refers to lnetctl as new, RHEL 7/3.10 kernel era |
| LNet_Router_Config_Guide.txt | References Intel OPA (legacy/EOL), needs health/sensitivity updates |
| Multi-Rail_LNet.txt | Still a project-planning placeholder; feature shipped in 2.10 (2017), needs complete rewrite |
| Lustre_Resiliency__Understanding_Lustre_Message_Loss_and_Tuning_for_Resiliency.txt | CUG 2015 paper; Cray-specific, needs generalization |
| Infiniband_Configuration_Howto.txt | 2.8/2.9 era patches, stale Whamcloud URLs, FMR/PMR outdated |
| Optimizing_o2iblnd_Performance.txt | Heavily Intel OPA-focused (EOL hardware) |
| Operating_System_Configuration_Guidelines_For_Lustre.txt | RHEL 7 only (EOL), needs RHEL 8/9 |

#### Installation & Setup

| Filename | Issues |
|----------|--------|
| Installing_the_Lustre_Software.txt | 2023; YUM repos reference el7 only |
| KVM_Quick_Start_Guide.txt | 2025; still uses CentOS 7 as primary target |
| Create_a_Virtual_HPC_Storage_Cluster_with_Vagrant.txt | 2025; Fedora 25, VirtualBox 5.1, CentOS 7, Vagrant 1.9.4 |
| Virtualization.txt | 2025; missing link to Lustre_with_Virtualbox_install |
| Configuring_the_Lustre_File_System.txt | 2009; obsolete modprobe.conf, broken URLs |

#### Administration & Operations

| Filename | Issues |
|----------|--------|
| Managing_Free_Space.txt | 2009; /proc/fs/lustre paths (now /sys), tagged NeedsReview |
| Working_with_File_System_Labels.txt | 2009; fsname length limits need verification |
| Upgrading_to_a_New_Version_of_Lustre.txt | Only covers 1.6→1.8 — needs complete rewrite |
| Creating_and_Managing_OST_Pools.txt | 2010; obsolete 1.6/1.8 compat notes |

#### High Availability & Failover

| Filename | Issues |
|----------|--------|
| Managing_Lustre_with_the_ZFS_backend_as_a_High_Availability_Service.txt | Title misleading (covers both backends); needs generalization |
| Creating_a_Framework_for_High_Availability_with_Pacemaker.txt | References RHEL 6/7 (EOL) |
| Creating_Pacemaker_Resources_for_Lustre_Storage_Services.txt | Lustre 2.10 era agents, may have changed |
| Lustre_Server_Fault_Isolation_with_Pacemaker_Node_Fencing.txt | RHEL 6 references, fence agents may need updating |

#### Monitoring & Performance

| Filename | Issues |
|----------|--------|
| Lustre_Tuning.txt | 2019; references 1.4.7-era parameters, overlaps with manual |
| Lustre_Monitoring_and_Statistics_Guide.txt | 2023; originally Lustre 2.4/2.5, needs 2.15+ parameter paths |
| Integrated_Manager_for_Lustre.txt | 2018; GitHub repo may be archived, needs status update |
| Server_Side_Advise_and_Hinting.txt | Sparse stub, feature exists since 2.9 but no usage docs |

#### Troubleshooting & Debugging

| Filename | Issues |
|----------|--------|
| Lustre_Debugging_Procedures.txt | 2010; dead manual links, /proc paths may have changed |
| Lustre_Debugging_for_Developers.txt | 2011; LWT tracing may be removed, dead links |
| Diagnostic_and_Debugging_Tools.txt | 2010; stale tool refs (Sun VirtualBox, VMware Server 2.0) |
| Handling_File_System_Errors.txt | 2010; dead links, should reference LFSCK |
| Wireshark.txt | Brief; only LUG 2013 ref, needs current plugin info |

#### Security

| Filename | Issues |
|----------|--------|
| Setting_up_Lustre_Security.txt | Extremely thin — only ACLs/root squash; missing SSK, nodemaps, encryption |
| Shared_Secret_Key_Authentication_And_Encryption.txt | Dead opensfs/hpdd links, needs current setup instructions |

#### Testing

| Filename | Issues |
|----------|--------|
| Acceptance_Small_(acc-sm)_Testing_on_Lustre.txt | Branch-specific test lists from 2010 |
| Testing_HOWTO.txt | 2018; CentOS 7.1, old Whamcloud URLs |
| Test_Descriptions.txt | 2020; suite status may have changed |
| Test_Groups_for_Patch_Testing.txt | 2021; test group composition likely changed |
| POSIX_Compliance_Testing.txt | 2016; gcc 2.96/3.x toolchains, broken download URLs |

#### Development & Contributing

| Filename | Issues |
|----------|--------|
| Development.txt | 2025; some stale opensfs URLs |
| Submitting_Changes.txt | 2020; some dead URLs in workflow doc |
| Simple_Gerrit_Builder_Howto.txt | 2019; niche but useful, stale links |
| Subsystem_Map.txt | 2008; code paths very outdated |
| Finding_a_Project.txt | 2021; still references Bugzilla |
| Reporting_Bugs.txt | 2021; one Bugzilla reference |
| Logging_API.txt | 2009; llog API internals very outdated |

#### Meta / Organizational

| Filename | Issues |
|----------|--------|
| GetInvolved_Get_Involved.txt | Dead links to Bull, Juelich, SourceForge |
| Mailing_Lists_and_IRC.txt | 2024; title says IRC but content has Slack (no IRC) |
| How_To.txt | 2024; some linked pages may be stale |
| Lustre.org_Infrastructure.txt | 2026; operational reference for admins |
| Download.txt | 2016; sparse, outdated |

#### HSM & Tiering

| Filename | Issues |
|----------|--------|
| Robinhood_Policy_Engine.txt | 2016; should note v3/v4 status and successors |

#### Other

| Filename | Issues |
|----------|--------|
| Running_Hadoop_with_Lustre.txt | 2009; needs modern Hadoop/Spark update |

---

### KEEP — Current and Accurate (No Changes Needed)

| Filename | Topic Area |
|----------|-----------|
| Lustre_Conferences.txt | Conferences & Events |
| Documentation_working_group.txt | Meta / Organizational |
| ZFS.txt | Storage Backends |
| ZFS_Compression.txt | Storage Backends |
| ZFS_OSD_Storage_Basics.txt | Storage Backends |
| ZFS_Snapshots_for_MDT_backup.txt | Administration & Operations |
| Examining_ZFS_Pools_with_zdb.txt | Troubleshooting & Debugging |
| LNet_Configuration_Edge_Case_Behaviors_and_Side-Effects.txt | LNet / Networking |
| LNET_Selftest.txt | LNet / Networking |
| Lustre_Networking_(LNET)_Overview.txt | LNet / Networking |
| Compiling_Lustre.txt | Installation & Setup |
| Lustre_with_Virtualbox_install.txt | Installation & Setup |
| Introduction_to_Lustre.txt | Architecture & Design Docs |
| Lustre_Kernel_configure_checks.txt | Development & Contributing |
| Lustre_Client_Requirements_Guidelines.txt | Installation & Setup |
| Lustre_Server_Requirements_Guidelines.txt | Installation & Setup |
| Lustre_Client_Cache.txt | Monitoring & Performance |
| Main_Page.txt | Meta / Organizational |
| Mounting_a_Lustre_File_System_on_Client_Nodes.txt | Installation & Setup |
| Creating_the_Lustre_Management_Service_(MGS).txt | Installation & Setup |
| Creating_the_Lustre_Metadata_Service_(MDS).txt | Installation & Setup |
| Creating_Lustre_Object_Storage_Services_(OSS).txt | Installation & Setup |
| Configuring_Lustre_File_Striping.txt | Striping & Layouts |
| Protecting_File_System_Volumes_from_Concurrent_Access.txt | HA & Failover |
| Starting_and_Stopping_Lustre_Services.txt | Administration & Operations |
| Lustre_Management_Service_(MGS).txt | Architecture & Design Docs |
| Lustre_Metadata_Service_(MDS).txt | Architecture & Design Docs |
| Lustre_Object_Storage_Service_(OSS).txt | Architecture & Design Docs |
| Progressive_File_Layouts.txt | Striping & Layouts |
| Data_on_MDT.txt | Striping & Layouts |
| Data_on_MDT_High_Level_Design.txt | Architecture & Design Docs |
| Data_on_MDT_Solution_Architecture.txt | Architecture & Design Docs |
| Layout_Enhancement_High_Level_Design.txt | Architecture & Design Docs |
| Layout_Enhancement_Solution_Architecture.txt | Architecture & Design Docs |
| Fault_Tolerant_MGS.txt | Architecture & Design Docs |
| Lustre_Snapshots.txt | Administration & Operations |
| Handling_Full_OSTs.txt | Administration & Operations |
| Lustre_Quota_Troubleshooting.txt | Troubleshooting & Debugging |
| Security.txt | Security |
| UID_GID_Mapping.txt | Security |
| Collectl.txt | Monitoring & Performance |
| Lustre_Timeout_Hierarchy.txt | Monitoring & Performance |
| IOR.txt | Testing |
| MDTest.txt | Testing |
| VDBench.txt | Testing |
| OBDFilter_Survey.txt | Testing |
| SGPDD_Survey.txt | Testing |
| Testing.txt | Testing |
| TestingLustreCode.txt | Testing |
| Using_Maloo.txt | Testing |
| Lustre_Coding_Style_Guidelines.txt | Development & Contributing |
| Lustre_Script_Coding_Style.txt | Development & Contributing |
| Commit_Comments.txt | Development & Contributing |
| Using_Gerrit.txt | Development & Contributing |
| Patch_Inspection.txt | Development & Contributing |
| Code_Reviewers.txt | Development & Contributing |
| Lustre_Upstreaming_to_Linux_Kernel.txt | Development & Contributing |
| Projects.txt | Development & Contributing |
| Lustre_Manual_Changes.txt | Development & Contributing |
| Frequently_Asked_Questions.txt | Meta / Organizational |
| Understanding_Lustre_Internals.txt | Architecture & Design Docs |
| NFS_vs._Lustre.txt | Architecture & Design Docs |
| Shine.txt | Administration & Operations |
| Trash_Can_Undelete_HLD.txt | Architecture & Design Docs |
| Enhanced_Adaptive_Compression_in_Lustre.txt | Architecture & Design Docs |
| Erasure_Coding_Read-Only_High_Level_Design.txt | Architecture & Design Docs |
| File_Level_Redundancy_Solution_Architecture.txt | Architecture & Design Docs |
| File_Level_Replication_High_Level_Design.txt | Architecture & Design Docs |
| Lreflink_High_Level_Design.txt | Architecture & Design Docs |
| PFL2_High_Level_Design.txt | Architecture & Design Docs |
| PFL2_Solution_Architecture.txt | Architecture & Design Docs |
| OST_Pool_Quotas.txt | Administration & Operations |
| OST_Pool_Quotas_HLD.txt | Architecture & Design Docs |
| OST_Pool_Quota_Test_Plan.txt | Testing |
| OST_Pool_Quotas_Test_Report.txt | Testing |
| Backing_Up_a_Lustre_File_System.txt | Administration & Operations |
| Lustre_Release_Information.txt | Changelogs & Releases |
| Release_Terminology.txt | Changelogs & Releases |
| Simplified_Interoperability.txt | Architecture & Design Docs |
| Lustre_2.15.0–2.18.0 Changelogs (14 pages) | Changelogs & Releases |
| Release_2.15.0–2.18.0 (4 pages) | Changelogs & Releases |

---

### PRESERVE — Historical/Archival (Do Not Modify)

All conference pages (LUG 2006–2025, Developer Days, workshops, all-hands meetings),
DWG meeting minutes, Lustre.org WG minutes, LFSCK Phase 1–4 design docs,
PFL prototype docs, old changelog/release pages (pre-2.15), and other
historical records. (~95 pages total — not enumerated here as they require no action.)

---

## Duplicate/Near-Duplicate Clusters Identified

| Cluster | Pages | Resolution |
|---------|-------|------------|
| FAQ | FAQ.txt, Frequently_Asked_Questions.txt, Frequently_Asked_Questions_(Old_Wiki).txt | Keep FAQ as redirect, merge Old into main, cull stub |
| HowTo | HowTo.txt, How_To.txt, How_Tos.txt | Keep How_To, cull redirects |
| Compiling | Compiling.txt, Compiling_Lustre.txt, Building_Lustre_Code.txt, Building_and_Installing_Lustre_from_Source_Code.txt | Keep Compiling_Lustre, merge/cull rest |
| ZFS JBOD Monitoring | ZFS_JBOD_Monitoring.txt, ZFSjbodMonitoring.txt | Keep ZFS_JBOD_Monitoring, cull redirect |
| ZFS System Design | ZFS_System_Design.txt, Zfs_system_design.txt | Keep ZFS_System_Design, cull redirect |
| LNet Router Guide | LNet_Router_Config_Guide.txt, LNet_Router_Config_Guide2.txt, LNet_Router_Config_Guide_(HPDD_Link).txt, LNET_Router.txt | Keep LNet_Router_Config_Guide, cull rest |
| Monitoring Guide | Lustre_Monitoring_and_Statistics_Guide.txt, Lustre_Monitoring_and_Statistiscs_Guide.txt | Keep correct spelling, cull typo |
| Multi-Rail LNet | Multi-Rail_LNet.txt, Multi-rail_lnet.txt | Keep Multi-Rail_LNet, cull redirect |
| Lustre Internals | Lustre_Internals.txt, Lustre_Internals_(Old).txt, Understanding_Lustre_Internals.txt | Keep Understanding_Lustre_Internals, merge/cull rest |
| Dynamic LNet Config | Dynamic_LNET_Configuration.txt, Dynamic_LNet_Configuration_and_lnetctl.txt | Keep lnetctl page, merge stub |
| Gerrit Builder | SimpleGerritBuilderHowto.txt, Simple_Gerrit_Builder_Howto.txt | Keep Simple_Gerrit_Builder_Howto, cull redirect |
| Test Descriptions | TestDescriptions.txt, Test_Descriptions.txt | Keep Test_Descriptions, cull redirect |
| Release Info | Lustre_Release_Information.txt, Lustre_Software_Releases.txt | Keep Lustre_Release_Information, merge stale copy |
| Intel/Integrated Manager | Intel_Manager_for_Lustre.txt, Integrated_Manager_for_Lustre.txt | Keep Integrated, cull Intel redirect |
