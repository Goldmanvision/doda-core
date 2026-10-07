# DoDA Design Decisions Addendum - 2026-10-07 (continued)

CONFIRMED user decisions recorded after the handoff's Part Five. Merge into
E:\Dev\tools\Workbench_Docs\DoDA_Working_Specification_and_Handoff_2026-10-07.md
(Part Five) when that folder is attached. Encoded in doda_network_rules.py (TASK_INTERRUPTION).

## Processing-task interruption (resolves TASK-01 and TASK-02)
- TASK-01a: Shift end pauses a processing task. It resumes at the person's next shift unless the player reassigns it to another person.
- TASK-01b: Incapacity mid-task fails the task. The unresolved evidence is destroyed: the processed portion keeps its positive credit and the remainder is recorded as lost evidence.
- TASK-01c: If the player cancels a task, the evidence waits as partly processed. It is not lost and not reset.
- TASK-02: Another qualified person may take over a partly finished processing task and keeps its progress.
- Unchanged: equipment unavailability gives reduced effectiveness or a pause, never destruction.

## System-update interruption
- UPD-01: An interrupted system update must restart from the beginning.

## Register changes
- TASK-01: RESOLVED (transfers via INT-01..10; processing via TASK-01a..c; updates via UPD-01).
- TASK-02: RESOLVED (keep progress on takeover).
- UPD-02 RESOLVED: overdue-update risk keeps building through a restart until the update completes.
- NET-03b RESOLVED: one technician may attend both transfer ends only if able to move between both device locations.
- INT-11 RESOLVED: permanent unavailability = death, dismissal, defection, or retirement.

## Network content (populated from diagram)
- NET-CONTENT-01: Five tiers confirmed: DIALUP G1 (14.4KB/s), DIALUP G2 (56K), LEASED_LINE G1 (1.5MB/s, T1), LEASED_LINE G2 (44MB/s, T3), FIBER G1 (2GB/s).
- NET-CONTENT-02: One placeholder router per tier confirmed (diagram shows no routers).
- NET-06 PARTIAL: diagram speed labels kept verbatim; file sizes are deliberately exaggerated for gamification. Numeric units for timing remain open.

Status: merged into the handoff document (shared in thread 2026-10-07); copy it over the Workbench_Docs version.
