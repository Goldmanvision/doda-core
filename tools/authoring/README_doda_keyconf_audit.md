# DoDA KEYCONF Default-Binding Audit Utility

## Purpose and Scope

`audit_doda_keyconf.py` is a standalone, dependency-free, read-only developer tool designed to parse and audit UZDoom/DoDA `KEYCONF` lumps. It analyzes default key bindings, cross-references menu key configurations with default binds, and reports conflicting duplicate default keys or orphan actions before runtime execution.

### Read-Only Scope
This utility is strictly read-only and performs offline static analysis. It does not modify KEYCONF files, does not select replacement keys, does not generate bindings, and does not alter engine or gameplay configurations.

### Explicit Scope Disclaimer
This tool does not determine whether hard-coded ZScript input, such as FOIMS-X O/Escape handling, is represented in the Options menu.

---

## Exact Run Command

Run the audit tool using the Python 3 standard library:

```bash
python tools/audit_doda_keyconf.py --keyconf <path-to-KEYCONF>
```

For example, to audit the active DoDA KEYCONF lump:

```bash
python tools/audit_doda_keyconf.py --keyconf C:/Dev/uzdoom_src/doda-core/KEYCONF
```

---

## Exit-Code Meanings

- `0` (Success): No duplicate default key bindings were found. The exact marker `DODA KEYCONF AUDIT PASSED` is printed to stdout.
- `1` (Audit Failure): One or more duplicate default key bindings were detected. The exact marker `DODA KEYCONF AUDIT FAILED` is printed to stdout.
- `2` (Input / Syntax Error): The specified KEYCONF file was missing, unreadable, or contained malformed syntax (e.g., unclosed quotes, invalid directive arguments). Diagnostic error details are printed to stderr.

---

## Example Duplicate-Key Result

When run against a KEYCONF containing conflicting default key bindings (such as the default `c` key bound to multiple actions):

```text
=== KEYCONF AUDIT REPORT ===
Target file: C:\Dev\uzdoom_src\doda-core\KEYCONF

Declared Key Sections (1):
  Line 3: addkeysection "DoDA Controls" DoDAControls

Declared Menu Keys (13):
  Line 8: addmenukey "Use" +use
  Line 11: addmenukey "Left Lean" +user1
  Line 14: addmenukey "Right Lean" +user2
  Line 17: addmenukey "Reload Weapon" +reload
  Line 23: addmenukey "DoDA Aim Mode" +doda_aimmode
  Line 31: addmenukey "Swap Beretta" +doda_swapberetta
  Line 40: addmenukey "Weapon Secondary Action" +doda_weaponsecondary
  Line 46: addmenukey "Toggle Pistol Swap Lock" +doda_toggle_pistol_swap_lock
  Line 52: addmenukey "Cycle MP5 Fire Mode" +doda_firemode
  Line 60: addmenukey "Select B92 Pistols" doda_select_b92
  Line 64: addmenukey "Select Shotgun" doda_select_shotgun
  Line 68: addmenukey "Select MP5KSD" doda_select_mp5
  Line 72: addmenukey "Holster" DoDA_Holster

Declared Aliases (14):
  Line 24: alias +doda_aimmode "DoDA_SetDeadzone 1"
  Line 25: alias -doda_aimmode "DoDA_SetDeadzone 0"
  Line 32: alias +doda_swapberetta "doda_swap_beretta 1"
  Line 33: alias -doda_swapberetta "doda_swap_beretta 0"
  Line 41: alias +doda_weaponsecondary "doda_weapon_secondary 1"
  Line 42: alias -doda_weaponsecondary "doda_weapon_secondary 0"
  Line 47: alias +doda_toggle_pistol_swap_lock "doda_toggle_pistol_swap_lock 1"
  Line 48: alias -doda_toggle_pistol_swap_lock "doda_toggle_pistol_swap_lock 0"
  Line 53: alias +doda_firemode "+user3"
  Line 54: alias -doda_firemode "-user3"
  Line 61: alias doda_select_b92 "slot 2"
  Line 65: alias doda_select_shotgun "slot 3"
  Line 69: alias doda_select_mp5 "slot 4"
  Line 73: alias DoDA_Holster "use DoDAHolster"

Declared Default Bindings (13):
  Line 9: defaultbind f +use
  Line 12: defaultbind q +user1
  Line 15: defaultbind e +user2
  Line 18: defaultbind r +reload
  Line 26: defaultbind mouse2 +doda_aimmode
  Line 34: defaultbind v +doda_swapberetta
  Line 43: defaultbind x +doda_weaponsecondary
  Line 49: defaultbind c +doda_toggle_pistol_swap_lock
  Line 55: defaultbind c +doda_firemode
  Line 62: defaultbind 2 doda_select_b92
  Line 66: defaultbind 3 doda_select_shotgun
  Line 70: defaultbind 4 doda_select_mp5
  Line 74: defaultbind 1 DoDA_Holster

Duplicate Default Bindings:
  Key 'c' (2 actions):
    Line 49: +doda_toggle_pistol_swap_lock
    Line 55: +doda_firemode

Menu Keys Lacking Defaultbind:
  None (all 13 menu key actions have default bindings)

Defaultbinds Lacking Menu Key Entry:
  None (all 13 defaultbound actions have menu key entries)

DODA KEYCONF AUDIT FAILED
```
