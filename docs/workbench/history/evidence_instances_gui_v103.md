# Evidence Type Instances editor v103

Added Content > Evidence Type Instances using the shared table editor.
Category dropdown references only the seven authored evidence stockpile IDs.
Inactive categories remain visible for draft authoring; active-reference
validation remains enforced by the v102 validator.
Admissible Evidence, Research Points, funding and entity counts are excluded.
Minimum and maximum fields are whole-number base values per piece.
Nonnegative bounds and min <= max are checked during draft/save validation.
Selecting an item does not create a live piece or roll a random value.
Existing source CSVs and all 12 starting definitions are unchanged.
Apply to List, Validate Draft and Save to Source remain separate.

v102 already supplies Validate All and Export All integration.
Automated acceptance: 570 baseline tests; 576 after installation.
Manual acceptance pending: page, category choices, draft range validation,
revert, Validate All and Export All.
