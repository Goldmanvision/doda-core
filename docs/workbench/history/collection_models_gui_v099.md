# Collection model GUI and multi-select v099

- Added Equipment > Collection Device Types and Collection Models.
- Evidence selections use a checkbox dropdown with semicolon-separated IDs.
- Choices come from authored EVIDENCE_* STOCKPILE resources.
- Unknown stored selections are retained, not silently discarded on refresh.
- Brand/version and draft collection properties remain optional.
- Positive decimal multiplier entry is validated.
- Candidate staging no longer overwrites a candidate model CSV.
- Validate All/rules validation and Export All/rules export include models.
- Existing source CSVs and inactive model values are preserved.
- No runtime inventory, collection, consumption, stacking or credit execution.

Automated acceptance: 530 baseline tests; 540 after integration.
Manual acceptance pending: pages, dropdown, draft validation and Export All.
