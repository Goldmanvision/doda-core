# DoDA Design Decisions Addendum - 2026-10-08

CONFIRMED user decisions from the 2026-10-08 session: alcohol and sobriety (data layer built, runtime not implemented) and territory (design only, nothing built). Values marked STARTING VALUE were accepted as defaults and are expected to be tuned. PROPOSED and OPEN items are not decisions.

## Alcohol and sobriety - CONFIRMED
- SOBR-01: Four stages: sober, buzzed, drunk, heavily intoxicated, driven by a 0-100 INTOXICATION condition stat. STARTING VALUE: stage thresholds 0 / 15 / 45 / 75.
- SOBR-02: Buzzed halves skills; drunk halves them again (multipliers 1 / 0.5 / 0.25). Low sobriety is detrimental to all skills, attributes and similar stats.
- SOBR-03: Buzzed and drunk agents cannot drive. They ask a friend to drive, which works mechanically like driving themselves.
- SOBR-04: Heavily intoxicated renders an agent or analyst unconscious until intoxication falls below a wake threshold. STARTING VALUES: wake below 60; decay 0.2 points per strategic minute.
- SOBR-05: Agents and analysts go to a bar only when off duty. Alcohol is also available at restaurants, and at resorts when the agent is off duty and not on vacation (feature CAP_ALCOHOL).
- SOBR-06: Agents with low Loyalty can arrive at a shift still buzzed or drunk, a visible sign that Loyalty is dwindling. STARTING VALUES: Loyalty 0-24 up to drunk, 25-49 up to buzzed, 50 and above sober.
- SOBR-07: Alcoholic drinks raise fatigue and hunger (scale HUNGER_LOSS, percent of the Nutrition range lost on finish) and greatly reduce stress. They raise intoxication on finish (scale INTOXICATION_GAIN).
- SOBR-08: Drinks, food, stress and intoxication are not tracked on vacation (2 days or more). Agents return from vacation sober.
- SOBR-09: Starting drinks, all inactive drafts: beer, glass of wine, cocktail, whiskey and shots at bars; beer, wine and cocktail at restaurants; beer, wine, cocktail and whiskey at resorts. STARTING VALUES: intoxication gain 15 / 20 / 25 / 30 / 35 for beer / wine / cocktail / whiskey / shots. Stress reduction, fatigue cost and hunger loss values are blank.
- Resolved: SOBR-OPEN-01 (the multiplier applies to all skills and attributes). Still open: how it combines with trait, training and equipment bonuses.

## Territory and mission areas - CONFIRMED
- TERR-01: Most territories are randomly generated. The starting territory and one or two plot territories are authored.
- TERR-02: A territory holds Places (recreation places, safe houses and similar). Places are not mission areas and the player cannot enter them. Territories are explored through FOIMS-X; its Territory page draws a crude map with Places as points. Each territory has an HQ or office, where the player is sent when traveling between territories. FOIMS-X can direct agents and analysts remotely in any territory.
- TERR-03: MAP01-MAP04 are the four base map formats: a briefing room with one objective, a computer lab with one objective, a small stealth map with one objective, and an assault map with no objective yet (it needs one to end the level). More maps are coming, including an outdoor level with exits to other maps and a static faux-vehicle map of a private FBI jet with a moving skybox.
- TERR-04: Plot missions are player-only mission areas, found only in authored plot territories, designed later. Agents (not analysts) can deploy to most other mission areas.
- TERR-05: Mission areas will be generated procedurally, probably with an Obsidian-style generator and authored prefab sectors. A mission area is a template with randomized variables.
- TERR-06: Mission outcomes (evidence collected, hostiles subdued, confidential informants interviewed) are the current set and will be extended. Each mission area gets randomized objects and outcomes from its template. Only outcomes and objectives that fit the map tags are used.
- TERR-07: Pass means all hostiles are subdued (counts toward Evidence) plus a random portion of the Evidence available in the mission area. Agents stay until all hostiles are subdued. The only true failure is death, more likely with more and higher-tier hostiles. Success depends on weapon accuracy, investigation, medical training (healing in the area), movement speed, precaution and stealth.
- TERR-08: Each mission area has a minimum and maximum duration in strategic minutes, randomized per deployment. Hostile count and the agent's loadout weight the dice.
- TERR-09: One catalog of weapons and tactical gear is shared by the player, agents and hostiles. It currently holds the Beretta M92, the pump shotgun and the MP5SD; more pistols, shotguns and one or two assault rifles will follow. Each agent gets one randomized preferred weapon or proficiency (design later).
- TERR-10: Evidence translates to Leads. Evidence has two counters: a lifetime total that drives mission tiers, and a spendable balance that buys Leads. Spending never lowers the lifetime total.
- TERR-11: A Lead is not tied to a mission area or a territory. Buying one makes a mission area deployment appear in FOIMS-X as a random visual pin (no real coordinates), with a generated name, address and building type (residential, commercial, industrial, public and others) matching its template. The player is loaded into a disconnected map. Deployed agents are not spawned; they run on stats and dice.
- TERR-12: Mission tiers are bands of lifetime Evidence; the tier count is undecided. The final tier is authored end-game content. Reaching it requires most or all major upgrades, enough Department Funding and other end-game ratings.
- TERR-13: Enough territories must exist for a few hundred agents and analysts working concurrently by the end of the game. Upgrades automate much of the micromanagement.
- TERR-14: After the player or agents leave, remaining Evidence and hostiles persist for a short time and are then culled, whether or not the attempt succeeded.
- TERR-15: The FBI jet is a plot device (it crashes and strands the player). Before that, the player occasionally returns to the plane map instead of an HQ or office map after exiting a mission area.

