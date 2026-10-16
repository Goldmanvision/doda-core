# DoDA v136 Final Verification and Generated-Artifact Reconciliation

Prepared: 2026-10-16 EDT. Final reconciliation: `2026-10-16T15:09:19.5197300-04:00`.

## Final status

v136 is complete for its agreed installation, automated verification, manual GUI acceptance, and post-manual integrity criteria. No further automated test run or console probe is required merely to close v136.

This report is based on user-supplied local command output, a supplied screenshot, explicit user manual acceptance, and the supplied game log. It does not claim that the assistant directly executed commands on the user's computer.

## Repository and scope

- Authoritative local repository: `E:\Dev\uzdoom_src\doda-core`.
- Branch at final reconciliation: `feature/workbench-data-bridge`.
- Local HEAD: `78ad68769931ae6bc9c5edbd590d068ee030c915`.
- Applicable AGENTS.md recorded SHA256: `DB55CEADCB6A8E648A469423C221B5F7445E0A70DCB84B1D0BDE1A8ADF34B071`.
- Permitted v136 files: new freshness helper, shared GUI integration, new targeted test file, all under `tools/doda_content_workbench`.
- The final reconciliation reported branch and HEAD, but did not supply a fresh index listing. Do not infer a current empty index from an earlier installation preflight.

## Verified v136 implementation

Paths relative to `tools/doda_content_workbench`:

| File | SHA256 |
|---|---|
| `doda_export_freshness.py` | `A7C15FF6A168F425727CD0941C7A0FAF4B4E546CFB14E98A7F6DB5B9C5FDC4DB` |
| `doda_content_gui.py` | `1826638F4EE262FBF4DEF302A398C00DB6E56ADD401805B3BF5AE641BB81AEC0` |
| `tests/test_export_freshness_v136.py` | `FE2A2BFFB9545D12468E2AD16190DE376C36704B6CF27106470FECCDCDB84D79` |

Only `update_status_labels` and `run_network_rules` changed among GUI methods; the staged AST scope guard passed. The GUI gained the helper import. Existing Export All ordering, the exporter, catalog generator/checker API, editor draft behavior, schema, and renderer were not changed by v136.

## Behavior

The read-only helper distinguishes:

1. Department export versus saved CSVs: canonical department table inventory from the existing exporter; manifest source hashes; recorded department JSON output hash; required schema/table evidence.
2. Generated ZScript versus existing JSON: the existing catalog check, explicitly labeled `Catalog vs JSON`.

Each stage reports CURRENT, STALE, MISSING, or UNVERIFIED with a reason and appropriate next step. Missing, malformed, inaccessible, or changing inputs do not produce a false-current result or a new refresh exception. Hash checks use saved files, not editor drafts. Neither helper inspection nor validation warnings automatically export or regenerate content.

The export status says BUILT/NOT BUILT for PK3 presence, with a separate two-stage freshness line. BUILT is not an archive-integrity or gameplay-readiness claim. Rules validation reports distinct freshness warnings while preserving its existing validation semantics and Export All ordering.

## Automated evidence

- Staged focused suite: 73 tests passed in 2.035 seconds.
- Installed focused suite: 73 tests passed in 1.804 seconds.
- New test definitions: 41. The other 32 focused tests are existing export-chain, draft-export-context, and catalog tests.
- Installed full regression: 1,433 tests passed in 38.547 seconds.
- All runs: no failures, errors, or skips.
- No tests were rerun during final post-manual reconciliation.

Existing evidence directory: `generated/_tests_tmp/v136_run_20261016_145259_483d9aba`.

- `installed_record.json` SHA256: `86178779902FA922DE2675A9502642F84D3235CCDB7A5004AD3A7A5207A9E8FE`.
- `v136_staging_install_and_tests.txt` SHA256: `EC9C9E5788326FA6E58B12B4DDDF1979D96112DD8BD9708A7E14821584AF91F2`, freshly matched to the record during the 15:05 closeout check.
- Original shared-GUI backup: `doda_content_gui.py.original.bak` in that directory.
- Installed record's original manual field remains pending because it predates later user acceptance. This report supplements the historical record instead of rewriting it.

## Manual GUI acceptance

The user explicitly confirmed all three checks passed at 14:57 EDT on 2026-10-16:

1. Status/layout: BUILT rather than READY, Department export CURRENT, Catalog vs JSON CURRENT; screenshot showed readable status lines without overlap.
2. Repeated Refresh: two refreshes retained correct status without a new error.
3. Validation: completed without a new freshness exception or inappropriate stale warning for the refreshed data. Existing draft-configuration warnings were allowed to remain.

Stale/missing/malformed/changing-input cases have automated coverage; they are not claimed manually exercised. Interactive editor Save to Source/backup confirmation was not part of this checklist.

## Prior data correction and runtime evidence

The preceding inspection found that the saved OCCULT_RESPONSE/OCCULT_RESPONSE global staffing range was 1/1/2 while department JSON and its faithfully generated catalog still contained 0/1/2. The facility override already yielded 1/2/2, masking the stale global baseline in the effective row.

The approved six-output refresh used the existing validation engine/exporter/generator, with validation reporting isolated in its evidence directory rather than adding a seventh live output. Validation passed with 0 errors and 25 warnings about incomplete draft task/template-flow configuration. It verified normalized CSV-to-JSON agreement, manifest hashes, original PK3 packaged bytes/integrity, rebuilt catalog/expected-dump agreement, and override provenance. It changed no authored CSVs or implementation source.

