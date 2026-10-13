# Physical Evidence authoring addition v094

CONFIRMED:
- Physical Evidence covers weapons, clothing and miscellaneous objects
  that do not fit an existing evidence category.
- Receptacles do not reclassify existing evidence categories.
- Investigation requires a pistol per agent and applicable collection
  receptacles, limited to evidence bags and chemical collection kits.
- Investigation's existing motor-vehicle requirement is retained.

Implemented in this slice:
- EVIDENCE_PHYSICAL: active STOCKPILE definition, no lifetime tracking.
- Five inactive weighted gathering choices, amounts and weights blank.
- Existing resources and flow rows preserved semantically.
- Staffing, equipment, task templates and Python implementation unchanged.
- No runtime collection, selection, balances or execution.

Pending:
- Physical Evidence processing template and station requirements.
- Collection-equipment authoring and evidence-type mappings.
- Missing-receptacle selection behavior remains undecided.
- Vehicle, pistol, surveillance and mobile-laptop prerequisite authoring.

Acceptance: 499 baseline tests; 502 after change.
Manual check pending: Resources and seven-choice gathering previews.