## PROPOSED - not confirmed
- Store a compact record per mission area (template, seed, tier, generated name, address and building type, remaining Evidence and hostiles, expiry) and generate the map only when the player deploys, from the seed, applying the remaining state. Agents never need a map.
- First territory slice: map types and maps (with an objective flag; MAP04 warns until it has one), the shared weapons catalog, an empty mission-tier table, and the territory table with the starting territory and plot slots.

## OPEN
- Which territory a newly bought mission area belongs to; whether unvisited purchased areas expire or are capped; how long persistence lasts.
- Team size and how several deployed agents combine their dice.
- Hostile catalog (types, tiers, weapons); loadout weighting in the dice.
- What limits agents per territory; mission-tier count, thresholds and gating rules.

## Territory and mission areas - CONFIRMED (continued, 2026-10-08)
- TERR-16: A newly bought mission area belongs to a randomly chosen territory the player has access to, not necessarily the one being viewed.
- TERR-17: There is a cap on open mission areas. Upgrades can raise it.
- TERR-18: How long Evidence and hostiles persist after a deployment is one global setting in strategic time. A template may override it.
- TERR-19: The team limit for one mission area is 4 for now. It may later vary by mission area or mission tier.
- TERR-20: Housing, hotels, safe houses and office space determine the maximum number of agents and analysts. If agents and analysts become too large a share of a territory's population (for example half), Public Perception takes a major hit.
- TERR-21: Hostiles get their own catalog.
- TERR-22: The starting territory is Ebon Falls, New York. Its HQ is called Ebon Falls DoDA Office.
- TERR-23: Rosewell, New Mexico is a plot territory. Unknown Kaddath is a player-only territory.
- TERR-24: Territory is granted by Congressional Support.
- TERR-25: Each territory has a population number (fixed for authored territories, randomized in a range for generated ones). Housing place types carry capacity ranges, and each generated place rolls its own. The Public Perception hit is a table of agent-share bands; every threshold and penalty is blank until the user supplies them.
- TERR-26: Residency must be spread out. Hoarding all agents in one location should be discouraged if not impossible. Agents may have to find housing outside the operational territory, which adds commute time.

## PROPOSED - not confirmed (added 2026-10-08, later)
- Territory Expansion points: a spendable counter earned from Congressional Support and spent to unlock a generated territory permanently (an acquisition-time check, so a later drop in Congressional Support does not remove the territory). The earning rule is blank.
- Rosewell and Unknown Kaddath unlock through plot events, not through Expansion points.
- Agents are never directed to Unknown Kaddath, and it has no HQ.
- Spreading rule: a hard cap per housing place from its capacity, a limit on the share of a territory's agents living in any one place, and a commute time for housing outside the operational territory, rolled per housing place in a range. All values blank.

## OPEN (updated)
- Team size per mission area or tier; open mission area cap value; persistence time value.
- Hostile catalog (types, tiers, weapons) and how loadout weights the dice.
- Mission tier count, thresholds and gating rules.
- Whether the first territory slice scope is accepted: territory table, global settings, mission tiers, map formats and maps, and the shared weapons catalog.

