# Mission System

### Confirmed Architectural Boundary
- Native Strategic Authority: Canonical strategic state implemented by the native DoDA simulation—including people, tasks, assignments, strategic time, validation, and save serialization—is native-owned. Additional strategic domains remain planned as their records and rules are implemented.
- ZScript Field Presentation: The ZScript mission classes represent temporary tactical state during active field deployment. No production mission-outcome submission contract is currently implemented.

### Confirmed In-Mission ZScript Components
- `DoDAMissionManager`: Tracks field tactical progression (`MissionResult`, `MissionIndex`, `MissionPercentComplete`, `MissionPhase`).
- `DoDAMissionState` / `DoDACampaignState`: Manages temporary tactical mission session state.
- `EvidenceLedger`: Tracks field evidence gathered during tactical deployment.
- `MissionDirector`: Orchestrates tactical triggers and level progression.
- `MissionInteractable` / `MissionTerminal` / `ExtractionInteractable`: Interactive world entities for field tasks.

### Planned
- Field-to-macro state event reporting bridge: Validated event submission for discrete mission outcomes is planned; no production submission contract is currently implemented.
