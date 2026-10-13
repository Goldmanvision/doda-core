# Tasks > Task Templates: current schema

Task templates describe work assigned to personnel at targets, not spawned timed resources.

Priority is retained for scheduling. Auto-allocation is department/personnel state, not a template flag.
Targets are STATION, TERRITORY or MISSION_AREA. Station families refer to LOCATION equipment;
a forensics station does not replace required analyst computer/device access.

Loop Task repeats a completed work cycle. Time To Complete is optional strategic minutes;
blank is open-ended, never a deadline. Active loops require a configured cycle duration.
CONTINUOUS templates use payout count 0. PERIODIC_LUMP_SUM uses a finite operation duration
and evenly spaced payouts; duration must divide evenly by payout count.

Templates are seeded as inactive drafts. Blank capability/rate means unconfigured, not unrestricted.
Resource flows, skills/equipment requirements, risk chances and assignment execution are not yet implemented.

Use New Template, fill the form, Save Template. New templates default to inactive.
An active template requires a configured active installed capability and valid station reference.
Saves validate a complete candidate and retain source-hash guards and backups.

The old SIGNAL_REVIEW/OCCULT_INCIDENT_RESPONSE demonstration templates were retired.
Use PROCESS_EVIDENCE_PAPER to review a draft. Revert Form discards unsaved edits, not saved changes.
Export All rebuilds department content, rules and the read-only ZScript catalog. Inactive templates
are absent from active ZScript lookups, but remain visible in authoring and CRT catalog browsing.
