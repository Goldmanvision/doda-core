# Collection value preview v100

Read-only value preview added to Collection Models.
Uses current form's multiplier captured when the preview opens.
Does not apply, save, activate, export, or modify source data.
Base value and piece count are sample inputs only.
Uses the existing exact-decimal, per-piece half-up value helper.
Total is rounded per-piece value multiplied by unchanged piece count.
No eligibility, inventory, stacking, repeated-photo or runtime simulation.

Example: base 1.25, multiplier 2, count 2 -> 3 each, total 6.
Automated acceptance: 540 baseline tests; 550 after change.
Manual acceptance pending: preview opens, recalculates and closes.
