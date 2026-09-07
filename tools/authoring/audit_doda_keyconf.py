#!/usr/bin/env python3
"""
DoDA KEYCONF Default-Binding Audit Utility

Standalone offline developer tool to parse, analyze, and audit KEYCONF lumps
for key binding conflicts, orphan menu actions, and unbound commands.
"""

import argparse
import collections
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class KeySectionEntry:
    line_number: int
    title: str
    section_name: str


@dataclass
class MenuKeyEntry:
    line_number: int
    description: str
    action: str


@dataclass
class AliasEntry:
    line_number: int
    name: str
    command: str


@dataclass
class DefaultBindEntry:
    line_number: int
    key: str
    action: str


@dataclass
class KeyConfAuditResult:
    sections: List[KeySectionEntry]
    menukeys: List[MenuKeyEntry]
    aliases: List[AliasEntry]
    defaultbinds: List[DefaultBindEntry]
    binds_by_key: Dict[str, List[DefaultBindEntry]]
    duplicate_keys: Dict[str, List[DefaultBindEntry]]
    menukeys_lacking_bind: List[MenuKeyEntry]
    binds_lacking_menukey: List[DefaultBindEntry]


def tokenize_line(line_text: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Strips inline comments (//) and splits a KEYCONF line into tokens.
    Respects double-quoted strings. Returns (tokens, error_message).
    """
    in_quote = False
    clean_chars: List[str] = []
    i = 0
    n = len(line_text)
    while i < n:
        c = line_text[i]
        if c == '"':
            in_quote = not in_quote
            clean_chars.append(c)
            i += 1
        elif not in_quote and c == '/' and i + 1 < n and line_text[i + 1] == '/':
            break
        else:
            clean_chars.append(c)
            i += 1

    clean_str = "".join(clean_chars).strip()
    if not clean_str:
        return [], None

    tokens: List[str] = []
    i = 0
    n = len(clean_str)
    while i < n:
        while i < n and clean_str[i].isspace():
            i += 1
        if i >= n:
            break
        if clean_str[i] == '"':
            i += 1
            tok_chars: List[str] = []
            while i < n and clean_str[i] != '"':
                tok_chars.append(clean_str[i])
                i += 1
            if i >= n:
                return None, "Unclosed double quote in line"
            tokens.append("".join(tok_chars))
            i += 1
        else:
            start = i
            while i < n and not clean_str[i].isspace() and clean_str[i] != '"':
                i += 1
            tokens.append(clean_str[start:i])

    return tokens, None


KNOWN_KEYCONF_DIRECTIVES = {
    "addkeysection",
    "addmenukey",
    "alias",
    "defaultbind",
    "weaponsection",
    "addslotdefault",
    "setslot",
    "clearplayerclasses",
    "addplayerclass",
    "realias",
}


def parse_and_audit_keyconf(keyconf_path: Path) -> Tuple[Optional[KeyConfAuditResult], Optional[str]]:
    if not keyconf_path.exists():
        return None, f"KEYCONF file does not exist: {keyconf_path}"
    if not keyconf_path.is_file():
        return None, f"KEYCONF path is not a regular file: {keyconf_path}"

    try:
        content = keyconf_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decoding error reading KEYCONF '{keyconf_path}': {exc}"
    except Exception as exc:
        return None, f"Failed to read KEYCONF '{keyconf_path}': {exc}"

    sections: List[KeySectionEntry] = []
    menukeys: List[MenuKeyEntry] = []
    aliases: List[AliasEntry] = []
    defaultbinds: List[DefaultBindEntry] = []

    lines = content.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        tokens, err = tokenize_line(line)
        if err:
            return None, f"Line {line_idx}: Malformed syntax - {err}"
        if not tokens:
            continue

        cmd = tokens[0].lower()
        if cmd not in KNOWN_KEYCONF_DIRECTIVES:
            return None, f"Line {line_idx}: Unknown KEYCONF directive '{tokens[0]}'"

        if cmd == "addkeysection":
            if len(tokens) < 3:
                return None, f"Line {line_idx}: 'addkeysection' expects 2 arguments (<title> <section_name>), got {len(tokens) - 1}"
            sections.append(KeySectionEntry(line_number=line_idx, title=tokens[1], section_name=tokens[2]))

        elif cmd == "addmenukey":
            if len(tokens) < 3:
                return None, f"Line {line_idx}: 'addmenukey' expects 2 arguments (<description> <action>), got {len(tokens) - 1}"
            menukeys.append(MenuKeyEntry(line_number=line_idx, description=tokens[1], action=tokens[2]))

        elif cmd == "alias":
            if len(tokens) < 3:
                return None, f"Line {line_idx}: 'alias' expects 2 arguments (<name> <command>), got {len(tokens) - 1}"
            aliases.append(AliasEntry(line_number=line_idx, name=tokens[1], command=tokens[2]))

        elif cmd == "defaultbind":
            if len(tokens) < 3:
                return None, f"Line {line_idx}: 'defaultbind' expects 2 arguments (<key> <action>), got {len(tokens) - 1}"
            defaultbinds.append(DefaultBindEntry(line_number=line_idx, key=tokens[1], action=tokens[2]))

    binds_by_key: Dict[str, List[DefaultBindEntry]] = collections.defaultdict(list)
    for bind in defaultbinds:
        binds_by_key[bind.key.lower()].append(bind)

    duplicate_keys = {
        key: entries for key, entries in binds_by_key.items() if len(entries) > 1
    }

    bound_actions: Set[str] = {b.action.lower() for b in defaultbinds}
    menukey_actions: Set[str] = {m.action.lower() for m in menukeys}

    menukeys_lacking_bind = [
        m for m in menukeys if m.action.lower() not in bound_actions
    ]
    binds_lacking_menukey = [
        b for b in defaultbinds if b.action.lower() not in menukey_actions
    ]

    return (
        KeyConfAuditResult(
            sections=sections,
            menukeys=menukeys,
            aliases=aliases,
            defaultbinds=defaultbinds,
            binds_by_key=binds_by_key,
            duplicate_keys=duplicate_keys,
            menukeys_lacking_bind=menukeys_lacking_bind,
            binds_lacking_menukey=binds_lacking_menukey,
        ),
        None,
    )


def format_report(result: KeyConfAuditResult, keyconf_path: Path) -> str:
    lines: List[str] = []
    lines.append("=== KEYCONF AUDIT REPORT ===")
    lines.append(f"Target file: {keyconf_path}")
    lines.append("")

    lines.append(f"Declared Key Sections ({len(result.sections)}):")
    if result.sections:
        for s in result.sections:
            lines.append(f"  Line {s.line_number}: addkeysection \"{s.title}\" {s.section_name}")
    else:
        lines.append("  (None)")
    lines.append("")

    lines.append(f"Declared Menu Keys ({len(result.menukeys)}):")
    if result.menukeys:
        for m in result.menukeys:
            lines.append(f"  Line {m.line_number}: addmenukey \"{m.description}\" {m.action}")
    else:
        lines.append("  (None)")
    lines.append("")

    lines.append(f"Declared Aliases ({len(result.aliases)}):")
    if result.aliases:
        for a in result.aliases:
            lines.append(f"  Line {a.line_number}: alias {a.name} \"{a.command}\"")
    else:
        lines.append("  (None)")
    lines.append("")

    lines.append(f"Declared Default Bindings ({len(result.defaultbinds)}):")
    if result.defaultbinds:
        for b in result.defaultbinds:
            lines.append(f"  Line {b.line_number}: defaultbind {b.key} {b.action}")
    else:
        lines.append("  (None)")
    lines.append("")

    lines.append("Duplicate Default Bindings:")
    if result.duplicate_keys:
        for key, entries in sorted(result.duplicate_keys.items()):
            display_key = entries[0].key
            lines.append(f"  Key '{display_key}' ({len(entries)} actions):")
            for entry in entries:
                lines.append(f"    Line {entry.line_number}: {entry.action}")
    else:
        lines.append("  None (all default keys are unique)")
    lines.append("")

    lines.append("Menu Keys Lacking Defaultbind:")
    if result.menukeys_lacking_bind:
        for m in result.menukeys_lacking_bind:
            lines.append(f"  Line {m.line_number}: addmenukey \"{m.description}\" {m.action}")
    else:
        lines.append(f"  None (all {len(result.menukeys)} menu key actions have default bindings)")
    lines.append("")

    lines.append("Defaultbinds Lacking Menu Key Entry:")
    if result.binds_lacking_menukey:
        for b in result.binds_lacking_menukey:
            lines.append(f"  Line {b.line_number}: defaultbind {b.key} {b.action}")
    else:
        lines.append(f"  None (all {len(result.defaultbinds)} defaultbound actions have menu key entries)")
    lines.append("")

    if result.duplicate_keys:
        lines.append("DODA KEYCONF AUDIT FAILED")
    else:
        lines.append("DODA KEYCONF AUDIT PASSED")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit KEYCONF files for duplicate default bindings and menu key mismatches."
    )
    parser.add_argument(
        "--keyconf",
        "-k",
        required=True,
        type=Path,
        help="Path to KEYCONF file to audit",
    )

    args = parser.parse_args()

    result, err = parse_and_audit_keyconf(args.keyconf)
    if err:
        sys.stderr.write(f"DODA KEYCONF AUDIT ERROR: {err}\n")
        return 2

    assert result is not None
    report = format_report(result, args.keyconf)
    print(report)

    if result.duplicate_keys:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
