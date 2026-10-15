# DoDA v130 Final Verification Checkpoint

Date: 2026-10-15 EDT. Status: v130 Facility Capabilities complete for the agreed installation, automated-test, and draft-only manual GUI criteria.

## Repository and permitted changes

Authoritative local repository: `E:\Dev\uzdoom_src\doda-core`.
Confirmed active branch: `feature/workbench-data-bridge`.
Local HEAD at final verification: `673ec61cd81f1b250db4bc8ca5a48c7af9b64183`; Git index was empty.

Exactly four Workbench implementation/test files were changed during v130, preserving prior uncommitted work. The final verification rechecked every installed hash against the files used in the passing automated tests.

| File under `tools\doda_content_workbench` | Verified SHA256 |
|---|---|
| `doda_facility_capabilities_editor.py` | `317E5AE68E1A41C79AEBA2C022F01DC1A8B5268506D91F900C9D5B9BCF87068E` |
| `doda_content_gui.py` | `766C71AA32934A3A4D0AA77AE56590C6847D0EADD3D3196A023F671CDA803E09` |
| `doda_facility_capabilities_draft_policy.py` | `3FA28C46DD8B949552668D32F27015D677023624A29B8E1E1A563BF4696324B5` |
| `tests\test_facility_capabilities_v130.py` | `1D41F81E58AA73420382CB1BA4A23CCE80157C53BF9279CB8ED0C12749119932` |

## Installation and automated evidence

The installed implementation separates draft Apply/Delete from Save to Source and preserves composite identity, deliberate mixed-value editing, per-facility capacity checks, reference protection, draft retention, close/project-switch guards, and validated writes with verified backups. Installed targeted tests passed 93/93 and the full Workbench regression passed 1,168/1,168, with no failures, errors, or skips; seven automated Tk widget checks and eight real-validator tests are included. ([Installation and automated verification report](https://github.com/Goldmanvision/doda-core/blob/7195c364134935711fa297080ca096ee2932aad5/temp_push/DoDA_v130_Installation_20261015_073801_4f9b1142.txt))

These are prior successful test runs, not newly rerun tests after manual verification. At this checkpoint, the local logs were reread for the expected test counts and successful completion, and their SHA256 hashes were recorded:

- Targeted: `generated\_tests_tmp\v130_direct_20261015_073801_4f9b1142\installed_targeted_tests.txt`, SHA256 `FA853B3FD492399EB93566068B2F87475CE0D188499FB9C802333EB7C624A510`.
- Full regression: `generated\_tests_tmp\v130_direct_20261015_073801_4f9b1142\installed_full_regression.txt`, SHA256 `BFE60D4017396126E182893CBE236E64E08088AAD83EC0E9D9737238332BE762`.

The existing Workbench `.venv` Python 3.14.6 and unittest discovery were used; a disposable test runner accommodated the Windows restricted-token temporary-directory behavior without changing product code or suppressing tests. ([Installation report](https://github.com/Goldmanvision/doda-core/blob/7195c364134935711fa297080ca096ee2932aad5/temp_push/DoDA_v130_Installation_20261015_073801_4f9b1142.txt))

## Manual GUI evidence

The user first confirmed personnel-limit rejection and referenced-installation deletion/deactivation rejection, then confirmed “All passed” for the remaining requested checks in this conversation on 2026-10-15. The following are recorded as user-reported successful manual GUI checks, not independently observed by Computer:

- Startup and Refresh load successfully with column alignment preserved.
- Single-row and multi-row Apply preserve selection identity and untouched mixed values.
- Blank FOIMS Panel ID is rejected; blank Display Override is allowed.
- Excessive personnel limits reject the whole edit using each installation's own facility capacity.
- Applied drafts survive Refresh; project switching is blocked.
- Canceling either window-close or File -> Exit preserves the app and draft.
- Revert Form restores draft values; Revert Draft restores source values.
- Deleting or deactivating an existing referenced installation is rejected before accepting the draft mutation.

Individual observations beyond these confirmed criteria were not supplied. Optional new-installation/delete checks, interactive Save to Source, and interactive backup confirmation are not claimed as manually verified.

## Post-manual integrity and limitations

All 64 authored CSVs were freshly compared with the pre-v130 baseline after the user reported manual success, and every file matched. The four installed source hashes also remained unchanged; no new implementation changes or test runs were made to close this checkpoint.

Python/Tk test success and the manual editor checks do not establish native-engine, ZScript, or in-game validity. No such validation was performed.

## Backups and publication boundaries

Original editor and GUI backups remain beneath:
`E:\Dev\uzdoom_src\doda-core\generated\_tests_tmp\v130_direct_20261015_073801_4f9b1142\originals`.

The original PowerShell installer encountered a write denial and its partial installation was rolled back before native filesystem installation succeeded. Do not rerun that installer; the successful installed hashes above are authoritative. ([Installation report](https://github.com/Goldmanvision/doda-core/blob/7195c364134935711fa297080ca096ee2932aad5/temp_push/DoDA_v130_Installation_20261015_073801_4f9b1142.txt))

The earlier installation report was published as a remote report-only commit, `7195c364134935711fa297080ca096ee2932aad5`; the commit changes only that report. ([Report-only commit](https://github.com/Goldmanvision/doda-core/commit/7195c364134935711fa297080ca096ee2932aad5))

This final checkpoint is approved for report-only publication under `temp_push` through the existing GitHub connection. Implementation source remains uncommitted, and local HEAD is deliberately left unchanged because the sandbox cannot create the local branch-ref lock. No fetch, pull, reset, branch switch, implementation commit, or ACL change is performed as part of closing v130.

## Next slice

v131 Facilities is the proposed next bounded editor modernization. Its current local source has been read, but no v131 implementation is installed and the v130 four-file authorization is not treated as approval to modify Facilities.
