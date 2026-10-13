# Evidence collection range preview v104

Added Preview Collection Range to Evidence Type Instances.
Reads a snapshot of current evidence form values, including unapplied values.
Reads saved collection models through catalog validation.
Filters by evidence-category membership and configured multiplier.
Inactive models remain inspectable with DRAFT / INACTIVE labels.
This is authored category compatibility, not runtime equipment eligibility.
No model selection is assigned to an agent or retained as inventory.

Computes min/max credited value per piece using existing exact half-up helper.
Computes total bounds by multiplying rounded per-piece endpoints by count.
No expected value, distribution, sample roll or actual evidence credit.
Evidence category and piece count remain unchanged.
No Apply/Save calls, catalog export, spawning, inventory or processing.
Original Collection Value Preview remains unchanged.

Current local bags selections are preserved:
Paper, Digital, Audio, Video and Physical.
All source CSVs are unchanged.

Automated acceptance: 576 baseline tests; 586 after change.
Manual acceptance pending: photo crime -> camera 2x -> 40 each / 80 for 2.