## Territory - CONFIRMED (later 2026-10-08)
- TERR-27: Territory Expansion points: a spendable counter earned from Congressional Support and spent to unlock a generated territory permanently. The earning rule is blank.
- TERR-28: Rosewell and Unknown Kaddath unlock through plot events, not Expansion points.
- TERR-29: Agents cannot be directed to Unknown Kaddath. It has no HQ.
- TERR-30: Spreading rule: a hard cap per housing place from its capacity, a limit on the share of a territory's agents living in one place, and a commute time for housing outside the operational territory, rolled per housing place in a range. All values blank.
- TERR-31: First territory slice scope accepted: territories, settings, mission tiers, map formats, maps and the shared weapons catalog, all seeded inactive.

## Hostiles - CONFIRMED (2026-10-08)
- HOST-01: Hostiles use the default Freedoom enemies for now. The Sailor (the blue uniformed Freedoom Phase 2 enemy) is the primary hostile. Zombie, Shotgun Zombie and Minigun Zombie are lower tier. All are placeholders, flagged so they can be retired when human hostiles replace them.
- HOST-02: Hostiles get their own catalog with an optional link to the shared weapons catalog (blank for hostiles that use their own attack).
- HOST-03: A hostile's tier matches the mission tiers, except hostiles used only in authored mission areas, which have no tier.
- HOST-04: Engine class names and all balance values (hit points, damage) are blank until the user supplies them.
- HOST-05: Seeded rows: Sailor, Zombie, Shotgun Zombie, Minigun Zombie, all inactive.

## Mission-tier progression - CONFIRMED (2026-10-08)
- MTIER-01: Six mission tiers initially. Tiers 1-5 use generated mission content; Tier 6 is authored end-game content. Lower tiers remain available after higher tiers unlock.
- MTIER-02: Lifetime Evidence drives tier eligibility. Spendable Evidence pays for Leads. Spending does not reduce lifetime Evidence.
- MTIER-03: Ordinary Lead prices are not tier-specific. One department-wide counter drives linear growth: next cost = base cost + successful ordinary paid purchases * increment. Base cost and increment are undecided.
- MTIER-04: Successful ordinary paid purchases advance the pricing counter. Free tutorial missions, failed purchase attempts and redeployments do not. Changing territory or choosing a lower tier does not reset it.
- MTIER-05: Starting resources include a small Evidence balance, Department Funding, a couple of personnel, a phone, a FOIMS-X computer with 14.4k internet, and further starter items/currencies. Exact quantities and identities remain open.
- MTIER-06: Introduction: free tutorial mission area, followed by a purchased mission area, followed by a lull teaching passive Evidence gathering through agent investigations and FOIMS-X.
- MTIER-07: After Tier 5 unlocks, periodic checks evaluate final-tier eligibility. The interval is undecided.
- MTIER-08: Eligibility requires the final lifetime Evidence threshold, required major upgrades, sufficient CURRENT AVAILABLE Department Funding, required plot milestones/items, high PREPAREDNESS, and sufficient operational territories. Concrete references and thresholds remain open.
- MTIER-09: When all eligibility checks pass, offer a special expensive authored Tier 5 capstone Lead. Its price is separate from ordinary Lead pricing and remains undecided.
- MTIER-10: Completing the capstone's authored objectives permanently unlocks Tier 6. Eliminating hostiles alone is not its completion condition.
- MTIER-11: The capstone does not expire. Unsuccessful attempts allow redeployment without buying the Lead again; mission state is retained.

### Mission-tier implementation status
- This foundation slice seeds six inactive tier rows and four regression tests.
- Tier 1 starts at zero lifetime Evidence. Tier 2-6 thresholds remain blank.
- Purchasing, pricing-counter state, periodic eligibility evaluation, starter grants, tutorial sequencing and the capstone mission are NOT implemented.
- Open: exact major-upgrade and plot-item references; readiness/funding/territory thresholds; check interval; capstone price, map and objectives.
- Resolved by MTIER-12: the special capstone purchase does not advance the ordinary Lead pricing counter.
- Resolved by MTIER-13: department eligibility is not rechecked after capstone purchase.
- Earlier TERR-OPEN-01 is narrowed: tier count is now six; thresholds and concrete gate requirements still need authoring.

