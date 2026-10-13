# Evidence Type Instance foundation v102

Confirmed: all 12 starting definitions use minimum = maximum at user values.
Ranges are inclusive nonnegative integer endpoints; wider ranges can be authored later.
No random distribution is selected and no values are sampled on export.
Definitions are reusable catalog entries, not live evidence pieces.
Collection models retain ownership of eligibility and multipliers.
Round half up per piece after the collection multiplier; piece count is unchanged.
No inventory, spawning, credits, consumption, stacking or bulk discovery implemented.
GUI instance page remains pending.

Narrative / incremental design rationale:
Early isolated notes suggest individual crimes. A smoking-gun discovery worth
around 100 points is an early breakthrough supporting several Leads.
Later discoveries expose thousands of high-value pieces implicating a global
cult in crimes across decades, suggesting thousands or potentially hundreds
of thousands of murders. Improved player capabilities reveal a threat whose
scale grows beyond the player's initial understanding.
The user-stated end-game Mission Tier threshold is 1 million evidence points.
That threshold was not independently checked or changed by this patch.
Higher-value definitions and future larger-scale recovery should support
progression rather than endless individual low-value pickups.
Points, piece counts and inferred victim counts are distinct quantities.
Initial values are not a ceiling for later authored evidence.

Sample-once/persisted live piece values remain a proposed runtime rule;
distribution and creation timing are not implemented by this authoring slice.
No Mission Tier or Lead-price changes.

Automated acceptance: 560 baseline tests; 570 after installation.
