# FOIMS-X Evidence Transactions - 2026-10-09

Added manual sandbox Gather and Spend controls. Gather increases available
and lifetime Evidence; Spend reduces only available Evidence and rejects
overspending. Both require positive whole amounts and share the existing
timestamped activity history, retaining the latest 200 events.

Evidence progress reads the session's mission-tier catalog, including draft
rows clearly labeled as drafts. It does not evaluate other requirements,
activate draft tiers, or unlock tiers. Missing thresholds remain explicit.
Reset restores initial balances and clears history.

No source CSV writes, native/game changes, automatic rewards or economy.
Added 12 headless Evidence tests.