## Mission pricing and gate contract - implementation (2026-10-08)
- Added seven numeric draft settings to territory_settings.csv: ordinary Lead base cost, increment, final-check interval, capstone cost, current available funding minimum, PREPAREDNESS minimum, operational territory minimum.
- All values blank and rows inactive. Numeric settings currently use positive whole units.
- territory_catalog.json now exports missionProgression configuration status and the approved rules under rules.missionProgression.
- Missing or inactive settings are unconfigured, never silently zero.
- Required upgrade/plot references, capstone mission reference, and two capstone policies are unresolved and prevent a fully configured final gate.
- Capstone purchase-counter policy resolved by MTIER-12.
- Post-purchase eligibility policy resolved by MTIER-13.
- Added eight tests. No campaign state, Evidence transactions or native runtime implemented.

## Capstone policies - CONFIRMED (2026-10-08)
- MTIER-12: Purchasing the special Tier 5 capstone Lead does not advance the ordinary Lead pricing counter.
- MTIER-13: Check all department eligibility requirements when purchasing the capstone. Do not recheck them after purchase; later funding, readiness or other department changes do not revoke access or prevent its objectives from unlocking Tier 6.
- Completing the capstone's authored objectives permanently unlocks Tier 6.
- These two policies are removed from missingConfiguration.
- Numeric values, required upgrade/plot references and the capstone mission reference remain unconfigured.
- Authoring/export only; no native campaign behavior implemented.

## Progression identity foundation - CONFIRMED (2026-10-08)
- PID-01: Upgrade is a broad term for something purchased or unlocked that grants abilities, better stats, access or other benefits. It is not limited to equipment contracts.
- PID-02: Upgrade definitions are distinct from individual equipment ownership and from campaign acquisition state. Optional department-track references group upgrades.
- PID-03: Milestone requirements check persistent completion. Plot-item requirements check current possession at capstone purchase. Permanent credit for acquiring an item can be represented by a milestone.
- PID-04: Tier requirements combine with ALL semantics. Each row has exactly one typed reference: upgrade, milestone or plot item.
- PID-05: Four catalogs seeded empty: upgrades, plot_milestones, plot_items, mission_tier_requirements. No mandatory definitions or requirements invented.
- PID-06: Numeric requirements stay in territory_settings.csv. Capstone mission reference remains unresolved pending mission authoring.
- Implementation stage A: standalone identity module, validator/exporter and twelve tests. GUI, Validate All/Export All wiring and territory-contract integration are pending stage B.
- Active definition means available authored content, not acquired/completed/held campaign state.

## Progression identity editor wiring - implementation (2026-10-08)
- Added four pages under Territory and Missions: Upgrades, Plot Milestones, Plot Items, Mission Tier Requirements.
- Requirement rows have typed optional reference dropdowns; exactly one is required by validation.
- Department Track references read department_tracks.csv without registering a duplicate generic track editor.
- Draft validation stages department_tracks.csv alongside registered identity tables.
- Main GUI validation and export include the progression identity module.
- Added five wiring tests.
- Territory final-gate reference integration remains pending B2.
- Catalogs remain empty; no upgrade or plot requirements selected.

## Territory identity integration - implementation (2026-10-08)
- B2 complete: territory validation reads progression identities when identity sources are present, and requires them in the actual workbench project.
- territory_catalog.json includes progressionIdentities and active typed Tier 6 requirements.
- Upgrade/plot reference blockers derive from validated authored requirements, not hard-coded missing entries.
- Empty catalogs remain unconfigured; inactive requirements do not satisfy reference configuration.
- Invalid references or partial identity installations block territory export.
- referenceConfigurationReady describes authored configuration only, never campaign eligibility.
- Numeric thresholds and the capstone mission reference remain unresolved.
- missionProgression contractVersion advanced to 2026-10-08.2.
- Added six integration tests. No campaign behavior implemented.
- This completes the B2 work marked pending in the earlier identity-wiring entry.

## Authored missions and capstone chain - CONFIRMED (2026-10-08)
- CAP-01: Plot missions and the Tier 5 capstone share one authored_missions table, separated by kind.
- CAP-02: The capstone is named "Savanah River Site Nuclear Research Facility, Georgia" (as written). It lives in a new authored territory, "Savanah River Site Nuclear Research Facility, Savanah River, Georgia" - not Rosewell and not a random territory.
- CAP-03: The capstone map stays blank; the mission has not been designed.
- CAP-04: Objectives are a separate table. Each capstone mission needs at least one active required objective before the final gate counts as configured.
- CAP-05: The capstone is a chain of missions, not a single mission.

