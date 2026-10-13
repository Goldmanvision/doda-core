# Task staffing minima v120

Source change: task_staffing_rules.csv only.
Adds 11 rows to the 2 existing rows, covering all 13 task templates.
Six forensic-processing tasks: minimum 1 ANALYST each.
Investigation, Mission Deployment and three Undercover tasks: minimum 1 AGENT each.
Field Surveillance: minimum 3 ANALYSTS.
Tech Development: minimum 1 ANALYST.
Maximums are left blank for later authoring; Investigation's old maximum 2 is cleared.
Investigation's existing preferred count 1 is retained.
No new preferred counts are assigned.
All staffing rows and existing task templates remain inactive.

Confirmed design decisions for later equipment-prerequisite authoring:
- Computer means desktop; computer-or-laptop is an alternative, not both.
- Individual computing devices and personal gear apply per assigned person.
- Cars, vans, labs and stations are shared task-level requirements.
- Paper: analyst, desktop-or-laptop, paper scanner and paper evidence.
- Photographic: analyst, desktop-or-laptop, color photo scanner and photo lab.
- Digital: analyst, desktop and digital forensics software; no laptop alternative.
- Audio/video/chemical: analyst, desktop-or-laptop and matching forensic lab.
- Investigation: agent, phone, pistol, car and desktop-or-laptop.
- Existing Investigation collection-receptacle prerequisite is retained.
- Mission Deployment: agent, phone, any weapon, car and desktop-or-laptop.
- Preferred weapon assignment is encouraged for Mission Deployment, not mandatory.
- Undercover: agent, mobile phone, disguise and laptop; no starting pistol requirement.
- A pistol may be acquired illegally during Undercover as a possible task event.
- Undercover acquisition probabilities, timing and inventory behavior remain undecided.
- Field Surveillance: 3 analysts, shared van, mobile surveillance station,
  a surveillance-equipment alternative, 1 shared mobile phone and 2 shared laptops.
- Tech Development: shared tech lab; 2 desktops AND 1 laptop PER ANALYST.
- Multiple analysts on the same Tech Development task provide a Research multiplier.
  Its formula and values remain undecided.

This slice does not implement those new equipment prerequisites.
Existing forensic station targets, prerequisites and flow definitions are unchanged.
No capability is created or linked; timing, amounts, weights and activation are unchanged.
No runtime inventory, eligibility, allocation or task execution is implemented.
Acceptance: 697 tests before/after plus staged project and temporary export checks.
Live staffing JSON is refreshed separately with Export All.
