# Vehicle integration v110

Generic types remain STANDARD_MOTOR_VEHICLE (4) and VAN (6).
Vehicle Types is an Equipment page using the existing shared table editor.
Main validation follows the optional-catalog convention used by adjacent slices.
Registered table metadata supplies vehicle CSV staging to shared candidates.
Task-template save candidates also include vehicle_types.csv.
GUI validation includes vehicle validation; GUI Export All's rules chain exports
vehicle_catalog.json and propagates vehicle export errors.
No extra vehicle table is added to department_content.json or the overlay PK3.
No runtime loader, capacity checks, inventory, allocation or balancing added.
Existing shared save/backup and external-change checks are reused unchanged.
All source CSVs remain unchanged by installation.
Expected tests: 614 baseline; 624 after installation.
