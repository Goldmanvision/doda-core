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