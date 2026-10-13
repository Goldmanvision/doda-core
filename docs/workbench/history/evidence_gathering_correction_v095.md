# Evidence gathering correction v095

Confirmed:
- Field Surveillance gathers only Photographic, Audio and Video Evidence.
- Investigate retains its Physical Evidence weighted choice.

Changes:
- Removed four inactive, unconfigured Field Surveillance outputs:
  Paper, Digital, Chemical and Physical.
- Grouped flow CSV rows by template for editor visibility.
- Preserved every retained row's values, including sort_order.
- Staffing, resources, equipment and task templates unchanged.
- No runtime execution or collection-kit selection behavior added.

This supersedes v094's seven-choice expectation for Field Surveillance.
Investigate and the three Undercover templates retain seven choices.
Acceptance: 502 baseline tests; 504 after correction; 44 flow rows.
Manual acceptance pending: editor, preview, Validate All and Export All.