### Assumptions recorded as OPEN (not confirmed)
- CAP-OPEN-01: The real Savannah River Site has two n's and is in South Carolina. Names are stored as written; confirm spelling and state.
- CAP-OPEN-02: The new territory is seeded as kind PLOT with agents allowed and no HQ. Confirm plot versus player-only.
- CAP-OPEN-03: Tier 6 unlocks when the final chain mission's required objectives complete (unlocks_tier_id sits on the final position only).
- CAP-OPEN-04: One capstone Lead purchase unlocks the whole chain with no further purchases. Capstone missions are player-only.

### Implementation status
- Authoring/export only. Added authored_missions.csv (one inactive seed), authored_mission_objectives.csv (empty), the new territory row, and two editor pages.
- The territory final gate now exports capstoneMissionReference and capstoneStatus. Missing map, objectives or inactive status keep the gate unconfigured.
- Contract version 2026-10-08.3. No campaign behavior implemented.

## Authored mission version-test correction (2026-10-08)
- Updated the existing territory identity integration test to expect missionProgression contract version 2026-10-08.3.
- The authored-mission slice added 16 tests, not the announced 17. Expected suite total is 294.
- No authored mission data, policy or native runtime behavior changed.

## Capstone setting corrections - CONFIRMED (2026-10-08)
- CAP-06: The setting is the real Savannah River Site in South Carolina, spelled with two n's. Names corrected in the territory and mission rows.
- CAP-07: Real-name use is acceptable only if legal review finds no problem; otherwise rename to an evocative fictional name. Open: legal review before release. Practical guardrails: no Department of Energy or contractor logos, no use in the title or marketing, consider a fictional-work disclaimer.
- CAP-08: Qualified agents can be deployed to the SRS operational territory, so agents_allowed stays true. Open: the qualification required, and the HQ name.
- Resolves earlier CAP-OPEN-01 (spelling and state) and CAP-OPEN-02 (territory kind). The territory remains kind PLOT.
- CAP-OPEN-03 stays undecided: the Tier 6 unlock trigger is TBD.
- CAP-OPEN-04 stays undecided, leaning no: Leads will still be required to open mission areas, so one capstone Lead probably does not open the whole chain.
- Authoring only; no campaign behavior implemented.

## Requirement vocabulary, pricing and HQ naming - CONFIRMED (2026-10-08)
- MTIER-14: Ordinary Lead pricing compounds. STARTING VALUES: first Lead costs 100 Evidence points; each paid Lead then costs 10 percent more than the previous. This supersedes the linear model in MTIER-03; the increment setting became LEAD_COST_GROWTH_PERCENT. Proposed rounding: whole Evidence points, half up (open).
- MTIER-15 / PLOT-01: The Tier 6 gate requires the player to have collected the Necronomicon and processed it forensically. Modeled as two milestones, PLOT_NECRONOMICON_COLLECTED and PLOT_NECRONOMICON_PROCESSED. A PLOT_ITEM_NECRONOMICON item is defined but not required, so losing or consuming the book cannot lock Tier 6 (assumption: collected means a permanent milestone, not currently held). Requirement rows are seeded inactive.
- Upgrade requirements for the Tier 6 gate are still undecided, so the final gate stays unconfigured.
- TERR-32: Headquarters are named "<territory name> DoDA Office". Examples: Ebon Falls DoDA Office (New York State), Manhattan DoDA Office (New York City), Southside Chicago DoDA Office (Illinois), Washington D.C. DoDA Office (stated as Maryland - to confirm), New Orleans DoDA Office (Louisiana), Roswell DoDA Office, Savannah River DoDA Office. Only the first, Roswell and Savannah River apply to authored territories now; the others are naming examples, not added territories.
- TERR-33: Unknown Kaddath has an HQ: DoDA Unknown Kaddath Satellite Operations Center (DUKSOC), in the Dreamlands. This supersedes TERR-29's "no HQ". Agents still cannot be directed there.
- OPEN: territory spelling Rosewell versus Roswell (the territory row still says Rosewell; a naming warning flags the mismatch).
- Authoring only. No campaign behavior implemented.
