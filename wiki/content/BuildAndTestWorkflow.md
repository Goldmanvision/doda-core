# Build and Test Workflow

Status: Source-confirmed

1. Human author uses SLADE to edit, validate, package, or inspect map and asset content.
2. Human author manually launches GZDoom with the unpacked `gzdoda/doda-core` folder or an explicitly chosen test archive.
3. GZDoom script parsing, map loading, in-game behavior, and the resulting `console_log.txt` determine compile/load/test status.

Agents must not launch GZDoom, invoke SLADE, or claim runtime validation.