Refresh evidence: `generated/_tests_tmp/foims_department_refresh_20261016_134751_1282b419/refresh_record.json`, SHA256 `9A9A5BAC25007F9C2C2BB61ACB7889CB6D1D1F8D094DE8F1E9D8C2243552A33D`.

The supplied `log-snapshot.txt`, beginning at 13:52:55 on 2026-10-16, records the unpacked working-folder load, completed script parsing/startup, MAP01 entry, and the actual catalog probe output:

- Generator 0.5.0; department fingerprint `ba31545886d7438d`.
- Six facilities, two capabilities, two links; four staffing defaults, four effective rows, three overrides.
- OCCULT_RESPONSE/OCCULT_RESPONSE: global 1/1/2; Field Operations Room effective 1/2/2, source OVERRIDE.
- OCCULT_RESPONSE/FIELD_RESPONSE: global/effective 1/2/2, source INHERITED.

That establishes observed loading and catalog values for the supplied run, not a new native-engine build, broad gameplay validity, or visual-pane acceptance. Three earlier in-game FOIMS-X visual checks remain unconfirmed and are separate from the completed v136 Workbench GUI gate.

## Post-manual integrity and generated-output reconciliation

The first final closeout at 15:05 freshly matched the three v136 sources, the installed record/log, and all 64 CSV hashes/inventory, then stopped because a generated network JSON byte hash had changed.

The read-only reconciliation at 15:09 confirmed:

- All three v136 source hashes still match.
- All 64 CSV hashes and inventory match.
- There are zero non-generated protected-file differences.
- 191 protected files are unchanged; five generated artifacts differ from installation-time byte hashes.
- Changed artifacts: network JSON, equipment JSON, department JSON, content manifest, and generated PK3.
- Network/equipment stable content fingerprints are unchanged and match current generated-catalog headers. Their changed bytes are consistent with new timestamps/JSON formatting, not a generator-relevant semantic change.
- The current department manifest matches all 12 department-source hashes and its two recorded output hashes.
- Generated WorkbenchCatalog.zs, expected dump, and LANGUAGE byte hashes remain unchanged from the verified refresh.

The network/equipment generated timestamps are around 18:56:18 UTC (14:56:18 EDT). The supplied screenshot also shows that newer PK3 build time. The evidence supports a normal re-export; this report does not claim an unobserved button click or exact byte-diff cause for every artifact. No rollback, guard bypass, regeneration, or tests occurred during reconciliation. PK3 archive-entry integrity was checked during the original 13:47 refresh, not re-executed against the later 14:56 archive during this closeout.

Stable content fingerprints, using the existing generator's timestamp-independent calculation:

- Network: `ca30bb147d2525c2d7ba9aeab9360fb3e53be65dd639812bee4f51ec8d0dfa36`.
- Equipment: `29cdce16968120b1daa127d59968b61cf37dacbd9e35cc7c59d938712c20f50d`.
- Current generated catalog department header: `ba31545886d7438d8538c5369049bebc88f47d634720bf0f3f8dc6eff1f3eaa7`.

## Current generated-output hashes

Paths relative to the repository, captured at final reconciliation:

| File | SHA256 |
|---|---|
| `build/doda-generated-content.pk3` | `88AFA9F0E5089DFA51F103DC6AF4200330AE77249DC54E0900EBF176157D092F` |
| `DoDA/Generated/WorkbenchCatalog.zs` | `16376AA9BF7FD202889061947745F34B5FD68B1429EB87ED5E40C1A68DBAB709` |
| `generated/data/department_content.json` | `BCFD871F3813D97351A9CEDD814EE9847DF7507F6B3DB6F5F9D22971BD3C3720` |
| `generated/data/equipment_catalog.json` | `444FC6590CB1367D9D5154B203770F05C8D75763A22F7598EB169EEFE62AD92A` |
| `generated/data/network_transfer_rules.json` | `BE750B2C731068719210EDA1D1ACDF4A5C66ABFECA4171581DF3097377A13CC6` |
| `generated/data/workbench_catalog_expected_dump.txt` | `5059EB5E70858782A8EE50463353B4DB4F69EAFAD20D688373318724A483FAB6` |
| `generated/language/DODA_GENERATED_LANGUAGE.txt` | `A23E4E7790B0A6901012EBE89EA328B202D7F1D48767C0A84E75411F75C20441` |
| `generated/manifest/content_manifest.json` | `862B29E2CBA37E7312E82187873B00A443A3620AD764326E126056EBDC90C07B` |

## Preservation, publication, and next work

No source/data edits, tests, runtime probes, exports, regeneration, or Git writes occurred in the final closeout/reconciliation. Existing bytecode and other uncommitted/untracked work were not cleaned up. No implementation commit, push, synchronization, native-engine modification, or simulation expansion was performed by these task packages.

This report and replacement current Project documents are prepared deliverables in the assistant's output environment. They are not automatically saved into the user's local repository, uploaded into the active Project, or published to GitHub. v136 report-only publication remains unperformed by the assistant. The user's HEAD advanced earlier with a message `updoot v135`; that alone does not establish which reports or documents were published. Reinspect remote state before any later publication and keep implementation publication separate.

The planned editor-conversion sequence and v136 safeguard are complete. No more tests/probes are required simply to record acceptance. Any next personnel/task persistence work must begin with explicit scope and a bounded review of existing behavior/evidence; do not assume the native loop is missing. The supplied runtime log already demonstrates initialized personnel/tasks/assignments and strategic-time progression, but does not establish save/load continuity.

Known cosmetic Enum status/delete wording saying tracks/facility remains recorded, not fixed. It is not a reason to reopen this completed safeguard or start broad cleanup.
