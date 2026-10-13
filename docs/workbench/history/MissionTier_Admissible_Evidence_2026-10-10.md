# Mission Tier Field Rename - 2026-10-10

Renamed mission_tiers.min_lifetime_evidence to min_lifetime_admissible_evidence
(and the exported minLifetimeEvidence key and editor label) so mission-tier
thresholds count lifetime Admissible Evidence, per the 2026-10-10 decision.
Replacement was a byte-level identifier rename across tools, source CSV and
manual. Generated output is refreshed by Export All. Added 2 regression tests.
The STARTING_EVIDENCE setting id is unchanged and is reviewed with the
resource ledger stage.
