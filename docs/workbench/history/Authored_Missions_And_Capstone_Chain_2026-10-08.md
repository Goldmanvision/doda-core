# Authored Missions and Capstone Chain - 2026-10-08

Authoring/export only. Added doda_authored_mission_rules.py, authored_missions.csv
(one inactive capstone seed), authored_mission_objectives.csv (empty), a new
authored territory row, two editor pages, GUI validate/export wiring and tests.

The territory contract now derives the capstone reference and its blockers from
the authored chain. Names are stored exactly as written; open items record the
real-world spelling/state difference and unconfirmed assumptions.
Backups are numbered with SHA-256 manifests.
