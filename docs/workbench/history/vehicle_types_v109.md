# Structured vehicle type foundation v109

Confirmed capacities authored as data:
STANDARD_MOTOR_VEHICLE max_team_members 4.
VAN max_team_members 6.

These are generic type definitions, not models or owned vehicles.
Active definitions create no inventory and activate no tasks.
Capacity is a team-member count per vehicle, not a vehicle quantity.
No additional driver seats, cargo values or travel rules are invented.
Investigation vehicle minimum 1 and staffing maximum 2 remain unchanged.
Existing computer/phone/PDA personal-device limits remain unchanged.
No runtime capacity checks or allocation implemented.
Oversized-team and multiple-vehicle policy remains open.

Standalone validator/export only.
Main validation, candidate staging, Export All and GUI integration follow.
Acceptance: 606 baseline tests; 614 after installation.
