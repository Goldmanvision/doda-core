<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# We need to rewrite the user manual document for the Content Workbench. Let's create a PDF with sections, tables, examples, table of contents, glossary, etc. A user with no knowledge of the Workbench application should be able to read this manual and understand how to use the Workbench, step-by-step when necessary. We can do this in batches if necessary, and I can combine the PDF sections myself.

Yes—we can rewrite the Content Workbench manual as a beginner-friendly PDF, with a table of contents, illustrated workflows, reference tables, worked examples, troubleshooting, and a glossary. I need the existing manual and current application sources first so the instructions describe the actual Workbench rather than assumed features.

## Source material needed

The project-file lookup returned DoDA game documentation rather than the Content Workbench manual or application code. The returned material covers engine systems, gameplay architecture, and development history—not the Workbench controls and authoring workflows needed for this rewrite.[^1_1][^1_2]

Please upload a ZIP containing the current Workbench documentation and application source, or upload the existing manual together with the relevant UI and data-handling files. Include these where available:


| Material | What it lets me verify |
| :-- | :-- |
| Existing user manual | Current coverage, terminology, and material to preserve or replace |
| README and launch scripts | Prerequisites, installation, and exact startup instructions |
| Application and UI source | Actual menus, tabs, buttons, dialogs, and keyboard shortcuts |
| Schemas and validation rules | Required fields, allowed values, relationships, and error conditions |
| Small sample project | Reproducible beginner exercises and realistic examples |
| Current screenshots | Visual orientation and annotated interface explanations |
| Known limitations | Unsupported operations and warnings users need before changing data |

The manual and source are the essential inputs. Screenshots and sample content can follow.

## Proposed manual structure

The manual should teach a complete first workflow before presenting exhaustive reference material.


| Part | Contents | Reader outcome |
| :-- | :-- | :-- |
| 1. Getting started | Purpose, core concepts, prerequisites, startup, interface tour, first guided exercise | Launch the application and complete a small, safe task |
| 2. Everyday authoring | Supported content types, creating and editing records, relationships, search and filtering | Perform routine authoring without guessing |
| 3. Checking and saving | Validation, resolving issues, saving, loading, importing or exporting where supported | Understand what changes, where it is stored, and how to verify it |
| 4. Worked examples | End-to-end examples using verified sample data | Connect individual controls into practical workflows |
| 5. Reference and recovery | Field tables, shortcuts, troubleshooting, limitations, glossary, task index | Find answers quickly after the initial read |

These are proposed documentation sections, not claims about which features the application currently supports.

## How procedures will read

Each substantial procedure will include:

- **Goal:** What the reader will accomplish.
- Prerequisites: What must already be open, selected, or available.
- Numbered steps using the exact visible control labels.
- Expected result: What the reader should see after completing the steps.
- Verification: How to confirm the operation succeeded.
- Warnings: Any overwrite, deletion, relationship, or unsaved-change implications.
- Recovery: What to do when the expected result does not appear.

Examples will explain both the action and its purpose. They will distinguish illustrative values from required values and avoid assuming that a beginner understands IDs, schemas, references, or validation.

## PDF delivery

We can produce the manual in separate batches without sacrificing consistency:


| Batch | Deliverable |
| :-- | :-- |
| A | Getting started and first guided workflow |
| B | Everyday authoring and content reference |
| C | Validation, saving, and end-to-end examples |
| D | Troubleshooting, glossary, and consolidated navigation |

Each PDF will have consistent typography, numbered sections, readable tables, page numbers, and bookmarks. Standalone batches will have their own contents pages; a consolidated contents page with final page numbers can be generated after the chapters are complete.

I have not generated a PDF yet because the essential Workbench-specific evidence is missing. Upload the current manual and Workbench source ZIP so I can begin the actual rewrite with Batch A.

<span style="display:none">[^1_3]</span>

<div align="center">⁂</div>

[^1_1]: wiki/junie/CHANGELOG.md

[^1_2]: wiki/DoDA_Wiki_Reconciliation_2026-08-17.md

[^1_3]: wiki/Consolidated_Wiki_Audit.md


---

# No documentation exists currently

Understood—we’re creating the **first** Content Workbench user manual, not rewriting an existing document. You do not need to supply any prior documentation.

We already have enough conversation evidence to outline the manual and document Task Templates accurately. For a complete beginner guide to all 12 editors, however, I need the current application source so I can verify each control, field, and workflow.

## What to provide

Please upload a ZIP containing these two folders from your current project:

```text
E:\Dev\uzdoom_src\doda-core\tools\doda_content_workbench
E:\Dev\uzdoom_src\doda-core\data_authoring\source
```

Exclude `.venv`, `__pycache__`, and backup folders to keep the upload small. Include the launcher, validator, exporter, editor modules, and current CSVs.

The project-file search did not locate the Workbench implementation; it returned unrelated DoDA refactor documentation, so those files cannot establish the application’s behavior.[^2_1][^2_2]

Screenshots are optional initially. A screenshot of the main window and representative editor tabs would help later with the interface tour.

## Manual structure

I suggest three PDF batches, each useful on its own:


| Batch | Sections | Purpose |
| :-- | :-- | :-- |
| 1 — Getting started | Purpose, terminology, files and folders, launching, interface tour, first guided workflow | Help a complete beginner start safely |
| 2 — Authoring reference | All 12 tables, field definitions, relationships, editor procedures, worked examples | Explain what to enter and why |
| 3 — Validation and recovery | Validation, export, backups, troubleshooting, limitations, glossary, task index | Help users verify work and recover from problems |

Each batch will contain a contents page, numbered sections, page numbers, readable tables, and step-by-step procedures. We can also produce a combined PDF once all sections are approved.

## Important distinctions

The manual will explicitly distinguish:

- Editing a form from saving a record.
- Authored CSVs from generated output.
- Validation success from runtime testing.
- Exporting a PK3 from enabling game integration.
- Deactivating a record from deleting it.
- Existing records from illustrative exercise data.

Those distinctions matter here: your verified export remains a data-only overlay, while Task Templates saves validate the complete candidate project before replacing its CSV.

## Writing approach

Procedures will use exact button names and explain:

1. What the task accomplishes.
2. What the reader needs beforehand.
3. Which controls to use, in order.
4. What result to expect.
5. How to verify success.
6. How to recover or undo safely.

We will use your existing `SIGNAL_REVIEW` and `OCCULT_INCIDENT_RESPONSE` records for concrete explanations, clearly labeling any new exercise records as examples. The manual will describe user behavior—not require readers to understand the implementation phases or regression-test scripts.

Upload the source ZIP next. That supplies the missing evidence for Batch 1 without requiring you to write documentation first.

<div align="center">⁂</div>

[^2_1]: docs/junie-refactor-plan.md

[^2_2]: docs/junie-refactor-tasks.md


---

# doda_content_workbench and source have been uploaded to this Perplexity Project space. Please review.

I can now access the uploaded Workbench files. I reviewed the README, the validator’s table definitions and validation logic, the exporter, and the complete Task Templates editor; this establishes a reliable foundation for the manual, though the GUI launcher, other editors, and uploaded CSV contents still need review.[^3_1][^3_2][^3_3][^3_4]

## Review findings

| Area | Confirmed behavior | Manual implication |
| :-- | :-- | :-- |
| Source data | Editable CSVs belong in `data_authoring/source`; generated files and build artifacts are not intended for manual editing. | Explain which files users should edit and which they should regenerate. [^3_1] |
| Validation | The validator registers 12 tables and checks keys, controlled values, numeric fields, and relationships. | Teach dependencies—not just individual form fields. [^3_2] |
| Export | The exporter validates first, then produces normalized JSON, a LANGUAGE fragment, a hash manifest, and a PK3. | Document saving and exporting as separate operations. [^3_3] |
| Runtime boundary | The export deliberately does not modify game integration files; its manifest marks runtime integration as disabled. | Make clear that exporting does not activate authored content in the game. [^3_3] |
| Task Templates saves | Saves validate a complete temporary candidate project, create a CSV backup, replace the source CSV, and refresh the application. | Explain the save sequence and how to locate backups. [^3_4] |
| External changes | Task Templates checks whether its CSV changed before saving and again after candidate validation. | Include a troubleshooting procedure for “Refresh before saving.” [^3_4] |

## The 12 authoring tables

The uploaded validator confirms the following table inventory. The explanations below summarize their fields and validation relationships—not yet the exact labels of every GUI tab.[^3_2]


| Table | Beginner-facing purpose |
| :-- | :-- |
| Enum catalog | Defines controlled choices used by other records |
| Department tracks | Defines departmental categories referenced by facilities |
| Metrics | Defines measurements, bounds, defaults, and display settings |
| Metric tiers | Divides metric ranges into labeled status bands |
| Facilities | Defines facilities, their departmental track, and personnel capacity |
| Flavor text | Stores titled descriptive text referenced by other content |
| Qualification catalog | Defines qualifications used in staffing rules |
| Capabilities | Defines capabilities and standing-operation labels |
| Facility capabilities | Associates a capability with a facility |
| Capability staffing rules | Defines qualification-based contributor counts for a capability |
| Facility capability staffing overrides | Defines installation-specific contributor counts |
| Task templates | Defines task defaults associated with a capability |

## Important documentation details

Several behaviors deserve explicit beginner explanations:

- Metric tiers must cover a metric’s complete range without gaps or overlaps. A valid-looking individual tier can therefore fail because of neighboring tiers.[^3_2]
- Contributor counts must satisfy $0 \leq \text{minimum} \leq \text{preferred} \leq \text{maximum}$. Facility-capability concurrency also cannot exceed its parent facility’s personnel capacity.[^3_2]
- Deactivation does not automatically remove dependency requirements. Several validators require references to active parent records even when checking an inactive child record. The manual should not present “uncheck Active” as a universal workaround.[^3_2]
- Task effort and deadline must each be positive, but there is no requirement that effort be less than deadline. We should document that rule without inventing runtime scheduling behavior.[^3_4][^3_2]
- In Task Templates, **Revert** reloads the selected record’s form values; it does not restore an earlier saved CSV. **Open Backups** opens the backup folder—it is not an automatic restore command.[^3_4]


## Documentation cleanup needed

The uploaded README is an early scaffold: it describes an “eventual desktop GUI” and gives `python -m doda_workbench --help` as a future command. It should not be used as the current launch guide without checking the launcher.[^3_1]

Version terminology also needs care. The validator declares `0.1.0`, while the exporter declares tool version `0.1.1` and export schema version `2`. Those are separate implementation identifiers; the manual should distinguish them rather than assign one version number to everything.[^3_3][^3_2]

## Next manual batch

The next review should cover the main GUI and remaining editors before producing the beginner PDF. Batch 1 will then contain:

1. What the Workbench does—and does not do.
2. Essential terminology and the project folder layout.
3. Verified launch instructions.
4. A tour of the actual tabs and application controls.
5. A safe, read-only first exercise.
6. A guided edit/save/validate/export workflow.
7. A contents page, quick-reference tables, and starter glossary.

No additional upload is needed for the files already retrieved. I have not generated the PDF yet: the remaining interface review is necessary to avoid giving beginners incorrect button names or unsupported procedures.

<div align="center">⁂</div>

[^3_1]: doda_content_workbench/README.md

[^3_2]: doda_content_workbench/doda_content_workbench.py

[^3_3]: doda_content_workbench/doda_content_export.py

[^3_4]: doda_content_workbench/doda_task_templates_editor.py


---

# If it would help to produce MD files with embedded CSVs before the PDF compilation, we can do that. I can then give you the md files to produce the finalized PDF. Does that work?

Yes—that works well. We can create and review the manual as **Markdown** chapters first, with embedded CSV examples, then use the approved chapters to produce the finalized PDF.

You can upload the edited Markdown files back here when ready. I can also generate both the Markdown deliverables and the PDF in this conversation, so re-uploading is only necessary if you edit them yourself.

## Recommended workflow

1. Review the remaining application sources to verify controls, procedures, and field rules.
2. Generate a first batch of Markdown chapters as downloadable files.
3. Review the chapters for accuracy, clarity, terminology, and coverage.
4. Revise and approve each batch.
5. Compile the approved chapters into one PDF—or separate PDFs—with a paginated contents page, bookmarks, tables, examples, and glossary.

The application source remains the authority for behavior; Markdown becomes the editable authority for the manual’s wording.

## How to include CSVs

Use readable tables for teaching and fenced CSV blocks when readers need exact source syntax.


| Format | Best use |
| :-- | :-- |
| Markdown table | Field definitions, allowed values, relationships, and comparisons |
| Fenced `csv` block | Exact headers and small, copyable examples |
| Separate CSV file | Complete datasets or exercise files |
| Appendix | Full schemas and longer reference material |

For example, a chapter could include this clearly labeled extract:

````markdown
### Example: Task timing fields

This is a partial example, not a complete importable task record.

```csv
task_template_id,default_target_effort_minutes,default_deadline_minutes
SIGNAL_REVIEW,240,120
```

Both timing values must be positive integers. Effort may exceed deadline.
````

That timing rule is supported by the uploaded validator and Task Templates editor.[^4_1][^4_2]

For wide tables such as Task Templates’ ten-column CSV, the PDF should primarily use a vertical field/value table. The exact CSV can remain in the Markdown or appendix without forcing readers to decipher tiny text. The editor’s `FIELDS` definition supplies those ten columns.[^4_2]

## Suggested chapter files

| Chapter | Contents |
| :-- | :-- |
| 01 — Introduction | Purpose, audience, limitations, and essential concepts |
| 02 — Getting started | Project layout, prerequisites, launch, and interface tour |
| 03 — First workflow | Guided inspection, editing, saving, validation, and export |
| 04 — Core content | Tracks, metrics, tiers, facilities, flavor text, and enums |
| 05 — Capabilities and staffing | Qualifications, capabilities, installations, rules, and overrides |
| 06 — Task templates | Fields, creation, editing, removal, and worked examples |
| 07 — Validation and recovery | Errors, warnings, backups, external changes, and troubleshooting |
| 08 — Reference | Glossary, schema reference, command reference, and task index |

We should keep full CSV snapshots separate from the procedural chapters and date them. Otherwise, readers could mistake the example dataset for required or permanently current content.

## PDF preparation

The Markdown chapters should use consistent heading levels, numbered procedures, exact control names, and labeled warnings. Cross-references should name sections rather than hard-code page numbers; final page numbers belong in the PDF compilation stage.

I can render the approved content into a formatted PDF, but we should not assume every Markdown extension or HTML fragment will convert automatically. Simple headings, tables, lists, code blocks, and separate image assets give us a predictable format.

**Next:** finish reviewing the main GUI and remaining editors, then generate Markdown Batch 1: Introduction, Getting Started, and the First Guided Workflow. No PDF compilation is needed until that text is reviewed.

<div align="center">⁂</div>

[^4_1]: doda_content_workbench/doda_content_workbench.py

[^4_2]: doda_content_workbench/doda_task_templates_editor.py


---

```
# \<q>Next: finish reviewing the main GUI and remaining editors, then generate Markdown Batch 1: Introduction, Getting Started, and the First Guided Workflow. No PDF compilation is needed until that text is reviewed.\</q> Let's continue
```

Markdown Batch 1 is ready: three beginner-facing chapters, separate review notes, and a ZIP containing all four files. No PDF has been compiled.

## What’s included

| Chapter | Coverage |
| :-- | :-- |
| 1 — Introduction | Purpose, limitations, the 12 content tables, essential terminology, and safety rules |
| 2 — Getting Started | Existing-installation launch instructions, project folders, verified menus, editor orientation, and a read-only exercise |
| 3 — First Guided Workflow | A controlled Task Templates edit, reversion, saving, validation, export, backup location, and troubleshooting |

The three chapters contain approximately **3,700 words**, with section-level contents lists, reference tables, numbered procedures, and embedded CSV, JSON, and PowerShell examples.

## Verified foundation

The draft uses the current GUI’s confirmed menu labels, startup behavior, and editor installation calls. Its launch procedure targets your existing installation rather than inventing a fresh setup process.[^5_1]

The guided exercise uses `SIGNAL_REVIEW` from the uploaded CSV and the actual Task Templates save, backup, and external-change checks.[^5_2][^5_3]

The export section documents the four generated artifacts and explicitly distinguishes successful packaging from enabled game integration.[^5_4]

## Review boundaries

I have **not** finished reviewing the other eleven editor implementations. Batch 1 therefore avoids claiming that all editors share Task Templates’ save or backup behavior.

The separate editorial notes record remaining verification gaps, including full refresh behavior, project switching, preview operation, and fresh installation instructions. They are not intended for the final beginner manual.

Review the launch instructions and guided workflow against the running application first. Any corrections can be made directly in the Markdown files before we continue with the editor-reference chapters and final PDF formatting.

<div align="center">⁂</div>

[^5_1]: doda_content_workbench/doda_content_gui.py

[^5_2]: source/task_templates.csv

[^5_3]: doda_content_workbench/doda_task_templates_editor.py

[^5_4]: doda_content_workbench/doda_content_export.py


---

# Looks good, let's continue.

Markdown Batch 2A is ready: Chapter 4, Core Content Authoring, plus separate editorial review notes and a ZIP containing both. The chapter adds approximately **3,900 words** of field reference, procedures, examples, and troubleshooting.

## Chapter coverage

| Editor | Included guidance |
| :-- | :-- |
| Department Tracks | Create, edit, remove, and understand facility dependencies |
| Metrics | Field rules, defaults, safe edits, and creation/removal limitations |
| Metric Tiers | Inclusive ranges, coverage rules, colors, and boundary-change precautions |
| Facilities | Controlled choices, linkage identifiers, capacity, and removal safeguards |
| Flavor Text | Create narrative records, edit categories, and handle tier references |
| Enum Catalog | Filter groups, edit labels, and understand controlled-value dependencies |

The procedures use the actual editor button labels and distinguish candidate rejection from a warning issued after a CSV has already been saved.[^6_1][^6_2][^6_3][^6_4][^6_5]

## Findings worth reviewing

The source review uncovered three issues that affect beginner instructions:

- Metric Tiers assigns several controls to overlapping grid positions. The chapter flags this for visual verification rather than promising that every control is accessible.[^6_6]
- Enum Catalog contains a self-recursive dependent-refresh helper. Its shown save method does not directly call that helper, so I have not claimed that ordinary saves fail.[^6_5]
- New metrics and complete tier sets cannot necessarily be created through sequential single-table saves: validation requires metrics to have tiers and tiers to reference existing metrics. The chapter explains this limitation instead of providing a misleading creation procedure.[^6_2][^6_7][^6_6]

No application code or authored CSVs were changed. No PDF has been compiled.

The next batch is Chapter 5: Qualifications, Capabilities, Installations, Staffing Rules, and Overrides.

<span style="display:none">[^6_10][^6_11][^6_8][^6_9]</span>

<div align="center">⁂</div>

[^6_1]: doda_content_workbench/doda_track_editor.py

[^6_2]: doda_content_workbench/doda_metrics_editor.py

[^6_3]: doda_content_workbench/doda_facilities_editor.py

[^6_4]: doda_content_workbench/doda_flavor_text_editor.py

[^6_5]: doda_content_workbench/doda_enum_catalog_editor.py

[^6_6]: doda_content_workbench/doda_metric_tiers_editor.py

[^6_7]: doda_content_workbench/doda_content_workbench.py

[^6_8]: source/department_tracks.csv

[^6_9]: source/metrics.csv

[^6_10]: source/metric_tiers.csv

[^6_11]: source/facilities.csv


---

```
# \<q>Metric Tiers assigns several controls to overlapping grid positions. The chapter flags this for visual verification rather than promising that every control is accessible.Enum Catalog contains a self-recursive dependent-refresh helper. Its shown save method does not directly call that helper, so I have not claimed that ordinary saves fail.New metrics and complete tier sets cannot necessarily be created through sequential single-table saves: validation requires metrics to have tiers and tiers to reference existing metrics. The chapter explains this limitation instead of providing a misleading creation procedure.\</q> Should we correct these issues before continuing and then write the documentation according to the updated code?
```

Yes—we should correct and test these issues before finalizing the affected documentation. The first two are code defects to address narrowly; the third is a workflow limitation that needs a deliberate design change, not weaker validation.

## Recommended treatment

| Issue | Recommended action | Required verification |
| :-- | :-- | :-- |
| Metric Tiers layout | Assign distinct grid rows to the presets, Flavor Text, Sort Order, buttons, and explanatory text. | Check the running GUI at its minimum supported window size; verify every field and button is accessible. [^7_1] |
| Enum Catalog recursive helper | Inspect its callers, then replace the self-call with the intended refresh operation—or remove the helper if it is genuinely unused. | Verify catalog saves and dependent dropdown refresh without recursion, stale choices, or loss of unsaved edits. [^7_2] |
| Metrics/tier coordinated changes | Add a supported workflow that stages and validates the metric and its complete tier set together. | Test creation, range changes, and failure recovery while preserving complete coverage and valid references. [^7_3][^7_4][^7_1] |

The layout problem is evident in the grid assignments, but its exact visible effect still needs GUI confirmation. Likewise, the enum helper is self-recursive, but the reviewed save method does not directly call it; we should resolve its actual role before patching.[^7_1][^7_2]

## Preserve validation

We should **not** allow missing tiers, gaps, overlaps, or dangling metric references merely to make sequential saves possible. Those checks protect the data model.[^7_3]

For the third issue, I recommend a proposed “Metric and Tiers” workflow that:

1. Stages a metric and its complete tier set without changing live CSVs.
2. Validates the full candidate project.
3. Backs up both affected source files.
4. Commits the coordinated change with explicit recovery handling.
5. Refreshes the GUI and reports the outcome.

That is a new feature proposal, not an existing capability. Replacing two files independently is not a single atomic transaction, so failure between replacements must be handled and tested.

The same workflow could support moving adjacent tier boundaries without forcing an invalid intermediate save. Metric deletion should remain a separate, explicitly designed operation rather than silently cascading into tier deletion.

## Implementation order

Keep the changes small and independently verifiable:

1. Repair and smoke-test the Metric Tiers layout.
2. Repair and regression-test Enum Catalog refresh.
3. Implement and sandbox-test coordinated metric/tier authoring.
4. Validate the unchanged live source data.
5. Upload the updated modules to this project.
6. Revise Chapter 4 and any affected Batch 1 passages against the tested implementation.

Until then, keep the Markdown drafts as review material and defer PDF compilation.

We should also correct the stale README and GUI introductory comments during the documentation pass: they describe a future GUI or read-only application despite the current editor installation code.[^7_5][^7_6]

## Next step

Start with a guarded patch for the **Metric Tiers layout only**. It should back up the module, verify the expected anchors, compile the candidate, and leave authored CSVs untouched. After the GUI check passes, move to the enum refresh repair—not combine all three changes into one patch.

<div align="center">⁂</div>

[^7_1]: doda_content_workbench/doda_metric_tiers_editor.py

[^7_2]: doda_content_workbench/doda_enum_catalog_editor.py

[^7_3]: doda_content_workbench/doda_content_workbench.py

[^7_4]: doda_content_workbench/doda_metrics_editor.py

[^7_5]: doda_content_workbench/README.md

[^7_6]: doda_content_workbench/doda_content_gui.py


---

```
# \<q>Next stepStart with a guarded patch for the Metric Tiers layout only. It should back up the module, verify the expected anchors, compile the candidate, and leave authored CSVs untouched. After the GUI check passes, move to the enum refresh repair—not combine all three changes into one patch.\</q> Go
```

Close the Workbench, then run this block. It patches **only the Metric Tiers layout**, moving the color presets, Flavor Text selector, buttons, and explanatory text into separate rows while leaving Sort Order on row 9. The overlapping positions are present in the uploaded editor source.[^8_1]

## Phase 32 — Repair tier layout

The block verifies its anchors, backs up the original module, checks that the Python syntax tree changes only in the four intended row assignments, and verifies live CSV hashes. It does not run an export or change validation rules.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$editorPath = Join-Path $toolDir 'doda_metric_tiers_editor.py'

foreach ($path in @($pythonPath, $editorPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required component not found: $path"
    }
}

Write-Host 'Phase 32: Metric Tiers layout repair only' -ForegroundColor Cyan

$patchScript = @'
import ast
import copy
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[^8_1]).resolve()
tools = root / "tools/doda_content_workbench"
path = tools / "doda_metric_tiers_editor.py"
source_dir = root / "data_authoring/source"
temporary = path.with_name(path.name + ".layout.tmp")

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(source_dir.is_dir(), "Source CSV directory not found.")
csv_paths = sorted(source_dir.glob("*.csv"))
require(len(csv_paths) == 12, "Expected exactly 12 source CSV files.")
source_before = {p.name: digest(p) for p in csv_paths}

original_bytes = path.read_bytes()
original_hash = digest(path)
original = original_bytes.decode("utf-8-sig")
original_tree = ast.parse(original, filename=str(path))

classes = [
    node for node in original_tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "MetricTiersEditor"
]
require(len(classes) == 1, "Expected one MetricTiersEditor class.")

builds = [
    node for node in classes[^8_0].body
    if isinstance(node, ast.FunctionDef) and node.name == "build"
]
require(len(builds) == 1, "Expected one build() method.")
build = builds[^8_0]

lines = original.splitlines(keepends=True)
changes = []

def grid_call(receiver):
    matches = []
    for node in ast.walk(build):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "grid"
        ):
            continue
        if ast.unparse(node.func.value) == receiver:
            matches.append(node)
    require(
        len(matches) == 1,
        "Expected one grid call for " + receiver
        + "; found " + str(len(matches)),
    )
    return matches[^8_0]

def row_keyword(call, expected):
    matches = [kw for kw in call.keywords if kw.arg == "row"]
    require(len(matches) == 1, "Expected one row keyword.")
    keyword = matches[^8_0]
    require(
        isinstance(keyword.value, ast.Constant)
        and type(keyword.value.value) is int
        and keyword.value.value == expected,
        "Layout differs from expected row " + str(expected)
        + ". No patch applied.",
    )
    return keyword

for receiver, old, new in (
    ("preset_frame", 9, 7),
    ("self.flavor_combo", 9, 8),
    ("buttons", 9, 10),
):
    call = grid_call(receiver)
    keyword = row_keyword(call, old)
    changes.append((keyword.value, new, receiver))

help_calls = []
for node in ast.walk(build):
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "grid"
        and isinstance(node.func.value, ast.Call)
    ):
        continue

    widget = node.func.value
    if ast.unparse(widget.func) != "ttk.Label":
        continue

    texts = [
        kw.value for kw in widget.keywords if kw.arg == "text"
    ]
    if (
        len(texts) == 1
        and isinstance(texts[^8_0], ast.Constant)
        and isinstance(texts[^8_0].value, str)
        and texts[^8_0].value.startswith(
            "Candidate validation enforces complete metric coverage,"
        )
    ):
        help_calls.append(node)

require(
    len(help_calls) == 1,
    "Expected one candidate-validation explanatory label.",
)
keyword = row_keyword(help_calls[^8_0], 10)
changes.append((keyword.value, 11, "validation help text"))

candidate_lines = list(lines)
for value, new, label in changes:
    require(
        value.lineno == value.end_lineno,
        "Unexpected multiline row value.",
    )
    index = value.lineno - 1
    raw = candidate_lines[index].encode("utf-8")
    replacement = (
        raw[:value.col_offset]
        + str(new).encode("ascii")
        + raw[value.end_col_offset:]
    )
    candidate_lines[index] = replacement.decode("utf-8")

candidate = "".join(candidate_lines)
candidate_tree = ast.parse(candidate, filename=str(path))
compile(candidate, str(path), "exec")

expected_tree = copy.deepcopy(original_tree)
expected_class = next(
    node for node in expected_tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "MetricTiersEditor"
)
expected_build = next(
    node for node in expected_class.body
    if isinstance(node, ast.FunctionDef) and node.name == "build"
)

positions = {
    (value.lineno, value.col_offset): new
    for value, new, label in changes
}
changed_count = 0
for node in ast.walk(expected_build):
    if isinstance(node, ast.Constant):
        position = (node.lineno, node.col_offset)
        if position in positions:
            node.value = positions[position]
            changed_count += 1

require(changed_count == 4, "Expected exactly four AST row changes.")
require(
    ast.dump(expected_tree, include_attributes=False)
    == ast.dump(candidate_tree, include_attributes=False),
    "Candidate contains changes beyond the four intended grid rows.",
)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup_dir = tools / "backups" / ("metric_tiers_layout_" + stamp)
backup_dir.mkdir(parents=True, exist_ok=False)
backup = backup_dir / path.name
shutil.copy2(path, backup)
require(digest(backup) == original_hash, "Backup verification failed.")

installed = False
try:
    temporary.write_bytes(candidate.encode("utf-8"))
    require(
        digest(path) == original_hash,
        "Editor changed externally. Installation cancelled.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == source_before,
        "Source CSV changed during preparation. Installation cancelled.",
    )

    os.replace(temporary, path)
    installed = True

    compile(
        path.read_text(encoding="utf-8-sig"),
        str(path),
        "exec",
    )
    require(
        path.read_bytes() == candidate.encode("utf-8"),
        "Installed module differs from candidate.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == source_before,
        "Source CSV hashes changed during patch.",
    )

    print("\n=== Metric Tiers Layout Repair ===")
    for value, new, label in changes:
        print(f"  {label}: row {value.value} -> {new}")
    print("PASS: exactly four layout-row changes")
    print("PASS: installed module syntax")
    print("PASS: all 12 live source CSV hashes unchanged")
    print("Backup:", backup)
    print("Previous SHA256:", original_hash)
    print("New SHA256:", digest(path))
    print("Phase 32 patch complete. GUI verification is still required.")

except Exception:
    if installed:
        shutil.copy2(backup, path)
        require(
            digest(path) == original_hash,
            "Rollback verification failed. Preserve the backup.",
        )
        print("Previous Metric Tiers module restored from backup.")
    raise

finally:
    if temporary.exists():
        temporary.unlink()
'@

$patchScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 32 failed. Review the error and rollback status above.'
}
```


## GUI verification

After the patch completes, launch the Workbench:

```powershell
$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'

& (Join-Path $toolDir '.venv\Scripts\python.exe') `
    (Join-Path $toolDir 'doda_content_gui.py') `
    --root $root
```

Perform these checks without saving or removing any records:

1. Open Metric Tiers and select `PREPAREDNESS / FRAGILE`.
2. Confirm UI Color, the color chooser, and swatch remain visible.
3. Confirm the six color presets occupy their own row.
4. Confirm Flavor Text and Sort Order are separately visible and populated.
5. Confirm Add Tier, Save Tier, Remove Tier, Revert Form, and Open Backups do not overlap other controls.
6. Resize the window down to its minimum size and check accessibility again.
7. If you try a color preset, click Revert Form afterward; do not save.
8. Close normally.

This patch fixes the identified row collisions; it does not yet prove that the entire form fits every display configuration. Paste the patch summary and report whether the GUI checks pass, including a screenshot if controls remain clipped or overlapped.

<div align="center">⁂</div>

[^8_1]: doda_content_workbench/doda_metric_tiers_editor.py


---

# }

Phase 32: Metric Tiers layout repair only

=== Metric Tiers Layout Repair ===
preset_frame: row 9 -> 7
self.flavor_combo: row 9 -> 8
buttons: row 9 -> 10
validation help text: row 10 -> 11
PASS: exactly four layout-row changes
PASS: installed module syntax
PASS: all 12 live source CSV hashes unchanged
Backup: E:\\Dev\\uzdoom_src\\doda-core\\tools\\doda_content_workbench\\backups\\metric_tiers_lay
out_20261006_071806_930300\\doda_metric_tiers_editor.py
Previous SHA256: c9736ebc4f215c51a80feaf10e3684ca0c12359b7fab7242be899c1890202776
New SHA256: 476e9e65664f20eb57555c766e794fd1e057c14baefb4e0122946443b0193eee
Phase 32 patch complete. GUI verification is still required.

The Phase 32 patch **passed** its code checks: exactly four layout-row assignments changed, the installed module compiled, and all 12 live source CSV hashes remained unchanged. GUI verification is still pending, so we should finish that before changing Enum Catalog.

## Launch the Workbench

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$guiPath = Join-Path $toolDir 'doda_content_gui.py'

& $pythonPath $guiPath --root $root

if ($LASTEXITCODE -ne 0) {
    throw 'Workbench exited with an error. Review the traceback above.'
}
```


## Check the repaired layout

Open Metric Tiers and select `PREPAREDNESS / FRAGILE`. Check the following arrangement; these are the controls defined by the reviewed editor.[^9_1]


| Area | Expected result |
| :-- | :-- |
| UI Color | Entry, Choose Color button, and swatch remain accessible |
| Presets | Grey, Green, Amber, Red, Blue, and Purple appear on their own row |
| Flavor Text | Dropdown appears separately from the presets and Sort Order |
| Sort Order | Entry remains visible on its own row |
| Action buttons | Add Tier, Save Tier, Remove Tier, Revert Form, and Open Backups do not overlap fields |
| Explanatory text | Appears below the action buttons |

Also resize the window down to its minimum size and check for clipping. Do not save or remove anything during this test. If you try a color preset, click Revert Form afterward.

Reply **success** if everything is accessible, or provide a screenshot of any remaining overlap or clipping. After that, we’ll inspect the Enum Catalog helper’s callers before preparing its guarded repair.

<div align="center">⁂</div>

[^9_1]: doda_content_workbench/doda_metric_tiers_editor.py


---

# success

Phase 32 is complete: the layout patch passed its code checks, and you confirmed the GUI checks succeeded. We can remove the Metric Tiers overlap warning when updating Chapter 4.

Next is a **read-only inspection** of the Enum Catalog refresh helper and its callers. The uploaded helper calls itself, but we need to establish how the current local application refreshes dependent editors before choosing the repair.[^10_1]

## Phase 33 — Inspect enum refresh

This block reads Python source without importing or executing the application. It does not modify files, validate data, or export content.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 33: read-only Enum Catalog refresh inspection' -ForegroundColor Cyan

$inspectionScript = @'
import ast
import sys
from pathlib import Path

tools = Path(sys.argv[^10_1]).resolve()
helper = "refresh_dependents_after_catalog_save"
enum_path = tools / "doda_enum_catalog_editor.py"
gui_path = tools / "doda_content_gui.py"

for path in (enum_path, gui_path):
    if not path.is_file():
        raise FileNotFoundError("Required module not found: " + str(path))

def read(path):
    text = path.read_text(encoding="utf-8-sig")
    return text, ast.parse(text, filename=str(path))

def print_function(path, class_name, function_name):
    text, tree = read(path)
    matches = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            matches.extend(
                item for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == function_name
            )

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one {class_name}.{function_name}; found {len(matches)}"
        )

    node = matches[^10_0]
    lines = text.splitlines()
    print(f"\n=== {path.name}: {class_name}.{function_name} ===")
    for index in range(node.lineno - 1, node.end_lineno):
        print(f"{index + 1:5}: {lines[index]}")

print_function(
    enum_path, "EnumCatalogEditor",
    "refresh_dependents_after_catalog_save"
)
print_function(enum_path, "EnumCatalogEditor", "save")
print_function(gui_path, "ContentWorkbenchApp", "refresh_all")

print("\n=== Helper references in top-level Workbench Python modules ===")
reference_count = 0
for path in sorted(tools.glob("*.py")):
    text = path.read_text(encoding="utf-8-sig")
    for number, line in enumerate(text.splitlines(), start=1):
        if helper in line:
            reference_count += 1
            print(f"{path.name}:{number}: {line.strip()}")

print("Reference lines found:", reference_count)

print("\n=== Calls to editor update methods inside refresh_all ===")
text, tree = read(gui_path)
app_class = next(
    node for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "ContentWorkbenchApp"
)
refresh = next(
    node for node in app_class.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "refresh_all"
)
calls = [
    node for node in ast.walk(refresh)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "update"
]
for node in sorted(calls, key=lambda item: item.lineno):
    print(f"{node.lineno}: {ast.unparse(node)}")

print("\nPhase 33 inspection complete. No files changed.")
'@

$inspectionScript | & $pythonPath - $toolDir

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 33 inspection failed. Review the Python error above.'
}
```

Paste the output. It will let us determine whether to remove an unused helper or replace it with a targeted refresh operation—without introducing another full refresh or unnecessarily resetting unsaved forms.

<div align="center">⁂</div>

[^10_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# Phase 33: read-only Enum Catalog refresh inspection

# === doda_enum_catalog_editor.py: EnumCatalogEditor.refresh_dependents_after_catalog_save

154: def refresh_dependents_after_catalog_save(self) -> None:
155: try:
156: self.refresh_dependents_after_catalog_save()
157: except Exception as error:
158: self.app.log(
159: "Enum Catalog saved, but dependent editor refresh failed: "
160: + str(error)
161: )
162: return
163:
164: self.app.log(
165: "Enum Catalog saved; refreshed dependent editor choices."
166: )

=== doda_enum_catalog_editor.py: EnumCatalogEditor.save ===
728: def save(self) -> None:
729: row = self.record()
730:
731: if row is None:
732: return
733:
734: rows = self.rows()
735:
736: if self.editing_key:
737: if (
738: row["enum_group"] != self.editing_key[0]
739: or row["enum_value"] != self.editing_key[1]
740: ):
741: messagebox.showerror(
742: "DoDA Content Workbench",
743: "Enum Group and Enum Value cannot change after creation.",
744: )
745: return
746:

747: rows = $$
748: row
749: if (
750: item.get("enum_group") == self.editing_key[0]
751: and item.get("enum_value") == self.editing_key[1]
752: )
753: else item
754: for item in rows
755:
$$

756:
757: action = "updated"
758:
759: else:
760: if any(
761: item.get("enum_group") == row["enum_group"]
762: and item.get("enum_value") == row["enum_value"]
763: for item in rows
764: ):
765: messagebox.showerror(
766: "DoDA Content Workbench",
767: "This Enum Group and Enum Value combination already exists.",
768: )
769: return
770:
771: rows.append(row)
772: action = "added"
773:
774: temporary = self.app.source_directory / (
775: f".enum-catalog-{uuid4().hex}.tmp.csv"
776: )
777:
778: self.app.config(cursor="watch")
779: self.app.update_idletasks()
780:
781: try:
782: self.write(temporary, rows)
783:
784: valid, output = self.candidate_valid(temporary)
785:
786: self.app.log("Enum Catalog candidate validation output:")
787:
788: for line in output.splitlines():
789: self.app.log(" " + line)
790:
791: if not valid:
792: messagebox.showerror(
793: "DoDA Content Workbench",
794: (
795: "Enum Catalog candidate validation failed. Source CSV "
796: "was unchanged.\\n\\nReview Activity Log for details."
797: ),
798: )
799: return
800:
801: folder = self.backup_directory()
802: folder.mkdir(parents=True, exist_ok=True)
803:
804: backup = folder / (
805: "enum_catalog\_"
806: + datetime.now().strftime("%Y%m%d\_%H%M%S\_%f")
807: + ".csv"
808: )
809:
810: shutil.copy2(self.source_path(), backup)
811: os.replace(temporary, self.source_path())
812:
813: self.editing_key = (
814: row["enum_group"],
815: row["enum_value"],
816: )
817:
818: self.app.log(f"Created Enum Catalog backup: {backup}")
819: self.app.log(
820: f"Enum Catalog {action}: "
821: f"{row['enum_group']} / {row['enum_value']}"
822: )
823:
824: self.app.refresh_all(False)
825:
826: valid, output = self.post_validate()
827:
828: for line in output.splitlines():
829: self.app.log(" " + line)
830:
831: self.app.refresh_all(False)
832:
833: if valid:
834: messagebox.showinfo(
835: "DoDA Content Workbench",
836: (
837: f"Enum Value '{row['enum_group']} / {row['enum_value']}' "
838: f"{action}.\\n\\nBackup created:\\n{backup}\\n\\n"
839: "Project validation passed."
840: ),
841: )
842: else:
843: messagebox.showwarning(
844: "DoDA Content Workbench",
845: (
846: f"Enum Catalog {action}, but post-save validation failed.\
n\\n"
847: f"Backup:\\n{backup}"
848: ),
849: )
850:
851: except (OSError, ValueError) as error:
852: self.app.log(f"ENUM CATALOG SAVE ERROR: {error}")
853:
854: messagebox.showerror(
855: "DoDA Content Workbench",
856: f"Unable to save Enum Catalog value.\\n\\n{error}",
857: )
858:
859: finally:
860: if temporary.exists():
861: temporary.unlink()
862:
863: self.app.config(cursor="")
864: self.app.update_idletasks()

=== doda_content_gui.py: ContentWorkbenchApp.refresh_all ===
1172: def refresh_all(self, show_message: bool = False) -> None:
1173: try:
1174: self.tables = {
1175: table_name: read_csv(self.source_directory / filename)
1176: for table_name, filename in SOURCE_FILES.items()
1177: }
1178: if hasattr(self, "metrics_editor"):
1179: self.metrics_editor.update()
1180:
1181: if hasattr(self, "metric_tiers_editor"):
1182: self.metric_tiers_editor.update()
1183:
1184: if hasattr(self, "facilities_editor"):
1185: self.facilities_editor.update()
1186:
1187: if hasattr(self, "enum_catalog_editor"):
1188: self.enum_catalog_editor.update()
1189:
1190: if hasattr(self, "qualification_catalog_editor"):
1191: self.qualification_catalog_editor.update()
1192:
1193: if hasattr(self, "capabilities_editor"):
1194: self.capabilities_editor.update()
1195:
1196: if hasattr(self, "facility_capabilities_editor"):
1197: self.facility_capabilities_editor.update()
1198:
1199: if hasattr(self, "capability_staffing_rules_editor"):
1200: self.capability_staffing_rules_editor.update()
1201:
1202: if hasattr(self, "facility_capability_staffing_overrides_editor"):
1203: self.facility_capability_staffing_overrides_editor.update()
1204:
1205: if hasattr(self, "task_templates_editor"):
1206: self.task_templates_editor.update()
1207:
1208: self.load_validation_report()
1209: self.update_dashboard()
1210: self.update_tracks()
1211: self.update_metrics()
1212: self.update_facilities()
1213: self.update_flavor_text()
1214: self.update_status_labels()
1215:
1216: self.status_text.set("Source data refreshed successfully.")
1217: self.log("Source data refreshed.")
1218:
1219: if show_message:
1220: messagebox.showinfo(
1221: APP_TITLE,
1222: "Source data was refreshed successfully.",
1223: )
1224:
1225: except Exception as error:
1226: self.status_text.set("Refresh failed.")
1227: self.log(f"REFRESH ERROR: {error}")
1228: messagebox.showerror(
1229: APP_TITLE,
1230: f"Unable to refresh source data.\\n\\n{error}",
1231: )

=== Helper references in top-level Workbench Python modules ===
doda_enum_catalog_editor.py:154: def refresh_dependents_after_catalog_save(self) -> None:
doda_enum_catalog_editor.py:156: self.refresh_dependents_after_catalog_save()
Reference lines found: 2

=== Calls to editor update methods inside refresh_all ===
1179: self.metrics_editor.update()
1182: self.metric_tiers_editor.update()
1185: self.facilities_editor.update()
1188: self.enum_catalog_editor.update()
1191: self.qualification_catalog_editor.update()
1194: self.capabilities_editor.update()
1197: self.facility_capabilities_editor.update()
1200: self.capability_staffing_rules_editor.update()
1203: self.facility_capability_staffing_overrides_editor.update()
1206: self.task_templates_editor.update()

Phase 33 inspection complete. No files changed.

Phase 33 confirms that the recursive helper has no references outside its definition and self-call in the top-level Workbench modules. The save method already calls `refresh_all(False)`, which reloads CSVs and updates the dependent editors. The safest narrow repair is therefore to **remove the unused helper**, not add another refresh path. The uploaded Enum Catalog source also shows this redundant helper and the existing save refresh calls.[^11_1]

## Phase 34 — Remove unused helper

Close the Workbench before running this block.

It checks the helper’s exact structure, refuses to proceed if another top-level module references it, backs up the module, and verifies that the only syntax-tree change is removing that method. It leaves the launcher, save method, and authored CSVs unchanged.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 34: remove unused recursive enum helper only' -ForegroundColor Cyan

$patchScript = @'
import ast
import copy
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[^11_1]).resolve()
tools = root / "tools/doda_content_workbench"
path = tools / "doda_enum_catalog_editor.py"
helper_name = "refresh_dependents_after_catalog_save"
temporary = path.with_name(path.name + ".cleanup.tmp")

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(path.is_file(), "Enum Catalog module not found.")

source_dir = root / "data_authoring/source"
csv_paths = sorted(source_dir.glob("*.csv"))
require(len(csv_paths) == 12, "Expected exactly 12 source CSV files.")
csv_before = {p.name: digest(p) for p in csv_paths}

original_bytes = path.read_bytes()
original_hash = digest(path)
original = original_bytes.decode("utf-8-sig")
tree = ast.parse(original, filename=str(path))

classes = [
    node for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "EnumCatalogEditor"
]
require(len(classes) == 1, "Expected one EnumCatalogEditor class.")
editor_class = classes[^11_0]

helpers = [
    node for node in editor_class.body
    if isinstance(node, ast.FunctionDef)
    and node.name == helper_name
]
require(
    len(helpers) == 1,
    "Expected one recursive helper. It may already be removed; no patch applied.",
)
helper = helpers[^11_0]
require(not helper.decorator_list, "Unexpected decorated helper.")

expected_helper = ast.parse('''
def refresh_dependents_after_catalog_save(self) -> None:
    try:
        self.refresh_dependents_after_catalog_save()
    except Exception as error:
        self.app.log(
            "Enum Catalog saved, but dependent editor refresh failed: "
            + str(error)
        )
        return

    self.app.log(
        "Enum Catalog saved; refreshed dependent editor choices."
    )
''').body[^11_0]

require(
    ast.dump(helper, include_attributes=False)
    == ast.dump(expected_helper, include_attributes=False),
    "Helper differs from the inspected implementation. No patch applied.",
)

references = []
for module_path in sorted(tools.glob("*.py")):
    text = module_path.read_text(encoding="utf-8-sig")
    for number, line in enumerate(text.splitlines(), start=1):
        if helper_name not in line:
            continue
        if (
            module_path == path
            and helper.lineno <= number <= helper.end_lineno
        ):
            continue
        references.append(f"{module_path.name}:{number}: {line.strip()}")

require(
    not references,
    "Additional helper references found; removal cancelled:\n"
    + "\n".join(references),
)

save_methods = [
    node for node in editor_class.body
    if isinstance(node, ast.FunctionDef) and node.name == "save"
]
require(len(save_methods) == 1, "Expected one save method.")
refresh_calls = [
    node for node in ast.walk(save_methods[^11_0])
    if isinstance(node, ast.Call)
    and ast.unparse(node.func) == "self.app.refresh_all"
]
require(
    len(refresh_calls) == 2
    and all(
        len(node.args) == 1
        and isinstance(node.args[^11_0], ast.Constant)
        and node.args[^11_0].value is False
        and not node.keywords
        for node in refresh_calls
    ),
    "Save refresh calls differ from the inspected implementation.",
)

lines = original.splitlines(keepends=True)
candidate = "".join(
    lines[:helper.lineno - 1] + lines[helper.end_lineno:]
)
candidate_tree = ast.parse(candidate, filename=str(path))
compile(candidate, str(path), "exec")

expected_tree = copy.deepcopy(tree)
expected_class = next(
    node for node in expected_tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "EnumCatalogEditor"
)
expected_class.body = [
    node for node in expected_class.body
    if not (
        isinstance(node, ast.FunctionDef)
        and node.name == helper_name
    )
]
require(
    ast.dump(candidate_tree, include_attributes=False)
    == ast.dump(expected_tree, include_attributes=False),
    "Candidate contains changes beyond helper removal.",
)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup_dir = tools / "backups" / ("enum_helper_cleanup_" + stamp)
backup_dir.mkdir(parents=True, exist_ok=False)
backup = backup_dir / path.name
shutil.copy2(path, backup)
require(digest(backup) == original_hash, "Backup verification failed.")

installed = False
try:
    temporary.write_bytes(candidate.encode("utf-8"))
    require(
        digest(path) == original_hash,
        "Module changed externally. Installation cancelled.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == csv_before,
        "Source CSV changed during preparation. Installation cancelled.",
    )

    os.replace(temporary, path)
    installed = True

    installed_text = path.read_text(encoding="utf-8-sig")
    compile(installed_text, str(path), "exec")
    require(
        path.read_bytes() == candidate.encode("utf-8"),
        "Installed file differs from candidate.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == csv_before,
        "Live source CSV hashes changed.",
    )

    print("\n=== Enum Helper Cleanup ===")
    print("PASS: no additional top-level helper references")
    print("PASS: only the unused recursive method removed")
    print("PASS: save method and existing refresh calls unchanged")
    print("PASS: installed module syntax")
    print("PASS: all 12 live source CSV hashes unchanged")
    print("Backup:", backup)
    print("Previous SHA256:", original_hash)
    print("New SHA256:", digest(path))
    print("Phase 34 complete: unused recursive helper removed.")

except Exception:
    if installed:
        shutil.copy2(backup, path)
        require(
            digest(path) == original_hash,
            "Rollback verification failed. Preserve the backup.",
        )
        print("Previous Enum Catalog module restored from backup.")
    raise

finally:
    if temporary.exists():
        temporary.unlink()
'@

$patchScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 34 failed. Review the error and rollback status above.'
}
```


## What this establishes

This removes dead recursive code while preserving the current refresh behavior. It does **not** prove that every dependent dropdown refreshes correctly or that unsaved form values survive refresh; those need a separate sandbox test.

Paste the Phase 34 summary. After it passes, we’ll test Enum Catalog saving and dependent-choice refresh without editing your live authored data.

<div align="center">⁂</div>

[^11_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# Phase 34: remove unused recursive enum helper only

=== Enum Helper Cleanup ===
PASS: no additional top-level helper references
PASS: only the unused recursive method removed
PASS: save method and existing refresh calls unchanged
PASS: installed module syntax
PASS: all 12 live source CSV hashes unchanged
Backup: E:\\Dev\\uzdoom_src\\doda-core\\tools\\doda_content_workbench\\backups\\enum_helper_clea
nup_20261006_072642_032749\\doda_enum_catalog_editor.py
Previous SHA256: 5ed135866cad0fa69f3a4f841a6fc7f9c7f7e1a760c902924cd07c362717797d
New SHA256: 463634478375e4aac296c6ffff0426839141c46bc87bf9e157231e56cccf91c8
Phase 34 complete: unused recursive helper removed.

Phase 34 passed. The unused recursive helper is removed, the save method is unchanged, and all 12 live CSV hashes remained unchanged.

Next we’ll test **actual Enum Catalog saving and GUI refresh in a temporary project**, including whether a new task priority appears in the Task Templates dropdown. The reviewed enum editor supplies the form fields and save path used by this test.[^12_1]

## Phase 35 — Sandbox enum tests

Close the Workbench first. This block creates a temporary project, copies the source CSVs and top-level application modules into it, and runs a hidden instance of the real GUI.

It tests creation, repeat editing, backup contents, dependent choices, preservation of an unsaved Task Templates name, and rejection of deactivating a referenced priority. Dialogs are captured rather than displayed.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 35: real GUI enum tests in a temporary project' -ForegroundColor Cyan

$testScript = @'
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^12_1]).resolve()
live_tools = root / "tools/doda_content_workbench"
live_source = root / "data_authoring/source"
csv_paths = sorted(live_source.glob("*.csv"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(csv_paths) == 12, "Expected exactly 12 live source CSVs.")
before = {p.name: digest(p) for p in csv_paths}
results = []
dialogs = []
app = None

def capture(kind):
    def handler(*args, **kwargs):
        message = str(args[^12_1]) if len(args) > 1 else str(kwargs)
        dialogs.append({"kind": kind, "message": message})
        return None
    return handler

def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def test(name, function):
    try:
        function()
        results.append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)
    except Exception as error:
        results.append({
            "name": name,
            "passed": False,
            "exception": repr(error),
        })
        print("FAIL: " + name, flush=True)
        print(repr(error), flush=True)

try:
    with tempfile.TemporaryDirectory(prefix="doda-enum-gui-test-") as tmp:
        sandbox = Path(tmp)
        tools = sandbox / "tools/doda_content_workbench"
        source = sandbox / "data_authoring/source"
        tools.mkdir(parents=True)
        source.mkdir(parents=True)
        (sandbox / "DoDA").mkdir()
        (sandbox / "generated/reports").mkdir(parents=True)
        (sandbox / "build").mkdir()

        for path in live_tools.glob("*.py"):
            shutil.copy2(path, tools / path.name)
        for path in csv_paths:
            shutil.copy2(path, source / path.name)

        sys.path.insert(0, str(tools))
        from doda_content_gui import ContentWorkbenchApp

        with (
            patch("tkinter.messagebox.showinfo", capture("info")),
            patch("tkinter.messagebox.showwarning", capture("warning")),
            patch("tkinter.messagebox.showerror", capture("error")),
            patch("tkinter.messagebox.askyesno", return_value=False),
        ):
            try:
                app = ContentWorkbenchApp(sandbox)
                app.withdraw()
                app.update()

                require(
                    not any(d["kind"] == "error" for d in dialogs),
                    "GUI startup reported errors: " + repr(dialogs),
                )

                enum = app.enum_catalog_editor
                tasks = app.task_templates_editor
                enum_path = source / "enum_catalog.csv"
                original_enum = enum_path.read_bytes()
                backup_dir = sandbox / "data_authoring/backups/enum_catalog"

                test_value = "WORKBENCH_TEST_PRIORITY"
                require(
                    not any(
                        row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                        for row in read_rows(enum_path)
                    ),
                    "Reserved test priority already exists in this snapshot.",
                )

                selected_task = next(
                    row for row in tasks.loaded_rows
                    if row["active"].upper() == "TRUE"
                )
                tasks.tree.selection_set(selected_task["task_template_id"])
                tasks.on_select()
                app.update()
                dirty_name = "UNSAVED SANDBOX NAME"
                tasks.vars["display_name"].set(dirty_name)

                def set_enum_form(group, value, label, description, order):
                    enum.enum_group.set(group)
                    enum.enum_value.set(value)
                    enum.display_label.set(label)
                    enum.description.delete("1.0", "end")
                    enum.description.insert("1.0", description)
                    enum.sort_order.set(str(order))
                    enum.active.set(True)

                def create_enum():
                    enum.new()
                    enum.catalog_group_filter.set("All Groups")
                    set_enum_form(
                        "TASK_PRIORITY", test_value,
                        "Workbench test priority",
                        "Temporary sandbox-only priority.",
                        enum.next_sort_order("TASK_PRIORITY"),
                    )
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        not any(d["kind"] in {"error", "warning"} for d in dialogs),
                        "Save reported an error or warning: " + repr(dialogs),
                    )
                    matches = [
                        row for row in read_rows(enum_path)
                        if row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                    ]
                    require(len(matches) == 1, "New priority was not saved.")
                    copies = list(backup_dir.glob("*.csv"))
                    require(len(copies) == 1, "Expected exactly one enum backup.")
                    require(
                        copies[^12_0].read_bytes() == original_enum,
                        "First backup differs from the original enum CSV.",
                    )

                test("Create enum through real save; exact backup", create_enum)

                def dependent_choices():
                    choices = tuple(tasks.widgets["priority"]["values"])
                    require(
                        test_value in choices,
                        "New priority is absent from Task Templates dropdown.",
                    )
                    require(
                        any(
                            row["enum_group"] == "TASK_PRIORITY"
                            and row["enum_value"] == test_value
                            for row in app.tables["enum_catalog"]
                        ),
                        "Application table cache did not reload the new enum.",
                    )

                test("Real refresh updates task choices and table cache", dependent_choices)

                def preserve_unsaved():
                    require(
                        tasks.vars["display_name"].get() == dirty_name,
                        "Refresh replaced the unsaved Task Templates name.",
                    )

                test("Unsaved selected-task display name survives enum save", preserve_unsaved)

                def repeat_edit():
                    key = "TASK_PRIORITY::" + test_value
                    require(enum.tree.exists(key), "New enum row is not visible.")
                    enum.tree.selection_set(key)
                    enum.on_select()
                    app.update()
                    previous = enum_path.read_bytes()
                    count = len(list(backup_dir.glob("*.csv")))
                    enum.display_label.set("Updated sandbox priority")
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        not any(d["kind"] in {"error", "warning"} for d in dialogs),
                        "Repeat save reported an error or warning: " + repr(dialogs),
                    )
                    row = next(
                        row for row in read_rows(enum_path)
                        if row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                    )
                    require(
                        row["display_label"] == "Updated sandbox priority",
                        "Repeat save did not update the label.",
                    )
                    copies = list(backup_dir.glob("*.csv"))
                    require(len(copies) == count + 1, "Repeat save created no backup.")
                    require(
                        any(p.read_bytes() == previous for p in copies),
                        "No backup matches the pre-edit CSV.",
                    )

                test("Repeat enum edit succeeds with pre-edit backup", repeat_edit)

                def reject_referenced_deactivation():
                    priority = selected_task["priority"]
                    key = "TASK_PRIORITY::" + priority
                    enum.catalog_group_filter.set("All Groups")
                    enum.update()
                    require(enum.tree.exists(key), "Referenced priority row missing.")
                    enum.tree.selection_set(key)
                    enum.on_select()
                    app.update()
                    previous = enum_path.read_bytes()
                    count = len(list(backup_dir.glob("*.csv")))
                    enum.active.set(False)
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        enum_path.read_bytes() == previous,
                        "Rejected deactivation changed the enum CSV.",
                    )
                    require(
                        len(list(backup_dir.glob("*.csv"))) == count,
                        "Rejected deactivation created a backup.",
                    )
                    require(
                        any(
                            d["kind"] == "error"
                            and "candidate validation failed" in d["message"].lower()
                            for d in dialogs
                        ),
                        "Expected candidate-validation rejection was not reported.",
                    )

                test(
                    "Referenced priority deactivation rejected without changes",
                    reject_referenced_deactivation,
                )

            finally:
                if app is not None:
                    app.destroy()
                    app = None

except Exception as error:
    results.append({
        "name": "Sandbox setup or GUI execution",
        "passed": False,
        "exception": repr(error),
    })
    print("FAIL: Sandbox setup or GUI execution", flush=True)
    print(repr(error), flush=True)

unchanged = before == {p.name: digest(p) for p in csv_paths}
results.append({"name": "Live source CSV hashes unchanged", "passed": unchanged})
print(
    ("PASS: " if unchanged else "FAIL: ")
    + "Live source CSV hashes unchanged",
    flush=True,
)

report_dir = root / "generated/reports"
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
report_path = report_dir / ("enum_gui_regression_" + stamp + ".json")
passed = sum(row["passed"] for row in results)
report = {
    "testedAtLocal": datetime.now().astimezone().isoformat(),
    "scope": (
        "Real hidden GUI and enum save/refresh in a temporary project; "
        "dialogs mocked; no export; selected Task Templates name preservation only"
    ),
    "valid": passed == len(results),
    "passedCount": passed,
    "testCount": len(results),
    "liveSourcesUnchanged": unchanged,
    "results": results,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("\n=== Enum GUI Regression Summary ===")
print(f"Passed: {passed}/{len(results)}")
print("Live sources unchanged:", unchanged)
print("Report:", report_path)

if not report["valid"]:
    raise SystemExit(1)

print("Phase 35 complete: sandbox enum GUI tests passed.")
'@

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 35 failed. Review the failed cases and regression report.'
}
```

The target is **6/6** checks passed. Preservation is tested only for one unsaved Task Templates display name—not every field in every editor.

Paste the summary and any failures. If a test fails, we’ll inspect that behavior before making another code change.

<div align="center">⁂</div>

[^12_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# Phase 35: real GUI enum tests in a temporary project

PASS: Create enum through real save; exact backup
PASS: Real refresh updates task choices and table cache
FAIL: Unsaved selected-task display name survives enum save
AssertionError('Refresh replaced the unsaved Task Templates name.')
PASS: Repeat enum edit succeeds with pre-edit backup
PASS: Referenced priority deactivation rejected without changes
PASS: Live source CSV hashes unchanged

=== Enum GUI Regression Summary ===
Passed: 5/6
Live sources unchanged: True
Report: E:\\Dev\\uzdoom_src\\doda-core\\generated\\reports\\enum_gui_regression_20261006_072741
\_835121.json
Phase 35 failed. Review the failed cases and regression report.
At line:321 char:5

- ```
throw 'Phase 35 failed. Review the failed cases and regression re ...
```

- ```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

    - CategoryInfo : OperationStopped: (Phase 35 failed...ression report.:Stri
ng) [], RuntimeException
    - FullyQualifiedErrorId : Phase 35 failed. Review the failed cases and regression r
eport.

Phase 35 found a real preservation failure in the tested workflow: saving an enum refreshed the Task Templates form and replaced its unsaved display name. The other five checks passed, including live-source integrity.

The likely mechanism is that Task Templates rebuilds its record list during `update()`, reselects the record, and then its selection handler reloads saved values into the form. Those operations are present in the editor, but we should confirm the event sequence before patching it.[^13_1]

## Phase 35A — Isolate refresh behavior

Close the Workbench. This diagnostic runs the real GUI in a temporary project, performs **no saves**, and records whether refresh triggers the selection handler and replaces unsaved fields.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 35A: sandbox refresh diagnostic - no saves' -ForegroundColor Cyan

$diagnosticScript = @'
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^13_1]).resolve()
live_tools = root / "tools/doda_content_workbench"
live_source = root / "data_authoring/source"
paths = sorted(live_source.glob("*.csv"))

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(paths) == 12, "Expected exactly 12 source CSVs.")
before = {p.name: digest(p) for p in paths}
errors = []
app = None

def error_dialog(*args, **kwargs):
    errors.append(str(args[^13_1]) if len(args) > 1 else str(kwargs))

try:
    with tempfile.TemporaryDirectory(prefix="doda-refresh-diagnostic-") as tmp:
        sandbox = Path(tmp)
        tools = sandbox / "tools/doda_content_workbench"
        source = sandbox / "data_authoring/source"
        tools.mkdir(parents=True)
        source.mkdir(parents=True)
        (sandbox / "DoDA").mkdir()
        (sandbox / "generated/reports").mkdir(parents=True)
        (sandbox / "build").mkdir()

        for path in live_tools.glob("*.py"):
            shutil.copy2(path, tools / path.name)
        for path in paths:
            shutil.copy2(path, source / path.name)

        sys.path.insert(0, str(tools))
        from doda_content_gui import ContentWorkbenchApp

        with (
            patch("tkinter.messagebox.showinfo"),
            patch("tkinter.messagebox.showwarning"),
            patch("tkinter.messagebox.showerror", error_dialog),
        ):
            try:
                app = ContentWorkbenchApp(sandbox)
                app.withdraw()
                app.update()
                require(not errors, "Startup errors: " + repr(errors))

                editor = app.task_templates_editor
                require(bool(editor.loaded_rows), "No task templates available.")

                row = editor.loaded_rows[^13_0]
                key = row["task_template_id"]
                editor.tree.selection_set(key)
                editor.on_select()

                # Drain selection events before creating unsaved input.
                app.update()
                app.update()

                events = []
                original_handler = editor.on_select

                def observe_selection(event=None):
                    events.append({
                        "selection": list(editor.tree.selection()),
                        "nameBeforeHandler": editor.vars["display_name"].get(),
                    })
                    original_handler(event)
                    events[-1]["nameAfterHandler"] = (
                        editor.vars["display_name"].get()
                    )

                editor.tree.bind("<<TreeviewSelect>>", observe_selection)

                dirty_name = "UNSAVED REFRESH DIAGNOSTIC"
                dirty_description = "Unsaved description for sandbox diagnosis."
                editor.vars["display_name"].set(dirty_name)
                editor.description.delete("1.0", "end")
                editor.description.insert("1.0", dirty_description)

                def snapshot():
                    values = {
                        field: var.get()
                        for field, var in editor.vars.items()
                    }
                    values["description"] = editor.description.get(
                        "1.0", "end-1c"
                    )
                    return values

                dirty = snapshot()

                # Check that idle event processing alone does not reset the form.
                app.update()
                require(
                    snapshot() == dirty,
                    "Form changed before refresh; event isolation failed.",
                )

                print("\n=== Before Refresh ===")
                print("Selected task:", key)
                print("Display name:", editor.vars["display_name"].get())
                print("Selection events after settling:", len(events))

                events.clear()
                app.refresh_all(False)
                immediate = snapshot()

                print("\n=== Immediately After refresh_all ===")
                print("Display name:", immediate["display_name"])
                print("Form preserved:", immediate == dirty)

                app.update()
                app.update()
                settled = snapshot()

                print("\n=== After Selection Events ===")
                print("Display name:", settled["display_name"])
                print("Form preserved:", settled == dirty)
                print("Changed fields:", [
                    field for field in dirty
                    if dirty[field] != settled[field]
                ])
                print("Selection event count:", len(events))
                for index, event in enumerate(events, start=1):
                    print("Event", index, event)

                require(not errors, "GUI errors: " + repr(errors))

            finally:
                if app is not None:
                    app.destroy()
                    app = None

finally:
    unchanged = before == {p.name: digest(p) for p in paths}
    print("\nLive source CSV hashes unchanged:", unchanged)
    require(unchanged, "Live source CSV hashes changed.")

print("Phase 35A diagnostic complete. No saves or exports performed.")
'@

$diagnosticScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 35A diagnostic failed. Review the error above.'
}
```

This will distinguish an immediate reset from a queued selection-event reset. Paste the diagnostic output; then we’ll make a narrow Task Templates refresh repair that preserves the form during list rebuilding while still allowing deliberate record selection and **Revert Form** to load saved values.

<div align="center">⁂</div>

[^13_1]: doda_content_workbench/doda_task_templates_editor.py


---

# Phase 35A: sandbox refresh diagnostic - no saves

=== Before Refresh ===
Selected task: SIGNAL_REVIEW
Display name: UNSAVED REFRESH DIAGNOSTIC
Selection events after settling: 0

=== Immediately After refresh_all ===
Display name: UNSAVED REFRESH DIAGNOSTIC
Form preserved: True

=== After Selection Events ===
Display name: Priority Signal Review
Form preserved: False
Changed fields: ['display_name', 'description']
Selection event count: 2
Event 1 {'selection': ['SIGNAL_REVIEW'], 'nameBeforeHandler': 'UNSAVED REFRESH DIAGNOSTIC
', 'nameAfterHandler': 'Priority Signal Review'}
Event 2 {'selection': ['SIGNAL_REVIEW'], 'nameBeforeHandler': 'Priority Signal Review', '
nameAfterHandler': 'Priority Signal Review'}

Live source CSV hashes unchanged: True
Phase 35A diagnostic complete. No saves or exports performed.

Phase 35A confirms the cause: refresh preserved the form initially, but two queued selection events then reloaded the saved record and replaced the unsaved name and description.

We’ll make a narrow repair: **ignore selection events for the record already being edited**. Selecting a different record will still load it, and direct calls from Save or Revert Form will still reload values. The existing handler accepts an optional event argument, which lets us distinguish those paths.[^14_1]

## Phase 36 — Preserve task form

Close the Workbench before running this block.

This patches only `TaskTemplatesEditor.on_select()`. It backs up the module, verifies that the syntax-tree change is limited to the new guard, and checks all 12 live CSV hashes.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 36: preserve Task Templates form during refresh events' -ForegroundColor Cyan

$patchScript = @'
import ast
import copy
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[^14_1]).resolve()
tools = root / "tools/doda_content_workbench"
path = tools / "doda_task_templates_editor.py"
temporary = path.with_name(path.name + ".selection.tmp")

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(path.is_file(), "Task Templates module not found.")
csv_paths = sorted((root / "data_authoring/source").glob("*.csv"))
require(len(csv_paths) == 12, "Expected exactly 12 source CSVs.")
before = {p.name: digest(p) for p in csv_paths}

original_bytes = path.read_bytes()
original_hash = digest(path)
original = original_bytes.decode("utf-8-sig")
tree = ast.parse(original, filename=str(path))

classes = [
    node for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "TaskTemplatesEditor"
]
require(len(classes) == 1, "Expected one TaskTemplatesEditor class.")

methods = [
    node for node in classes[^14_0].body
    if isinstance(node, ast.FunctionDef) and node.name == "on_select"
]
require(len(methods) == 1, "Expected one on_select method.")
method = methods[^14_0]

require(
    [arg.arg for arg in method.args.args] == ["self", "_event"],
    "Selection-handler arguments differ from expected.",
)

lines = original.splitlines(keepends=True)
method_text = "".join(lines[method.lineno - 1:method.end_lineno])
normalized = method_text.replace("\r\n", "\n")

anchor = (
    '        selected = self.tree.selection()\n'
    '        if not selected:\n'
    '            return\n'
    '        row = next(\n'
)
replacement = (
    '        selected = self.tree.selection()\n'
    '        if not selected:\n'
    '            return\n'
    '        if _event is not None and selected[^14_0] == self.editing_id:\n'
    '            return\n'
    '        row = next(\n'
)

require(
    normalized.count(anchor) == 1,
    "Expected selection-handler anchor missing or changed. No patch applied.",
)
require(
    "_event is not None and selected[^14_0] == self.editing_id" not in original,
    "Selection guard is already installed. No patch applied.",
)

updated_method = normalized.replace(anchor, replacement, 1)
newline = "\r\n" if "\r\n" in method_text else "\n"
updated_method = updated_method.replace("\n", newline)
candidate = (
    "".join(lines[:method.lineno - 1])
    + updated_method
    + "".join(lines[method.end_lineno:])
)

candidate_tree = ast.parse(candidate, filename=str(path))
compile(candidate, str(path), "exec")

expected_tree = copy.deepcopy(tree)
expected_class = next(
    node for node in expected_tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "TaskTemplatesEditor"
)
expected_method = next(
    node for node in expected_class.body
    if isinstance(node, ast.FunctionDef) and node.name == "on_select"
)

require(
    len(expected_method.body) >= 3
    and isinstance(expected_method.body[^14_0], ast.Assign)
    and isinstance(expected_method.body[^14_1], ast.If)
    and ast.unparse(expected_method.body[^14_1].test) == "not selected",
    "Selection-handler structure differs from expected.",
)

guard = ast.parse(
    "if _event is not None and selected[^14_0] == self.editing_id:\n"
    "    return\n"
).body[^14_0]
expected_method.body.insert(2, guard)

require(
    ast.dump(candidate_tree, include_attributes=False)
    == ast.dump(expected_tree, include_attributes=False),
    "Candidate contains changes beyond the intended selection guard.",
)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup_dir = tools / "backups" / ("task_selection_guard_" + stamp)
backup_dir.mkdir(parents=True, exist_ok=False)
backup = backup_dir / path.name
shutil.copy2(path, backup)
require(digest(backup) == original_hash, "Backup verification failed.")

installed = False
try:
    temporary.write_bytes(candidate.encode("utf-8"))
    require(
        digest(path) == original_hash,
        "Module changed externally. Installation cancelled.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == before,
        "Source CSV changed during preparation. Installation cancelled.",
    )

    os.replace(temporary, path)
    installed = True

    compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
    require(
        path.read_bytes() == candidate.encode("utf-8"),
        "Installed module differs from candidate.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == before,
        "Live source CSV hashes changed.",
    )

    print("\n=== Task Selection Guard ===")
    print("PASS: only the same-record event guard added")
    print("PASS: installed module syntax")
    print("PASS: all 12 live source CSV hashes unchanged")
    print("Backup:", backup)
    print("Previous SHA256:", original_hash)
    print("New SHA256:", digest(path))
    print("Phase 36 patch complete. Regression verification is required.")

except Exception:
    if installed:
        shutil.copy2(backup, path)
        require(
            digest(path) == original_hash,
            "Rollback verification failed. Preserve the backup.",
        )
        print("Previous Task Templates module restored from backup.")
    raise

finally:
    if temporary.exists():
        temporary.unlink()
'@

$patchScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 36 failed. Review the error and rollback status above.'
}
```


## Verify the repair

After the patch passes:

1. Rerun the **Phase 35A diagnostic**. Both the immediate and settled results should now report `Form preserved: True`, with no changed fields.
2. Rerun the **Phase 35 sandbox enum tests**. The target is `Passed: 6/6`.
3. In the live GUI, make an unsaved Task Templates name edit, choose Actions > Refresh Source Data, and confirm it remains.
4. Click Revert Form and confirm the saved name returns.
5. Select the other template and confirm its values load normally.
6. Close without saving.

This repair is limited to Task Templates; it does not establish unsaved-form preservation in the other editors. It also does not change the external-change guard or introduce a conflict-resolution workflow.

Paste the patch summary and regression results before we proceed to coordinated metric/tier authoring.

<div align="center">⁂</div>

[^14_1]: doda_content_workbench/doda_task_templates_editor.py


---

# Phase 36: preserve Task Templates form during refresh events

=== Task Selection Guard ===
PASS: only the same-record event guard added
PASS: installed module syntax
PASS: all 12 live source CSV hashes unchanged
Backup: E:\\Dev\\uzdoom_src\\doda-core\\tools\\doda_content_workbench\\backups\\task_selection_g
uard_20261006_072931_265561\\doda_task_templates_editor.py
Previous SHA256: 0ecc740f591858f02d6333d39f431d13791a63b203122369625b49d96053ff00
New SHA256: 79f6a58b316b740e79e68cad242766b95bd385b45d4c9c709e60ac963b6064c0
Phase 36 patch complete. Regression verification is required.

Phase 36 passed its patch checks: only the selection guard changed, the module compiled, and all 12 live CSV hashes remained unchanged. Now we need to verify preservation, deliberate record switching, and Revert Form—not just syntax.

## Phase 36A — Selection regression

Close the Workbench and run this block. It uses the real GUI in a temporary project, makes no saves, and captures dialogs.

The tests exercise `update()`, `on_select()`, and `revert()`—the methods involved in the original reset.[^15_1]

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 36A: sandbox selection regression - no saves' -ForegroundColor Cyan

$testScript = @'
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^15_1]).resolve()
live_tools = root / "tools/doda_content_workbench"
paths = sorted((root / "data_authoring/source").glob("*.csv"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(paths) == 12, "Expected exactly 12 source CSVs.")
before = {p.name: digest(p) for p in paths}
results = []
errors = []
app = None

def capture_error(*args, **kwargs):
    errors.append(str(args[^15_1]) if len(args) > 1 else str(kwargs))

def test(name, function):
    try:
        function()
        results.append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)
    except Exception as error:
        results.append({
            "name": name,
            "passed": False,
            "exception": repr(error),
        })
        print("FAIL: " + name, flush=True)
        print(repr(error), flush=True)

try:
    with tempfile.TemporaryDirectory(prefix="doda-selection-test-") as tmp:
        sandbox = Path(tmp)
        tools = sandbox / "tools/doda_content_workbench"
        source = sandbox / "data_authoring/source"
        tools.mkdir(parents=True)
        source.mkdir(parents=True)
        (sandbox / "DoDA").mkdir()
        (sandbox / "generated/reports").mkdir(parents=True)
        (sandbox / "build").mkdir()

        for path in live_tools.glob("*.py"):
            shutil.copy2(path, tools / path.name)
        for path in paths:
            shutil.copy2(path, source / path.name)

        sys.path.insert(0, str(tools))
        from doda_content_gui import ContentWorkbenchApp

        with (
            patch("tkinter.messagebox.showinfo"),
            patch("tkinter.messagebox.showwarning"),
            patch("tkinter.messagebox.showerror", capture_error),
        ):
            try:
                app = ContentWorkbenchApp(sandbox)
                app.withdraw()
                app.update()
                require(not errors, "Startup errors: " + repr(errors))

                editor = app.task_templates_editor
                require(
                    len(editor.loaded_rows) >= 2,
                    "These tests require at least two task templates.",
                )
                first = dict(editor.loaded_rows[^15_0])
                second = dict(editor.loaded_rows[^15_1])

                def settle():
                    app.update()
                    app.update()

                def form():
                    result = {
                        field: variable.get()
                        for field, variable in editor.vars.items()
                    }
                    result["description"] = editor.description.get(
                        "1.0", "end-1c"
                    )
                    return result

                def select(row):
                    editor.tree.selection_set(row["task_template_id"])
                    settle()

                select(first)
                editor.on_select()
                settle()

                def preserve_existing():
                    editor.vars["display_name"].set("UNSAVED TEST NAME")
                    editor.description.delete("1.0", "end")
                    editor.description.insert("1.0", "Unsaved test description.")
                    expected = form()
                    for _ in range(3):
                        app.refresh_all(False)
                        settle()
                        require(
                            form() == expected,
                            "Repeated refresh changed the existing-record form.",
                        )

                test(
                    "Repeated refresh preserves existing unsaved form",
                    preserve_existing,
                )

                def revert_existing():
                    editor.revert()
                    settle()
                    require(
                        form() == first,
                        "Revert did not reload the saved first record.",
                    )

                test("Revert Form reloads saved values", revert_existing)

                def switch_records():
                    editor.vars["display_name"].set("UNSAVED SWITCH TEST")
                    select(second)
                    require(
                        editor.editing_id == second["task_template_id"],
                        "Switch did not update the editing ID.",
                    )
                    require(
                        form() == second,
                        "Selecting another record did not load its values.",
                    )

                test("Different-record selection loads that record", switch_records)

                def preserve_new():
                    editor.new()
                    settle()
                    editor.vars["task_template_id"].set("UNSAVED_NEW_TEMPLATE")
                    editor.vars["display_name"].set("Unsaved new template")
                    editor.description.insert("1.0", "Unsaved new description.")
                    expected = form()
                    app.refresh_all(False)
                    settle()
                    require(editor.editing_id is None, "New form became an edit.")
                    require(
                        form() == expected,
                        "Refresh changed the unsaved new-record form.",
                    )

                test("Refresh preserves unsaved new-record form", preserve_new)

                require(not errors, "GUI errors: " + repr(errors))

            finally:
                if app is not None:
                    app.destroy()
                    app = None

except Exception as error:
    results.append({
        "name": "Sandbox setup or GUI execution",
        "passed": False,
        "exception": repr(error),
    })
    print("FAIL: Sandbox setup or GUI execution", flush=True)
    print(repr(error), flush=True)

unchanged = before == {p.name: digest(p) for p in paths}
results.append({"name": "Live source CSV hashes unchanged", "passed": unchanged})
print(
    ("PASS: " if unchanged else "FAIL: ")
    + "Live source CSV hashes unchanged",
    flush=True,
)

passed = sum(result["passed"] for result in results)
report_dir = root / "generated/reports"
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
report_path = report_dir / ("task_selection_regression_" + stamp + ".json")

report = {
    "testedAtLocal": datetime.now().astimezone().isoformat(),
    "scope": "Real hidden GUI in temporary project; no saves; dialogs mocked",
    "valid": passed == len(results),
    "passedCount": passed,
    "testCount": len(results),
    "liveSourcesUnchanged": unchanged,
    "results": results,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("\n=== Task Selection Regression Summary ===")
print(f"Passed: {passed}/{len(results)}")
print("Live sources unchanged:", unchanged)
print("Report:", report_path)

if not report["valid"]:
    raise SystemExit(1)

print("Phase 36A complete: selection regression passed.")
'@

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 36A failed. Review the failed cases and regression report.'
}
```

Expected result is **5/5**. After that, rerun the Phase 35 enum sandbox block to confirm the original save-triggered preservation failure is fixed; its target remains **6/6**.

Paste the regression summaries. Do not rerun the Phase 36 patch—it is already installed.

<div align="center">⁂</div>

[^15_1]: doda_content_workbench/doda_task_templates_editor.py


---

# Phase 36A: sandbox selection regression - no saves

PASS: Repeated refresh preserves existing unsaved form
PASS: Revert Form reloads saved values
PASS: Different-record selection loads that record
PASS: Refresh preserves unsaved new-record form
PASS: Live source CSV hashes unchanged

=== Task Selection Regression Summary ===
Passed: 5/5
Live sources unchanged: True
Report: E:\\Dev\\uzdoom_src\\doda-core\\generated\\reports\\task_selection_regression_20261006\_
073010_645943.json
Phase 36A complete: selection regression passed.

PS E:\\Dev\\uzdoom_src\\doda-core>

Phase 36A **passed: 5/5**. The sandbox confirmed that refresh preserves both existing and new unsaved Task Templates forms, while Revert Form and selecting a different record still load saved values correctly. Live CSV hashes remained unchanged.

## One regression remains

Rerun the **Phase 35 sandbox enum tests**—not any patch or installer block. That tests the original failing sequence: an Enum Catalog save invokes the application refresh while a Task Templates form contains unsaved text. The enum save implementation already performs those refresh calls.[^16_1]

The expected result is:

```text
=== Enum GUI Regression Summary ===
Passed: 6/6
Live sources unchanged: True
Phase 35 complete: sandbox enum GUI tests passed.
```

Phase 36A verified refresh directly; Phase 35 will confirm the complete enum-save workflow.

## Current repair status

| Repair | Status |
| :-- | :-- |
| Metric Tiers layout | Patch checks and GUI verification passed |
| Unused recursive enum helper | Removed; syntax and live-source integrity checks passed |
| Task Templates refresh preservation | Patch checks and 5/5 selection regression passed |
| Enum-save preservation regression | Awaiting Phase 35 rerun |
| Coordinated metric/tier authoring | Not implemented yet |

After Phase 35 passes, we can move to the remaining metric/tier workflow limitation. We should update the manual against the repaired modules after that implementation and its tests are complete.

Paste the Phase 35 summary and any failed cases.

<div align="center">⁂</div>

[^16_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# Phase 35A: sandbox refresh diagnostic - no saves

=== Before Refresh ===
Selected task: SIGNAL_REVIEW
Display name: UNSAVED REFRESH DIAGNOSTIC
Selection events after settling: 0

=== Immediately After refresh_all ===
Display name: UNSAVED REFRESH DIAGNOSTIC
Form preserved: True

=== After Selection Events ===
Display name: UNSAVED REFRESH DIAGNOSTIC
Form preserved: True
Changed fields: []
Selection event count: 2
Event 1 {'selection': ['SIGNAL_REVIEW'], 'nameBeforeHandler': 'UNSAVED REFRESH DIAGNOSTIC
', 'nameAfterHandler': 'UNSAVED REFRESH DIAGNOSTIC'}
Event 2 {'selection': ['SIGNAL_REVIEW'], 'nameBeforeHandler': 'UNSAVED REFRESH DIAGNOSTIC
', 'nameAfterHandler': 'UNSAVED REFRESH DIAGNOSTIC'}

Live source CSV hashes unchanged: True
Phase 35A diagnostic complete. No saves or exports performed.

PS E:\\Dev\\uzdoom_src\\doda-core>

The Phase 35A rerun confirms the fix: both queued selection events now leave the unsaved name and description intact. No fields changed, and the live CSV hashes remained unchanged.

This is the **refresh-only diagnostic**, not the Phase 35 enum-save regression. One check remains before closing this repair.

## Run Phase 35 next

Use the earlier block whose opening message is:

```text
Phase 35: real GUI enum tests in a temporary project
```

It tests the complete save path, including backup creation, dependent dropdown refresh, repeat editing, and preservation of the unsaved task name. Enum Catalog saving invokes the application refresh, so that is the original workflow we need to recheck.[^17_1]

The expected summary is:

```text
=== Enum GUI Regression Summary ===
Passed: 6/6
Live sources unchanged: True
Phase 35 complete: sandbox enum GUI tests passed.
```

Do not rerun the patch blocks. Phase 36 is installed, and Phase 36A already passed all five selection tests.

Paste the **Enum GUI Regression Summary** next; once it passes, we’ll move to coordinated metric/tier authoring.

<div align="center">⁂</div>

[^17_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# please repost Phase 35 script

Here is the complete **Phase 35** script. Close the Workbench, then run the entire block. It tests the real enum save/refresh workflow in a temporary project using the editor’s existing save path.[^18_1]

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 35: real GUI enum tests in a temporary project' -ForegroundColor Cyan

$testScript = @'
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^18_1]).resolve()
live_tools = root / "tools/doda_content_workbench"
live_source = root / "data_authoring/source"
csv_paths = sorted(live_source.glob("*.csv"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(csv_paths) == 12, "Expected exactly 12 live source CSVs.")
before = {p.name: digest(p) for p in csv_paths}
results = []
dialogs = []
app = None

def capture(kind):
    def handler(*args, **kwargs):
        message = str(args[^18_1]) if len(args) > 1 else str(kwargs)
        dialogs.append({"kind": kind, "message": message})
        return None
    return handler

def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def test(name, function):
    try:
        function()
        results.append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)
    except Exception as error:
        results.append({
            "name": name,
            "passed": False,
            "exception": repr(error),
        })
        print("FAIL: " + name, flush=True)
        print(repr(error), flush=True)

try:
    with tempfile.TemporaryDirectory(prefix="doda-enum-gui-test-") as tmp:
        sandbox = Path(tmp)
        tools = sandbox / "tools/doda_content_workbench"
        source = sandbox / "data_authoring/source"
        tools.mkdir(parents=True)
        source.mkdir(parents=True)
        (sandbox / "DoDA").mkdir()
        (sandbox / "generated/reports").mkdir(parents=True)
        (sandbox / "build").mkdir()

        for path in live_tools.glob("*.py"):
            shutil.copy2(path, tools / path.name)
        for path in csv_paths:
            shutil.copy2(path, source / path.name)

        sys.path.insert(0, str(tools))
        from doda_content_gui import ContentWorkbenchApp

        with (
            patch("tkinter.messagebox.showinfo", capture("info")),
            patch("tkinter.messagebox.showwarning", capture("warning")),
            patch("tkinter.messagebox.showerror", capture("error")),
            patch("tkinter.messagebox.askyesno", return_value=False),
        ):
            try:
                app = ContentWorkbenchApp(sandbox)
                app.withdraw()
                app.update()

                require(
                    not any(d["kind"] == "error" for d in dialogs),
                    "GUI startup reported errors: " + repr(dialogs),
                )

                enum = app.enum_catalog_editor
                tasks = app.task_templates_editor
                enum_path = source / "enum_catalog.csv"
                original_enum = enum_path.read_bytes()
                backup_dir = sandbox / "data_authoring/backups/enum_catalog"

                test_value = "WORKBENCH_TEST_PRIORITY"
                require(
                    not any(
                        row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                        for row in read_rows(enum_path)
                    ),
                    "Reserved test priority already exists in this snapshot.",
                )

                selected_task = next(
                    row for row in tasks.loaded_rows
                    if row["active"].upper() == "TRUE"
                )
                tasks.tree.selection_set(selected_task["task_template_id"])
                tasks.on_select()
                app.update()
                dirty_name = "UNSAVED SANDBOX NAME"
                tasks.vars["display_name"].set(dirty_name)

                def set_enum_form(group, value, label, description, order):
                    enum.enum_group.set(group)
                    enum.enum_value.set(value)
                    enum.display_label.set(label)
                    enum.description.delete("1.0", "end")
                    enum.description.insert("1.0", description)
                    enum.sort_order.set(str(order))
                    enum.active.set(True)

                def create_enum():
                    enum.new()
                    enum.catalog_group_filter.set("All Groups")
                    set_enum_form(
                        "TASK_PRIORITY",
                        test_value,
                        "Workbench test priority",
                        "Temporary sandbox-only priority.",
                        enum.next_sort_order("TASK_PRIORITY"),
                    )
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        not any(
                            d["kind"] in {"error", "warning"}
                            for d in dialogs
                        ),
                        "Save reported an error or warning: " + repr(dialogs),
                    )
                    matches = [
                        row for row in read_rows(enum_path)
                        if row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                    ]
                    require(len(matches) == 1, "New priority was not saved.")
                    copies = list(backup_dir.glob("*.csv"))
                    require(
                        len(copies) == 1,
                        "Expected exactly one enum backup.",
                    )
                    require(
                        copies[^18_0].read_bytes() == original_enum,
                        "First backup differs from the original enum CSV.",
                    )

                test(
                    "Create enum through real save; exact backup",
                    create_enum,
                )

                def dependent_choices():
                    choices = tuple(tasks.widgets["priority"]["values"])
                    require(
                        test_value in choices,
                        "New priority is absent from Task Templates dropdown.",
                    )
                    require(
                        any(
                            row["enum_group"] == "TASK_PRIORITY"
                            and row["enum_value"] == test_value
                            for row in app.tables["enum_catalog"]
                        ),
                        "Application table cache did not reload the new enum.",
                    )

                test(
                    "Real refresh updates task choices and table cache",
                    dependent_choices,
                )

                def preserve_unsaved():
                    require(
                        tasks.vars["display_name"].get() == dirty_name,
                        "Refresh replaced the unsaved Task Templates name.",
                    )

                test(
                    "Unsaved selected-task display name survives enum save",
                    preserve_unsaved,
                )

                def repeat_edit():
                    key = "TASK_PRIORITY::" + test_value
                    require(
                        enum.tree.exists(key),
                        "New enum row is not visible.",
                    )
                    enum.tree.selection_set(key)
                    enum.on_select()
                    app.update()
                    previous = enum_path.read_bytes()
                    count = len(list(backup_dir.glob("*.csv")))
                    enum.display_label.set("Updated sandbox priority")
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        not any(
                            d["kind"] in {"error", "warning"}
                            for d in dialogs
                        ),
                        "Repeat save reported an error or warning: "
                        + repr(dialogs),
                    )
                    row = next(
                        row for row in read_rows(enum_path)
                        if row["enum_group"] == "TASK_PRIORITY"
                        and row["enum_value"] == test_value
                    )
                    require(
                        row["display_label"] == "Updated sandbox priority",
                        "Repeat save did not update the label.",
                    )
                    copies = list(backup_dir.glob("*.csv"))
                    require(
                        len(copies) == count + 1,
                        "Repeat save created no backup.",
                    )
                    require(
                        any(p.read_bytes() == previous for p in copies),
                        "No backup matches the pre-edit CSV.",
                    )

                test(
                    "Repeat enum edit succeeds with pre-edit backup",
                    repeat_edit,
                )

                def reject_referenced_deactivation():
                    priority = selected_task["priority"]
                    key = "TASK_PRIORITY::" + priority
                    enum.catalog_group_filter.set("All Groups")
                    enum.update()
                    require(
                        enum.tree.exists(key),
                        "Referenced priority row missing.",
                    )
                    enum.tree.selection_set(key)
                    enum.on_select()
                    app.update()
                    previous = enum_path.read_bytes()
                    count = len(list(backup_dir.glob("*.csv")))
                    enum.active.set(False)
                    dialogs.clear()
                    enum.save()
                    app.update()

                    require(
                        enum_path.read_bytes() == previous,
                        "Rejected deactivation changed the enum CSV.",
                    )
                    require(
                        len(list(backup_dir.glob("*.csv"))) == count,
                        "Rejected deactivation created a backup.",
                    )
                    require(
                        any(
                            d["kind"] == "error"
                            and "candidate validation failed"
                            in d["message"].lower()
                            for d in dialogs
                        ),
                        "Expected candidate-validation rejection "
                        "was not reported.",
                    )

                test(
                    "Referenced priority deactivation rejected without changes",
                    reject_referenced_deactivation,
                )

            finally:
                if app is not None:
                    app.destroy()
                    app = None

except Exception as error:
    results.append({
        "name": "Sandbox setup or GUI execution",
        "passed": False,
        "exception": repr(error),
    })
    print("FAIL: Sandbox setup or GUI execution", flush=True)
    print(repr(error), flush=True)

unchanged = before == {p.name: digest(p) for p in csv_paths}
results.append({
    "name": "Live source CSV hashes unchanged",
    "passed": unchanged,
})
print(
    ("PASS: " if unchanged else "FAIL: ")
    + "Live source CSV hashes unchanged",
    flush=True,
)

report_dir = root / "generated/reports"
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
report_path = report_dir / ("enum_gui_regression_" + stamp + ".json")
passed = sum(row["passed"] for row in results)

report = {
    "testedAtLocal": datetime.now().astimezone().isoformat(),
    "scope": (
        "Real hidden GUI and enum save/refresh in a temporary project; "
        "dialogs mocked; no export; "
        "selected Task Templates name preservation only"
    ),
    "valid": passed == len(results),
    "passedCount": passed,
    "testCount": len(results),
    "liveSourcesUnchanged": unchanged,
    "results": results,
}
report_path.write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)

print("\n=== Enum GUI Regression Summary ===")
print(f"Passed: {passed}/{len(results)}")
print("Live sources unchanged:", unchanged)
print("Report:", report_path)

if not report["valid"]:
    raise SystemExit(1)

print("Phase 35 complete: sandbox enum GUI tests passed.")
'@

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 35 failed. Review the failed cases and regression report.'
}
```

The target is `Passed: 6/6` with `Live sources unchanged: True`. Paste the final summary and any failed cases.

<div align="center">⁂</div>

[^18_1]: doda_content_workbench/doda_enum_catalog_editor.py


---

# Phase 35: real GUI enum tests in a temporary project

PASS: Create enum through real save; exact backup
PASS: Real refresh updates task choices and table cache
PASS: Unsaved selected-task display name survives enum save
PASS: Repeat enum edit succeeds with pre-edit backup
PASS: Referenced priority deactivation rejected without changes
PASS: Live source CSV hashes unchanged

=== Enum GUI Regression Summary ===
Passed: 6/6
Live sources unchanged: True
Report: E:\\Dev\\uzdoom_src\\doda-core\\generated\\reports\\enum_gui_regression_20261006_073416
\_860204.json
Phase 35 complete: sandbox enum GUI tests passed.

Phase 35 now **passes: 6/6**. The complete enum-save workflow updates the Task Templates priority choices, preserves the unsaved task name, creates verified backups, and rejects deactivation of a referenced priority. Your live source CSVs remained unchanged.

## Repairs verified

| Repair | Verification |
| :-- | :-- |
| Metric Tiers layout | Patch checks and your GUI inspection passed |
| Recursive enum helper | Removed without changing the save method |
| Task Templates refresh preservation | 5/5 selection tests passed |
| Enum save and dependent refresh | 6/6 sandbox tests passed |

The remaining issue is coordinated metric/tier authoring. The validator requires every metric to have complete tier coverage, while tiers must reference an existing metric; the current editors validate and save one table at a time.[^19_1][^19_2][^19_3]

## Next implementation

We should build this in two stages:

1. A coordinated-save service that stages both CSVs, validates the complete candidate project, backs up both originals, detects external changes, and handles partial-write failures.
2. A GUI workflow that lets users prepare a metric and its complete tier set before invoking that service.

We’ll test the service in a sandbox before connecting it to the GUI. Validation rules should remain intact—no temporary allowance for missing tiers, gaps, overlaps, or dangling references.

The documentation can now drop the resolved layout and recursive-helper warnings, but should retain the metric/tier workflow limitation until its replacement is implemented and tested. Unsaved-form preservation is verified for Task Templates only, not all editors.

<div align="center">⁂</div>

[^19_1]: doda_content_workbench/doda_content_workbench.py

[^19_2]: doda_content_workbench/doda_metrics_editor.py

[^19_3]: doda_content_workbench/doda_metric_tiers_editor.py


---

```
# \<q>Next implementationWe should build this in two stages:A coordinated-save service that stages both CSVs, validates the complete candidate project, backs up both originals, detects external changes, and handles partial-write failures.A GUI workflow that lets users prepare a metric and its complete tier set before invoking that service.\</q> Go
```

We’ll build the coordinated-save service first, without connecting it to the GUI. It will validate Metrics and Metric Tiers together using the existing full-project validator, preserving the current coverage and reference rules.[^20_1]

## Phase 37 — Create coordinated service

Close the Workbench and run this block. It creates one new Python module, syntax-checks it, and verifies that the live CSVs remain unchanged.

The service includes:

- A snapshot of all 12 source files.
- Complete candidate-project validation.
- Backups of both affected CSVs.
- External-change checks before replacement.
- Rollback handling for caught failures between replacements.
- A transaction record and a cooperative lock.

Two file replacements are **not** one atomic operation. This implementation blocks further coordinated saves when it detects an unfinished transaction; it does not promise automatic recovery from power loss or prevent unrelated applications from editing the CSVs.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$servicePath = Join-Path $toolDir 'doda_metric_bundle_service.py'
$tempPath = "$servicePath.new"
$sourceDir = Join-Path $root 'data_authoring\source'

foreach ($path in @(
    $pythonPath,
    (Join-Path $toolDir 'doda_content_workbench.py')
)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required component not found: $path"
    }
}

if (Test-Path -LiteralPath $servicePath) {
    throw "Service already exists. No files changed: $servicePath"
}

$csvFiles = @(Get-ChildItem -LiteralPath $sourceDir -Filter '*.csv' -File)
if ($csvFiles.Count -ne 12) {
    throw 'Expected exactly 12 source CSV files.'
}

$sourceHashes = @{}
foreach ($file in $csvFiles) {
    $sourceHashes[$file.Name] = (
        Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
    ).Hash
}

Write-Host 'Phase 37: create metric bundle service only' -ForegroundColor Cyan

$serviceSource = @'
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from doda_content_workbench import TABLE_SPECS


TARGETS = ("metrics.csv", "metric_tiers.csv")
FINAL_STATES = {"committed", "rolled_back", "aborted"}


class BundleError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_files(root: Path) -> dict[str, Path]:
    return {
        spec["filename"]: root / "data_authoring/source" / spec["filename"]
        for spec in TABLE_SPECS.values()
    }


def read_snapshot(root: Path) -> dict:
    root = Path(root).resolve()
    files = source_files(root)
    raw = {name: path.read_bytes() for name, path in files.items()}
    hashes = {name: sha256(data) for name, data in raw.items()}
    if hashes != {
        name: sha256(path.read_bytes()) for name, path in files.items()
    }:
        raise BundleError("Source changed during snapshot. Reload and retry.")

    rows = {}
    for name, data in raw.items():
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
        records = []
        for row in reader:
            if None in row:
                raise BundleError("Extra CSV cells in " + name)
            if any((value or "").strip() for value in row.values()):
                records.append({
                    key.strip(): (value or "").strip()
                    for key, value in row.items()
                })
        rows[name] = records
    return {"hashes": hashes, "rows": rows}


def encode_table(table: str, rows: list[dict]) -> bytes:
    fields = TABLE_SPECS[table]["required_columns"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        if set(row) != set(fields):
            raise BundleError(
                table + " candidate fields must exactly match its schema."
            )
        writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def validate_candidate(root: Path, raw: dict[str, bytes]) -> str:
    validator = root / "tools/doda_content_workbench/doda_content_workbench.py"
    with tempfile.TemporaryDirectory(prefix="doda-metric-bundle-") as tmp:
        candidate_root = Path(tmp)
        destination = candidate_root / "data_authoring/source"
        destination.mkdir(parents=True)
        for name, data in raw.items():
            (destination / name).write_bytes(data)
        completed = subprocess.run(
            [
                sys.executable, str(validator),
                "--root", str(candidate_root), "validate",
            ],
            cwd=candidate_root,
            text=True, encoding="utf-8", errors="replace",
            capture_output=True,
        )
        output = completed.stdout + "\n" + completed.stderr
        if completed.returncode:
            raise BundleError("Candidate validation failed:\n" + output)
        return output


def write_journal(path: Path, record: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def commit_bundle(
    root: Path,
    metric_rows: list[dict],
    tier_rows: list[dict],
    expected_hashes: dict[str, str],
) -> dict:
    root = Path(root).resolve()
    files = source_files(root)
    folder = root / "data_authoring/backups/metric_bundles"
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / ".bundle.lock"
    token = uuid4().hex

    try:
        descriptor = os.open(
            lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
    except FileExistsError as error:
        raise BundleError(
            "Coordinated-save lock exists. Inspect it and transaction "
            "records before attempting recovery: " + str(lock)
        ) from error

    transaction = None
    journal = None
    record = None
    replaced = []
    temporary_paths = []

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "token": token}))

        for existing in folder.glob("*/transaction.json"):
            status = json.loads(existing.read_text(encoding="utf-8"))["status"]
            if status not in FINAL_STATES:
                raise BundleError(
                    "Unfinished transaction requires inspection: "
                    + str(existing)
                )

        originals = {
            name: path.read_bytes() for name, path in files.items()
        }
        hashes = {
            name: sha256(data) for name, data in originals.items()
        }
        if set(expected_hashes) != set(files) or hashes != expected_hashes:
            raise BundleError("Source changed since loading. Reload and retry.")

        candidate = dict(originals)
        candidate["metrics.csv"] = encode_table("metrics", metric_rows)
        candidate["metric_tiers.csv"] = encode_table("metric_tiers", tier_rows)
        output = validate_candidate(root, candidate)
        candidate_hashes = {
            name: sha256(data) for name, data in candidate.items()
        }

        if {
            name: sha256(path.read_bytes()) for name, path in files.items()
        } != hashes:
            raise BundleError("Source changed during validation. No CSV replaced.")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        transaction = folder / (stamp + "_" + token)
        transaction.mkdir()
        journal = transaction / "transaction.json"

        for name in TARGETS:
            backup = transaction / name
            backup.write_bytes(originals[name])
            if sha256(backup.read_bytes()) != hashes[name]:
                raise BundleError("Backup verification failed: " + name)

        record = {
            "transactionId": token,
            "createdAtUtc": datetime.now(timezone.utc).isoformat(),
            "status": "prepared",
            "originalHashes": hashes,
            "candidateHashes": candidate_hashes,
            "replaced": [],
        }
        write_journal(journal, record)

        staged = {}
        for name in TARGETS:
            path = files[name].with_name("." + name + "." + token + ".tmp")
            temporary_paths.append(path)
            path.write_bytes(candidate[name])
            if sha256(path.read_bytes()) != candidate_hashes[name]:
                raise BundleError("Staged file verification failed: " + name)
            staged[name] = path

        for name in TARGETS:
            expected_now = dict(hashes)
            for changed in replaced:
                expected_now[changed] = candidate_hashes[changed]
            if {
                item: sha256(path.read_bytes())
                for item, path in files.items()
            } != expected_now:
                raise BundleError("Source changed before replacement: " + name)

            os.replace(staged[name], files[name])
            replaced.append(name)
            record["status"] = "replacing"
            record["replaced"] = list(replaced)
            write_journal(journal, record)

        if {
            name: sha256(path.read_bytes()) for name, path in files.items()
        } != candidate_hashes:
            raise BundleError("Source changed during final verification.")

        record["status"] = "committed"
        write_journal(journal, record)
        return {
            "transactionDirectory": str(transaction),
            "hashes": candidate_hashes,
            "validationOutput": output,
        }

    except BaseException as error:
        recovery_errors = []
        if replaced:
            for name in reversed(replaced):
                try:
                    if sha256(files[name].read_bytes()) != candidate_hashes[name]:
                        raise BundleError(
                            "External change detected; refusing to overwrite "
                            + name + " during rollback."
                        )
                    restore = files[name].with_name(
                        "." + name + "." + token + ".restore"
                    )
                    temporary_paths.append(restore)
                    restore.write_bytes((transaction / name).read_bytes())
                    os.replace(restore, files[name])
                    if sha256(files[name].read_bytes()) != hashes[name]:
                        raise BundleError("Rollback hash mismatch: " + name)
                except Exception as recovery_error:
                    recovery_errors.append(str(recovery_error))

        if record is not None:
            record["status"] = (
                "recovery_required" if recovery_errors
                else "rolled_back" if replaced else "aborted"
            )
            record["error"] = repr(error)
            record["recoveryErrors"] = recovery_errors
            try:
                write_journal(journal, record)
            except Exception as journal_error:
                recovery_errors.append("Journal update failed: " + str(journal_error))

        if recovery_errors:
            raise BundleError(
                "Recovery requires inspection. Backups: "
                + str(transaction) + "\n" + "\n".join(recovery_errors)
            ) from error
        raise

    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()
        if lock.exists():
            owner = json.loads(lock.read_text(encoding="utf-8"))
            if owner.get("token") == token:
                lock.unlink()
'@

try {
    [System.IO.File]::WriteAllText(
        $tempPath,
        $serviceSource,
        [System.Text.UTF8Encoding]::new($false)
    )

    $syntaxCheck = @'
import ast
import sys
from pathlib import Path

path = Path(sys.argv[^20_1])
text = path.read_text(encoding="utf-8-sig")
tree = ast.parse(text, filename=str(path))
compile(tree, str(path), "exec")
required = {"read_snapshot", "validate_candidate", "commit_bundle"}
present = {
    node.name for node in tree.body
    if isinstance(node, ast.FunctionDef)
}
assert required <= present, "Required service functions are missing."
print("PASS: service syntax and required function definitions")
'@

    $syntaxCheck | & $pythonPath - $tempPath

    if ($LASTEXITCODE -ne 0) {
        throw 'Service syntax check failed. Module not installed.'
    }

    foreach ($file in $csvFiles) {
        $current = (
            Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
        ).Hash

        if ($current -ne $sourceHashes[$file.Name]) {
            throw "Source CSV changed during preparation: $($file.Name)"
        }
    }

    Move-Item -LiteralPath $tempPath -Destination $servicePath

    Write-Host ''
    Write-Host 'PASS: all 12 live source CSV hashes unchanged' -ForegroundColor Green
    Write-Host 'Phase 37 complete: coordinated service created; not connected to GUI.' -ForegroundColor Green

    Get-Item -LiteralPath $servicePath |
        Select-Object Name, Length, LastWriteTime |
        Format-Table -AutoSize
}
finally {
    if (Test-Path -LiteralPath $tempPath) {
        Remove-Item -LiteralPath $tempPath -Force
    }
}
```


## Verification comes next

This phase establishes syntax only. Before GUI integration, we’ll sandbox-test:

1. Creating a metric with complete tiers.
2. Changing metric bounds and tier coverage together.
3. Rejecting gaps, overlaps, and stale snapshots.
4. Verifying both backups byte-for-byte.
5. Injecting failure at the second replacement and checking rollback.
6. Blocking unresolved transactions and existing locks.

Paste the Phase 37 status. Do not call `commit_bundle()` against the live project yet.

<div align="center">⁂</div>

[^20_1]: doda_content_workbench/doda_content_workbench.py


---

# Phase 37: create metric bundle service only

PASS: service syntax and required function definitions

PASS: all 12 live source CSV hashes unchanged
Phase 37 complete: coordinated service created; not connected to GUI.

Name Length LastWriteTime

______________________________________________________________________

doda_metric_bundle_service.py 10142 10/6/2026 7:38:10 AM

PS E:\\Dev\\uzdoom_src\\doda-core>

Phase 37 passed: the service exists, its syntax checks passed, and your live CSVs remained unchanged. Next is **sandbox regression testing before GUI integration**.

## Phase 38 — Test coordinated saves

This block tests the new service using temporary project copies and the real validator. The gap and overlap cases exercise the existing metric-tier coverage rules.[^21_1]

It writes a regression report, but does not save to your live CSVs, modify application code, or run an export.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 38: coordinated-save sandbox regression' -ForegroundColor Cyan

$testScript = @'
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^21_1]).resolve()
tools = root / "tools/doda_content_workbench"
sys.path.insert(0, str(tools))
import doda_metric_bundle_service as service

live_paths = sorted((root / "data_authoring/source").glob("*.csv"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(live_paths) == 12, "Expected exactly 12 live source CSVs.")
live_before = {p.name: digest(p) for p in live_paths}
results = []

def contents(sandbox):
    return {
        p.name: p.read_bytes()
        for p in (sandbox / "data_authoring/source").glob("*.csv")
    }

def journals(sandbox):
    return list(
        (sandbox / "data_authoring/backups/metric_bundles")
        .glob("*/transaction.json")
    )

def clean(sandbox):
    source = sandbox / "data_authoring/source"
    require(not list(source.glob(".*.tmp")), "Staged CSV files remain.")
    require(not list(source.glob(".*.restore")), "Restore files remain.")
    require(
        not (
            sandbox / "data_authoring/backups/metric_bundles/.bundle.lock"
        ).exists(),
        "Service-owned lock remains.",
    )

def candidate(snapshot):
    metrics = [dict(row) for row in snapshot["rows"]["metrics.csv"]]
    tiers = [dict(row) for row in snapshot["rows"]["metric_tiers.csv"]]
    require(bool(metrics), "At least one metric is required.")
    new_id = "WORKBENCH_BUNDLE_TEST"
    require(
        all(row["metric_id"] != new_id for row in metrics),
        "Reserved test metric already exists.",
    )
    base_id = metrics[^21_0]["metric_id"]
    new_metric = dict(metrics[^21_0])
    new_metric["metric_id"] = new_id
    new_metric["display_name"] = "Sandbox bundle metric"
    metrics.append(new_metric)

    copied = []
    for row in tiers:
        if row["metric_id"] == base_id:
            item = dict(row)
            item["metric_id"] = new_id
            copied.append(item)
    require(len(copied) >= 2, "At least two baseline tiers required.")
    tiers.extend(copied)
    return metrics, tiers, new_id

def rejected(operation, fragment):
    try:
        operation()
    except service.BundleError as error:
        require(
            fragment.lower() in str(error).lower(),
            "Unexpected rejection: " + str(error),
        )
    else:
        raise AssertionError("Operation unexpectedly succeeded.")

def run_case(name, function):
    try:
        with tempfile.TemporaryDirectory(prefix="doda-bundle-test-") as tmp:
            sandbox = Path(tmp)
            destination = sandbox / "data_authoring/source"
            sandbox_tools = sandbox / "tools/doda_content_workbench"
            destination.mkdir(parents=True)
            sandbox_tools.mkdir(parents=True)
            for path in live_paths:
                shutil.copy2(path, destination / path.name)
            shutil.copy2(
                tools / "doda_content_workbench.py",
                sandbox_tools / "doda_content_workbench.py",
            )
            snapshot = service.read_snapshot(sandbox)
            function(sandbox, snapshot)

        results.append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)
    except Exception as error:
        results.append({
            "name": name,
            "passed": False,
            "exception": repr(error),
        })
        print("FAIL: " + name, flush=True)
        print(repr(error), flush=True)

def create_complete(sandbox, snapshot):
    original = contents(sandbox)
    metrics, tiers, new_id = candidate(snapshot)
    result = service.commit_bundle(
        sandbox, metrics, tiers, snapshot["hashes"]
    )
    saved = service.read_snapshot(sandbox)
    require(
        any(
            row["metric_id"] == new_id
            for row in saved["rows"]["metrics.csv"]
        ),
        "New metric missing.",
    )
    require(
        saved["rows"]["metrics.csv"] == metrics
        and saved["rows"]["metric_tiers.csv"] == tiers,
        "Saved records differ from proposed records.",
    )
    backup = Path(result["transactionDirectory"])
    for name in service.TARGETS:
        require(
            (backup / name).read_bytes() == original[name],
            "Backup differs byte-for-byte: " + name,
        )
    record = json.loads((backup / "transaction.json").read_text())
    require(record["status"] == "committed", "Journal is not committed.")
    require(
        result["hashes"] == saved["hashes"],
        "Returned hashes differ from saved sources.",
    )
    for name, data in original.items():
        if name not in service.TARGETS:
            require(contents(sandbox)[name] == data, "Unrelated CSV changed.")
    clean(sandbox)

def coordinated_bounds(sandbox, snapshot):
    metrics = [dict(row) for row in snapshot["rows"]["metrics.csv"]]
    tiers = [dict(row) for row in snapshot["rows"]["metric_tiers.csv"]]
    metric = metrics[^21_0]
    metric_id = metric["metric_id"]
    new_max = int(metric["internal_max"]) + 1
    metric["internal_max"] = str(new_max)
    last = max(
        (row for row in tiers if row["metric_id"] == metric_id),
        key=lambda row: int(row["max_inclusive"]),
    )
    last["max_inclusive"] = str(new_max)
    service.commit_bundle(sandbox, metrics, tiers, snapshot["hashes"])
    saved = service.read_snapshot(sandbox)
    require(saved["rows"]["metrics.csv"] == metrics, "Metric bounds not saved.")
    require(saved["rows"]["metric_tiers.csv"] == tiers, "Tier bounds not saved.")
    clean(sandbox)

def invalid_coverage(sandbox, snapshot, overlap):
    original = contents(sandbox)
    metrics, tiers, new_id = candidate(snapshot)
    selected = sorted(
        (row for row in tiers if row["metric_id"] == new_id),
        key=lambda row: int(row["min_inclusive"]),
    )
    if overlap:
        selected[^21_1]["min_inclusive"] = selected[^21_0]["max_inclusive"]
    else:
        selected[^21_1]["min_inclusive"] = str(
            int(selected[^21_0]["max_inclusive"]) + 2
        )
    rejected(
        lambda: service.commit_bundle(
            sandbox, metrics, tiers, snapshot["hashes"]
        ),
        "Candidate validation failed",
    )
    require(contents(sandbox) == original, "Invalid candidate changed sources.")
    require(not journals(sandbox), "Invalid candidate created a transaction.")
    clean(sandbox)

def stale_snapshot(sandbox, snapshot):
    metrics, tiers, _ = candidate(snapshot)
    path = sandbox / "data_authoring/source/flavor_text.csv"
    path.write_bytes(path.read_bytes() + b"\n")
    external = contents(sandbox)
    rejected(
        lambda: service.commit_bundle(
            sandbox, metrics, tiers, snapshot["hashes"]
        ),
        "Source changed since loading",
    )
    require(contents(sandbox) == external, "External change was overwritten.")
    clean(sandbox)

def change_during_validation(sandbox, snapshot):
    metrics, tiers, _ = candidate(snapshot)
    validator = service.validate_candidate
    external = {}

    def validate_then_change(project, raw):
        output = validator(project, raw)
        path = sandbox / "data_authoring/source/flavor_text.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        external.update(contents(sandbox))
        return output

    with patch.object(service, "validate_candidate", validate_then_change):
        rejected(
            lambda: service.commit_bundle(
                sandbox, metrics, tiers, snapshot["hashes"]
            ),
            "Source changed during validation",
        )
    require(contents(sandbox) == external, "Concurrent change overwritten.")
    require(not journals(sandbox), "Changed-source rejection created a transaction.")
    clean(sandbox)

def rollback_second_replace(sandbox, snapshot):
    original = contents(sandbox)
    metrics, tiers, _ = candidate(snapshot)
    real_replace = service.os.replace
    target = sandbox / "data_authoring/source/metric_tiers.csv"
    injected = []

    def fail_second(src, dst):
        if Path(dst) == target and str(src).endswith(".tmp"):
            injected.append(True)
            raise OSError("Injected second CSV replacement failure")
        return real_replace(src, dst)

    try:
        with patch.object(service.os, "replace", fail_second):
            service.commit_bundle(
                sandbox, metrics, tiers, snapshot["hashes"]
            )
    except OSError as error:
        require("Injected second" in str(error), "Unexpected replacement error.")
    else:
        raise AssertionError("Injected failure did not abort the operation.")

    require(len(injected) == 1, "Second replacement failure was not injected.")
    require(contents(sandbox) == original, "Rollback did not restore all sources.")
    records = journals(sandbox)
    require(len(records) == 1, "Expected one transaction journal.")
    record = json.loads(records[^21_0].read_text())
    require(record["status"] == "rolled_back", "Journal does not record rollback.")
    for name in service.TARGETS:
        require(
            (records[^21_0].parent / name).read_bytes() == original[name],
            "Rollback backup differs: " + name,
        )
    clean(sandbox)

def pending_transaction(sandbox, snapshot):
    original = contents(sandbox)
    folder = sandbox / "data_authoring/backups/metric_bundles/test_pending"
    folder.mkdir(parents=True)
    (folder / "transaction.json").write_text(
        json.dumps({"status": "prepared"}), encoding="utf-8"
    )
    metrics, tiers, _ = candidate(snapshot)
    rejected(
        lambda: service.commit_bundle(
            sandbox, metrics, tiers, snapshot["hashes"]
        ),
        "Unfinished transaction",
    )
    require(contents(sandbox) == original, "Pending transaction changed sources.")
    clean(sandbox)

def existing_lock(sandbox, snapshot):
    original = contents(sandbox)
    folder = sandbox / "data_authoring/backups/metric_bundles"
    folder.mkdir(parents=True)
    lock = folder / ".bundle.lock"
    lock_bytes = b'{"pid": 0, "token": "existing-test-lock"}'
    lock.write_bytes(lock_bytes)
    metrics, tiers, _ = candidate(snapshot)
    rejected(
        lambda: service.commit_bundle(
            sandbox, metrics, tiers, snapshot["hashes"]
        ),
        "lock exists",
    )
    require(contents(sandbox) == original, "Existing-lock rejection changed sources.")
    require(lock.read_bytes() == lock_bytes, "Existing lock was changed or removed.")

run_case("Create metric and complete tiers; verify both backups", create_complete)
run_case("Change metric bounds and tier coverage together", coordinated_bounds)
run_case(
    "Reject tier gap without source changes",
    lambda root, snapshot: invalid_coverage(root, snapshot, False),
)
run_case(
    "Reject tier overlap without source changes",
    lambda root, snapshot: invalid_coverage(root, snapshot, True),
)
run_case("Reject stale full-project snapshot", stale_snapshot)
run_case("Preserve external change made during validation", change_during_validation)
run_case("Second replacement failure rolls back byte-for-byte", rollback_second_replace)
run_case("Block unfinished transaction", pending_transaction)
run_case("Block and preserve existing lock", existing_lock)

unchanged = live_before == {p.name: digest(p) for p in live_paths}
results.append({"name": "Live source CSV hashes unchanged", "passed": unchanged})
print(
    ("PASS: " if unchanged else "FAIL: ")
    + "Live source CSV hashes unchanged",
    flush=True,
)

passed = sum(row["passed"] for row in results)
report_dir = root / "generated/reports"
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
report_path = report_dir / ("metric_bundle_regression_" + stamp + ".json")
report = {
    "testedAtLocal": datetime.now().astimezone().isoformat(),
    "scope": (
        "Temporary-project service tests using real validator; "
        "injected caught replacement failure; not power-loss recovery testing"
    ),
    "valid": passed == len(results),
    "passedCount": passed,
    "testCount": len(results),
    "liveSourcesUnchanged": unchanged,
    "results": results,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("\n=== Metric Bundle Regression Summary ===")
print(f"Passed: {passed}/{len(results)}")
print("Live sources unchanged:", unchanged)
print("Report:", report_path)

if not report["valid"]:
    raise SystemExit(1)

print("Phase 38 complete: coordinated-save sandbox tests passed.")
'@

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 38 failed. Review the failed cases and regression report.'
}
```

The target is **10/10**. These tests cover a caught replacement failure, not process termination or power-loss recovery. Paste the final summary and any failures; we’ll address those before adding GUI controls.

<div align="center">⁂</div>

[^21_1]: doda_content_workbench/doda_content_workbench.py


---

# Phase 38: coordinated-save sandbox regression

PASS: Create metric and complete tiers; verify both backups
PASS: Change metric bounds and tier coverage together
PASS: Reject tier gap without source changes
PASS: Reject tier overlap without source changes
PASS: Reject stale full-project snapshot
PASS: Preserve external change made during validation
PASS: Second replacement failure rolls back byte-for-byte
PASS: Block unfinished transaction
PASS: Block and preserve existing lock
PASS: Live source CSV hashes unchanged

=== Metric Bundle Regression Summary ===
Passed: 10/10
Live sources unchanged: True
Report: E:\\Dev\\uzdoom_src\\doda-core\\generated\\reports\\metric_bundle_regression_20261006_0
74356_258082.json
Phase 38 complete: coordinated-save sandbox tests passed.

Phase 38 **passed: 10/10**. The service successfully saved coordinated changes, rejected invalid coverage and stale snapshots, verified both backups, and restored the original CSVs after an injected second-replacement failure. Your live CSVs remained unchanged.

We can now build the GUI workflow. It should stage a metric and its tiers in a separate window, leaving the ordinary editors and their validation rules intact. Complete tier coverage remains required.[^22_1]

## Phase 39 — Inspect integration points

Before patching the launcher, run this read-only block to capture its current menu structure and command handling. This avoids guessing insertion anchors or adding the new command in the wrong place.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 39: read-only metric bundle GUI integration inspection' -ForegroundColor Cyan

$inspectionScript = @'
import ast
import sys
from pathlib import Path

tools = Path(sys.argv[^22_1]).resolve()
gui_path = tools / "doda_content_gui.py"
service_path = tools / "doda_metric_bundle_service.py"

for path in (gui_path, service_path):
    if not path.is_file():
        raise FileNotFoundError("Required module not found: " + str(path))

text = gui_path.read_text(encoding="utf-8-sig")
lines = text.splitlines()
tree = ast.parse(text, filename=str(gui_path))

classes = [
    node for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "ContentWorkbenchApp"
]
if len(classes) != 1:
    raise RuntimeError("Expected one ContentWorkbenchApp class.")

app_class = classes[^22_0]

print("\n=== GUI imports and version declarations ===")
for node in tree.body:
    show = isinstance(node, (ast.Import, ast.ImportFrom))
    if isinstance(node, ast.Assign):
        show = any(
            isinstance(target, ast.Name)
            and target.id in {"APP_TITLE", "APP_VERSION"}
            for target in node.targets
        )
    if show:
        for index in range(node.lineno - 1, node.end_lineno):
            print(f"{index + 1:5}: {lines[index]}")

for name in ("_build_menu", "run_command", "choose_project_root"):
    matches = [
        node for node in app_class.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one {name} method; found {len(matches)}"
        )
    node = matches[^22_0]
    print(f"\n=== ContentWorkbenchApp.{name} ===")
    for index in range(node.lineno - 1, node.end_lineno):
        print(f"{index + 1:5}: {lines[index]}")

print("\n=== Existing bundle-related GUI references ===")
references = []
for number, line in enumerate(lines, start=1):
    if "metric_bundle" in line.lower() or "coordinated" in line.lower():
        references.append((number, line.strip()))
if references:
    for number, line in references:
        print(f"{number}: {line}")
else:
    print("None found.")

print("\n=== Coordinated service public function signatures ===")
service_text = service_path.read_text(encoding="utf-8-sig")
service_tree = ast.parse(service_text, filename=str(service_path))
for node in service_tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in {
        "read_snapshot", "validate_candidate", "commit_bundle"
    }:
        signature = ast.unparse(node).splitlines()[^22_0]
        print(signature)

print("\nPhase 39 inspection complete. No files changed.")
'@

$inspectionScript | & $pythonPath - $toolDir

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 39 inspection failed. Review the Python error above.'
}
```


## Planned GUI behavior

The new workflow will provide:

- A choice to create a metric or load an existing one.
- A metric form and a staged tier list.
- Add, edit, and remove controls that affect only staged tiers.
- Candidate validation before saving.
- One confirmed coordinated save through the tested service.
- Cancel/close behavior that discards staged changes only after confirmation.
- A clear backup/transaction location after saving.

We’ll create the window module first, then integrate it through a guarded launcher patch and sandbox-test it. No export or runtime integration will be added.

Paste the Phase 39 output so the next block can match your current launcher exactly.

<div align="center">⁂</div>

[^22_1]: doda_content_workbench/doda_content_workbench.py


---

# Phase 39: read-only metric bundle GUI integration inspection

=== GUI imports and version declarations ===
18: from __future__ import annotations
20: import argparse
21: import csv
22: import json
23: import os
24: import subprocess
25: import sys
26: import tkinter as tk
27: from datetime import datetime
28: from pathlib import Path
29: from tkinter import filedialog, messagebox, ttk
30: from typing import Any
31: from doda_track_editor import install_track_editor
32: from doda_metrics_editor import install_metrics_editor
33: from doda_metric_tiers_editor import install_metric_tiers_editor
34: from doda_facilities_editor import install_facilities_editor
35: from doda_flavor_text_editor import install_flavor_text_editor
36: from doda_enum_catalog_editor import install_enum_catalog_editor
37: from doda_qualification_catalog_editor import install_qualification_catalog_editor
38: from doda_capabilities_editor import install_capabilities_editor
39: from doda_facility_capabilities_editor import install_facility_capabilities_editor
40: from doda_capability_staffing_rules_editor import install_capability_staffing_rule
s_editor
41: from doda_facility_capability_staffing_overrides_editor import install_facility_ca
pability_staffing_overrides_editor
42: from doda_task_templates_editor import install_task_templates_editor
43: from doda_foims_x_preview import FoimsXPreview
46: APP_TITLE = "DoDA Content Workbench"
47: APP_VERSION = "0.9.0"

=== ContentWorkbenchApp.\_build_menu ===
506: def \_build_menu(self) -> None:
507: """Create dark drop-down menus without attaching a native Windows menu bar
."""
508:
509: menu_options = {
510: "tearoff": False,
511: "background": "\#1f2933",
512: "foreground": "\#e6edf3",
513: "activebackground": "\#264f78",
514: "activeforeground": "\#ffffff",
515: "disabledforeground": "\#6e7681",
516: "borderwidth": 0,
517: "relief": tk.FLAT,
518: }
519:
520: self.file_menu = tk.Menu(self, \*\*menu_options)
521: self.file_menu.add_command(
522: label="Choose Project Root...",
523: command=self.choose_project_root,
524: )
525: self.file_menu.add_separator()
526: self.file_menu.add_command(label="Exit", command=self.destroy)
527:
528: self.actions_menu = tk.Menu(self, \*\*menu_options)
529: self.actions_menu.add_command(
530: label="Refresh Source Data",
531: command=lambda: self.refresh_all(show_message=True),
532: )
533: self.actions_menu.add_command(
534: label="Run Validation",
535: command=self.run_validation,
536: )
537: self.actions_menu.add_command(
538: label="Export Generated Content",
539: command=self.run_export,
540: )
541:
542: self.folders_menu = tk.Menu(self, \*\*menu_options)
543: self.folders_menu.add_command(
544: label="Open Source Data Folder",
545: command=lambda: self.open_folder(self.source_directory),
546: )
547: self.folders_menu.add_command(
548: label="Open Generated Output Folder",
549: command=lambda: self.open_folder(self.generated_directory),
550: )
551: self.folders_menu.add_command(
552: label="Open Validation Reports Folder",
553: command=lambda: self.open_folder(self.report_directory),
554: )
555: self.folders_menu.add_command(
556: label="Open Build Folder",
557: command=lambda: self.open_folder(self.build_directory),
558: )
559:
560: self.preview_menu = tk.Menu(self, \*\*menu_options)
561: self.preview_menu.add_command(
562: label="Open FOIMS-X Monitor",
563: command=self.open_foims_preview,
564: )
565: self.preview_menu.add_command(
566: label="Refresh FOIMS-X Monitor",
567: command=self.refresh_foims_preview,
568: )
569:
570: self.view_menu = tk.Menu(self, \*\*menu_options)
571: self.view_menu.add_command(
572: label="Fullscreen",
573: command=self.toggle_fullscreen,
574: accelerator="F11",
575: )
576: self.view_menu.add_separator()
577: self.view_menu.add_command(
578: label="FOIMS-X Preview",
579: command=self.open_foims_preview,
580: accelerator="Ctrl+O",
581: )
582:
583: self.help_menu = tk.Menu(self, \*\*menu_options)
584: self.help_menu.add_command(label="About", command=self.show_about)

=== ContentWorkbenchApp.run_command ===
1556: def run_command(
1557: self,
1558: label: str,
1559: command: list[str],
1560: success_message: str,
1561: ) -> None:
1562: self.config(cursor="watch")
1563: self.update_idletasks()
1564:
1565: self.log(f"Starting {label.lower()}: {' '.join(command)}")
1566:
1567: try:
1568: completed = subprocess.run(
1569: command,
1570: cwd=self.project_root,
1571: text=True,
1572: encoding="utf-8",
1573: errors="replace",
1574: capture_output=True,
1575: )
1576:
1577: combined_output = (
1578: completed.stdout.rstrip()
1579: + ("\\n" if completed.stdout and completed.stderr else "")
1580: + completed.stderr.rstrip()
1581: ).strip()
1582:
1583: if combined_output:
1584: self.log(f"{label} output:")
1585: for line in combined_output.splitlines():
1586: self.log(f" {line}")
1587:
1588: self.log(f"{label} process exit code: {completed.returncode}")
1589:
1590: self.refresh_all(show_message=False)
1591:
1592: if completed.returncode == 0:
1593: self.status_text.set(success_message)
1594: messagebox.showinfo(APP_TITLE, success_message)
1595: else:
1596: self.status_text.set(f"{label} failed.")
1597: messagebox.showerror(
1598: APP_TITLE,
1599: f"{label} failed with exit code {completed.returncode}.\\n\\n"
1600: "Review the Activity Log tab for complete output.",
1601: )
1602:
1603: except OSError as error:
1604: self.status_text.set(f"{label} could not start.")
1605: self.log(f"{label} launch error: {error}")
1606: messagebox.showerror(
1607: APP_TITLE,
1608: f"Could not start {label.lower()}.\\n\\n{error}",
1609: )
1610: finally:
1611: self.config(cursor="")
1612: self.update_idletasks()

=== ContentWorkbenchApp.choose_project_root ===
1637: def choose_project_root(self) -> None:
1638: selected = filedialog.askdirectory(
1639: title="Choose DoDA Project Root",
1640: initialdir=str(self.project_root),
1641: )
1642:
1643: if not selected:
1644: return
1645:
1646: candidate = Path(selected)
1647:
1648: try:
1649: verified_root = find_project_root(candidate)
1650: except FileNotFoundError as error:
1651: messagebox.showerror(APP_TITLE, str(error))
1652: return
1653:
1654: self.project_root = verified_root
1655: self.workbench_directory = (
1656: self.project_root / "tools" / "doda_content_workbench"
1657: )
1658: self.validator_path = (
1659: self.workbench_directory / "doda_content_workbench.py"
1660: )
1661: self.exporter_path = (
1662: self.workbench_directory / "doda_content_export.py"
1663: )
1664: self.source_directory = self.project_root / "data_authoring" / "source"
1665: self.generated_directory = self.project_root / "generated"
1666: self.report_directory = self.generated_directory / "reports"
1667: self.build_directory = self.project_root / "build"
1668: self.validation_report_path = (
1669: self.report_directory / "content_validation_report.json"
1670: )
1671:
1672: self.project_text.set(str(self.project_root))
1673: self.log(f"Project root changed to: {self.project_root}")
1674: self.refresh_all(show_message=True)

=== Existing bundle-related GUI references ===
None found.

=== Coordinated service public function signatures ===
def read_snapshot(root: Path) -> dict:
def validate_candidate(root: Path, raw: dict[str, bytes]) -> str:
def commit_bundle(root: Path, metric_rows: list[dict], tier_rows: list[dict], expected_ha
shes: dict[str, str]) -> dict:

Phase 39 inspection complete. No files changed.

Phase 39 confirms the integration points. We’ll create the separate staging-window module now, then add its Actions menu entry only after the module is checked.

## Phase 40 — Create staging window

This window will let users prepare one metric and its complete tier set without saving intermediate invalid states. Saving will use the coordinated service; the full-project coverage rules remain unchanged.[^23_1]

Close the Workbench and run the block below. It creates **one new module**; it does not modify the launcher, CSVs, or exports.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$modulePath = Join-Path $toolDir 'doda_metric_bundle_editor.py'
$tempPath = "$modulePath.new"

foreach ($path in @(
    $pythonPath,
    (Join-Path $toolDir 'doda_metric_bundle_service.py')
)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required component not found: $path"
    }
}

if (Test-Path -LiteralPath $modulePath) {
    throw "Module already exists. No files changed: $modulePath"
}

$csvFiles = @(
    Get-ChildItem -LiteralPath (Join-Path $root 'data_authoring\source') `
        -Filter '*.csv' -File
)

if ($csvFiles.Count -ne 12) {
    throw 'Expected exactly 12 source CSVs.'
}

$hashes = @{}
foreach ($file in $csvFiles) {
    $hashes[$file.Name] = (
        Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
    ).Hash
}

Write-Host 'Phase 40: create metric-and-tiers staging window only' -ForegroundColor Cyan

$moduleSource = @'
from __future__ import annotations

import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import doda_metric_bundle_service as service
from doda_content_workbench import TABLE_SPECS
from doda_metric_tiers_editor import MetricTiersEditor


ID_PATTERN = re.compile(r"[A-Z][A-Z0-9_]*")
METRIC_FIELDS = tuple(TABLE_SPECS["metrics"]["required_columns"])
TIER_FIELDS = tuple(
    field for field in TABLE_SPECS["metric_tiers"]["required_columns"]
    if field != "metric_id"
)
LABELS = {
    "metric_id": "Metric ID",
    "display_name": "Display Name",
    "description": "Description",
    "owner_system": "Owner System",
    "internal_min": "Internal Minimum",
    "internal_max": "Internal Maximum",
    "default_value": "Default Value",
    "polarity": "Polarity",
    "ui_display_mode": "UI Display Mode",
    "update_notes": "Update Notes",
    "active": "Active",
    "tier_id": "Tier ID",
    "min_inclusive": "Minimum (inclusive)",
    "max_inclusive": "Maximum (inclusive)",
    "display_label": "Display Label",
    "short_status": "Short Status",
    "ui_color": "UI Color",
    "flavor_text_id": "Flavor Text",
    "sort_order": "Sort Order",
}


class MetricBundleEditor(tk.Toplevel):
    def __init__(self, app):
        self.app = app
        self.root_path = Path(app.project_root).resolve()
        self.snapshot = service.read_snapshot(self.root_path)
        super().__init__(app)

        self.title("Metric and Tiers - Coordinated Editor")
        self.geometry("1100x760")
        self.minsize(1000, 700)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.editing_id = None
        self.tiers = []
        self.tier_index = None
        self.metric_vars = {}
        self.metric_widgets = {}
        self.tier_vars = {}
        self.tier_widgets = {}
        self.load_id = tk.StringVar(master=self)
        self.status = tk.StringVar(master=self)
        self.build()
        self.set_new_metric()
        self.grab_set()

    def enum_choices(self, group):
        rows = [
            row for row in self.snapshot["rows"]["enum_catalog.csv"]
            if row["enum_group"] == group
            and row["active"].upper() == "TRUE"
        ]
        return [
            row["enum_value"]
            for row in sorted(
                rows, key=lambda row: (int(row["sort_order"]), row["enum_value"])
            )
        ]

    def build(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(
            outer, text=str(self.root_path), wraplength=1000
        ).pack(anchor="w")

        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=8)
        values = sorted(
            row["metric_id"]
            for row in self.snapshot["rows"]["metrics.csv"]
        )
        ttk.Combobox(
            toolbar, textvariable=self.load_id,
            values=values, state="readonly", width=28
        ).pack(side="left")
        ttk.Button(
            toolbar, text="Load Metric", command=self.load_metric
        ).pack(side="left", padx=6)
        ttk.Button(
            toolbar, text="New Metric", command=self.new_metric
        ).pack(side="left")

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        metric_tab = ttk.Frame(notebook, padding=10)
        tier_tab = ttk.Frame(notebook, padding=10)
        notebook.add(metric_tab, text="Metric")
        notebook.add(tier_tab, text="Staged Tiers")

        self.build_form(
            metric_tab, METRIC_FIELDS,
            self.metric_vars, self.metric_widgets, metric=True
        )

        left = ttk.Frame(tier_tab)
        right = ttk.Frame(tier_tab)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(
            left, columns=("id", "min", "max", "label"),
            show="headings", selectmode="browse"
        )
        for field, title in (
            ("id", "Tier ID"), ("min", "Min"),
            ("max", "Max"), ("label", "Label")
        ):
            self.tree.heading(field, text=title)
            self.tree.column(field, width=100, minwidth=50)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select_tier)

        self.build_form(
            right, TIER_FIELDS, self.tier_vars, self.tier_widgets
        )
        tier_buttons = ttk.Frame(right)
        tier_buttons.grid(
            row=len(TIER_FIELDS), column=0, columnspan=2,
            sticky="ew", pady=8
        )
        for label, command in (
            ("New Tier", self.new_tier),
            ("Apply Tier to Draft", self.apply_tier),
            ("Remove Staged Tier", self.remove_tier),
        ):
            ttk.Button(
                tier_buttons, text=label, command=command
            ).pack(fill="x", pady=2)

        ttk.Label(
            outer,
            text=(
                "Apply each tier edit to the draft before validation or saving. "
                "Draft changes do not alter CSVs. Saving replaces metrics.csv "
                "and metric_tiers.csv together through the coordinated service. "
                "No export is performed."
            ),
            wraplength=1000,
        ).pack(anchor="w", pady=8)

        bottom = ttk.Frame(outer)
        bottom.pack(fill="x")
        for label, command in (
            ("Validate Draft", self.validate_draft),
            ("Save Metric and Tiers", self.save_bundle),
            ("Cancel / Close", self.close),
        ):
            ttk.Button(
                bottom, text=label, command=command
            ).pack(side="left", padx=(0, 8))
        ttk.Label(
            outer, textvariable=self.status, wraplength=1000
        ).pack(anchor="w", pady=(8, 0))

    def build_form(self, parent, fields, variables, widgets, metric=False):
        parent.columnconfigure(1, weight=1)
        for index, field in enumerate(fields):
            ttk.Label(parent, text=LABELS[field] + ":").grid(
                row=index, column=0, sticky="nw", padx=(0, 8), pady=3
            )
            var = tk.StringVar(master=self)
            variables[field] = var
            if field == "active":
                widget = ttk.Checkbutton(
                    parent, variable=var, onvalue="TRUE", offvalue="FALSE"
                )
            elif field in {"polarity", "ui_display_mode", "flavor_text_id"}:
                if field == "flavor_text_id":
                    values = sorted(
                        row["flavor_text_id"]
                        for row in self.snapshot["rows"]["flavor_text.csv"]
                    )
                else:
                    group = (
                        "METRIC_POLARITY" if field == "polarity"
                        else "METRIC_DISPLAY_MODE"
                    )
                    values = self.enum_choices(group)
                widget = ttk.Combobox(
                    parent, textvariable=var,
                    values=values, state="readonly"
                )
            elif field in {"description", "update_notes", "short_status"}:
                widget = tk.Text(parent, height=2, wrap="word")
            else:
                widget = ttk.Entry(parent, textvariable=var)
            widget.grid(row=index, column=1, sticky="ew", pady=3)
            widgets[field] = widget

    @staticmethod
    def get_form(variables, widgets):
        values = {}
        for field, var in variables.items():
            widget = widgets[field]
            values[field] = (
                widget.get("1.0", "end-1c")
                if isinstance(widget, tk.Text) else var.get()
            )
        return values

    @staticmethod
    def set_form(values, variables, widgets):
        for field, var in variables.items():
            value = values.get(field, "")
            widget = widgets[field]
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
            else:
                var.set(value)

    def state(self):
        return json.dumps({
            "metric": self.get_form(self.metric_vars, self.metric_widgets),
            "tiers": self.tiers,
            "tierForm": self.get_form(self.tier_vars, self.tier_widgets),
        }, sort_keys=True)

    def allow_discard(self):
        return self.state() == self.baseline or messagebox.askyesno(
            "Discard draft?",
            "Discard unsaved metric and tier draft changes?",
            parent=self, default=messagebox.NO,
        )

    def check_root(self):
        if Path(self.app.project_root).resolve() != self.root_path:
            raise service.BundleError(
                "The application project changed. Close and reopen this editor."
            )

    def set_new_metric(self):
        self.editing_id = None
        self.tiers = []
        self.metric_widgets["metric_id"].configure(state="normal")
        polarities = self.enum_choices("METRIC_POLARITY")
        modes = self.enum_choices("METRIC_DISPLAY_MODE")
        self.set_form({
            "owner_system": "NativeStrategicCore",
            "internal_min": "0", "internal_max": "1000",
            "default_value": "0", "active": "TRUE",
            "polarity": (
                "HIGHER_IS_BETTER" if "HIGHER_IS_BETTER" in polarities
                else polarities[^23_0] if polarities else ""
            ),
            "ui_display_mode": (
                "TIERED_BAR" if "TIERED_BAR" in modes
                else modes[^23_0] if modes else ""
            ),
        }, self.metric_vars, self.metric_widgets)
        self.draw_tiers()
        self.reset_tier()
        self.baseline = self.state()
        self.status.set("New metric draft. Stage complete tier coverage.")

    def new_metric(self):
        if self.allow_discard():
            self.set_new_metric()

    def load_metric(self):
        try:
            self.check_root()
            key = self.load_id.get()
            row = next(
                (row for row in self.snapshot["rows"]["metrics.csv"]
                 if row["metric_id"] == key), None
            )
            if row is None:
                raise ValueError("Choose an existing metric.")
            if not self.allow_discard():
                return
            self.editing_id = key
            self.metric_widgets["metric_id"].configure(state="normal")
            self.set_form(row, self.metric_vars, self.metric_widgets)
            self.metric_widgets["metric_id"].configure(state="disabled")
            self.tiers = [
                dict(row)
                for row in self.snapshot["rows"]["metric_tiers.csv"]
                if row["metric_id"] == key
            ]
            self.draw_tiers()
            self.reset_tier()
            self.baseline = self.state()
            self.status.set("Loaded " + key + " from the opening snapshot.")
        except (ValueError, service.BundleError) as error:
            messagebox.showerror("Metric and Tiers", str(error), parent=self)

    def reset_tier(self):
        self.tier_index = None
        self.tree.selection_remove(*self.tree.selection())
        self.tier_widgets["tier_id"].configure(state="normal")
        self.set_form(
            {"ui_color": "#8C939F", "sort_order": str(len(self.tiers) + 1)},
            self.tier_vars, self.tier_widgets
        )
        self.tier_baseline = self.get_form(self.tier_vars, self.tier_widgets)

    def tier_dirty(self):
        return (
            self.get_form(self.tier_vars, self.tier_widgets)
            != self.tier_baseline
        )

    def new_tier(self):
        if self.tier_dirty() and not messagebox.askyesno(
            "Discard tier form?",
            "Discard the unapplied tier form?",
            parent=self, default=messagebox.NO,
        ):
            return
        self.reset_tier()

    def draw_tiers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, row in enumerate(self.tiers):
            self.tree.insert(
                "", "end", iid=str(index),
                values=(
                    row["tier_id"], row["min_inclusive"],
                    row["max_inclusive"], row["display_label"]
                )
            )

    def select_tier(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[^23_0])
        if index == self.tier_index:
            return
        if self.tier_dirty() and not messagebox.askyesno(
            "Discard tier form?",
            "Discard the unapplied tier form and select another tier?",
            parent=self, default=messagebox.NO,
        ):
            if self.tier_index is not None:
                self.tree.selection_set(str(self.tier_index))
            else:
                self.tree.selection_remove(*self.tree.selection())
            return
        self.tier_index = index
        self.set_form(
            self.tiers[index], self.tier_vars, self.tier_widgets
        )
        self.tier_widgets["tier_id"].configure(state="disabled")
        self.tier_baseline = self.get_form(self.tier_vars, self.tier_widgets)

    def apply_tier(self):
        try:
            row = {
                key: value.strip()
                for key, value in self.get_form(
                    self.tier_vars, self.tier_widgets
                ).items()
            }
            if not ID_PATTERN.fullmatch(row["tier_id"]):
                raise ValueError("Tier ID must use uppercase ID syntax.")
            for field in ("display_label", "short_status"):
                if not row[field]:
                    raise ValueError(LABELS[field] + " is required.")
            if int(row["min_inclusive"]) > int(row["max_inclusive"]):
                raise ValueError("Tier minimum cannot exceed its maximum.")
            if int(row["sort_order"]) < 1:
                raise ValueError("Tier Sort Order must be at least 1.")
            flavor_ids = {
                row["flavor_text_id"]
                for row in self.snapshot["rows"]["flavor_text.csv"]
            }
            if row["flavor_text_id"] not in flavor_ids:
                raise ValueError("Choose an existing Flavor Text.")
            row["ui_color"] = MetricTiersEditor.normalized_ui_color(
                row["ui_color"]
            )
            if any(
                item["tier_id"] == row["tier_id"] and index != self.tier_index
                for index, item in enumerate(self.tiers)
            ):
                raise ValueError("Tier ID already exists in this draft.")
            row["metric_id"] = self.metric_vars["metric_id"].get().strip()
            if self.tier_index is None:
                self.tiers.append(row)
            else:
                if row["tier_id"] != self.tiers[self.tier_index]["tier_id"]:
                    raise ValueError("Existing Tier ID cannot change.")
                self.tiers[self.tier_index] = row
            self.draw_tiers()
            self.reset_tier()
            self.status.set(
                "Tier applied to draft only. Complete coverage is checked "
                "by Validate Draft or Save."
            )
        except ValueError as error:
            messagebox.showerror("Tier draft", str(error), parent=self)

    def remove_tier(self):
        if self.tier_index is None:
            messagebox.showwarning(
                "Tier draft", "Select a staged tier first.", parent=self
            )
            return
        if messagebox.askyesno(
            "Remove staged tier?",
            "Remove this tier from the draft only?",
            parent=self, default=messagebox.NO,
        ):
            del self.tiers[self.tier_index]
            self.draw_tiers()
            self.reset_tier()
            self.status.set("Tier removed from draft only.")

    def candidate_rows(self):
        self.check_root()
        if self.tier_dirty():
            raise ValueError(
                "Apply the tier form to the draft, or discard it with New Tier, "
                "before validating or saving."
            )
        metric = {
            field: value.strip()
            for field, value in self.get_form(
                self.metric_vars, self.metric_widgets
            ).items()
        }
        key = metric["metric_id"]
        if not ID_PATTERN.fullmatch(key):
            raise ValueError("Metric ID must use uppercase ID syntax.")
        for field in ("display_name", "description", "owner_system"):
            if not metric[field]:
                raise ValueError(LABELS[field] + " is required.")
        minimum = int(metric["internal_min"])
        maximum = int(metric["internal_max"])
        default = int(metric["default_value"])
        if not minimum <= default <= maximum:
            raise ValueError("Default must be inside the inclusive metric range.")
        if metric["active"] not in {"TRUE", "FALSE"}:
            raise ValueError("Active must be TRUE or FALSE.")
        original_metrics = self.snapshot["rows"]["metrics.csv"]
        if self.editing_id is not None and key != self.editing_id:
            raise ValueError("Existing Metric ID cannot change.")
        if self.editing_id is None and any(
            row["metric_id"] == key for row in original_metrics
        ):
            raise ValueError("Metric ID already exists. Load it for editing.")
        if not self.tiers:
            raise ValueError("Stage at least one tier covering the full range.")
        metrics = [
            dict(row) for row in original_metrics if row["metric_id"] != key
        ] + [metric]
        tiers = [
            dict(row)
            for row in self.snapshot["rows"]["metric_tiers.csv"]
            if row["metric_id"] != key
        ] + [dict(row, metric_id=key) for row in self.tiers]
        return metrics, tiers

    def validate_draft(self):
        try:
            metrics, tiers = self.candidate_rows()
            files = service.source_files(self.root_path)
            raw = {name: path.read_bytes() for name, path in files.items()}
            if {
                name: service.sha256(data) for name, data in raw.items()
            } != self.snapshot["hashes"]:
                raise service.BundleError(
                    "Source changed since opening. Preserve your draft "
                    "elsewhere, then close and reopen this editor."
                )
            raw["metrics.csv"] = service.encode_table("metrics", metrics)
            raw["metric_tiers.csv"] = service.encode_table("metric_tiers", tiers)
            output = service.validate_candidate(self.root_path, raw)
            self.app.log(output)
            self.status.set("Draft validation passed. No source CSVs changed.")
            messagebox.showinfo(
                "Metric and Tiers",
                "Draft validation passed. No source CSVs changed.",
                parent=self,
            )
        except (ValueError, OSError, service.BundleError) as error:
            self.app.log(str(error))
            messagebox.showerror("Metric and Tiers", str(error), parent=self)

    def save_bundle(self):
        try:
            metrics, tiers = self.candidate_rows()
            if not messagebox.askyesno(
                "Save Metric and Tiers?",
                "Save metric " + self.metric_vars["metric_id"].get().strip()
                + " with " + str(len(self.tiers))
                + " staged tier(s)?\n\n"
                "Both CSVs will be backed up and replaced after full validation. "
                "No export will run.",
                parent=self, default=messagebox.NO,
            ):
                return
            result = service.commit_bundle(
                self.root_path, metrics, tiers, self.snapshot["hashes"]
            )
        except (ValueError, OSError, service.BundleError) as error:
            self.app.log(str(error))
            messagebox.showerror("Metric and Tiers", str(error), parent=self)
            return

        self.app.log(result["validationOutput"])
        self.app.log(
            "Metric bundle committed. Backups: "
            + result["transactionDirectory"]
        )
        try:
            self.app.refresh_all(False)
        except Exception as error:
            self.app.log("Bundle saved; GUI refresh raised: " + str(error))
        messagebox.showinfo(
            "Metric and Tiers",
            "Coordinated save completed.\n\nBackups and transaction record:\n"
            + result["transactionDirectory"]
            + "\n\nThe editor will close. Export separately when needed.",
            parent=self,
        )
        self.destroy()

    def close(self):
        if self.allow_discard():
            self.destroy()


def open_metric_bundle_editor(app):
    try:
        return MetricBundleEditor(app)
    except (ValueError, OSError, service.BundleError) as error:
        messagebox.showerror("Metric and Tiers", str(error), parent=app)
        return None
'@

try {
    [System.IO.File]::WriteAllText(
        $tempPath,
        $moduleSource,
        [System.Text.UTF8Encoding]::new($false)
    )

    $checkScript = @'
import ast
import sys
from pathlib import Path

path = Path(sys.argv[^23_1])
tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
compile(tree, str(path), "exec")
assert any(
    isinstance(node, ast.ClassDef) and node.name == "MetricBundleEditor"
    for node in tree.body
)
assert any(
    isinstance(node, ast.FunctionDef)
    and node.name == "open_metric_bundle_editor"
    for node in tree.body
)
print("PASS: staging-window syntax and entry points")
'@

    $checkScript | & $pythonPath - $tempPath

    if ($LASTEXITCODE -ne 0) {
        throw 'Staging-window syntax check failed. Module not installed.'
    }

    foreach ($file in $csvFiles) {
        $current = (
            Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
        ).Hash
        if ($current -ne $hashes[$file.Name]) {
            throw "Source CSV changed during preparation: $($file.Name)"
        }
    }

    Move-Item -LiteralPath $tempPath -Destination $modulePath

    Write-Host ''
    Write-Host 'PASS: all 12 live source CSV hashes unchanged' -ForegroundColor Green
    Write-Host 'Phase 40 complete: staging-window module created; launcher unchanged.' -ForegroundColor Green

    Get-Item -LiteralPath $modulePath |
        Select-Object Name, Length, LastWriteTime |
        Format-Table -AutoSize
}
finally {
    if (Test-Path -LiteralPath $tempPath) {
        Remove-Item -LiteralPath $tempPath -Force
    }
}
```


## Next verification

This establishes syntax only. Before adding the menu command, we’ll test the window in a temporary project for:

- Loading and creating metric drafts.
- Applying tier changes without saving CSVs.
- Rejecting unapplied tier-form changes.
- Validating complete coverage.
- Confirmed save and canceled save.
- Discard confirmation and project-root protection.

Paste the Phase 40 status. Do not use the new window to save against live data until its sandbox tests pass.

<div align="center">⁂</div>

[^23_1]: doda_content_workbench/doda_content_workbench.py


---

# Phase 40: create metric-and-tiers staging window only

PASS: staging-window syntax and entry points

PASS: all 12 live source CSV hashes unchanged
Phase 40 complete: staging-window module created; launcher unchanged.

Name Length LastWriteTime

______________________________________________________________________

doda_metric_bundle_editor.py 21681 10/6/2026 7:57:09 AM

Phase 40 passed its syntax checks, and the launcher and live CSVs remain unchanged. Next we’ll test the staging window with the **real GUI and coordinated service in temporary projects** before adding its menu entry.

## Phase 41 — Staging-window regression

Close the Workbench and run the entire block. Dialog responses are supplied by the tests; all saves occur in temporary copies. Coverage validation still uses the existing validator rules.[^24_1]

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 41: metric bundle window sandbox regression' -ForegroundColor Cyan

$testScript = @'
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[^24_1]).resolve()
tools = root / "tools/doda_content_workbench"
sys.path.insert(0, str(tools))

from doda_content_gui import ContentWorkbenchApp
from doda_metric_bundle_editor import MetricBundleEditor
import doda_metric_bundle_service as service

live_paths = sorted((root / "data_authoring/source").glob("*.csv"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

require(len(live_paths) == 12, "Expected exactly 12 source CSVs.")
before = {p.name: digest(p) for p in live_paths}
results = []

def source_bytes(sandbox):
    return {
        p.name: p.read_bytes()
        for p in (sandbox / "data_authoring/source").glob("*.csv")
    }

def capture(dialogs, kind):
    def handler(*args, **kwargs):
        text = str(args[^24_1]) if len(args) > 1 else str(kwargs)
        dialogs.append({"kind": kind, "message": text})
    return handler

def no_errors(dialogs):
    require(
        not any(d["kind"] in {"error", "warning"} for d in dialogs),
        "Unexpected dialogs: " + repr(dialogs),
    )

def run_case(name, function):
    app = None
    window = None
    try:
        with tempfile.TemporaryDirectory(prefix="doda-bundle-window-") as tmp:
            sandbox = Path(tmp)
            source = sandbox / "data_authoring/source"
            sandbox_tools = sandbox / "tools/doda_content_workbench"
            source.mkdir(parents=True)
            sandbox_tools.mkdir(parents=True)
            (sandbox / "DoDA").mkdir()
            (sandbox / "generated/reports").mkdir(parents=True)
            (sandbox / "build").mkdir()

            for path in live_paths:
                shutil.copy2(path, source / path.name)
            for path in tools.glob("*.py"):
                shutil.copy2(path, sandbox_tools / path.name)

            dialogs = []
            with (
                patch("tkinter.messagebox.showinfo", capture(dialogs, "info")),
                patch("tkinter.messagebox.showwarning", capture(dialogs, "warning")),
                patch("tkinter.messagebox.showerror", capture(dialogs, "error")),
                patch("tkinter.messagebox.askyesno", return_value=False) as confirm,
            ):
                try:
                    app = ContentWorkbenchApp(sandbox)
                    app.withdraw()
                    app.update()
                    no_errors(dialogs)

                    window = MetricBundleEditor(app)
                    window.withdraw()
                    app.update()
                    no_errors(dialogs)
                    dialogs.clear()

                    function(sandbox, app, window, dialogs, confirm)

                finally:
                    if window is not None and window.winfo_exists():
                        window.destroy()
                    if app is not None:
                        app.destroy()
                    window = None
                    app = None

        results.append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)
    except Exception as error:
        results.append({
            "name": name,
            "passed": False,
            "exception": repr(error),
        })
        print("FAIL: " + name, flush=True)
        print(repr(error), flush=True)

def prepare_new(app, window, dialogs):
    base = dict(window.snapshot["rows"]["metrics.csv"][^24_0])
    base_id = base["metric_id"]
    new_id = "WORKBENCH_GUI_BUNDLE_TEST"
    require(
        all(
            row["metric_id"] != new_id
            for row in window.snapshot["rows"]["metrics.csv"]
        ),
        "Reserved test metric already exists.",
    )
    base["metric_id"] = new_id
    base["display_name"] = "Sandbox GUI bundle metric"
    window.set_form(base, window.metric_vars, window.metric_widgets)

    copied = [
        dict(row)
        for row in window.snapshot["rows"]["metric_tiers.csv"]
        if row["metric_id"] == base_id
    ]
    require(bool(copied), "Baseline metric has no tiers.")

    for row in copied:
        window.set_form(row, window.tier_vars, window.tier_widgets)
        window.apply_tier()
        app.update()
        no_errors(dialogs)

    require(
        len(window.tiers) == len(copied),
        "Tier forms were not applied to the draft.",
    )
    return new_id

def load_existing(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    expected = window.snapshot["rows"]["metrics.csv"][^24_0]
    window.load_id.set(expected["metric_id"])
    window.load_metric()
    app.update()
    no_errors(dialogs)
    require(window.editing_id == expected["metric_id"], "Metric was not loaded.")
    require(
        window.get_form(window.metric_vars, window.metric_widgets) == expected,
        "Loaded metric form differs from source.",
    )
    require(
        str(window.metric_widgets["metric_id"]["state"]) == "disabled",
        "Existing Metric ID is not disabled.",
    )
    expected_tiers = [
        row for row in window.snapshot["rows"]["metric_tiers.csv"]
        if row["metric_id"] == expected["metric_id"]
    ]
    require(window.tiers == expected_tiers, "Loaded tiers differ from source.")
    require(source_bytes(sandbox) == original, "Loading changed source CSVs.")

def stage_and_validate(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    prepare_new(app, window, dialogs)
    window.validate_draft()
    app.update()
    no_errors(dialogs)
    require(
        "validation passed" in window.status.get().lower(),
        "Draft validation did not report success.",
    )
    require(source_bytes(sandbox) == original, "Draft validation changed CSVs.")

def cancel_save(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    prepare_new(app, window, dialogs)
    confirm.return_value = False
    window.save_bundle()
    app.update()
    require(confirm.called, "Save did not request confirmation.")
    no_errors(dialogs)
    require(window.winfo_exists(), "Canceled save closed the window.")
    require(source_bytes(sandbox) == original, "Canceled save changed CSVs.")
    require(
        not list(
            (sandbox / "data_authoring/backups/metric_bundles")
            .glob("*/transaction.json")
        ),
        "Canceled save created a transaction.",
    )

def confirmed_save(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    key = prepare_new(app, window, dialogs)
    expected_count = len(window.tiers)
    confirm.return_value = True
    window.save_bundle()
    app.update()
    no_errors(dialogs)
    require(not window.winfo_exists(), "Successful save did not close the window.")
    snapshot = service.read_snapshot(sandbox)
    require(
        any(row["metric_id"] == key for row in snapshot["rows"]["metrics.csv"]),
        "New metric was not saved.",
    )
    require(
        len([
            row for row in snapshot["rows"]["metric_tiers.csv"]
            if row["metric_id"] == key
        ]) == expected_count,
        "Saved tier count differs from draft.",
    )
    require(
        any(row["metric_id"] == key for row in app.tables["metrics"]),
        "Application metric cache did not refresh.",
    )
    journals = list(
        (sandbox / "data_authoring/backups/metric_bundles")
        .glob("*/transaction.json")
    )
    require(len(journals) == 1, "Expected one committed transaction.")
    record = json.loads(journals[^24_0].read_text())
    require(record["status"] == "committed", "Transaction is not committed.")
    for name in service.TARGETS:
        require(
            (journals[^24_0].parent / name).read_bytes() == original[name],
            "Backup differs from original: " + name,
        )
    for name, data in original.items():
        if name not in service.TARGETS:
            require(
                source_bytes(sandbox)[name] == data,
                "Unrelated CSV changed: " + name,
            )

def unapplied_form(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    prepare_new(app, window, dialogs)
    window.tier_vars["display_label"].set("UNAPPLIED CHANGE")
    try:
        window.candidate_rows()
    except ValueError as error:
        require("Apply the tier form" in str(error), "Unexpected rejection.")
    else:
        raise AssertionError("Unapplied tier form was accepted.")
    require(source_bytes(sandbox) == original, "Unapplied form changed CSVs.")

def gap_rejection(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    prepare_new(app, window, dialogs)
    first = min(window.tiers, key=lambda row: int(row["min_inclusive"]))
    first["min_inclusive"] = str(int(first["min_inclusive"]) + 1)
    dialogs.clear()
    window.validate_draft()
    app.update()
    require(
        any(
            d["kind"] == "error"
            and "Candidate validation failed" in d["message"]
            for d in dialogs
        ),
        "Invalid coverage did not produce a validation rejection.",
    )
    require(source_bytes(sandbox) == original, "Gap rejection changed CSVs.")

def discard_confirmation(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    window.metric_vars["display_name"].set("UNSAVED CLOSE TEST")
    confirm.return_value = False
    window.close()
    require(window.winfo_exists(), "Declining discard closed the window.")
    require(confirm.called, "Dirty close did not request confirmation.")
    confirm.return_value = True
    window.close()
    require(not window.winfo_exists(), "Confirmed discard did not close.")
    require(source_bytes(sandbox) == original, "Discard changed CSVs.")

def root_protection(sandbox, app, window, dialogs, confirm):
    original = source_bytes(sandbox)
    prepare_new(app, window, dialogs)
    app.project_root = sandbox / "different-project"
    try:
        window.candidate_rows()
    except service.BundleError as error:
        require("project changed" in str(error), "Unexpected root rejection.")
    else:
        raise AssertionError("Changed project root was accepted.")
    require(source_bytes(sandbox) == original, "Root rejection changed CSVs.")

run_case("Load existing metric and tiers without saving", load_existing)
run_case("Apply new tier forms and validate complete draft", stage_and_validate)
run_case("Canceled save changes no CSVs or transactions", cancel_save)
run_case("Confirmed save commits both tables and exact backups", confirmed_save)
run_case("Reject unapplied tier form", unapplied_form)
run_case("Reject incomplete coverage without saving", gap_rejection)
run_case("Dirty close requires discard confirmation", discard_confirmation)
run_case("Reject changed application project root", root_protection)

unchanged = before == {p.name: digest(p) for p in live_paths}
results.append({"name": "Live source CSV hashes unchanged", "passed": unchanged})
print(
    ("PASS: " if unchanged else "FAIL: ")
    + "Live source CSV hashes unchanged",
    flush=True,
)

passed = sum(row["passed"] for row in results)
report_dir = root / "generated/reports"
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
report_path = report_dir / ("metric_bundle_window_regression_" + stamp + ".json")
report = {
    "testedAtLocal": datetime.now().astimezone().isoformat(),
    "scope": (
        "Real hidden GUI and coordinated service in temporary projects; "
        "dialogs mocked; no export; not a visual layout acceptance test"
    ),
    "valid": passed == len(results),
    "passedCount": passed,
    "testCount": len(results),
    "liveSourcesUnchanged": unchanged,
    "results": results,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("\n=== Metric Bundle Window Regression Summary ===")
print(f"Passed: {passed}/{len(results)}")
print("Live sources unchanged:", unchanged)
print("Report:", report_path)

if not report["valid"]:
    raise SystemExit(1)

print("Phase 41 complete: staging-window sandbox tests passed.")
'@

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 41 failed. Review the failed cases and regression report.'
}
```

The target is **9/9**. These tests check behavior, not whether the window’s controls fit visually at every size.

Paste the summary and any failures. If they pass, the next block will add the Actions menu command, followed by a non-destructive visual check.

<div align="center">⁂</div>

[^24_1]: doda_content_workbench/doda_content_workbench.py


---

# Phase 41: metric bundle window sandbox regression

PASS: Load existing metric and tiers without saving
PASS: Apply new tier forms and validate complete draft
PASS: Canceled save changes no CSVs or transactions
python.exe : invalid command name "2456996011648\<lambda>"
At line:352 char:15

- \$testScript | \& \$pythonPath - \$root
- ```
          ~~~~~~~~~~~~~~~~~~~~~
```

    - CategoryInfo : NotSpecified: (invalid command...011648\<lambda>":String)\
[], RemoteException
    - FullyQualifiedErrorId : NativeCommandError

The first three tests passed, but Phase 41 did not finish. The error is consistent with the test harness repeatedly creating and destroying Tk applications while a delayed callback is still pending. The GUI schedules a title-bar callback with `after(250, lambda: ...)`; that callback is unrelated to the staging-window tests.[^25_1]

We should correct the **test harness**, not change application behavior or suppress the error.

## Phase 41A — Cancel test callbacks

Run this in the **same PowerShell window** where you ran Phase 41. It uses the existing `$testScript`, inserts cancellation of pending startup callbacks immediately after constructing each test application, and reruns the full suite.

It does not modify any application file.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$pythonPath = Join-Path $root 'tools\doda_content_workbench\.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

if (
    -not (Get-Variable -Name testScript -ErrorAction SilentlyContinue) -or
    [string]::IsNullOrWhiteSpace($testScript)
) {
    throw 'Phase 41 testScript is not present. Use the same PowerShell window that ran Phase 41.'
}

if (
    -not $testScript.Contains('Metric Bundle Window Regression Summary') -or
    -not $testScript.Contains('def confirmed_save(')
) {
    throw 'The current testScript is not the Phase 41 staging-window regression script. Nothing executed.'
}

if ($testScript.Contains('Cancel pending startup callbacks in this test harness')) {
    throw 'The test-harness correction is already present. Nothing changed.'
}

$anchor = '                    app = ContentWorkbenchApp(sandbox)'

$anchorCount = (
    [regex]::Matches(
        $testScript,
        [regex]::Escape($anchor)
    )
).Count

if ($anchorCount -ne 1) {
    throw "Expected one application-construction anchor; found $anchorCount. Nothing changed."
}

$replacement = @'
                    app = ContentWorkbenchApp(sandbox)
                    # Cancel pending startup callbacks in this test harness.
                    pending = app.tk.call("after", "info")
                    if isinstance(pending, str):
                        pending = app.tk.splitlist(pending)
                    for callback_id in pending:
                        app.after_cancel(callback_id)
'@

if ($testScript.Contains("`r`n")) {
    $replacement = $replacement.Replace("`r`n", "`n").Replace("`n", "`r`n")
}
else {
    $replacement = $replacement.Replace("`r`n", "`n")
}

$testScript = $testScript.Replace($anchor, $replacement)

Write-Host 'Phase 41A: rerun staging-window tests with startup callbacks canceled' -ForegroundColor Cyan

$testScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 41A failed. Review the complete error and regression results.'
}
```

The target remains:

```text
Passed: 9/9
Live sources unchanged: True
Phase 41 complete: staging-window sandbox tests passed.
```

The final message still says Phase 41 because this is the same regression suite with a harness correction. Paste the summary or complete error output; we should not integrate the menu until the suite finishes successfully.

<div align="center">⁂</div>

[^25_1]: doda_content_workbench/doda_content_gui.py


---

# Phase 41A: rerun staging-window tests with startup callbacks canceled

PASS: Load existing metric and tiers without saving
PASS: Apply new tier forms and validate complete draft
PASS: Canceled save changes no CSVs or transactions
PASS: Confirmed save commits both tables and exact backups
PASS: Reject unapplied tier form
PASS: Reject incomplete coverage without saving
PASS: Dirty close requires discard confirmation
PASS: Reject changed application project root
PASS: Live source CSV hashes unchanged

=== Metric Bundle Window Regression Summary ===
Passed: 9/9
Live sources unchanged: True
Report: E:\\Dev\\uzdoom_src\\doda-core\\generated\\reports\\metric_bundle_window_regression_202
61006_083358_370802.json
Phase 41 complete: staging-window sandbox tests passed.

Phase 41 passed: **9/9**, including confirmed coordinated saves, exact backups, canceled saves, draft validation, and project-root protection. Live CSVs remained unchanged.

We can now add **Edit Metric and Tiers…** to the Actions menu, between Run Validation and Export Generated Content. This keeps the existing editor tabs and commands unchanged. The launcher’s Actions menu is the appropriate integration point.[^26_1]

## Phase 42 — Integrate menu command

Close the Workbench, then run this block. It backs up the launcher, verifies the insertion anchors, checks that only one import and one menu command are added, and restores the launcher if installed checks fail.

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Workbench Python not found: $pythonPath"
}

Write-Host 'Phase 42: integrate coordinated metric editor menu command' -ForegroundColor Cyan

$patchScript = @'
import ast
import copy
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[^26_1]).resolve()
tools = root / "tools/doda_content_workbench"
sys.path.insert(0, str(tools))

path = tools / "doda_content_gui.py"
temporary = path.with_name(path.name + ".bundle-menu.tmp")

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for required in (
    path,
    tools / "doda_metric_bundle_service.py",
    tools / "doda_metric_bundle_editor.py",
):
    require(required.is_file(), "Required module not found: " + str(required))

csv_paths = sorted((root / "data_authoring/source").glob("*.csv"))
require(len(csv_paths) == 12, "Expected exactly 12 source CSV files.")
csv_before = {p.name: digest(p) for p in csv_paths}

original_hash = digest(path)
original = path.read_text(encoding="utf-8-sig")
normalized = original.replace("\r\n", "\n")
original_tree = ast.parse(original, filename=str(path))

require(
    "doda_metric_bundle_editor" not in original
    and "Edit Metric and Tiers..." not in original,
    "Bundle integration already exists or is partially installed. No patch applied.",
)

import_anchor = (
    "from doda_metric_tiers_editor import install_metric_tiers_editor"
)
menu_anchor = (
    '        self.actions_menu.add_command(\n'
    '            label="Run Validation",\n'
    '            command=self.run_validation,\n'
    '        )'
)

require(normalized.count(import_anchor) == 1, "Import anchor missing or repeated.")
require(normalized.count(menu_anchor) == 1, "Menu anchor missing or repeated.")

new_import = (
    "from doda_metric_bundle_editor import open_metric_bundle_editor"
)
new_menu = (
    '        self.actions_menu.add_command(\n'
    '            label="Edit Metric and Tiers...",\n'
    '            command=lambda: open_metric_bundle_editor(self),\n'
    '        )'
)

candidate = normalized.replace(
    import_anchor, import_anchor + "\n" + new_import, 1
).replace(
    menu_anchor, menu_anchor + "\n" + new_menu, 1
)
candidate_tree = ast.parse(candidate, filename=str(path))
compile(candidate, str(path), "exec")

reduced = copy.deepcopy(candidate_tree)
imports = [
    node for node in reduced.body
    if isinstance(node, ast.ImportFrom)
    and node.module == "doda_metric_bundle_editor"
]
require(len(imports) == 1, "Expected exactly one added import.")
require(
    len(imports[^26_0].names) == 1
    and imports[^26_0].names[^26_0].name == "open_metric_bundle_editor"
    and imports[^26_0].names[^26_0].asname is None,
    "Unexpected bundle import structure.",
)
reduced.body.remove(imports[^26_0])

classes = [
    node for node in reduced.body
    if isinstance(node, ast.ClassDef)
    and node.name == "ContentWorkbenchApp"
]
require(len(classes) == 1, "Expected one application class.")
menus = [
    node for node in classes[^26_0].body
    if isinstance(node, ast.FunctionDef) and node.name == "_build_menu"
]
require(len(menus) == 1, "Expected one menu builder.")

expected_command = ast.parse(
    'self.actions_menu.add_command(\n'
    '    label="Edit Metric and Tiers...",\n'
    '    command=lambda: open_metric_bundle_editor(self),\n'
    ')'
).body[^26_0]

added = [
    node for node in menus[^26_0].body
    if ast.dump(node, include_attributes=False)
    == ast.dump(expected_command, include_attributes=False)
]
require(len(added) == 1, "Expected exactly one added menu command.")
menus[^26_0].body.remove(added[^26_0])

require(
    ast.dump(reduced, include_attributes=False)
    == ast.dump(original_tree, include_attributes=False),
    "Candidate contains changes beyond the import and menu command.",
)

def import_check(text):
    namespace = {
        "__name__": "_doda_gui_integration_check",
        "__file__": str(path),
    }
    exec(compile(text, str(path), "exec"), namespace)
    require(
        callable(namespace.get("open_metric_bundle_editor")),
        "Bundle editor entry point is not callable.",
    )
    require(
        "ContentWorkbenchApp" in namespace,
        "Application class missing after import.",
    )

import_check(candidate)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
backup_dir = tools / "backups" / ("metric_bundle_menu_" + stamp)
backup_dir.mkdir(parents=True, exist_ok=False)
backup = backup_dir / path.name
shutil.copy2(path, backup)
require(digest(backup) == original_hash, "Backup verification failed.")

installed = False
try:
    temporary.write_bytes(candidate.encode("utf-8"))
    require(
        digest(path) == original_hash,
        "Launcher changed externally. Installation cancelled.",
    )
    require(
        {p.name: digest(p) for p in csv_paths} == csv_before,
        "Source CSV changed during preparation. Installation cancelled.",
    )

    os.replace(temporary, path)
    installed = True

    installed_text = path.read_text(encoding="utf-8-sig")
    require(installed_text == candidate, "Installed launcher differs from candidate.")
    import_check(installed_text)
    require(
        {p.name: digest(p) for p in csv_paths} == csv_before,
        "Live source CSV hashes changed.",
    )

    print("\n=== Metric Bundle Menu Integration ===")
    print("PASS: only one import and one Actions command added")
    print("PASS: candidate and installed launcher import checks")
    print("PASS: all 12 live source CSV hashes unchanged")
    print("Backup:", backup)
    print("Previous SHA256:", original_hash)
    print("New SHA256:", digest(path))
    print("Phase 42 complete: coordinated editor menu integrated.")

except Exception:
    if installed:
        shutil.copy2(backup, path)
        require(
            digest(path) == original_hash,
            "Rollback verification failed. Preserve the backup.",
        )
        print("Previous launcher restored from backup.")
    raise

finally:
    if temporary.exists():
        temporary.unlink()
'@

$patchScript | & $pythonPath - $root

if ($LASTEXITCODE -ne 0) {
    throw 'Phase 42 failed. Review the error and rollback status above.'
}
```


## Non-destructive GUI check

Launch normally:

```powershell
$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'

& (Join-Path $toolDir '.venv\Scripts\python.exe') `
    (Join-Path $toolDir 'doda_content_gui.py') `
    --root $root
```

Then:

1. Choose Actions > Edit Metric and Tiers….
2. Confirm the displayed project root is correct.
3. Select `PREPAREDNESS` and click Load Metric.
4. Confirm the Metric form loads and its ID is disabled.
5. Open Staged Tiers and confirm the four existing tiers appear.
6. Select a tier and confirm its fields populate.
7. Check that fields, tier controls, and bottom buttons remain accessible at the window’s minimum size.
8. Click Validate Draft; confirm success without saving.
9. Click Cancel / Close, then reopen the window to confirm it can be opened again.
10. Close without saving or removing anything.

Paste the Phase 42 summary and reply **success** if the visual checks pass. If controls overlap or are clipped, provide a screenshot before we update the manual.

<div align="center">⁂</div>

[^26_1]: doda_content_workbench/doda_content_gui.py


---

# Phase 42: integrate coordinated metric editor menu command

=== Metric Bundle Menu Integration ===
PASS: only one import and one Actions command added
PASS: candidate and installed launcher import checks
PASS: all 12 live source CSV hashes unchanged
Backup: E:\\Dev\\uzdoom_src\\doda-core\\tools\\doda_content_workbench\\backups\\metric_bundle_me
nu_20261006_083448_293221\\doda_content_gui.py
Previous SHA256: ad55b300c94f4f55ed1a73c8f3cd19afa3fa8a0e24112e02d672d55059d52de6
New SHA256: 7e5adbe7354a3248294c7ea253d4433e4438ed0cd723e8dc42748c8741052a2b
Phase 42 complete: coordinated editor menu integrated.

Phase 42 passed: the Actions command is integrated, both import checks succeeded, and all 12 live CSV hashes remained unchanged. The remaining check is the window’s visible layout and behavior through the menu.

## Launch and verify

```powershell
$ErrorActionPreference = 'Stop'

$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$guiPath = Join-Path $toolDir 'doda_content_gui.py'

& $pythonPath $guiPath --root $root

if ($LASTEXITCODE -ne 0) {
    throw 'Workbench exited with an error. Review the traceback above.'
}
```

Perform these checks **without saving**:

1. Choose Actions > Edit Metric and Tiers….
2. Confirm the displayed project root is correct.
3. Select `PREPAREDNESS` and click Load Metric.
4. Confirm its Metric ID is disabled and its bounds are 0–1000, with default 300. Those are the uploaded snapshot values.[^27_1]
5. Open Staged Tiers and confirm `FRAGILE`, `OPERATIONAL`, `HARDENED`, and `OVEREXTENDED` appear.[^27_2]
6. Select a tier and confirm its fields populate.
7. Resize the window to its minimum size; check that all fields and buttons remain accessible.
8. Click Validate Draft and confirm success.
9. Click Cancel / Close, reopen through Actions, and confirm it opens again.
10. Close the staging window and Workbench without saving.

Reply **success**, or provide a screenshot and any error if controls are clipped, overlapping, or inaccessible.

Once this passes, we’ll update the Markdown manual to describe the coordinated workflow and remove the resolved defect warnings. Before the next source review, upload the changed modules and two new bundle modules so the Project files match your tested local installation.

<div align="center">⁂</div>

[^27_1]: source/metrics.csv

[^27_2]: source/metric_tiers.csv


---

# success

The coordinated editor’s visual check **passed**. We now have the service’s 10/10 sandbox checks, the window’s 9/9 behavioral checks, and your confirmation that the integrated menu and window work visually.

## Implementation checkpoint

| Component | Verified result |
| :-- | :-- |
| Metric Tiers layout | Corrected and visually checked |
| Recursive enum helper | Removed without changing the save path |
| Task Templates refresh | Unsaved-form preservation and deliberate selection/revert tested |
| Coordinated-save service | Creation, range changes, validation rejection, backups, and caught-failure rollback tested |
| Coordinated editor | Draft handling, save/cancel, validation, and project-root protection tested |
| Actions menu integration | Installed and visually checked |

The coordinated workflow retains complete tier coverage rather than weakening the validator’s rules.[^28_1]

## Return to the manual

Upload the current versions of these **six modules** to the Project, replacing their earlier copies where applicable:

```text
doda_content_gui.py
doda_metric_tiers_editor.py
doda_enum_catalog_editor.py
doda_task_templates_editor.py
doda_metric_bundle_service.py
doda_metric_bundle_editor.py
```

They are all in:

```text
E:\Dev\uzdoom_src\doda-core\tools\doda_content_workbench
```

No CSV re-upload is needed unless you changed authored data separately.

Once the updated source is available, we’ll revise Chapters 2–4 to:

- Add Actions > Edit Metric and Tiers….
- Explain form edits, applied draft tiers, validation, and coordinated saving.
- Provide new-metric and coordinated range-change procedures.
- Document transaction backups, locks, and recovery boundaries.
- Remove the resolved layout and recursive-helper warnings.
- Keep metric deletion limitations explicit—the new window does not provide metric deletion.

Then we’ll continue Chapter 5, Capabilities and Staffing. PDF compilation remains deferred until the Markdown manual is complete and reviewed.

<div align="center">⁂</div>

[^28_1]: doda_content_workbench/doda_content_workbench.py


---

# Before we continue, i'd like you to take a look at this. This is how the Department Tracks should be laid out, with their various progression elements in a tree.

DoDA_ProgressionTree.drawio.png

I can see that `DoDA_ProgressionTree.drawio.png` is uploaded, but the Project reader could not retrieve its image contents. I haven’t inspected the tree yet, so I should not guess its branches or progression elements.[^29_1]

Please **attach the PNG directly to your next message** rather than only storing it in the Project. If you have the original `.drawio` file, attach that too; it would help verify the exact node labels and connections.

## What we need to reconcile

The current Department Tracks CSV contains six flat category records: Evidence Handling, Field Operations, Intelligence and Analysis, Public Communication and Liaison, Internal Affairs and Ethics, and Technical Infrastructure. Its fields define identity, wording, order, and activity—not progression nodes or parent-child relationships.[^29_2]

Once the diagram is readable, I’ll compare:


| Diagram element | Question to resolve |
| :-- | :-- |
| Track roots | Do they match the current six categories? |
| Progression nodes | Are these facilities, capabilities, upgrades, or a separate content type? |
| Connections | Do they represent grouping, progression order, or unlock prerequisites? |
| Branches | Can users pursue multiple branches, or must they choose between them? |
| Levels and tiers | Are these the existing facility tiers or a different progression system? |
| Cross-track links | Does one track depend on progress in another? |

We should pause the affected manual sections until that comparison is complete. If the tree requires relationships the current schema cannot represent, documenting the flat Tracks editor as the full progression-authoring interface would be misleading.

Attach the diagram directly, and I’ll first produce an exact tree inventory and a current-schema gap analysis—before proposing code or CSV changes.

<div align="center">⁂</div>

[^29_1]: source/department_tracks.csv


---

# Files

DoDA_ProgressionTree.json

I found `DoDA_ProgressionTree.json`, but the Project reader is returning only its first two lines:

```json
{
  "version": "32.2.0",
```

That is not enough to inspect the tree’s nodes or connections, so I have not yet verified its structure.[^30_1]

## Make the contents accessible

Please attach the JSON directly to the conversation. If that still does not expose its contents, paste the JSON in a fenced code block:

````text
```json
...file contents...
```
````

You can split it across messages labeled **Part 1**, **Part 2**, and so on. Preserve the node IDs, parent IDs, and connection records; those are necessary to reconstruct the tree accurately.

## Review we’ll perform

Once the contents are readable, I’ll produce:


| Review item | Result |
| :-- | :-- |
| Track inventory | Exact root names and their correspondence to the current six tracks |
| Progression structure | Branches, nodes, levels, and connections |
| Relationship meaning | What is explicitly encoded versus what still needs clarification |
| Schema gaps | Which elements the current Workbench can represent and which require new fields or tables |
| Documentation impact | Which manual sections need revised concepts or procedures |

The current Tracks CSV represents six flat categories, with no parent-node or prerequisite fields. We should not change it—or describe it as a progression-tree editor—until we understand your intended structure.[^30_2]

<div align="center">⁂</div>

[^30_1]: DoDA_ProgressionTree.json

[^30_2]: source/department_tracks.csv


---

# {

"version": "32.2.0",
"data": "\<mxfile host="app.diagrams.net">\<diagram name="Page-1" id="9kQY978w7nLeNKkXzHlE">\<mxGraphModel dx="2283" dy="3155" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">\<root>\<mxCell id="0"/>\<mxCell id="1" parent="0"/>\<mxCell id="BAutZteO0cHRs6NIlrK\_-109" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-2" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-111">\<mxGeometry relative="1" as="geometry">\<mxPoint x="260.0000000000001" y="-300" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-110" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-2" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-112">\<mxGeometry relative="1" as="geometry">\<mxPoint x="260.0000000000001" y="-265.08333333333326" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-114" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-2" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-113">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-115" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-2" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-116">\<mxGeometry relative="1" as="geometry">\<mxPoint x="300" y="-210" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-2" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="FIELD OPERATIONS" vertex="1">\<mxGeometry height="60" width="120" x="40" y="-360" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-63" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-3" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-68">\<mxGeometry relative="1" as="geometry">\<mxPoint x="320" y="40" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-64" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-3" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-69">\<mxGeometry relative="1" as="geometry">\<mxPoint x="320" y="80" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-65" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-3" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-70">\<mxGeometry relative="1" as="geometry">\<mxPoint x="320" y="120" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-66" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-3" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-71">\<mxGeometry relative="1" as="geometry">\<mxPoint x="320" y="120" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-67" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-3" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-72">\<mxGeometry relative="1" as="geometry">\<mxPoint x="290" y="150" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-3" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="TECH INFRASTRUCTURE" vertex="1">\<mxGeometry height="60" width="120" x="70" y="-25" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-16" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-4" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-17">\<mxGeometry relative="1" as="geometry">\<mxPoint x="280" y="240" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-18" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-4" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-21">\<mxGeometry relative="1" as="geometry">\<mxPoint x="280" y="285" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-23" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-4" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-22">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-25" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-4" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-26">\<mxGeometry relative="1" as="geometry">\<mxPoint x="290" y="340" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-28" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-4" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-29">\<mxGeometry relative="1" as="geometry">\<mxPoint x="360" y="380" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-4" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="EVIDENCE HANDLING" vertex="1">\<mxGeometry height="60" width="120" x="70" y="270" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-30" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-6" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-31">\<mxGeometry relative="1" as="geometry">\<mxPoint x="290" y="410" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-32" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-6" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-33">\<mxGeometry relative="1" as="geometry">\<mxPoint x="360" y="460" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-34" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-6" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-35">\<mxGeometry relative="1" as="geometry">\<mxPoint x="340" y="510" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-36" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-6" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-37">\<mxGeometry relative="1" as="geometry">\<mxPoint x="340" y="560" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-6" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="INTELLIGENCE" vertex="1">\<mxGeometry height="60" width="120" x="70" y="470" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-58" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-7" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-47">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-59" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-7" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;entryX=0.067;entryY=0.48;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-48">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-60" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-7" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-50">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-61" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-7" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-53">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-62" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-7" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-56">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-7" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="PUBLIC RELATIONS" vertex="1">\<mxGeometry height="60" width="120" x="50" y="710" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-88" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-8" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-91">\<mxGeometry relative="1" as="geometry">\<mxPoint x="280" y="1290" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-89" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-8" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-92">\<mxGeometry relative="1" as="geometry">\<mxPoint x="340" y="1350" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-90" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-8" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-93">\<mxGeometry relative="1" as="geometry">\<mxPoint x="290" y="1380" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-94" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-8" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-95">\<mxGeometry relative="1" as="geometry">\<mxPoint x="340" y="1470" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-8" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="CONGRESSIONAL\<div>SUPPORT\</div>" vertex="1">\<mxGeometry height="60" width="120" x="80" y="1350" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-74" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-77">\<mxGeometry relative="1" as="geometry">\<mxPoint x="280" y="920" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-75" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-79">\<mxGeometry relative="1" as="geometry">\<mxPoint x="270" y="990" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-76" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-78">\<mxGeometry relative="1" as="geometry">\<mxPoint x="300" y="965" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-84" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-80">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-85" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-81">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-86" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-82">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-87" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-9" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-83">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-9" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="DEPARTMENT FUNDING" vertex="1">\<mxGeometry height="60" width="120" x="70" y="950" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-98" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-97">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-100" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-99">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-102" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=12;startSize=8;endSize=8;" target="BAutZteO0cHRs6NIlrK\_-101">\<mxGeometry relative="1" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-103" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.75;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-104">\<mxGeometry relative="1" as="geometry">\<mxPoint x="330" y="1690" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-105" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=1;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-106">\<mxGeometry relative="1" as="geometry">\<mxPoint x="350" y="1770" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-107" edge="1" parent="1" source="BAutZteO0cHRs6NIlrK\_-10" style="edgeStyle=none;curved=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.75;exitY=1;exitDx=0;exitDy=0;fontSize=12;startSize=8;endSize=8;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="BAutZteO0cHRs6NIlrK\_-108">\<mxGeometry relative="1" as="geometry">\<mxPoint x="350" y="1810" as="targetPoint"/>\</mxGeometry>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-10" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="SEIZED ASSETS" vertex="1">\<mxGeometry height="60" width="120" x="80" y="1610" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-17" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="PAPER RECORDS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="122" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-21" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="PHOTOGRAPHIC FORENSICS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="172" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-22" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="BIOLOGICAL FORENSICS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="222" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-26" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="AUDIO VIDEO FORENSICS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="272" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-29" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="DIGITAL FORENSICS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="322" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-31" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="CONFIDENTIAL INFORMANTS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="392" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-33" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="UNDERCOVER\<div>SURVEILLANCE\</div>" vertex="1">\<mxGeometry height="40" width="120" x="344" y="442" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-35" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="EMBEDDED AGENTS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="492" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-37" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="OCCULT RESEARCH" vertex="1">\<mxGeometry height="40" width="120" x="344" y="542" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-47" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="CIVILIAN" vertex="1">\<mxGeometry height="40" width="120" x="340" y="620" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-48" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="FEDERAL" vertex="1">\<mxGeometry height="40" width="120" x="340" y="670" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-50" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="PRESS" vertex="1">\<mxGeometry height="40" width="120" x="340" y="720" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-53" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="CRIMINAL" vertex="1">\<mxGeometry height="40" width="120" x="340" y="770" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-56" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="OCCULT" vertex="1">\<mxGeometry height="40" width="120" x="340" y="820" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-68" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="DATA PROCESSING" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-158" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-69" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="COMMUNICATIONS" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-103" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-70" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="INTERNET AND INTRANET" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-48" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-71" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="AUDIO AND VIDEO" vertex="1">\<mxGeometry height="40" width="120" x="344" y="2" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-72" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="DIGITAL ENCANTATION" vertex="1">\<mxGeometry height="40" width="120" x="344" y="52" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-77" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="STAFFING" vertex="1">\<mxGeometry height="40" width="120" x="340" y="900" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-78" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="TACTICAL GEAR" vertex="1">\<mxGeometry height="40" width="120" x="340" y="950" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-79" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="OFFICE AND LABORATORY" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1000" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-80" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="COLLATERAL RESTITUTION" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1050" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-81" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="PRINT AND ADVERTISING" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1100" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-82" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="RESEARCH AND EXPEDITIONS" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1150" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-83" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="BLACK BUDGET" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1200" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-91" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="LEGISLATION" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1290" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-92" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="GRANTED JURISDICTIONS" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1340" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-93" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="DIRECT FUNDING" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1390" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-95" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="SCIF COOPERATION" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1440" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-97" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="MONETARY" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1520" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-99" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="ILLEGAL NARCOTICS" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1570" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-101" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="LAND AND REAL ESTATE PROPERTY" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1620" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-104" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="MOTOR VEHICLES" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1670" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-106" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="WEAPONRY" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1720" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-108" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="OCCULT PARAPHENALIA" vertex="1">\<mxGeometry height="40" width="120" x="340" y="1770" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-111" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="SURVEILLANCE" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-438" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-112" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="RAID" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-380" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-113" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="INVESTIGATION" vertex="1">\<mxGeometry height="40" width="120" x="344" y="-324" as="geometry"/>\</mxCell>\<mxCell id="BAutZteO0cHRs6NIlrK\_-116" parent="1" style="rounded=1;whiteSpace=wrap;html=1;roundedPerimeter=1;" value="CONFIDENTIAL INFORMANT MEETING" vertex="1">\<mxGeometry height="50" width="120" x="344" y="-268" as="geometry"/>\</mxCell>\</root>\</mxGraphModel>\</diagram>\</mxfile>",

"pages": \[
{
"id": "9kQY978w7nLeNKkXzHlE",
"name": "Page-1",
"cells": \[
{
"id": "1",
"type": "layer"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-109",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-2",
"target": "BAutZteO0cHRs6NIlrK\_-111"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-110",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-2",
"target": "BAutZteO0cHRs6NIlrK\_-112"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-114",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-2",
"target": "BAutZteO0cHRs6NIlrK\_-113"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-115",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-2",
"target": "BAutZteO0cHRs6NIlrK\_-116"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-2",
"type": "node",
"parent": "1",
"label": "FIELD OPERATIONS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-63",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-3",
"target": "BAutZteO0cHRs6NIlrK\_-68"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-64",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-3",
"target": "BAutZteO0cHRs6NIlrK\_-69"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-65",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-3",
"target": "BAutZteO0cHRs6NIlrK\_-70"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-66",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-3",
"target": "BAutZteO0cHRs6NIlrK\_-71"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-67",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-3",
"target": "BAutZteO0cHRs6NIlrK\_-72"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-3",
"type": "node",
"parent": "1",
"label": "TECH INFRASTRUCTURE"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-16",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-4",
"target": "BAutZteO0cHRs6NIlrK\_-17"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-18",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-4",
"target": "BAutZteO0cHRs6NIlrK\_-21"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-23",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-4",
"target": "BAutZteO0cHRs6NIlrK\_-22"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-25",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-4",
"target": "BAutZteO0cHRs6NIlrK\_-26"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-28",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-4",
"target": "BAutZteO0cHRs6NIlrK\_-29"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-4",
"type": "node",
"parent": "1",
"label": "EVIDENCE HANDLING"
},

[stand-by for part 2]

Received Part 1. I’ll wait for Part 2 before analyzing the tree or proposing schema changes.

---

# {

"id": "BAutZteO0cHRs6NIlrK\_-30",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-6",
"target": "BAutZteO0cHRs6NIlrK\_-31"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-32",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-6",
"target": "BAutZteO0cHRs6NIlrK\_-33"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-34",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-6",
"target": "BAutZteO0cHRs6NIlrK\_-35"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-36",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-6",
"target": "BAutZteO0cHRs6NIlrK\_-37"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-6",
"type": "node",
"parent": "1",
"label": "INTELLIGENCE"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-58",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-7",
"target": "BAutZteO0cHRs6NIlrK\_-47"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-59",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-7",
"target": "BAutZteO0cHRs6NIlrK\_-48"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-60",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-7",
"target": "BAutZteO0cHRs6NIlrK\_-50"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-61",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-7",
"target": "BAutZteO0cHRs6NIlrK\_-53"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-62",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-7",
"target": "BAutZteO0cHRs6NIlrK\_-56"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-7",
"type": "node",
"parent": "1",
"label": "PUBLIC RELATIONS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-88",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-8",
"target": "BAutZteO0cHRs6NIlrK\_-91"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-89",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-8",
"target": "BAutZteO0cHRs6NIlrK\_-92"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-90",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-8",
"target": "BAutZteO0cHRs6NIlrK\_-93"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-94",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-8",
"target": "BAutZteO0cHRs6NIlrK\_-95"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-8",
"type": "node",
"parent": "1",
"label": "CONGRESSIONAL\\nSUPPORT",
"html": "CONGRESSIONAL\<div>SUPPORT\</div>"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-74",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-77"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-75",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-79"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-76",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-78"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-84",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-80"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-85",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-81"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-86",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-82"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-87",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-9",
"target": "BAutZteO0cHRs6NIlrK\_-83"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-9",
"type": "node",
"parent": "1",
"label": "DEPARTMENT FUNDING"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-98",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-97"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-100",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-99"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-102",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-101"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-103",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-104"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-105",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-106"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-107",
"type": "edge",
"parent": "1",
"source": "BAutZteO0cHRs6NIlrK\_-10",
"target": "BAutZteO0cHRs6NIlrK\_-108"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-10",
"type": "node",
"parent": "1",
"label": "SEIZED ASSETS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-17",
"type": "node",
"parent": "1",
"label": "PAPER RECORDS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-21",
"type": "node",
"parent": "1",
"label": "PHOTOGRAPHIC FORENSICS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-22",
"type": "node",
"parent": "1",
"label": "BIOLOGICAL FORENSICS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-26",
"type": "node",
"parent": "1",
"label": "AUDIO VIDEO FORENSICS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-29",
"type": "node",
"parent": "1",
"label": "DIGITAL FORENSICS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-31",
"type": "node",
"parent": "1",
"label": "CONFIDENTIAL INFORMANTS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-33",
"type": "node",
"parent": "1",
"label": "UNDERCOVER\\nSURVEILLANCE",
"html": "UNDERCOVER\<div>SURVEILLANCE\</div>"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-35",
"type": "node",
"parent": "1",
"label": "EMBEDDED AGENTS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-37",
"type": "node",
"parent": "1",
"label": "OCCULT RESEARCH"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-47",
"type": "node",
"parent": "1",
"label": "CIVILIAN"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-48",
"type": "node",
"parent": "1",
"label": "FEDERAL"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-50",
"type": "node",
"parent": "1",
"label": "PRESS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-53",
"type": "node",
"parent": "1",
"label": "CRIMINAL"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-56",
"type": "node",
"parent": "1",
"label": "OCCULT"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-68",
"type": "node",
"parent": "1",
"label": "DATA PROCESSING"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-69",
"type": "node",
"parent": "1",
"label": "COMMUNICATIONS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-70",
"type": "node",
"parent": "1",
"label": "INTERNET AND INTRANET"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-71",
"type": "node",
"parent": "1",
"label": "AUDIO AND VIDEO"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-72",
"type": "node",
"parent": "1",
"label": "DIGITAL ENCANTATION"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-77",
"type": "node",
"parent": "1",
"label": "STAFFING"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-78",
"type": "node",
"parent": "1",
"label": "TACTICAL GEAR"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-79",
"type": "node",
"parent": "1",
"label": "OFFICE AND LABORATORY"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-80",
"type": "node",
"parent": "1",
"label": "COLLATERAL RESTITUTION"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-81",
"type": "node",
"parent": "1",
"label": "PRINT AND ADVERTISING"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-82",
"type": "node",
"parent": "1",
"label": "RESEARCH AND EXPEDITIONS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-83",
"type": "node",
"parent": "1",
"label": "BLACK BUDGET"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-91",
"type": "node",
"parent": "1",
"label": "LEGISLATION"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-92",
"type": "node",
"parent": "1",
"label": "GRANTED JURISDICTIONS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-93",
"type": "node",
"parent": "1",
"label": "DIRECT FUNDING"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-95",
"type": "node",
"parent": "1",
"label": "SCIF COOPERATION"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-97",
"type": "node",
"parent": "1",
"label": "MONETARY"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-99",
"type": "node",
"parent": "1",
"label": "ILLEGAL NARCOTICS"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-101",
"type": "node",
"parent": "1",
"label": "LAND AND REAL ESTATE PROPERTY"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-104",
"type": "node",
"parent": "1",
"label": "MOTOR VEHICLES"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-106",
"type": "node",
"parent": "1",
"label": "WEAPONRY"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-108",
"type": "node",
"parent": "1",
"label": "OCCULT PARAPHENALIA"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-111",
"type": "node",
"parent": "1",
"label": "SURVEILLANCE"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-112",
"type": "node",
"parent": "1",
"label": "RAID"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-113",
"type": "node",
"parent": "1",
"label": "INVESTIGATION"
},
{
"id": "BAutZteO0cHRs6NIlrK\_-116",
"type": "node",
"parent": "1",
"label": "CONFIDENTIAL INFORMANT MEETING"
}
\]

}
\]

}

I can now read the complete diagram from your two pasted parts. It shows **eight Department Track roots with 40 child elements and 40 track-to-child connections**—48 labeled nodes altogether. This is a different structure from the six flat track categories currently authored in the Workbench.

The important distinction is that the diagram encodes **grouping**, but does not yet encode child-to-child progression, unlock requirements, costs, levels, or effects. We should represent the tree faithfully without inventing those rules.

## Exact tree inventory

The following names preserve your diagram’s wording, including “Digital Encantation” and “Occult Paraphenalia.”


| Department Track | Children | Elements |
| :-- | --: | :-- |
| Field Operations | 4 | Surveillance; Raid; Investigation; Confidential Informant Meeting |
| Tech Infrastructure | 5 | Data Processing; Communications; Internet and Intranet; Audio and Video; Digital Encantation |
| Evidence Handling | 5 | Paper Records; Photographic Forensics; Biological Forensics; Audio Video Forensics; Digital Forensics |
| Intelligence | 4 | Confidential Informants; Undercover Surveillance; Embedded Agents; Occult Research |
| Public Relations | 5 | Civilian; Federal; Press; Criminal; Occult |
| Department Funding | 7 | Staffing; Tactical Gear; Office and Laboratory; Collateral Restitution; Print and Advertising; Research and Expeditions; Black Budget |
| Congressional Support | 4 | Legislation; Granted Jurisdictions; Direct Funding; SCIF Cooperation |
| Seized Assets | 6 | Monetary; Illegal Narcotics; Land and Real Estate Property; Motor Vehicles; Weaponry; Occult Paraphenalia |
| Total | 40 | Eight roots and 40 child elements |

These counts exclude diagram layers, geometry, and edge objects. They also avoid double-counting the same diagram represented both in the embedded XML and in `pages[].cells`.

All the supplied child nodes connect directly to a track root. There are no encoded connections between child elements or between tracks.

## Differences from current data

The current CSV defines Evidence Handling, Field Operations, Intelligence and Analysis, Public Communication and Liaison, Internal Affairs and Ethics, and Technical Infrastructure.[^32_1]


| Intended diagram track | Current counterpart | Reconciliation needed |
| :-- | :-- | :-- |
| Field Operations | `FIELD_OPERATIONS` | Existing category matches |
| Tech Infrastructure | `TECHNICAL_INFRASTRUCTURE` | Decide whether to change only its display name |
| Evidence Handling | `EVIDENCE_HANDLING` | Existing category matches |
| Intelligence | `INTELLIGENCE` — Intelligence and Analysis | Confirm intended display name and scope |
| Public Relations | `PUBLIC_COMMUNICATION` — Public Communication and Liaison | Confirm whether this is the same category or a replacement |
| Department Funding | None in Tracks CSV | New track |
| Congressional Support | None in Tracks CSV | New track |
| Seized Assets | None in Tracks CSV | New track |
| Not shown in diagram | `INTERNAL_AFFAIRS` — Internal Affairs and Ethics | Decide whether to retain it separately, replace it, or retire it |

We should not simply delete Internal Affairs to match the drawing. The current `OVERSIGHT_WING` facility references that track, so migration must account for that relationship.[^32_2]

Likewise, stable IDs need not change merely because a display name changes.

## What the diagram establishes

There are two technical details worth separating from gameplay meaning:

- Every node’s `"parent": "1"` refers to the diagram layer. It is not its Department Track parent.
- The track-to-element relationships come from each edge’s `source` and `target`.

For example, the diagram explicitly groups **Digital Forensics under Evidence Handling**. It does not say that Digital Forensics requires Paper Records, Biological Forensics, or any other sibling.

Similarly, “Staffing” appears under Department Funding. That does not automatically make it the same thing as the Workbench’s qualification-based contributor rules.

The children also appear to cover different concepts: operations, technical disciplines, relationship groups, budget categories, authorities, and asset categories. That is a reason not to force all 40 into the existing Capabilities table without defining their intended roles.

## Recommended Workbench structure

I recommend separating the intended hierarchy from operational implementation:


| Layer | Purpose | Proposed treatment |
| :-- | :-- | :-- |
| Department Track | Root category | Retain the track catalog, reconciled to your intended roots |
| Track element | Child shown in this diagram | Add a dedicated element catalog associated with a track |
| Progression definition | Levels, prerequisites, costs, and benefits | Add only after those rules are specified |
| Operational linkage | Connection to facilities, capabilities, tasks, or other systems | Explicit references where appropriate—not inferred from names |
| Tree interface | Navigate and edit the hierarchy | Track roots expanded into their associated elements |

A minimal proposed element table could begin with:

```csv
track_element_id,track_id,display_name,description,sort_order,active
```

That would represent the current two-level diagram. It is a proposal, not an implemented schema. If you intend deeper nesting, shared elements, or prerequisite networks, we should design those relationships before choosing the final fields.

The manual should then distinguish **Department Tracks and their progression elements** from facilities, installed capabilities, and staffing rules. Those concepts may connect, but they are not interchangeable.

## Decision before implementation

This diagram is sufficient to establish the intended grouping, but not the progression mechanics.

**Are the 40 children independently developable branches, each with its own levels or upgrades, or are they individual unlockable items?**

That answer determines whether the Workbench needs a branch-and-level editor, an unlock-node editor, or both. We should settle it before migrating the current CSVs or continuing the affected manual chapters.

<div align="center">⁂</div>

[^32_1]: source/department_tracks.csv

[^32_2]: source/facilities.csv


---

# \<q>Are the 40 children independently developable branches, each with its own levels or upgrades, or are they individual unlockable items?\</q> They are a combination of developable branches each with their own levels and upgrades, unlockable when certain criteria are met. For instance, upgrading Communications leads to Internet and Intranet, upgrading that eventually leads to Digital Encantations, etc. Seized assets start out as just monetary, then through upgrading / getting points in Congressional Support > Legislation, the player can convert other seized assets like Real Estate and Weaponry into Department Funding (player currency)

That clarifies the model: Department Tracks contain upgradeable branches, and progression within those branches can unlock other branches or grant permissions across tracks. We need both a **hierarchy** for organizing content and a separate dependency system for expressing unlock rules.

Your examples also establish that Seized Assets progression governs which assets can be converted into Department Funding—the player currency—not merely which asset categories exist.

## Confirmed design intent

| Area | What you’ve established | Not yet specified |
| :-- | :-- | :-- |
| Technical progression | Communications upgrades lead to Internet and Intranet, which eventually leads to Digital Encantations | Required levels, points, costs, and additional conditions |
| Starting asset access | Seized Assets starts with Monetary | Whether other assets can be collected before conversion is authorized |
| Cross-track progression | Congressional Support > Legislation upgrades or points enable conversion of additional seized asset types | Thresholds and which authorization each upgrade grants |
| Conversion outcome | Assets such as Real Estate and Weaponry can become Department Funding | Conversion values, delays, fees, and repeatability |

We should preserve these as confirmed relationships without inventing numerical thresholds.

## Two different structures

The Workbench should distinguish where an element belongs from what unlocks it.

For your technical example:

```text
Department Track: Tech Infrastructure

Branches:
  Communications
  Internet and Intranet
  Digital Encantations

Unlock relationships:
  Communications [required progression]
      → Internet and Intranet

  Internet and Intranet [required progression]
      → Digital Encantations
```

Internet and Intranet can remain a child of Tech Infrastructure even though Communications is its prerequisite. A single `parent_id` cannot adequately express both relationships.

The same distinction matters across tracks:

```text
Congressional Support
  Legislation [required progression]
      → Permission to convert Real Estate

Seized Assets
  Real Estate
      → Conversion produces Department Funding
```

Legislation grants the permission; it does not need to become the organizational parent of Real Estate.

## Proposed authoring model

I recommend separating the definitions into these responsibilities. These are proposed additions, not existing Workbench features.


| Definition | Purpose |
| :-- | :-- |
| Tracks | The top-level categories |
| Branches | The 40 elements grouped under those tracks |
| Branch levels or upgrades | Each branch’s developable stages, costs, and descriptions |
| Requirements | Conditions for unlocking a branch, purchasing an upgrade, or using an action |
| Effects and permissions | What an upgrade grants or changes |
| Asset conversion rules | Which asset type converts into currency, under which permission, and at what value |

Requirements should identify the action they govern. “Unlock this branch,” “buy its next upgrade,” and “convert this asset” are different gates.

For example, an asset might exist in inventory while its conversion action remains locked. Your explanation does not yet establish whether that is allowed, so the schema should not silently equate possession with conversion permission.

We should also distinguish:

- Accumulated progression points from points spent on upgrades.
- Department Funding as a track from Department Funding as a currency balance.
- Authored starting values from the player’s current progression.
- A permission being unlocked from it being exercised.

The current Tracks schema only stores category identity, wording, order, and activity; it has no branch-level or unlock-rule definitions. This therefore requires a schema expansion, not just a tree-shaped view of the existing CSV.[^33_1][^33_2]

## Workbench presentation

A suitable interface would provide:

- A track-and-branch tree for navigation.
- A level/upgrade list for the selected branch.
- A requirements panel showing prerequisites, including cross-track references.
- An effects panel showing granted permissions or other outcomes.
- An asset-conversion editor linking asset types, permissions, and currency.
- A dependency view separate from the organizational tree.

Validation should check references, duplicate levels, malformed thresholds, and unintended prerequisite cycles. It should not assume sibling order in the drawing is an unlock sequence.

We can retain the existing facilities, capabilities, staffing, and task systems, then add explicit links where progression affects them. We should not convert every branch into an operational capability automatically.

## Next design step

Before another code patch, we should write a progression specification using your two examples as acceptance cases:

1. Communications progression unlocks Internet and Intranet.
2. Internet and Intranet progression unlocks Digital Encantations.
3. Monetary conversion is available initially.
4. Legislation progression authorizes specified additional asset conversions.
5. Authorized conversion credits the Department Funding currency.

Unknown thresholds and economic values should remain marked **TBD**, not filled with guessed numbers. We should also reconcile the intended eight tracks with the current six before migrating existing references.

One important rule to settle first: **once Legislation unlocks an asset-conversion permission, is that permission permanent, or can it be lost if Congressional Support later falls?**

<div align="center">⁂</div>

[^33_1]: doda_content_workbench/doda_content_workbench.py

[^33_2]: source/department_tracks.csv


---

# \<q>One important rule to settle first: once Legislation unlocks an asset-conversion permission, is that permission permanent, or can it be lost if Congressional Support later falls?\</q> I did not consider this, but it is a good question - the permission can be lost if Congressional Support falls.

Then asset-conversion permission is **conditional**, not a permanent unlock. We should record your rule as: a qualifying Legislation upgrade grants eligibility, but the player must also maintain the required Congressional Support to use that permission.

The distinction matters: losing authorization does not necessarily mean losing the upgrade that originally enabled it.

## Separate progress from authorization

I recommend modeling these as separate states:


| State | Meaning |
| :-- | :-- |
| Acquired progression | The player has earned or purchased the relevant Legislation upgrade |
| Current Congressional Support | A changing value used to assess continuing authorization |
| Effective permission | Whether the conversion action is allowed now |

A proposed rule would be:

```text
Real Estate conversion is available when:

    Required Legislation progression has been acquired
    AND
    Current Congressional Support meets the required threshold
```

Weaponry could have its own requirements and threshold. Neither numerical thresholds nor their relative difficulty have been established yet.

This avoids a one-time check that permanently marks the conversion action as unlocked.

## Recommended loss behavior

Your confirmed rule is that permission can be lost when support falls. For the surrounding behavior, I recommend the following defaults—but these remain proposals:


| Situation | Proposed behavior |
| :-- | :-- |
| Support falls below the requirement | Suspend affected conversion actions |
| Player retains seized assets | Keep them in inventory; do not automatically confiscate or delete them |
| Conversion completed before support fell | Preserve the resulting Department Funding |
| Support later recovers | Restore permission if the Legislation prerequisite is still satisfied |
| Player starts a conversion | Check current authorization before consuming the asset or granting currency |

For example, the player could hold seized real estate but see:

```text
Real Estate Conversion — Suspended

Legislation requirement: Met
Congressional Support requirement: Not met
```

This communicates why an acquired feature is temporarily unavailable without implying that the player’s investment disappeared.

If conversions take time rather than completing immediately, we will also need an explicit rule for transactions already in progress when support falls.

## Workbench implications

The proposed requirements editor should distinguish two purposes:

- **Acquisition requirements:** what must be true to obtain a branch or upgrade.
- **Ongoing requirements:** what must remain true to exercise its effects or permissions.

A conversion definition would reference its asset type, output currency, progression prerequisite, and ongoing authorization conditions. The Workbench would author those rules; the eventual runtime would evaluate them against player state.

We also need a definition for the Congressional Support value itself. The reviewed metric catalog currently contains Preparedness, Intelligence Quality, Public Trust, Corruption Pressure, and Staff Stress—not Congressional Support. We should not silently substitute Public Trust or assume that a track’s earned upgrade points are its current support value.[^34_1]

## Decision to record

We can now add this confirmed requirement to the progression specification:

> Asset-conversion permissions dependent on Congressional Support must be revocable when current support no longer satisfies their requirements.

The next distinction to settle is: **when support recovers, should the permission return automatically, without repurchasing the Legislation upgrade?** I recommend automatic restoration while preserving acquired progression.

<div align="center">⁂</div>

[^34_1]: source/metrics.csv


---

# Yes, permission should return automatically, a sort of enabled / disabled state.

I also want to make clear that the different progression tiers do not replace older tiers - for instance, communications is not replaced by internet and intranet - it is enhanced, allowing for new capabilities in the communications tier, like development of internet-connected pre-smart phone PDAs and faster data processing / transfer bandwidth.

Understood. We now have two explicit design rules: permissions can switch between enabled and disabled without repurchasing the prerequisite upgrade, and progression is **additive**—new branches enhance earlier branches rather than replacing them.

That means the progression model needs to track acquired development separately from currently usable permissions and capabilities.

## Confirmed progression rules

| Rule | Meaning |
| :-- | :-- |
| Conditional permission | A qualifying upgrade does not guarantee that its permission is always usable |
| Automatic restoration | When Congressional Support satisfies the requirement again, the conversion permission returns automatically |
| Non-replacing progression | Developing Internet and Intranet does not remove Communications |
| Enhancement across branches | Internet and Intranet can make new Communications developments available |
| Continuing development | Earlier branches remain relevant and can gain further capabilities as related branches advance |

The last two points are especially important: Communications is not merely a prerequisite that becomes obsolete after unlocking Internet and Intranet.

## Communications example

Your example implies relationships in both directions, serving different purposes:

```text
Communications progression
    → unlocks Internet and Intranet

Internet and Intranet progression
    → enables additional Communications developments
        • Internet-connected pre-smartphone PDAs
        • Faster data processing / transfer bandwidth

Further Internet and Intranet progression
    → unlocks Digital Encantations
```

These are not replacements:

```text
Communications → deleted
Internet and Intranet → substituted
```

They are additions to the Department’s accumulated capabilities.

We should keep development of a capability distinct from availability of that development. For example, reaching an Internet and Intranet requirement might make PDA development eligible; it should not automatically mean the PDA development has been purchased or completed unless its effect explicitly says so.

## Avoid false dependency cycles

The branch-level picture can appear circular:

```text
Communications → Internet and Intranet → Communications enhancement
```

But the actual upgrade dependencies can still be valid:

```text
Communications: foundational upgrade
    → Internet and Intranet: qualifying upgrade
        → Communications: networked-PDA upgrade
```

Therefore, prerequisites should reference specific upgrades, levels, or thresholds—not just entire branches. Otherwise, a validator could mistake an intended enhancement relationship for an impossible cycle.

The current Workbench’s metric tiers are numeric status bands, with complete range coverage. Those are a different concept from these additive progression levels; we should not reuse metric-tier behavior for the progression system.[^35_1]

## Permission state model

For asset conversion, the intended behavior is now:


| Acquired prerequisite | Current support requirement | Conversion state |
| :-- | :-- | :-- |
| Not met | Met or not met | Locked by progression |
| Met | Not met | Disabled by current support |
| Met | Met | Enabled |
| Met; support recovers | Met again | Automatically re-enabled |

This does not yet determine whether technical capabilities also have ongoing operational conditions. The Congressional Support rule should apply where explicitly authored, not automatically to every upgrade.

Also, an authored record’s `active` checkbox must remain separate from this runtime enabled/disabled state. “Included in the content catalog” and “usable by the player right now” are different meanings.

## Specification direction

The progression specification should now distinguish:

- Organizational membership: which track contains a branch.
- Acquisition prerequisites: what permits a particular upgrade to be developed.
- Acquired progress: what the player has already developed.
- Additive effects: capabilities or improvements contributed by that development.
- Ongoing conditions: what must remain true for a permission or effect to operate.
- Effective availability: the resulting enabled, disabled, or locked state.

Next, we should capture these confirmed rules in a Markdown progression specification, including the Communications and asset-conversion examples. Numerical thresholds, costs, effect magnitudes, and treatment of in-progress conversions can remain explicitly unresolved. That gives us a stable design document before expanding the CSV schemas or changing the manual further.

<div align="center">⁂</div>

[^35_1]: doda_content_workbench/doda_content_workbench.py


---

# Right, we should have an "unlocked by" field that allows for multiple selections, as well as a point value criteria, for instance, Congressional Support > Legislation point count must be X and Audio / Video > Video Surveillance must be Y to unlock this tier, etc.

Yes—**Unlocked by** should support multiple prerequisite selections, with a separate point threshold for each one. Your example means the target tier becomes eligible only when Legislation has at least $X$ points **and** Video Surveillance has at least $Y$ points.

A single point-value field for the entire selection would be insufficient: each prerequisite can require a different value.

## Proposed editor control

Rather than a plain multi-select dropdown, use an editable requirements list:


| Prerequisite | Point measure | Minimum required | Check timing |
| :-- | :-- | --: | :-- |
| Congressional Support > Legislation | To be specified | $X$ | Acquisition, ongoing, or both |
| Tech Infrastructure > Audio and Video > Video Surveillance | To be specified | $Y$ | Acquisition, ongoing, or both |

Controls would include:

- Add prerequisite: choose a node from the progression tree.
- Set its minimum point requirement.
- Choose when the requirement applies.
- Edit or remove a requirement.
- Show the complete path so similarly named nodes are distinguishable.

“Video Surveillance” adds another level beneath Audio and Video in your example. The model should therefore support deeper nesting, not assume every branch is directly beneath a track.

## Combining requirements

For the example you gave, the rule is:

```text
Eligible to develop the target tier =
    Legislation points >= X
    AND
    Video Surveillance points >= Y
```

I recommend **All requirements** as the default. We can also provide **Any requirement** where a designer deliberately wants alternative unlock paths.

Eligibility should remain distinct from acquisition: satisfying prerequisites allows development, but does not automatically purchase or complete it unless that behavior is explicitly authored.

## Unlocking versus remaining enabled

To preserve your Congressional Support rule, the editor should distinguish:


| Requirement timing | Behavior |
| :-- | :-- |
| Acquisition only | Must be satisfied when developing the upgrade |
| Ongoing only | Must remain satisfied for the acquired permission or effect to operate |
| Both | Required for acquisition and continued operation |

An acquired upgrade stays acquired when an ongoing condition fails. Its affected permission becomes disabled and returns automatically when the condition is satisfied again.

We should not automatically make every technical prerequisite ongoing. For example, whether a developed PDA capability remains usable after a related point value falls is a separate authored decision.

## Proposed data representation

Keep the GUI label “Unlocked by,” but store one structured row per requirement rather than a comma-separated list of names.

An illustrative schema is:

```csv
requirement_id,target_node_id,source_node_id,point_measure,minimum_points,check_timing
```

The target definition could separately specify whether its requirements use `ALL` or `ANY`. Stable node IDs would preserve references when display names change.

This is a proposed schema expansion. The current Department Tracks definition has no progression prerequisites or point-threshold fields.[^36_1]

Validation should check that referenced nodes exist, thresholds are valid, requirement rows are not duplicated, and acquisition dependencies do not create impossible cycles. Organizational parent-child links must remain separate from those prerequisite links.

## Define what points mean

Before implementing the fields, we need to distinguish **earned progression** from **current support** and **spendable points**. Otherwise, spending points on an upgrade could accidentally disable a permission intended to depend on accumulated development.

For your Legislation example, should $X$ mean **cumulative points invested in Legislation**, with a separate ongoing Congressional Support threshold—or a **current Legislation point value that can itself rise and fall**?

<div align="center">⁂</div>

[^36_1]: doda_content_workbench/doda_content_workbench.py


---

# \<q>For your Legislation example, should X mean cumulative points invested in Legislation, with a separate ongoing Congressional Support threshold—or a current Legislation point value that can itself rise and fall?\</q> The unlockable tier, feature, capability, etc should have a variable for this, as well as whether or not it is bound to the current point value or the point value at time of purchase (therefore is not deactivated when points are below threshold).

In other words, yes, some criteria should be based on total cumulative points versus current point value.

Understood. Each unlockable should support multiple requirements, and **each requirement** should independently specify both which point value it measures and whether it is checked only at acquisition or continuously afterward.

Those are two separate settings. This allows one feature to depend on cumulative development in one branch while remaining conditional on current support in another.

## Two independent settings

| Setting | Options | Meaning |
| :-- | :-- | :-- |
| Point basis | Current value; cumulative total | Which value is compared with the threshold |
| Evaluation timing | Acquisition only; ongoing only; acquisition and ongoing | When that comparison must succeed |

“Value at time of purchase” is an acquisition-time check, not a third point basis. At purchase, the system checks the selected current or cumulative value and records that the acquisition requirement passed.

For acquisition-only requirements, later decreases do not deactivate the acquired feature. Other ongoing requirements on that same feature can still disable it.

## Mixed-requirement example

For an illustrative asset-conversion permission:


| Requirement | Point basis | Threshold | Evaluation timing |
| :-- | :-- | :-- | :-- |
| Congressional Support > Legislation | Cumulative total | $X$ | Acquisition only |
| Audio and Video > Video Surveillance | Current value | $Y$ | Acquisition and ongoing |

With **All requirements** selected:

1. Both conditions must pass when the permission is acquired.
2. The Legislation acquisition check remains satisfied afterward.
3. Video Surveillance continues to be checked.
4. If its current value falls below $Y$, the permission is disabled—not deleted.
5. When that value returns to $Y$ or above, the permission automatically re-enables.

The thresholds and associations here are illustrative, not finalized balancing values.

## Proposed requirement fields

The earlier schema can be refined to:

```csv
requirement_id,target_node_id,source_node_id,point_basis,minimum_points,evaluation_timing
```

Suggested controlled values:


| Field | Proposed values |
| :-- | :-- |
| `point_basis` | `CURRENT`, `CUMULATIVE` |
| `evaluation_timing` | `ACQUISITION_ONLY`, `ONGOING_ONLY`, `ACQUISITION_AND_ONGOING` |

The target node would specify `ALL` or `ANY` separately for acquisition and ongoing requirements, so the combination rules remain explicit.

The Workbench’s **Unlocked by** panel should show these settings as editable rows, not hide them behind one global checkbox. These fields are proposed additions; the current Tracks schema does not implement them.[^37_1]

## Runtime state distinction

The eventual runtime needs to distinguish:

- Acquired upgrades and capabilities.
- Current source-point values.
- Cumulative source-point totals.
- Acquisition-time requirement results.
- Present enabled/disabled state and its reasons.

The Workbench authors the definitions. Player-specific purchase records and changing point values belong in runtime/save data—not the source CSVs.

If a purchase itself consumes points, the acquisition check should use the value **before deduction**. Whether that deduction then affects an ongoing requirement must be explicitly defined; acquisition eligibility and purchase cost should not be silently conflated.

## One definition still needed

We now have the configuration model, but “cumulative” needs a precise accounting definition. **Does cumulative total mean all points ever earned in that branch, or all points invested/spent on developing it?** Those can diverge, so we should name the counter accordingly rather than treat them as interchangeable.

<div align="center">⁂</div>

[^37_1]: doda_content_workbench/doda_content_workbench.py


---

# \<q>Does cumulative total mean all points ever earned in that branch, or all points invested/spent on developing it?\</q> This should also be optional criteria, as it can vary from category to category. For instance, total criminals apprehended or cases closed does not change and thus is cumulative, however Public Relations rises and falls constantly based directly on the player's actions. Department Funding is something that rises and falls constantly, but, Evidence Handling does not, as Evidence is not "spent" and does not "disappear" when invested into a department track

Yes—the accounting method should also be configurable by category, and each unlock requirement should select the appropriate counter. **Cumulative** must not automatically mean “spent”: achievements, retained evidence, available funding, and fluctuating reputation have different behaviors.

## Category accounting

Your examples establish these distinctions:


| Category or measure | Behavior in your design | Effect of investment or use |
| :-- | :-- | :-- |
| Total criminals apprehended | Cumulative achievement count; does not decrease | Checking it does not consume achievements |
| Total cases closed | Cumulative achievement count; does not decrease | Checking it does not consume closed cases |
| Public Relations | Current standing rises and falls with player actions | Changes reflect actions, not necessarily spending |
| Department Funding | Current funding rises and falls | Any expenditure should be defined separately |
| Evidence Handling | Retained, non-consumable evidence/progression | Investing evidence does not remove or spend it |

Evidence Handling, Public Relations, and Department Funding are already distinct tracks in `DoDA_ProgressionTree.json`; these accounting rules would define how their associated values behave, rather than change their organizational placement.[^38_1]

## Selectable requirement measures

Instead of the earlier two-value `CURRENT / CUMULATIVE` field, the proposed requirement editor should offer explicitly named measures where applicable:


| Measure | What it checks |
| :-- | :-- |
| Current value | Present standing, balance, or retained quantity |
| Lifetime earned or collected | Total accumulated receipts or collection |
| Lifetime achievement count | Total qualifying events, such as apprehensions or closed cases |
| Total invested | Amount credited toward development in a specified track |
| Total spent | Amount actually consumed through expenditure |

**Invested** and spent must remain separate. Evidence can contribute to development without being deducted from the evidence total.

Each category should declare which measures it supports. The editor should not offer “Total spent” for evidence or apprehension counts unless a deliberately authored mechanic makes that meaningful.

## Three separate decisions

For each requirement, the design now needs three independent decisions:

1. **Measure:** Which counter is checked?
2. Threshold: What minimum value is required?
3. Evaluation timing: Is the check acquisition-only, ongoing-only, or both?

Consumption belongs to a separate cost or investment rule—not to the prerequisite itself.

For example, a feature could require:

```text
Cases closed: lifetime achievement count >= X
    Acquisition only

Public Relations: current standing >= Y
    Acquisition and ongoing

Evidence Handling: total invested >= Z
    Acquisition only
    Evidence is not consumed by investment
```

After acquisition, declining Public Relations could disable that feature. Its completed-case and evidence-investment qualifications remain satisfied. Restoring Public Relations automatically restores availability, without repurchasing.

## Revised specification direction

The proposed data model should therefore separate:

- Category definitions: supported counters and their accounting behavior.
- Requirement definitions: source counter, threshold, and evaluation timing.
- Cost/investment definitions: what is deducted, retained, or credited toward development.
- Runtime records: accumulated totals, current values, acquired features, and acquisition-time qualifications.

For retained evidence, we should record investment credits explicitly rather than repeatedly add the same evidence to a counter whenever a requirement is checked. Whether the same evidence may contribute to several tracks is a separate allocation rule; non-consumption alone does not decide that.

This removes the need to choose one universal meaning of points. Each category defines its accounting, and each tier, feature, or capability chooses which supported measure governs its unlock and continued availability.

<div align="center">⁂</div>

[^38_1]: DoDA_ProgressionTree.json


---

# Does this clash with the other design or coding patterns of the Content Workbench? Do both combine or work together or do we need to do some replacement / refactoring?

They can work together. The new progression design fits the Content Workbench’s CSV-based, ID-linked authoring approach, but it needs **extensions** and targeted refactoring—not a replacement of the Workbench. The main incompatibility would come from trying to treat existing metric tiers as progression unlocks.[^39_1][^39_2]

I checked the validator, Metrics and Tracks editors, Metric Tiers editor, and exporter. This is a source-level assessment; I have not run the application or tests.

## What already fits

| Existing pattern | How the proposed design fits |
| :-- | :-- |
| CSV catalogs with stable IDs | Categories, counters, upgrades, and requirements can follow the same pattern |
| Separate relationship tables | Multiple prerequisites fit the existing approach used by facility-capability and staffing relationships |
| Central validation | Reference checks, threshold checks, and accounting rules can be added to the validator |
| Isolated candidate validation | Progression edits can be validated before replacing source files |
| Backups and atomic file replacement | These safeguards should remain |
| Validated JSON and PK3 export | New definitions can use the same pipeline |

The validator already defines catalogs and relationship tables through `TABLE_SPECS`, while the editors validate candidate data and create backups before replacing source CSVs. Those are useful foundations for this work.[^39_3][^39_4][^39_1]

**Multiple requirements** should therefore be stored as related rows, not as a comma-separated list inside an “Unlocked by” cell. The UI can present them as a multi-selection requirements panel while retaining structured storage underneath.

## Where concepts must stay separate

### Metric tiers versus progression upgrades

Existing `metric_tiers` are numeric status bands. Their validator requires complete coverage of the metric’s range, without gaps or overlaps. The editor explicitly enforces that model.[^39_2][^39_1]

Progression upgrades behave differently:


| Metric status band | Progression upgrade |
| :-- | :-- |
| Describes the current numeric value | Describes an acquired development |
| Covers a defined range | Requires one or more qualifying conditions |
| Changes as the value changes | Remains acquired after purchase |
| Must form contiguous, non-overlapping ranges | Can coexist with other acquired upgrades |

**Keep both.** Public Relations could have a current status band and also serve as an ongoing prerequisite for an acquired permission. Neither system needs to replace the other.

### Content active versus gameplay enabled

The existing catalogs contain authored `active` fields, and validators use active records when checking several relationships.[^39_1]

Those fields must not become the player’s temporary enabled/disabled state. Otherwise, declining Congressional Support could effectively remove an authored capability from the catalog rather than suspend its permission.

### Capability definition versus availability

The existing schema separates capabilities, facility installations, staffing rules, and task templates.[^39_1]

Progression should add another qualification layer, not replace those relationships. A proposed runtime availability check could consider:

```text
Capability is defined and available in content
AND required installation exists
AND required progression has been acquired
AND ongoing progression conditions pass
AND applicable operational conditions pass
```

That is a proposed integration rule—not behavior already implemented by these authoring files.

## Targeted refactoring needed

There are three concrete coding issues worth addressing before adding more editors.

1. **Centralize the table registry.** The validator has `TABLE_SPECS`, the exporter has `TABLE_FILES`, and the inspected editors each repeat a `FILES` list. Adding progression tables only to the validator would leave candidate-validation copies and exports incomplete. A shared registry would prevent those lists from drifting.[^39_4][^39_5][^39_3][^39_1]
2. **Centralize field definitions and serialization.** Editors write only the columns listed in their local `FIELDS` tuples. Adding accounting columns to an existing CSV without updating its editor could cause those columns to disappear on the next save. Schema changes must update readers, forms, writers, validation, and export together.[^39_3][^39_4]
3. **Remove duplicated enum restrictions.** The Metrics editor populates choices from `enum_catalog.csv`, but its form validation still hard-codes polarity choices and permits only `TIERED_BAR` as a display mode. That needs refactoring if we introduce additional counter-display modes.[^39_3]

These are localized improvements to the existing framework, not reasons to rewrite it.

## Recommended model changes

I recommend adding a progression layer with clearly separated responsibilities:


| Definition | Responsibility |
| :-- | :-- |
| Counter/accounting definitions | Identify current, earned, achievement, invested, or spent measures and their behavior |
| Progression nodes | Define branches and acquired developments |
| Requirement rows | Reference a specific counter or acquired prerequisite, threshold, and evaluation timing |
| Effect relationships | Connect developments to existing capabilities or enhancements |
| Cost/investment rules | Specify deductions and retained investment credits separately from eligibility |

Existing bounded metrics can remain suitable for fluctuating values such as Public Relations. However, the present metric schema requires integer minimums and maximums, and every metric must have status-tier coverage. Forcing lifetime apprehension or case totals into that model would impose unnecessary limits and display requirements. Either introduce a separate counter catalog or explicitly generalize metrics to support counters without mandatory status bands. My preference is a linked counter catalog that preserves existing metric behavior.[^39_1]

Also, requirement sources should reference a **specific counter**, not merely a track. “Department Funding” alone does not identify whether a rule checks available funds, lifetime receipts, or total expenditure.

## Implementation boundary and order

The inspected exporter reports schema version 2 and packages data without activating runtime behavior; its manifest explicitly marks the native loader as unavailable. Authoring the rules therefore does not yet implement automatic disabling, restoration, acquisition snapshots, or save-state accounting in the game.[^39_5]

The safest sequence is:

1. Document the accounting and progression contract.
2. Refactor shared table/field metadata and candidate validation.
3. Add the new tables, validators, and requirements editor.
4. Extend export with a schema-version change and compatibility handling.
5. Implement runtime evaluation and persistence separately.
6. Test mixed criteria, non-consumed evidence, permanent acquisition, and automatic permission restoration.

**Bottom line:** preserve the Workbench’s catalogs, metrics, status tiers, capabilities, and safe authoring pipeline. Add progression as a connected layer, and refactor duplicated schema plumbing before expanding it.

<div align="center">⁂</div>

[^39_1]: doda_content_workbench/doda_content_workbench.py

[^39_2]: doda_content_workbench/doda_metric_tiers_editor.py

[^39_3]: doda_content_workbench/doda_metrics_editor.py

[^39_4]: doda_content_workbench/doda_track_editor.py

[^39_5]: doda_content_workbench/doda_content_export.py


---

# Okay, good. I felt like this was the missing layer to tie the everything else together. The other missing layer is the personnel stats (HP, skill levels, abilities, expertise, etc).

Yes—progression provides the Department-level development layer, while personnel stats provide the individual-level layer: who can perform the work, how effectively, and whether they are currently fit to do it. Importantly, the project already has a substantial personnel design in the workbook, so this should be an **integration** effort rather than a new system built alongside it.[^40_1]

## Existing personnel foundation

The workbook `xlsx/Workbooks/dodabase-v102.xlsx` already distinguishes these areas, generally marked as planned rather than implemented:


| Existing definition | Intended responsibility |
| :-- | :-- |
| `StatsCat` | Numerical conditions such as Health, Injury, Fatigue, Nutrition, Stress, and Workload |
| `CondBandsCat` | Readable labels derived from condition values |
| `TraitDefsCat` | Characteristics such as Courage, Agility, and Paranormal Sensitivity |
| `TrainingCat` | Learned competencies such as Combat and Investigative Training |
| `ActivePersRoster` | Persistent personnel identities |
| `ActivePersConds` | Current changing conditions |
| Personnel schedules, locations, and history | Duty, deployment, recovery, whereabouts, and significant events |

The workbook also establishes `person_id` as persistent identity and treats map actors as temporary representations—not the personnel record itself. That is a valuable boundary to preserve.[^40_1]

So I would refine “missing layer” to mean: **missing from the integrated Workbench authoring and gameplay pipeline**, not missing from the project’s design altogether.

## Separate personnel concepts

For the Workbench expansion, I recommend keeping the following concepts distinct. These are proposed authoring boundaries, not claims that every field already exists:


| Concept | What it describes | Example |
| :-- | :-- | :-- |
| Vitals and conditions | Current physical or operational state | HP, fatigue, injury |
| Attributes and traits | Relatively persistent personal characteristics | Agility, courage |
| Skills and training | Learned proficiency | Investigative training level |
| Expertise | Specialized knowledge or experience | Biological forensics specialization |
| Qualifications | Eligibility to fill an operational role | Signals Analysis |
| Personal abilities | Specific actions or effects an individual can use | An authored specialist action |

We should define expertise carefully before creating another catalog: if it is simply a specialized skill, it can be represented within the skill system rather than duplicated.

Similarly, personal abilities should be explicitly distinguished from the existing Department/facility `capabilities`.

## How the layers connect

The Workbench already has a bridge into personnel: qualifications and capability staffing requirements.

For example, `source/qualification_catalog.csv` defines Signals Analysis, Data Systems, Field Response, and Occult Response. Electronic Surveillance requires at least one Signals Analysis contributor, with two preferred; the TechOps Hub also has facility-specific staffing overrides.[^40_2][^40_3][^40_4]

The proposed integration would extend that bridge:

```text
Department progression
    → develops facilities, capabilities, and training opportunities

Personnel qualifications
    → determine eligibility for staffing roles

Personnel skills and expertise
    → influence effectiveness within those roles

Current personnel conditions
    → determine availability and operational limitations

Completed work
    → contributes to Department counters and future progression
```

That creates the connection you are looking for without making qualifications, skill levels, and Department unlocks interchangeable.

For instance, an upgraded surveillance capability could exist and be enabled, but still lack enough eligible personnel. A qualified analyst could fill the role while their skill level affects performance. Fatigue could temporarily limit that analyst without deleting their qualification or learned proficiency.

Those are proposed behaviors to author explicitly, not automatic consequences of adding the fields.

## HP needs a clear contract

One existing design detail deserves attention before implementation: the workbook describes strategic **Health** as an overall condition influenced by current Health Points, Base Health Points, Injury, Nutrition, and events. It therefore does not simply equate strategic Health with HP.[^40_1]

We should preserve that distinction until deliberately revised:

- Base or maximum HP: the individual’s health capacity.
- Current HP: the immediate health-point value.
- Strategic Health: the broader condition defined by the personnel rules.
- Injury: a separate trauma measure.

The exact relationship between field damage and persistent personnel condition needs an explicit synchronization rule. Otherwise, combat and strategic systems could disagree about whether someone is healthy, incapacitated, or dead.

## Recommended next design step

I recommend specifying the personnel layer alongside progression before expanding the editors:

1. Map the existing workbook definitions to Workbench catalogs, avoiding duplicate terminology.
2. Define skills, expertise, qualifications, and personal abilities precisely.
3. Separate authored defaults and templates from individual runtime/save records.
4. Define how staffing rules reference qualifications and, where needed, minimum skill levels.
5. Define how conditions modify availability and performance.
6. Establish the HP-to-strategic-condition contract.

The workbook already calls for native-owned personnel records, derived condition labels, and a presentation interface that does not fabricate unavailable data. Those principles should carry through this expansion.[^40_1]

The architectural direction is now clearer: **progression** defines what the Department has developed; personnel definitions describe who can use it; staffing and task rules connect the two; runtime conditions determine what can operate at the moment.

<div align="center">⁂</div>

[^40_1]: xlsx/Workbooks/dodabase-v102.xlsx

[^40_2]: source/qualification_catalog.csv

[^40_3]: source/capability_staffing_rules.csv

[^40_4]: source/facility_capability_staffing_overrides.csv


---

# I'm noticing also that if we include any more tabs in the Content Workbench, the tab titles will not be legible. We will need another method of navigating through tabs. Perhaps tab groups, perhaps categories, perhaps a vertical tab list, perhaps more selections in the "View" top menu - I'm not sure yet.

Agreed—the navigation needs to change before we add progression and personnel editors. My recommendation is a **grouped vertical navigation panel**, with the View menu providing alternate access to the same pages—not another growing row of tabs.

This can be a navigation-shell refactor rather than a rewrite of the editors. The current GUI installs separate editor modules, although navigation is coupled to a shared notebook and next/previous-tab functions. Those connections would need updating.[^41_1]

## Navigation options

| Option | Advantage | Limitation | Proposed role |
| :-- | :-- | :-- | :-- |
| Grouped horizontal tabs | Familiar; fewer top-level titles | Inner groups can still become crowded | Possible transitional approach |
| Flat vertical list | Gives titles more room | Becomes a long, undifferentiated list | Better than the current row, but incomplete |
| Grouped vertical panel | Combines categories, readable titles, and scrolling | Uses some editor width | Primary navigation |
| View-menu selections | Uses no permanent workspace width | Destinations are hidden until opened | Alternate access |
| Page search | Finds an editor without browsing categories | Requires knowing part of its name | Useful supplementary control |

For this Workbench, I would combine categories and a vertical list, rather than choose between them.

## Proposed page groups

The following is a proposed organization, not a finalized list. Existing and planned pages should be visibly distinguished.


| Group | Pages |
| :-- | :-- |
| Department | Tracks, Metrics, Metric Status Bands |
| Progression | Development Nodes, Requirements, Counters and Accounting, Effects, Costs and Investment |
| Facilities and Operations | Facilities, Department Capabilities, Facility Capabilities, Staffing Rules, Staffing Overrides, Task Templates |
| Personnel | Qualifications, Conditions and Vitals, Attributes and Traits, Skills and Training, Expertise or Specializations, Personal Abilities |
| Content and Tools | Flavor Text, Enum Catalog, Preview, Validation and Export |

The current application already installs editors for tracks, metrics, metric tiers, facilities, capabilities, staffing relationships, task templates, qualifications, flavor text, and enums. This proposal reorganizes those destinations while reserving room for the new layers.[^41_1]

I would also change the navigation label “Metric Tiers” to **Metric Status Bands**. That would help distinguish the existing numeric bands from acquired progression tiers without necessarily renaming the underlying CSV.

## Suggested workspace behavior

The proposed layout would have:

- A resizable left navigation panel with collapsible categories.
- A filter field that searches page names.
- One main editor displayed at a time.
- A clear heading such as “Personnel / Skills and Training.”
- An option to collapse the navigation panel for more editing space.
- View-menu entries generated from the same page list.
- Keyboard navigation and a visible selected-page indicator.

The sidebar’s width matters: the current application defaults to 1280×800 and permits a minimum size of 1040×650. We should check existing forms at that minimum size rather than assume a sidebar will fit without adjustments.[^41_1]

Switching pages should preserve selections and unfinished form edits. Where that is not possible, the application should warn before discarding changes—not silently rebuild the editor.

## Coding direction

I recommend introducing a shared **page registry**, conceptually containing:

```text
page_id
display_title
navigation_group
editor_frame
sort_order
```

Both the sidebar and View menu would use that registry. A central `show_page(page_id)` operation would handle page selection, heading updates, and selection synchronization.

This avoids maintaining separate lists of destinations in the notebook, sidebar, and menu. It also gives future editors one registration point.

The refactor would need to cover:

- Notebook-dependent editor installation.
- Direct notebook selection calls.
- Existing next/previous-tab navigation.
- Page refresh behavior.
- Form-state preservation and unsaved-change handling.

The inspected GUI already has notebook-relative navigation, and existing editor installers can add or relabel notebook tabs. That means changing only the visible tab strip would not fully decouple navigation.[^41_2][^41_1]

**Recommendation:** establish the page registry and grouped sidebar before adding the two new layers. Preserve the editor forms and data pipeline; replace the crowded navigation structure. There is no need to finalize every category today—the registry should make regrouping pages a small change rather than another refactor.

<div align="center">⁂</div>

[^41_1]: doda_content_workbench/doda_content_gui.py

[^41_2]: doda_content_workbench/doda_metrics_editor.py


---

# Okay, what's the plan? Any questions before we start? What do you need for me?

The plan is to build this in **stages**: stabilize navigation first, add the progression/accounting layer second, then integrate personnel definitions. Before starting, I need confirmation of the current source baseline and a few scope decisions—not a complete set of stats or balancing values.

## Implementation sequence

| Stage | Work | Completion checkpoint |
| :-- | :-- | :-- |
| 1. Baseline and specification | Confirm current files, document agreed rules, identify existing validation/test commands | Clear scope and a recorded baseline |
| 2. Navigation | Add a page registry, grouped sidebar, and matching View-menu destinations | Existing editors remain accessible and retain their behavior |
| 3. Shared schema plumbing | Centralize table metadata and candidate-validation file lists | Editors, validator, and exporter use consistent definitions |
| 4. Progression and accounting | Add counters, development nodes, requirements, effects, and separate costs/investment definitions | Mixed prerequisites can be authored, validated, and exported |
| 5. Personnel authoring | Bring existing personnel concepts into Workbench catalogs and connect them to staffing | Personnel definitions integrate without duplicating existing qualifications |
| 6. Runtime integration | Implement loading, evaluation, acquisition records, and persistence | Separate gameplay milestone |

I recommend the first implementation package cover **Stages 1–3**, with progression and personnel specifications drafted alongside it. That gives us room to add editors without immediately crowding the interface again.

The inspected code already separates editor modules, but duplicates table lists across editors, validation, and export. That supports this incremental approach rather than a rewrite.[^42_1][^42_2][^42_3][^42_4][^42_5]

## Rules already settled

I would record these as agreed requirements, rather than ask you to decide them again:

- Progression is additive; newer developments do not erase older ones.
- Unlockables support multiple requirements with individual thresholds.
- Each requirement selects a specific supported counter.
- Accounting varies by category: current, lifetime earned/collected, achievements, invested, or spent.
- Investment does not necessarily consume the underlying resource.
- Evidence is retained when invested into a Department track.
- Acquisition checks and ongoing conditions are independent.
- Acquired developments remain acquired when an ongoing condition fails.
- Conditional permissions automatically return when their requirements recover.
- Authoring `active` flags remain separate from gameplay enabled/disabled state.

The personnel workbook will be an existing design input, not something we replace silently. It already separates conditions, traits, training, persistent identities, and live personnel records.[^42_6]

## Questions before starting

These are the decisions that affect the first package:


| Question | Recommended default |
| :-- | :-- |
| Should we adopt the grouped sidebar, with View-menu access to the same pages? | Yes; resizable and collapsible |
| Is this phase limited to Workbench authoring, validation, export, and documentation? | Yes; no game-runtime changes yet |
| Should existing CSV IDs and behavior remain compatible wherever possible? | Yes; explicit migration only where needed |
| Is `dodabase-v102.xlsx` the current personnel design baseline? | Use it as a starting reference, with your newer decisions taking precedence |
| What should happen to unfinished edits when changing pages? | Preserve them; warn before any operation that would discard them |

We do **not** need to settle every skill scale, ability, expertise category, or HP formula before the navigation work begins. Those belong in the personnel specification checkpoint.

For progression, I would initially use **All requirements** by default and support explicit alternative paths without jumping straight to an unrestricted rule-expression language.

## What I need from you

1. **Source confirmation:** Are the project files here the latest working Workbench? If not, provide the current Workbench scripts, source CSVs, launch instructions, and any tests together.
2. Personnel baseline confirmation: Is the uploaded v102 workbook still the right starting point, or is there a newer version?
3. Scope approval: Confirm or amend the defaults above.
4. UI review: After the navigation change, provide a screenshot and report whether forms fit at your normal window size, labels remain readable, and page switching preserves edits.

You do not need to prepare a full content catalog first. We can use clearly labeled sample definitions to exercise the new schemas without treating them as finalized game balance.

## Verification and delivery

Each package should include a change list, any migration instructions, and a precise distinction between what was inspected, what was tested, and what still needs your verification.

The first package’s acceptance checks should include:

- Every existing editor remains reachable.
- Navigation and View-menu selection stay synchronized.
- Page switching preserves form state.
- Existing validation and export still work.
- Save operations retain backups and candidate validation.
- New schema fields cannot be silently dropped by an older editor.

The exporter currently packages definitions without activating game behavior, so successful export must not be presented as successful gameplay integration. Repository guidance also reserves engine launches and runtime verification for the human author.[^42_4][^42_7]

**Please confirm whether the files here are current, whether v102 is the personnel baseline, and whether you approve the recommended navigation and authoring-only scope.** Those answers are enough to begin the first package.

<span style="display:none">[^42_8]</span>

<div align="center">⁂</div>

[^42_1]: doda_content_workbench/doda_content_workbench.py

[^42_2]: doda_content_workbench/doda_metrics_editor.py

[^42_3]: doda_content_workbench/doda_track_editor.py

[^42_4]: doda_content_workbench/doda_content_export.py

[^42_5]: doda_content_workbench/doda_content_gui.py

[^42_6]: xlsx/Workbooks/dodabase-v102.xlsx

[^42_7]: wiki/content/BuildAndTestWorkflow.md

[^42_8]: wiki/content/TestDebugging.md


---

# 1. the updates we made in this thread have not been uploaded to the Project space.

1. v102 workbook should be relatively accurate.
2. confirm
3. I'm unable to upload screenshots (you cannot read them either) - the UI cuts off any tab text after "--" or longer than 20 characters

Confirmed. We’ll use v102 as the personnel reference, proceed with the grouped navigation and authoring-only scope, and use text-based UI checks instead of screenshots. The remaining blocker is the **current code baseline**: the Project files do not include the updates made during this thread, so I should not build replacements against them blindly.

## Updated working agreement

| Item | Decision |
| :-- | :-- |
| Workbench source | Uploaded files are an older baseline; preserve the newer thread changes |
| Personnel reference | v102 is relatively accurate, with your newer decisions taking precedence |
| Navigation | Grouped, resizable, collapsible sidebar with matching View-menu access |
| Scope | Authoring, validation, export, and documentation; no gameplay-runtime changes |
| UI verification | Written observations, logs, and checklists; no screenshots required |

The uploaded personnel workbook remains useful because it already separates conditions, traits, training, and persistent personnel records. We’ll reconcile it with the new design rather than treat every workbook entry as final.[^43_1]

## Addressing the label cutoff

I’ll treat “text cuts off after `--` or beyond approximately 20 characters” as your observed behavior—not yet as a diagnosed cause.

For the new navigation, I propose short labels without suffixes such as “-- Editor.” The page heading can show the full descriptive title.


| Navigation label | Full page heading |
| :-- | :-- |
| Tracks | Department Tracks |
| Status Bands | Metric Status Bands |
| Requirements | Progression Requirements |
| Accounting | Counters and Accounting |
| Staffing Overrides | Facility Capability Staffing Overrides |
| Vitals | Personnel Conditions and Vitals |
| Skills and Training | Personnel Skills and Training |

All those navigation labels stay within 20 characters. Categories provide context, so individual entries do not need to repeat “Department,” “Personnel,” or “Editor.”

That is a defensive naming choice, not a substitute for fixing layout. The navigation should still support resizing and scrolling, and full titles should remain available in the main heading.

## What I need next

Please provide the **latest local Workbench source**, preferably as one ZIP containing:

- The Workbench Python scripts, including editor modules.
- The current authoring CSVs.
- Launch scripts and any tests.
- Relevant documentation changed during this thread.

You do not need to include maps, textures, or other game assets for this first package.

If file upload is unavailable, paste the updated files in chunks, starting with the main GUI and any editor-installation or navigation changes. Also clarify whether the unuploaded updates are actual code changes, design decisions, or both.

The uploaded GUI directly installs editor modules and uses notebook-based navigation, so the current versions of those files matter for a safe refactor.[^43_2]

## First package acceptance

Once the baseline is reconciled, the first package will cover navigation and shared schema plumbing—not all progression and personnel editors at once.

You can verify it with a simple written checklist:

- Every existing editor opens.
- Labels are readable.
- Sidebar and View-menu selections match.
- Switching pages preserves unfinished edits.
- Forms remain usable at your normal window size.
- Validation, backups, and export still behave correctly.

No screenshots are necessary. A report such as “Staffing Overrides opens, but the Save button is clipped” is enough to identify a concrete issue.

**Next step: provide the latest Workbench source, or tell me that the unuploaded updates are design-only.** That determines whether we reconcile changed code first or can begin from the uploaded implementation.

<div align="center">⁂</div>

[^43_1]: xlsx/Workbooks/dodabase-v102.xlsx

[^43_2]: doda_content_workbench/doda_content_gui.py


---

# Files

doda_content_workbench

I can now access `doda_content_workbench` in the Project files. The main GUI identifies itself as version **0.9.0** and installs the existing editor modules, including qualifications, capabilities, staffing rules, and task templates. I’ll use the supplied files as the working baseline.[^44_1]

## First implementation scope

The first package remains:

1. Introduce a shared page registry.
2. Replace the crowded tab navigation with a grouped, resizable sidebar.
3. Generate matching View-menu destinations from that registry.
4. Preserve editor forms, selections, and unfinished edits when switching pages.
5. Consolidate schema metadata and candidate-validation file lists.
6. Document the agreed progression and personnel contracts without adding gameplay-runtime behavior.

Navigation labels will stay short and avoid `-- Editor` suffixes. Full descriptive titles will appear in the editor heading.

## Baseline cleanup

One issue is already visible: the GUI’s opening documentation still describes a read-only v0.1 browser that cannot edit CSVs, while the actual file declares v0.9.0 and installs editing modules. That documentation should be corrected during the baseline cleanup.[^44_1]

I have confirmed access and inspected the main GUI; I have **not** modified files or run tests yet. Next is a complete source review of navigation dependencies, save/refresh behavior, and available validation commands before constructing the replacement package.

No screenshots or additional balancing decisions are needed for this first stage.

<div align="center">⁂</div>

[^44_1]: doda_content_workbench/doda_content_gui.py


---

# Okay, let's start with the first PowerShell script. Do not create python files, I will use PowerShell ISE to do this via CLI

Start with a **baseline-and-backup PowerShell script**. It will locate the Workbench, back up its scripts and authoring CSVs, and produce a text report for the navigation refactor—without creating Python files or changing existing code.

This follows the current layout: the GUI expects scripts under `tools\doda_content_workbench` and authoring data under `data_authoring\source`.[^45_1]

## Script 1: Establish baseline

Paste the complete script into PowerShell ISE and run it with **F5**. Enter your local project root when prompted—the folder containing `tools` and `data_authoring`.

The script writes only to a new timestamped backup folder. It does not launch the GUI, run Python, export content, or touch game files.

```powershell
# DoDA Content Workbench - Step 01: Baseline and backup
# Compatible with Windows PowerShell 5.1 / PowerShell ISE.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ProjectRootInput = Read-Host 'Enter the DoDA project root (contains tools and data_authoring)'
$ProjectRootInput = $ProjectRootInput.Trim().Trim('"')

if (-not (Test-Path -LiteralPath $ProjectRootInput -PathType Container)) {
    throw "Project folder does not exist: $ProjectRootInput"
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRootInput).Path
$WorkbenchDirectory = Join-Path $ProjectRoot 'tools\doda_content_workbench'
$SourceDirectory = Join-Path $ProjectRoot 'data_authoring\source'
$GuiPath = Join-Path $WorkbenchDirectory 'doda_content_gui.py'
$ValidatorPath = Join-Path $WorkbenchDirectory 'doda_content_workbench.py'
$ExporterPath = Join-Path $WorkbenchDirectory 'doda_content_export.py'

foreach ($RequiredDirectory in @($WorkbenchDirectory, $SourceDirectory)) {
    if (-not (Test-Path -LiteralPath $RequiredDirectory -PathType Container)) {
        throw "Required directory missing: $RequiredDirectory"
    }
}

foreach ($RequiredFile in @($GuiPath, $ValidatorPath, $ExporterPath)) {
    if (-not (Test-Path -LiteralPath $RequiredFile -PathType Leaf)) {
        throw "Required script missing: $RequiredFile"
    }
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$BackupRoot = Join-Path $ProjectRoot (
    'data_authoring\backups\workbench_refactor\baseline_' + $Stamp
)
$ScriptsBackup = Join-Path $BackupRoot 'workbench'
$SourceBackup = Join-Path $BackupRoot 'source'
$ReportPath = Join-Path $BackupRoot 'baseline_report.txt'
$ManifestPath = Join-Path $BackupRoot 'baseline_manifest.csv'

New-Item -ItemType Directory -Path $ScriptsBackup -Force | Out-Null
New-Item -ItemType Directory -Path $SourceBackup -Force | Out-Null

$Manifest = New-Object 'System.Collections.Generic.List[object]'

$BackupSets = @(
    [pscustomobject]@{
        Name = 'workbench'
        Source = $WorkbenchDirectory
        Destination = $ScriptsBackup
    },
    [pscustomobject]@{
        Name = 'source'
        Source = $SourceDirectory
        Destination = $SourceBackup
    }
)

foreach ($Set in $BackupSets) {
    $Files = @(
        Get-ChildItem -LiteralPath $Set.Source -File -Recurse |
        Where-Object {
            $_.FullName -notmatch '[\\/](?:__pycache__|\.git|\.venv|venv)[\\/]' -and
            $_.Extension -notin @('.pyc', '.pyo')
        }
    )

    foreach ($File in $Files) {
        $RelativePath = $File.FullName.Substring($Set.Source.Length)
        $RelativePath = $RelativePath.TrimStart([char[]]@('\', '/'))
        $Destination = Join-Path $Set.Destination $RelativePath
        $DestinationParent = Split-Path -Path $Destination -Parent

        New-Item -ItemType Directory -Path $DestinationParent -Force |
            Out-Null

        $OriginalHash = (
            Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256
        ).Hash

        Copy-Item -LiteralPath $File.FullName -Destination $Destination

        $BackupHash = (
            Get-FileHash -LiteralPath $Destination -Algorithm SHA256
        ).Hash

        $CurrentHash = (
            Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256
        ).Hash

        if ($OriginalHash -ne $BackupHash -or $OriginalHash -ne $CurrentHash) {
            throw "File changed during backup or verification failed: $($File.FullName)"
        }

        $Manifest.Add([pscustomobject]@{
            Area = $Set.Name
            RelativePath = $RelativePath
            Bytes = $File.Length
            LastWriteTimeUtc = $File.LastWriteTimeUtc.ToString('o')
            SHA256 = $BackupHash
        })
    }
}

$Manifest |
    Export-Csv -LiteralPath $ManifestPath -NoTypeInformation -Encoding UTF8

$Report = New-Object 'System.Collections.Generic.List[string]'
$Report.Add('DoDA Content Workbench - Baseline Report')
$Report.Add('Created: ' + (Get-Date -Format 'o'))
$Report.Add('Project root: ' + $ProjectRoot)
$Report.Add('Backup folder: ' + $BackupRoot)
$Report.Add('Verified files: ' + $Manifest.Count)
$Report.Add('')
$Report.Add('No source files were modified.')
$Report.Add('Python, GUI, validator, exporter, and game runtime were not executed.')
$Report.Add('')

$Report.Add('=== Workbench file inventory ===')
foreach ($Entry in ($Manifest | Where-Object Area -eq 'workbench' |
        Sort-Object RelativePath)) {
    $Report.Add(
        '{0} | {1} bytes' -f $Entry.RelativePath, $Entry.Bytes
    )
}

$Report.Add('')
$Report.Add('=== Authoring CSV headers ===')
$CsvFiles = @(
    Get-ChildItem -LiteralPath $SourceBackup -Filter '*.csv' -File |
    Sort-Object Name
)
foreach ($CsvFile in $CsvFiles) {
    $Header = Get-Content -LiteralPath $CsvFile.FullName -TotalCount 1
    $Report.Add($CsvFile.Name + ': ' + [string]$Header)
}

$Report.Add('')
$Report.Add('=== Navigation and schema references ===')

$Patterns = @(
    'APP_VERSION\s*=',
    'SCHEMA_VERSION\s*=',
    '^\s*(SOURCE_FILES|TABLE_FILES|TABLE_SPECS|FILES|FIELDS)\s*=',
    '^\s*def\s+.*(menu|layout|notebook|tab|refresh)',
    'notebook\.(add|select|tab|tabs|hide|forget)',
    'Notebook',
    'install_.*editor',
    'label=.*(View|Tab|Previous|Next)',
    'fieldnames=',
    'candidate_valid'
)

$PythonFiles = @(
    Get-ChildItem -LiteralPath $ScriptsBackup -Filter '*.py' -File |
    Sort-Object Name
)

foreach ($PythonFile in $PythonFiles) {
    $Matches = @(
        Select-String -LiteralPath $PythonFile.FullName -Pattern $Patterns
    )

    if ($Matches.Count -gt 0) {
        $Report.Add('')
        $Report.Add('--- ' + $PythonFile.Name + ' ---')

        foreach ($Match in $Matches) {
            $Report.Add(
                '{0}: {1}' -f $Match.LineNumber, $Match.Line.Trim()
            )
        }
    }
}

$Report | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host ''
Write-Host 'Baseline backup completed and hashes verified.' -ForegroundColor Green
Write-Host ('Files backed up: ' + $Manifest.Count)
Write-Host ('Backup folder: ' + $BackupRoot)
Write-Host ('Report: ' + $ReportPath)
Write-Host ('Manifest: ' + $ManifestPath)
Write-Host ''
Write-Host 'No existing scripts or CSVs were changed.' -ForegroundColor Cyan
Write-Host 'Review the text report before the navigation patch.'
```


## What comes next

This first step records your actual local baseline and gives us a verified backup before patching existing files. Hash verification confirms the copied files match; it does **not** claim that the application or validator passes.

For the next script, I’ll keep PowerShell as the patching mechanism and avoid introducing new `.py` files. The navigation work will necessarily modify existing Python application code, but you will apply those changes through PowerShell ISE.

After running this script, paste the report’s **Navigation and schema references** section and any error output. That will let the next script check exact patch anchors and stop safely if your local code differs.

<div align="center">⁂</div>

[^45_1]: doda_content_workbench/doda_content_gui.py


---

# paste.txt

I decoded `paste.txt` successfully. It contains an expanded progression diagram as URL-encoded `mxGraphModel` XML—not Workbench Python code. It gives us a concrete hierarchy to use when designing the progression catalogs.[^46_1]

## Diagram contents

The decoded diagram contains **80 nodes**, connected by 72 edges, with eight top-level tracks:[^46_1]


| Track | Immediate branches |
| :-- | :-- |
| Field Operations | Surveillance, Raid, Investigation, Sting |
| Tech Infrastructure | Data Processing, Communications, Internet and Intranet, Audio and Video, Digital Encantation |
| Evidence Handling | Paper Records, Photographic Forensics, Biological Forensics, Audio Video Forensics, Digital Forensics |
| Intelligence | Confidential Informants, Undercover Surveillance, Embedded Agents, Occult Research |
| Public Relations | Civilian, Federal, Press, Criminal, Occult |
| Congressional Support | Legislation, Granted Jurisdictions, Direct Funding, SCIF Cooperation |
| Department Funding | Staffing, Office and Laboratory, Tactical Gear, Collateral Restitution, Print and Advertising, Research and Expeditions, Black Budget |
| Seized Assets | Monetary, Illegal Narcotics, Land and Real Estate Property, Motor Vehicles, Weaponry, Occult Paraphenalia |

These names preserve the diagram’s terminology; spelling normalization can be handled separately.[^46_1]

## Important implementation details

The diagram confirms that we need more than a simple track-and-branch structure:

- Data Processing contains Desktop Computers, Laptop Computers, and PDA Devices.
- Communications contains Landline Telephonics, Fax and Modem, Cellular Devices, and Web IRC.
- Audio and Video contains Audio Processing and Video Processing, which contain further formats.
- Field Operations includes deeper operational categories under Surveillance, Raid, Investigation, and Sting.[^46_1]

For example, one path is:

```text
Tech Infrastructure
    → Audio and Video
        → Video Processing
            → Digital Video
```

That supports a parent-linked node catalog with variable depth, rather than fixed columns such as `track`, `branch`, and `subbranch`.[^46_1]

Repeated labels also matter: **Covert** and **Non-Covert** occur under both Surveillance and Raid. Display names therefore cannot serve as unique identifiers; each node needs its own stable ID and contextual path.[^46_1]

## Hierarchy is not eligibility

I would use these connections as the proposed organizational hierarchy, keeping unlock requirements separate.

For instance:

```text
Organizational placement:
Data Processing → PDA Devices

Possible unlock requirement:
PDA development requires an Internet and Intranet threshold
```

The second relationship comes from our design discussion, not from an explicit threshold in this attachment. The diagram does not yet specify point measures, purchase costs, acquisition checks, or ongoing enablement conditions. Its modem labels should likewise be preserved as authored names—not automatically interpreted as sequential purchase dependencies.[^46_1]

**One confirmation:** should this expanded diagram supersede the older progression-tree file as our hierarchy baseline?

<div align="center">⁂</div>

[^46_1]: paste.txt


---

# Yes, I'm still working on it. I'm going to continue working on it before we continue with updating the python code

Understood—we’ll **pause** all Python changes while you continue developing the diagram. The expanded version in `paste.txt` supersedes the older progression tree as our working hierarchy, but remains a draft.[^47_1]

The agreed implementation direction stays in place:

- Grouped sidebar navigation with matching View-menu access.
- Additive progression with multiple configurable prerequisites.
- Category-specific accounting and separate acquisition/ongoing checks.
- Personnel integration using v102 as a reference.
- Authoring-only scope initially, without gameplay-runtime changes.

When you provide the next diagram revision, we’ll review its structure and distinguish organizational connections from unlock requirements before translating it into schemas or editors. No additional decisions or files are needed from you right now.

<div align="center">⁂</div>

[^47_1]: paste.txt


---

# DoDA_ProgressionTree.drawio (1).jpg

I can see this diagram image. I’ll treat it as your latest **visual draft**, while keeping Python changes paused until you say the design is ready.[^48_1]

## What this revision clarifies

The diagram now shows more than a hierarchy of upgrades—it brings together development categories, operational permissions, equipment, funding uses, and asset-disposition options.[^48_1]


| Area | Visible detail |
| :-- | :-- |
| Communications | Phone systems, fax machines, encrypted communications, and voice over IP |
| Data Processing | Desktop computers, laptops, and PDA devices, with a note about different evidence-processing rates |
| Audio and Video | Analog, digital, and film formats, alongside examples of recording media |
| Congressional Support | Jurisdictions, legislation, operational territory, and permissions |
| Seized Assets | Handoff and auction options |
| Department Funding | Staffing, equipment, facilities, advertising, research, and discretionary operations |

Some small annotations are difficult to read at this resolution, so I will not treat their exact wording as confirmed.[^48_1]

## Important modeling distinction

We should preserve the diagram’s richness without making every box the same kind of record.

For example, the visible items suggest several different roles:

- Category: Communications.
- Equipment or development: a phone-system option.
- Effect: a change in evidence-processing rate.
- Permission: authorization for an operation.
- Action: auction or hand off seized assets.
- Personnel role: Analyst or Special Agent.
- Annotation: explanatory design notes.[^48_1]

Those are proposed classifications for our later review—not a decision to reorganize your diagram now.

The repeated references to Field Operations, Intelligence, and Evidence Handling also suggest cross-system connections. We should distinguish a reference to an existing track from a separate progression node rather than create duplicates automatically.[^48_1]

## When you finish the draft

The editable `.drawio` file or another XML/text export will be the best source for extracting exact labels and connections. This image is useful for understanding the overall layout, but I won’t infer prerequisites solely from proximity or assume every connecting arrow means “unlocked by.”

For now, continue developing the diagram. We’ll reconcile its categories, developments, permissions, effects, and actions before translating it into Workbench schemas.

<div align="center">⁂</div>

[^48_1]: DoDA_ProgressionTree.drawio-1.jpg


---

# Here it is in XML

The XML parsed successfully, so I can now read the exact labels, annotations, and connections rather than relying on the image. I’ll treat this as the latest **working draft**, with Python changes still paused.[^49_1]

## Structure verified

The file contains **122 diagram vertices and 147 connections**. Every connection references existing vertices. That is a structural check—not validation of gameplay prerequisites.[^49_1]

Those 122 vertices are not 122 upgrades: they include category boxes, repeated track references, explanatory notes, and one unlabeled vertex. We should classify them before converting anything into content records.[^49_1]

## Design details now explicit

| XML annotation | Meaning for the proposed model |
| :-- | :-- |
| “Each item tier … various upgrade models … incrementally better stats,” with about 3–10 items per tier | Distinguish item tiers from individual equipment models |
| Models grant different stat boosts and abilities to NPCs or the player | Equipment effects need explicit recipients and effect definitions |
| Computers process evidence at different rates; laptops and PDAs are mobile | Processing performance and mobility are separate properties |
| All instances of Legislation act as unlocks or ability grants | Legislation contributes permissions, not just a numerical status |
| Digital Encantation unlocks spells stored as text on digital devices | A development can grant an ability whose use also depends on equipment |
| Black Budget includes discretionary spending and “off-the-record” operations | Funding categories can support distinct operational uses |

These statements are now readable directly from the XML, including the small annotations that were uncertain in the image.[^49_1]

## Important distinctions to preserve

The emerging model has several connected—but separate—parts:

- Department development: what the organization has acquired.
- Item tiers and models: which equipment options exist.
- Equipment effects: what a model contributes to its user.
- Permissions: which operations are authorized.
- Processing capabilities: what evidence can be handled and at what rate.
- Personnel eligibility: who can perform the work.

For example, the diagram supports distinguishing a PDA model’s processing performance and mobility from a Digital Encantation permission. It does **not** yet establish that every PDA supports spells, or what additional requirements that combination needs. We should author those relationships explicitly rather than infer them.[^49_1]

The XML also confirms repeated references to Field Operations, Intelligence, and Evidence Handling. We should resolve those as cross-references where intended, rather than automatically create duplicate Department tracks.[^49_1]

This gives us a readable design source for the next review. I have only inspected and parsed it; I have not changed the Workbench, converted the diagram into production CSVs, or assumed that submitting the XML means the draft is finished.

<div align="center">⁂</div>

[^49_1]: DoDA_ProgressionTree.drawio.xml


---

# Does this work in conjunction with the work we've done so far on the Content Workbench and the v102 workbook? What is different? What is compatible? What is incompatible? What needs refactoring? What is unclear? Where does the logic this model / flowchart breakdown (if anywhere)?

Please respond strictly in TTS format. No copy blocks, no charts or tables

Yes. The flowchart can work with both the Content Workbench and the version one hundred two workbook. It fills in Department development, equipment, permissions, and funding relationships that the existing authoring system does not yet express. It does not require replacing the personnel, staffing, facilities, or task designs. However, it is currently a mixed design map, not a complete executable progression model. Importing every box as an upgrade and every arrow as a prerequisite would create problems.[^50_1][^50_2][^50_3]

I will distinguish confirmed compatibility from proposed changes. My workbook assessment uses the excerpts retrieved earlier in this conversation; the latest lookup did not return additional workbook sections. I have parsed the diagram and inspected source code, but I have not tested gameplay integration.

First, what is compatible.

The Workbench already separates Department tracks, metrics, facilities, capabilities, qualifications, staffing rules, and task templates. Those can remain the foundation. Progression can determine which capabilities become available, while staffing determines whether the Department has the people needed to operate them. These are complementary questions, not competing systems.[^50_1]

The workbook also separates persistent personnel identity, changing conditions, relatively persistent traits, and learned training. Your diagram’s equipment bonuses and personal abilities can connect to that structure. For example, a device might modify an analyst’s effective processing performance without permanently increasing their learned skill. The workbook’s distinction between conditions, traits, and training should remain intact.[^50_2][^50_3]

Your additive progression rule also fits. The Department can retain older communications equipment while acquiring newer equipment and capabilities. There is no requirement in the inspected authoring schema that Communications must disappear when Internet and Intranet becomes available.[^50_1]

Second, what is different.

The flowchart introduces equipment tiers and individual models, including the note that a tier may contain roughly three to ten items. It also describes processing rates, mobility, permissions, asset-disposition actions, and equipment effects on either personnel or the player. These are richer concepts than the existing capability and staffing catalogs.[^50_3]

This means we now need to distinguish developing something, purchasing it, possessing it, installing it, assigning it, and using it. Those are not necessarily the same event.

Developing a laptop model might make it purchasable. Purchasing one might place it in Department inventory. Assigning it might let an analyst use it. Its availability could then depend on power, location, compatibility, or other explicitly authored conditions. Those additional conditions are design possibilities, not requirements already established by your diagram.

The personnel workbook provides an individual-state foundation, but its retrieved index marks many systems as planned. The flowchart therefore connects to a design foundation, not proof that all those behaviors already exist in code.[^50_2]

Third, what is incompatible as currently represented.

The clearest incompatibility is using existing metric tiers as progression tiers. The current validator requires metric tiers to cover an entire numeric range without gaps or overlaps. That is appropriate for a status such as low, moderate, or high support. It is not appropriate for a collection of independently acquired equipment developments. We should preserve metric status bands and add a separate progression model.[^50_4][^50_1]

Another incompatibility would be treating every category as spendable currency. Your evidence rule explicitly rejects that. Evidence can contribute to development without being consumed. Funding can have a changing balance. Public Relations can fluctuate without being spent. Closed cases can be cumulative achievements. These require different accounting definitions, not one universal points balance.

Similarly, an authored active checkbox cannot represent a permission that temporarily switches off. The existing active fields participate in content validation and catalog relationships. Gameplay availability needs separate state, so a support drop does not remove the capability definition or erase its acquisition.[^50_1]

There is also a scope mismatch to resolve around capabilities. The Workbench currently requires active capabilities to have staffing rules, and active task templates must reference a capability with an active facility installation. A personal equipment ability, such as using a digital spell, should not automatically become that same kind of facility capability. We need either distinct ability definitions or an explicit distinction between capability types.[^50_3][^50_1]

Fourth, where the flowchart’s logic becomes unclear.

The biggest issue is that the arrows do not have declared meanings. Some appear to organize categories. Others relate equipment to benefits, legislation to permissions, or funding to operational uses. A single arrow type cannot safely represent all of those.

We need to distinguish “belongs to,” “requires,” “grants,” “improves,” “funds,” and “can process.” Otherwise, the importer would have to guess. The XML contains valid references between diagram vertices, but valid references do not establish valid gameplay dependencies.[^50_3]

The word tier also carries several meanings. A metric status tier is different from a development milestone, an equipment family, an individual model, and a facility’s initial tier. The existing Workbench already has metric tiers and facility-tier references, while the diagram adds item tiers. These should be named and modeled separately.[^50_3][^50_1]

Legislation needs more precision. The diagram says legislation acts as unlocks or ability grants. Our earlier discussion also used Legislation points as a prerequisite measure. Those ideas can coexist, but the point total and the acquired legal grant cannot be the same record. A score might qualify the Department to obtain a grant; the grant might then authorize an operation, possibly subject to current support or jurisdiction.[^50_3]

Granted Jurisdictions and operational territory need scope as well. Permission for a counter-occult operation might apply only in a particular region, to a particular operation type, or under particular circumstances. One Department-wide enabled flag would be insufficient if permissions vary by location.

Repeated track boxes also need interpretation. The diagram repeats Field Operations, Intelligence, and Evidence Handling. These may be references to existing systems rather than new tracks. If we import them literally, we could create multiple independent copies of what should be one Department track.[^50_3]

Fifth, where the logic could break down during play.

Asset disposition is a major example. Auctioning an asset, handing it to another agency, and retaining it for use are actions affecting a particular asset. Unless deliberately allowed, the same asset should not be auctioned and handed off and retained at the same time. A progression unlock can permit an action, but the asset record needs its own disposition state.

Evidence introduces a related distinction. Retaining evidence credit does not necessarily mean retaining possession of the physical item forever. If seized equipment is sold, the Department might still retain historical evidence credit, but should not automatically retain the equipment’s usable inventory instance. We need to distinguish historical contribution from current custody.

Investment can also create accidental double counting. Non-consumption means the source is not deducted. It does not settle whether one evidence item can contribute once to several tracks, repeatedly to one track, or only to one chosen allocation. That rule is still open.

Equipment bonuses can break down if they are applied directly to permanent personnel values. Equipping and unequipping a device repeatedly could accumulate bonuses. A safer proposed model separates base proficiency, learned progression, temporary conditions, and active equipment modifiers. Effective performance is derived from those components.

Processing rate needs an ownership rule. Your diagram says different computers process evidence at different rates. But we still need to decide whether the device, analyst, facility, or combination determines the rate. A faster device should not accidentally bypass missing qualifications or unsupported evidence formats.[^50_3]

Digital Encantation illustrates the same issue. The diagram grants the ability to use spells stored as text on digital devices. It does not yet define which users qualify, which devices support them, whether a spell must be acquired separately, or which ongoing conditions apply. That is an incomplete usage contract, not a contradiction.[^50_3]

There is also a potential deadlock around ongoing thresholds. If a disabled capability is the only way to restore the counter that enables it, the player could become permanently stuck. Every reversible permission should have a recovery path that does not depend entirely on that permission already being enabled.

Finally, prerequisite cycles require careful handling. An enhancement flowing back into an older branch is compatible with your additive model. But a particular upgrade cannot require another upgrade that ultimately requires the first. We need to check specific acquisition dependencies, not reject every cross-branch connection as a cycle.

Sixth, what needs refactoring.

The Workbench’s navigation should still be refactored independently of the gameplay model. The current GUI uses a notebook, direct tab registration, and previous-and-next-tab functions. A shared page registry and grouped sidebar can replace that navigation without replacing the editors’ data responsibilities.[^50_5]

Schema metadata also needs consolidation. The validator, exporter, and inspected editors maintain separate table lists. Editors serialize only their declared fields. Adding new columns without updating all those paths could cause validation failures, incomplete exports, or fields disappearing during a save.[^50_6][^50_7][^50_8][^50_1]

The new domain definitions should then be added around the existing catalogs. We need progression nodes, typed requirements, counter definitions, equipment models, effects, permissions, and cost or investment rules. We should reuse existing facilities, qualifications, and staffing relationships rather than duplicate them.

Personnel templates and definitions should remain authoring data. Current health, acquired skills, inventory assignments, purchase history, and enabled permissions belong to campaign state. This follows the workbook’s existing separation between static catalogs and persistent live records.[^50_2]

We also need one authoritative definition for each concept. The workbook and Workbench should not independently define the same qualification, condition band, or Department score with different identifiers and rules. Their terminology needs a mapping and an agreed ownership direction.

Finally, the exporter currently packages data without activating runtime behavior. Automatic permission restoration, equipment effects, and persistent accounting still require a separate runtime implementation. Extending the authoring tool alone will not make those mechanics operate in the game.[^50_8]

My overall judgment is that the design is compatible and useful. I do not see a fundamental contradiction that requires abandoning it. The breakdown occurs when a visual relationship is mistaken for a fully specified rule, or when category, upgrade, item, permission, and runtime state are collapsed into one concept.

Before changing Python, the most valuable next step is to classify each box and each connection. Then resolve equipment ownership, permission scope, evidence allocation, effect stacking, and processing-rate rules. We can leave numerical balancing unfinished while still making those structural decisions precise.

<div align="center">⁂</div>

[^50_1]: doda_content_workbench/doda_content_workbench.py

[^50_2]: xlsx/Workbooks/dodabase-v102.xlsx

[^50_3]: DoDA_ProgressionTree.drawio.xml

[^50_4]: doda_content_workbench/doda_metric_tiers_editor.py

[^50_5]: doda_content_workbench/doda_content_gui.py

[^50_6]: doda_content_workbench/doda_metrics_editor.py

[^50_7]: doda_content_workbench/doda_track_editor.py

[^50_8]: doda_content_workbench/doda_content_export.py


---

# Firstly, do you suggest that you regenerate the flowchart to be neater, clearer, and more defined, or should we go over the flowchart in detail so I can clarify anything that isn't yet clearly defined?

I recommend clarifying the flowchart first, then regenerating it. We can tidy individual sections as we resolve them, but a complete redraw now could make my assumptions look like decisions you have already made.

Your diagram includes categories, equipment, operational permissions, effects, and explanatory notes. The important uncertainty is what those elements and their connections mean—not just where they sit on the page.[^51_1]

I suggest we work through it in small sections. For each section, I’ll describe my interpretation in plain language, separate what you have already confirmed from what remains uncertain, and ask only the questions that affect the model. You can correct the interpretation before we move on.

We should first establish the diagram’s basic vocabulary. A connection might mean “belongs to this category,” “requires this development,” “grants this permission,” or “improves this capability.” Those meanings should be explicit. We should also distinguish a category from a purchasable development, an equipment model, and an action.

Then I suggest starting with Tech Infrastructure, particularly Data Processing and Communications. That section brings together most of the important distinctions: additive development, equipment tiers, individual models, processing performance, mobility, and benefits to personnel or the player. Resolving it will give us a pattern we can reuse elsewhere. The diagram already explicitly mentions different processing rates, mobile laptops and PDAs, and model-specific stat boosts and abilities.[^51_1]

After that, we can examine Evidence Handling alongside Seized Assets, because that is where retained evidence credit, physical possession, investment, auctioning, and agency handoffs need to be separated. Then we can review Congressional Support and operational permissions, followed by staffing, personnel, and funding relationships.

We do not need to finalize numerical thresholds or every equipment model during this review. We need to establish the rules those values will follow. Anything unresolved can remain visibly marked as unresolved rather than filled in by guesswork.

Once those meanings are agreed, I would regenerate an editable diagram with a concise overview and separate detailed sections. The overview would show the Department’s major systems. The detailed sections would show developments, requirements, permissions, and effects without forcing everything into one crowded tree. The original would remain preserved for comparison.

So my recommendation is: clarify first, redraw second, and update Python third. Small layout improvements can happen during clarification, but the polished diagram should document your decisions—not substitute for them.

To begin, should the connection from Tech Infrastructure to Data Processing mean only that Data Processing belongs to that track, or does Tech Infrastructure itself have an acquired level or point threshold that unlocks Data Processing?

<div align="center">⁂</div>

[^51_1]: DoDA_ProgressionTree.drawio.xml


---

# Okay, let's go section by section, small batches

Let’s start with one small batch: Tech Infrastructure and Data Processing. Your diagram connects those two, then places Desktop Computers, Laptop Computers, and PDA Devices beneath Data Processing.[^52_1]

For now, we’ll clarify only what those boxes represent—not costs, equipment stats, or personnel requirements.

First question: Is Tech Infrastructure simply the category that groups these developments, or does it also have its own points or development level?

Second question: Is Data Processing itself something the player develops or invests in, or is it simply the category containing computer equipment?

Third question: Are Desktop Computers, Laptop Computers, and PDA Devices equipment families, each containing several purchasable models, rather than three sequential upgrades?

You can answer those three in ordinary language. I’ll record the distinctions before we move to the next batch.

<div align="center">⁂</div>

[^52_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. tech infrastructure has it's own points. It starts with communication > rotary phones and data processing > desktop computers by default. Acquiring more tech infrastructure or investing in it with department funding will unlock more types of tech, like multiline phones and PDA devices.

1. It is both. When resources are invested in Data Processing, the player gains access to purchase better computers and devices.
2. they are three separate equipment families, but are unlock sequentially through investing resources in tech infrastructrure

That clarifies the first batch. Tech Infrastructure is a progression track with its own points, and Data Processing is both an organizational branch and an area the player can invest in.

The starting technology includes rotary phones under Communications and desktop computers under Data Processing. Further acquisition or investment unlocks additional technology families. Investment in Data Processing also opens access to better computer and device models, which the player then purchases separately.

Desktop Computers, Laptop Computers, and PDA Devices are distinct equipment families, matching their placement in the diagram. Their availability progresses sequentially, but newer families do not replace older ones.[^53_1]

The next small batch should clarify how investment and purchase affect those points.

First question: When Department Funding is invested in Data Processing, does that increase both Data Processing points and the parent Tech Infrastructure points, or only Data Processing points?

Second question: When the player purchases an available computer or device, does that purchase also contribute progression points, or are development investment and equipment purchases accounted for separately?

Third question: At the start, does the Department already own rotary phones and desktop computers, or are those families simply unlocked and available to purchase?

<div align="center">⁂</div>

[^53_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. it increases both, with Tech Infrastructure points being cumulative from all tech infrastructure branches.

1. equipment purchase is separate.
2. yes, to start, the Department owns rotary phones and desktop computers, and the player can purchase more as they hire more analysts.

Understood. Investment in Data Processing increases that branch’s points, and those points also contribute to the cumulative Tech Infrastructure total. Equipment purchases are separate from development investment.

The Department starts with actual rotary phones and desktop computers, not merely permission to buy them. The player can purchase additional units as staffing grows.

That establishes two distinct forms of advancement: development investment expands the available technology, while equipment purchases expand the Department’s owned equipment. The diagram’s separate computer families and processing-rate annotation fit that distinction.[^54_1]

For the next small batch, let’s clarify how the parent total and branch points control availability.

First question: Does unlocking the Laptop or PDA family require only the overall Tech Infrastructure total, or must the player also meet a Data Processing threshold?

Second question: Within an unlocked family, do better equipment models become purchasable automatically at Data Processing point thresholds, or must the player purchase a separate development upgrade first?

Third question: Once technology becomes unlocked through these cumulative development points, does it remain unlocked permanently, even if Department Funding later falls? This would be separate from any explicitly authored ongoing conditions on its use.

<div align="center">⁂</div>

[^54_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. both tech total and data processing threshold (analysts using data processing tech add data processing and evidence gathering points per tick)

1. the player must purchase a separate development upgrade first in the form of "contracts". When the player meets a threshold, it will unlock contracts the player can purchase which will then allow the player to purchase and use that equipment model.
2. They remain unlocked. For Public Perception and Congressional Support, those thresholds are variable and benefits / abilities can be locked if the Department falls below those thresholds. For anything that is generally cumulative, like evidence, intelligence, field operations, etc, those values remain constant and cumulative totals.

That establishes contracts as the missing step between meeting development thresholds and purchasing equipment.

The sequence is now clear. The Department must meet both the overall Tech Infrastructure threshold and the relevant Data Processing threshold. That makes a contract available to purchase. Purchasing the contract then authorizes purchase and use of its equipment model. Buying individual equipment units remains a separate transaction.

Analysts actively using Data Processing technology also generate Data Processing points and evidence-gathering points per tick. The Data Processing contribution feeds the cumulative Tech Infrastructure total, as you confirmed earlier. Your diagram’s equipment families and different processing rates fit this more specific progression loop.[^55_1]

For cumulative tracks, I’ll interpret “remain constant and cumulative” as meaning earned progress is retained and can continue increasing, rather than that the value stops growing. Technology unlocks persist. Public Perception and Congressional Support can fluctuate, temporarily disabling their conditional benefits, with automatic restoration when the requirements recover.

For the next small batch, let’s clarify contracts and point generation.

First question: Are technology contracts one-time, permanent purchases, or can they expire or require renewal?

Second question: Does purchasing a contract itself add development points, or does it only grant access to the equipment model?

Third question: Do analysts earn these points only while actively processing evidence or performing a qualifying task, or does simply being assigned to a computer generate points even when there is no work available?

<div align="center">⁂</div>

[^55_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. permanent purchases. The player always has them once they are purchased, even if they are rendered obsolete by new contracts.

1. contracts only grant access to the equipment model
2. being assigned earns a small amount of points, but active processing and performing tasks earn significantly more.

Understood. Technology contracts are permanent access grants. Buying a newer contract does not remove an older one, and purchasing a contract does not generate development points.

Assigned analysts generate a small amount of progression, while active processing and qualifying tasks generate significantly more. We can leave the exact rates undecided.

This adds a useful distinction to the diagram’s equipment-model structure: development thresholds make a contract available, the purchased contract grants model access, and separate equipment purchases provide actual units.[^56_1]

For the next small batch, let’s clarify assignment and point generation.

First question: Does the small assignment-based gain contribute to both Data Processing and evidence-gathering points, or only Data Processing when no evidence is being processed?

Second question: During active work, does the higher point rate replace the small assignment rate, or is it added on top?

Third question: Does assignment-based progression require an analyst to be on duty with access to an operational device, or does the assignment continue generating points while they are off duty or unavailable?

<div align="center">⁂</div>

[^56_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. yes, each task will have relevant point gain and loss values for department tracks / metrics, personnel stats, etc

1. added on top
2. analyst must be on-duty with access to an operational device.

Understood. Assignment-based gains require the analyst to be on duty with access to an operational device. Active processing and task gains are added on top of that baseline, rather than replacing it.

Each task will define its own relevant gains and losses across Department tracks, metrics, and personnel stats. We should therefore treat task effects as configurable, rather than assume every Data Processing task awards the same points. The diagram’s separate equipment models and processing-rate effects remain part of that calculation.[^57_1]

Your first answer establishes configurable task effects, but leaves one distinction open: which counters increase from assignment alone when there is no active work.

Let’s resolve that with two other closely related details in this batch.

First question: Should idle, on-duty assignment generate both Data Processing and evidence-gathering points, or should evidence-gathering points require actual processing or a qualifying task?

Second question: Should task effects support separate values for each active tick, successful completion, and failure? For example, ongoing work might increase fatigue, while completing the task grants an additional progression reward.

Third question: When a task has a negative effect, should it be prevented from reducing an established cumulative total, such as lifetime evidence or Tech Infrastructure development, while still being allowed to reduce fluctuating metrics such as Public Perception?

<div align="center">⁂</div>

[^57_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. evidence-gathering points require actual processing or a qualifying task.

1. yes, task effects should support separate values for each active tick, successful, completion, and failure.
2. yes it should be prevented from reducing an established cumulative total, however we should also track cumulative positive points and cumulative negative points as separate metrics. For instance if the Department's current cumulative Public Perception metric is 2000, but the cumulative lifetime negative Public Perception metric is -2500, that might lock the player out of a particular upgrade, ability, etc.

Understood. Evidence-gathering points require actual processing or a qualifying task. Assignment alone can generate the small Data Processing gain, but not evidence-gathering credit.

Task effects should also support separately authored values for active ticks, success, completion, and failure. That expands the diagram’s processing-rate concept into a more explicit task-effects model.[^58_1]

Your third point introduces another important distinction: retained progression, current standing, lifetime positive contributions, and lifetime negative contributions are separate measures.

For Public Perception, a favorable present value would not erase its negative history. A requirement could therefore check both present standing and lifetime negative points. In your example, a present value of two thousand could meet one requirement, while lifetime negative points of minus twenty-five hundred could fail another.

For an established cumulative development total, a negative task outcome would not subtract earned progress. Where negative outcomes are tracked, they would contribute to a separate negative-history measure.

That means requirements need more than minimum thresholds. They must also support limits on negative history, with the comparison direction made explicit.

Let’s keep the next batch to three clarifications.

First question: In your Public Perception example, does two thousand mean the current standing after gains and losses, or the lifetime total of positive contributions?

Second question: Should success and completion be distinct events, so successful completion can apply both effects, while failed completion can apply completion and failure effects? Or should each task apply only one final outcome effect?

Third question: During active work, should task-tick gains be added to the small assignment gain, or replace it?

The earlier question about off-duty or unavailable analysts remains open; I won’t assume your negative-history rule answered that.

<div align="center">⁂</div>

[^58_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. current standing after gains and losses

1. completion and success are the same essentially - that just means the task is finished successfully. Failure should be rare (based on NPC loyalty and competence in that field). Failure results in negative NPC stats and evidence loss.
2. they should be added to the small assignment gain.

Understood. Public Perception’s current standing reflects gains and losses, while lifetime positive and lifetime negative contributions remain separate historical measures.

Success and completion are one outcome, so there should be one successful-completion effect, not two rewards for the same event. Tasks can separately define active-tick effects and failure effects. Failure should be rare, influenced by the assigned person’s loyalty and competence in the relevant field, and can cause adverse personnel-stat changes and evidence loss.

During active work, task-tick gains are added to the small assignment-based Data Processing gain. Evidence-gathering credit still requires actual processing or a qualifying task. This refines the diagram’s processing-rate concept without changing its equipment-family structure.[^59_1]

The next small batch should resolve what evidence loss means and when assignment gains apply.

First question: When a task fails, does it lose or damage the specific evidence being processed while leaving previously earned cumulative Evidence Handling points untouched?

Second question: Should assignment-based gains stop when the analyst is off duty, incapacitated, or otherwise unavailable, even if their assignment remains recorded?

Third question: On failure, are the Data Processing and evidence-gathering points already earned during active ticks retained, with separate failure penalties applied afterward, or is some of that task’s provisional credit withheld until successful completion?

<div align="center">⁂</div>

[^59_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. the evidence is destroyed, meaning that evidence value is deducted from the Evidence Handling points.

1. assignment-based gains stop when the analyst is off duty, incapacitated, or otherwise unavailable.
2. On failure the Data Processing and evidence-gathering points already earned during active ticks retained, with separate failure penalties applied afterward.

Understood. These clarify evidence loss, analyst availability, and failure handling. I’ll record them as those rules rather than assume they answer the previous questions about Public Perception or success-versus-completion effects.

Assignment-based gains stop when an analyst is off duty, incapacitated, or otherwise unavailable.

On task failure, Data Processing and evidence-gathering points already earned during active ticks are retained. Separate failure penalties then apply; failure does not automatically reverse the tick rewards.

Destroyed evidence is different: its evidence value is deducted from Evidence Handling points. This qualifies the earlier non-consumption rule. Investing evidence does not consume it, but destruction can reduce its current value.

That means we need to distinguish current Evidence Handling value from lifetime evidence-related gains and losses. Your diagram identifies Evidence Handling as its own track, but this accounting distinction comes from your clarification here.[^60_1]

For example, if a task earns points before destroying evidence, the earned tick contributions remain recorded. The destruction deduction is then applied separately to the appropriate current measure. We should not silently erase the historical gains or count the same destruction penalty twice.

Let’s resolve this distinction before moving further. Two questions for this batch.

First question: Are Evidence Handling points and evidence-gathering points two names for the same counter, or separate counters?

Second question: When evidence destruction lowers the current Evidence Handling value, can that disable an already acquired evidence-related benefit if it has an ongoing threshold, while permanent contracts remain owned? Or should destruction affect only eligibility for future unlocks?

<div align="center">⁂</div>

[^60_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. two names for the same counter - my apologies

1. if the analysts is 25% through processing the piece of evidence, then fails, the 25% of evidence points are retained, but the remaining 75% of evidence is lost. That 75% of evidence points lost will then be added to the total lifetime negative evidence points. A high lifetime negative evidence point score (evidence lost score) will negatively effect Public Perception and Congressional Support, blocking certain upgrades or reducing the amount of benefits of positive points / currency the Department receives.

That resolves the evidence accounting. Evidence Handling and evidence-gathering points are the same counter. Successfully processed evidence contributes retained positive points; the unprocessed portion destroyed on failure contributes to lifetime negative evidence points.

For a piece worth one hundred evidence points, failure after twenty-five percent processing leaves twenty-five earned points intact. The remaining seventy-five points are recorded as evidence lost. They are not subtracted from previously earned evidence points, because that remaining value had not yet been earned.

This corrects my earlier interpretation that destruction necessarily deducts from the established positive Evidence Handling total.

The loss history then has separate consequences. It can negatively affect Public Perception and Congressional Support, block certain upgrades, or reduce positive rewards and funding received. Those consequences should be defined separately from the evidence-loss record itself, rather than treating every lost evidence point as an automatic one-point reduction in every affected track.

That gives a more precise connection between the Evidence Handling and Congressional Support areas already represented in your diagram.[^61_1]

For the next small batch, two questions.

First question: Should evidence-loss consequences occur immediately when evidence is lost, through ongoing penalties based on lifetime loss thresholds, or both?

Second question: Can later good performance reduce those consequences without erasing the lifetime loss record? For example, could improved Public Perception or a better ratio of processed evidence to lost evidence restore benefits, or are some lifetime-loss thresholds intended to create permanent restrictions?

<div align="center">⁂</div>

[^61_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. immediate consequences

1. yes, it is ratio based.

Understood. Evidence loss has immediate consequences, but later successful processing can improve the ratio and restore affected benefits without erasing the lifetime loss record.

The positive evidence total remains earned progress. The negative evidence total records lost potential. The ratio connects that history to Public Perception, Congressional Support, and conditional benefits. This makes the relationship between those tracks more explicit than the diagram alone does.[^62_1]

For the next small batch, we need to define the ratio and distinguish immediate penalties from recoverable restrictions.

First question: Should the ratio be the percentage of resolved evidence value successfully processed? For example, twenty-five points processed and seventy-five lost would mean a twenty-five percent success rate. Evidence still awaiting processing would not count yet.

Second question: When evidence is lost, should Public Perception and Congressional Support receive a one-time deduction, while the updated ratio separately controls upgrade eligibility and reward reductions? Or should the ratio itself determine the immediate change in those scores?

Third question: Should the ratio use lifetime totals, or a recent period of performance? Lifetime totals preserve the whole history, while a recent-period ratio would allow recovery without overcoming every earlier loss.

Your answer has established that recovery is possible. These questions only define how that recovery is measured and applied.

<div align="center">⁂</div>

[^62_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. yes, the ratio should be the percentage of resolved evidence value successfully processed.

1. When evidence is lost, Public Perception and Congressional Support should receive a one-time deduction, while the updated ratio separately controls upgrade eligibility and reward reductions
2. we should use both as separate metrics. Perhaps the two ratios can than be ratio'd to determine if an "congressional appeal" or "public appeal" is granted. If recent performance is high, and it is not outweighted by prior failure, previous negative performance can be "exonorated" or "appealed"

Understood. We now have three separate mechanisms: a one-time reputation and support deduction when evidence is lost, performance ratios that govern eligibility and reward reductions, and an appeal mechanism that can relieve consequences after sufficient improvement.

Both lifetime and recent success ratios will measure successfully processed evidence value as a percentage of resolved evidence value. Evidence still awaiting processing is excluded.

The appeal concept adds a recovery mechanism to the Evidence Handling and Congressional Support relationships shown in the diagram. Public appeals would provide a corresponding route for Public Perception.[^63_1]

I’ll record comparing the two ratios as a proposal, not a finalized formula. Simply dividing recent performance by lifetime performance would not necessarily capture whether improvement outweighs prior failure. A small amount of recent success could produce a favorable comparison despite substantial historical losses. We should consider the amount of evidence resolved as well as the percentages.

My proposed distinction is that an appeal changes how past losses affect current penalties or eligibility, without deleting the historical evidence-loss record. That remains subject to your confirmation.

For the next small batch, three questions.

First question: Should recent performance cover a rolling period of strategic time, a fixed number of resolved tasks, or a fixed amount of resolved evidence value?

Second question: Does the player actively request a public or congressional appeal once eligible, or is relief granted automatically?

Third question: What does a successful appeal restore: some of the previously deducted Public Perception or Congressional Support points, relief from upgrade restrictions and reward reductions, or both?

<div align="center">⁂</div>

[^63_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. recent performance cover a rolling period of strategic time

1. relief is granted automatically
2. both

Confirmed. Recent performance uses a rolling period of strategic time. Relief is granted automatically when its conditions are met, and it can both restore previously deducted Public Perception or Congressional Support points and relieve upgrade restrictions or reward reductions.

We’ll keep public and congressional relief separately configurable. They relate to distinct areas of your diagram, so they do not have to use identical thresholds or restoration amounts.[^64_1]

There is one important distinction still to settle: restoring points is an event, while lifting a restriction is a state change. We need to prevent an eligible Department from receiving the same point restoration every tick.

For the next small batch, three questions.

First question: Once a particular evidence-loss penalty has been appealed successfully, should that relief remain permanent for that incident, with only new losses creating new penalties? Or can deteriorating performance reactivate consequences from previously appealed losses?

Second question: Should an appeal restore all points deducted for the covered losses, or a configurable portion? Either way, I would keep restoration limited to those deductions so an appeal cannot generate unlimited points.

Third question: Should eligibility require a minimum amount of evidence resolved within the recent window, as well as a good success ratio? This would prevent a tiny amount of successful work—or simply waiting for failures to leave the window—from being treated as sufficient recovery.

<div align="center">⁂</div>

[^64_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. permanent relief with a probationary period of strategic time

1. it should only restore losses to congressional support and public perception. Department funds, evidence-handling points, intelligence points, etc cannot be recovered.
2. yes, eligibility should require a minimum amount of evidence resolved within the recent window, as well as a good success ratio

Understood. Automatic relief includes a probationary period measured in strategic time. Eligibility requires both a sufficiently good recent success ratio and a minimum amount of evidence resolved during that rolling window.

An appeal can restore losses to Public Perception and Congressional Support only. It cannot recover lost funding, evidence value, Intelligence points, or other operational losses. This keeps reputation recovery separate from the resources and development tracks shown in your diagram.[^65_1]

One detail remains open: “permanent relief with probation” could mean relief is provisional until probation ends, or that relief is permanent immediately while probation governs future consequences. I won’t choose between those interpretations without your clarification.

For the next small batch, two questions.

First question: Are reputation and support points restored immediately when probation begins, or only after the Department successfully completes probation?

Second question: If performance deteriorates during probation, does that revoke relief for the old incident, extend or restart probation, or leave the old relief intact while applying penalties for new failures?

We can leave the probation duration and exact thresholds for later.

<div align="center">⁂</div>

[^65_1]: DoDA_ProgressionTree.drawio.xml


---

# Yes, relief is provisional until probation ends.

1. reputation and support points are restored immediately when probation begins, but can be revoked during probation with additional penalties to reputation and support.
2. it revokes relief for the old incident and applies ne penalties.

Confirmed. Relief is provisional during probation. Public Perception and Congressional Support points are restored immediately when probation begins. If probation is breached, that restoration is revoked and new penalties apply. Successful completion makes relief permanent for the covered incident.

The distinction is between reversing the restoration and applying an additional penalty. Revocation should undo the amount actually restored, rather than deducting the original loss a second time. Any additional probation penalty is separate from that reversal and from penalties caused by the new failure.

This probation mechanism is an additional rule connecting the evidence-loss and support systems; it is not yet specified in the diagram itself.[^66_1]

For the next small batch, two questions.

First question: What breaches probation? Does any new evidence loss trigger revocation, or only losses severe enough to cross a configurable threshold or push recent performance below the required ratio?

Second question: During probation, are the covered upgrade restrictions and reward reductions also lifted immediately, then reinstated if relief is revoked? Or do those remain in place until probation is successfully completed?

<div align="center">⁂</div>

[^66_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. only severe infractions

1. until probation is completed

Confirmed. Only severe infractions breach probation. Upgrade restrictions and reward reductions remain in effect until probation is successfully completed, even though Public Perception and Congressional Support points are provisionally restored at the start.

The sequence is now defined: evidence loss causes immediate deductions; improved performance qualifies the Department for automatic provisional relief; probation begins; successful completion makes the restoration permanent and lifts the covered restrictions. A severe infraction during probation reverses the provisional restoration and applies new penalties.

This also means the covered restrictions need their own probation state. They cannot disappear merely because the provisional point restoration raises support above a numerical threshold. Other, unrelated requirements would still apply after probation ends.

We have expanded the relationship between Evidence Handling and Congressional Support beyond what the diagram currently specifies. Those confirmed rules should be recorded separately before the redraw.[^67_1]

Two final structural questions for this batch, then we can return to technology and equipment.

First question: Should “severe infraction” be explicitly assigned to particular failure or event types, determined by the amount or percentage of evidence lost, or support both methods?

Second question: Does probation complete when its strategic-time duration expires without a severe infraction, or must the Department also maintain a minimum success ratio and amount of resolved evidence during probation?

<div align="center">⁂</div>

[^67_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. should support both methods

1. strategic time, plus minimum success ratio for high level appeals

Confirmed. Severe infractions can be identified either by an explicitly designated event or failure type, or by a numerical severity rule. Both methods must be supported.

Ordinary probation completes after its strategic-time duration, provided no severe infraction revokes relief. High-level appeals additionally require a minimum success ratio. The minimum amount of recently resolved evidence remains an eligibility requirement for beginning an appeal; you have not added it as a probation-completion requirement.

We can leave durations, severity thresholds, and the definition of a high-level appeal configurable. We should also mark what happens when a high-level appeal reaches its end date without meeting the ratio as unresolved, rather than assume automatic failure or extension.

That is enough to park the appeal section and return to Data Processing equipment. Your diagram identifies desktops, laptops, and PDAs, with different processing rates and mobility.[^68_1]

Two questions for the next batch.

First question: Must each working analyst have a dedicated computer or device, or can multiple analysts share one, subject to a capacity limit?

Second question: Is processing performance determined by the equipment model alone, or by a combination of the model, the analyst’s skills, and their current condition?

<div align="center">⁂</div>

[^68_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. each working analysts must have dedicated computers and devices (can be assigned multiple computers and devices, with diminishing returns)

1. determined by a combination of model, analyst skill, and current analyst condition

Confirmed. Each working analyst needs dedicated equipment. An analyst can have multiple computers and devices, but additional equipment provides diminishing returns rather than a full repeated benefit.

Processing performance depends on the equipment model, the analyst’s skill, and their current condition. This gives the diagram’s different processing rates a personnel-dependent meaning, rather than making equipment speed the sole factor.[^69_1]

We’ll keep the diminishing-returns formula undecided for now. Assigning multiple devices also does not yet establish whether the analyst can perform multiple tasks simultaneously.

For the next small batch, two questions.

First question: Does additional equipment mainly improve performance on one task, allow the analyst to process multiple tasks simultaneously, or support both depending on the equipment and task?

Second question: Are desktops, laptops, and PDAs interchangeable for basic processing, with different speed and mobility, or does each family also support particular evidence types or tasks that the others cannot?

<div align="center">⁂</div>

[^69_1]: DoDA_ProgressionTree.drawio.xml


---

# Analysts and agents can use up to two computers, two phones, and two PDAs at one time. Some analysts and agents will benefit from more technology, others will not.

Analysts and agents can be assigned to more than 6 devices, but can only use two of each type (up to six total) on a single task, and they must all be in the same location for the analyst or agent to use them all at the same time. This means they can have an office desktop computer and a undercover laptop location computer that they can be assigned, but they cannot use them both at the same time because they are in two separate locations.

2. desktops, laptops, and PDA devices all have specific uses with some overlap. They can all read text files, send and receive emails and data, but each type has specific capabilities the others don't. Desktops can do heavy lab processing, laptops can do light field processing, and PDAs are mainly for communication but can also be used for gathering text-based and photographic evidence.

Understood. Assignment and simultaneous use are separate. Analysts and agents may have more than six devices assigned, but a single task can use at most two computers, two phones, and two PDAs, for a maximum of six devices. All devices used together must be at the person’s current location.

A desktop at the office and a laptop at an undercover location can both be assigned to the same person, but they cannot contribute simultaneously from those separate locations. Merely being assigned should therefore not make a device count toward task performance.

Additional devices also do not guarantee additional benefit. The benefit depends on the individual, alongside the diminishing-returns rule already established.

The equipment families have overlapping basic functions but distinct capabilities. Desktops support heavy laboratory processing. Laptops support light field processing. PDAs primarily support communication, with text-based and photographic evidence gathering. That clarifies the diagram’s distinction between device families and its mobility annotation.[^70_1]

For the next small batch, two questions.

First question: Do desktops and laptops share the same two-computer limit? For example, could someone use one desktop and one laptop together, but not two desktops plus a laptop?

Second question: What determines whether someone benefits from additional devices: particular skills or traits, an explicit multitasking or technology-proficiency stat, or a combination?

<div align="center">⁂</div>

[^70_1]: DoDA_ProgressionTree.drawio.xml


---

# Laptops and desktops count as two separate types

2. a combination

Understood. Desktops and laptops are separate device types, consistent with their separate equipment families in the diagram. Benefits from additional devices depend on a combination of skills, traits, and relevant technology or multitasking proficiency.[^71_1]

There is one limit to reconcile before we continue. You previously specified two devices of each type, with six devices total. Separating desktops and laptops now gives us four types: desktops, laptops, phones, and PDAs.

Should the maximum become eight devices per task—two of each type—or remain six overall, with no more than two of any individual type?

The same-location requirement and diminishing returns remain unchanged.

<div align="center">⁂</div>

[^71_1]: DoDA_ProgressionTree.drawio.xml


---

# Yes, eight devices total, my mistake

Confirmed: eight devices maximum per person on a single task—two desktops, two laptops, two phones, and two PDAs. This replaces the earlier six-device limit.

All participating devices must be at the person’s location. More devices may remain assigned elsewhere, but they do not contribute to that task. Actual benefits depend on the person’s skills, traits, proficiency, and condition, with diminishing returns. The diagram’s equipment families remain separate.[^72_1]

For the next small batch, two questions.

First question: Does the player explicitly select which assigned devices a person uses for a task, does the system automatically choose the most suitable available devices, or should both options exist?

Second question: Can an analyst or agent work on multiple tasks simultaneously, or do the eight devices support only one active task at a time?

<div align="center">⁂</div>

[^72_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. both options

1. one active task at a time

Confirmed. Device selection supports both manual choice and automatic selection. Each analyst or agent performs only one active task at a time, so additional devices support that task rather than create parallel task slots.

The eight-device maximum, two-per-type limits, same-location requirement, and individual diminishing returns remain unchanged. These rules clarify how the diagram’s equipment models contribute to a person’s work.[^73_1]

For the next small batch, let’s clarify equipment availability.

First question: Can equipment be freely reassigned between personnel when it is not in use, or is it permanently attached to its assigned person?

Second question: If a device becomes unavailable during a task, should the person continue at reduced effectiveness when the remaining equipment still meets the task requirements, and pause when it does not? Or should every equipment change interrupt the task?

<div align="center">⁂</div>

[^73_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. permanently attached unless reassigned by player, in which case the analyst or agent must receive a replacement, otherwise the device cannot be reassigned. Each analyst / agent device will have a "hard drive" or "storage card" that must be transfered to the new device. We can imagine this as Agent020Desktop1.HDD, Agent020Laptop1.HDD, Agent020PDA1.HDD, Analyst005Desktop1.HDD, Analyst005Desktop2.HDD, etc

Understood. Devices remain assigned to their person until the player explicitly reassigns them. Reassignment requires a replacement for the original analyst or agent, and their storage must transfer to that replacement.

Your examples establish persistent, person-specific storage for individual device assignments. Agent twenty’s first desktop storage is separate from their first laptop storage, and Analyst five’s first and second desktop storage are separate from each other.

The key distinction is between the equipment unit and the person’s stored data. Replacing a computer should preserve that assignment’s data rather than leave it on the hardware being handed to someone else. This adds an equipment-and-storage relationship beyond the model families shown in the diagram.[^74_1]

For the next small batch, two questions.

First question: Must a replacement be the same device type—for example, desktop replacing desktop—or can another type substitute if it supports the required work?

Second question: Is the storage transfer an immediate administrative operation, or does it require the devices to be brought together and take strategic time?

The earlier question about device failure during an active task remains open; I won’t infer its answer from the replacement rule.

<div align="center">⁂</div>

[^74_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. I should have clarified that AnalystXXXPDA1.HDD shouldn't use HDD but rather SC for storage card. That means laptops and desktops storage data is interchangeable, but PDAs are not. Therefore, an example would be Analyst003PDA1.SC = assigned to PDA.Newton.v2.009, Analyst003PDA2.SC = unassigned

Understood. Desktop and laptop storage uses the HDD designation and is interchangeable between those two device families. PDA storage uses SC, meaning storage card, and is not interchangeable with desktop or laptop storage.

In your example, Analyst three’s first PDA storage card is assigned to the Newton device identified as version two, unit zero zero nine. Their second PDA storage card has no device assigned. That distinguishes the person’s storage identity from the hardware assignment.

This adds storage compatibility to the separate device families already shown in the diagram.[^75_1]

Storage compatibility does not automatically mean task compatibility: transferring desktop data to a laptop would not give the laptop heavy laboratory-processing capabilities.

For the next small batch, two questions.

First question: Does “unassigned” mean the second storage card already exists and retains its data without a device, or is it an empty slot where a card will be created when equipment is assigned?

Second question: Is transferring compatible storage immediate, or does it require the old and replacement devices to be at the same location and take strategic time?

I’ll leave cross-family replacement eligibility open until we distinguish storage transfer from whether the replacement can perform the required work.

<div align="center">⁂</div>

[^75_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. programmatically, every agent / analyst is assigned hard drives and storage cards for desktops, laptops, and PDAs (phones do not apply). These HDD and SC IDs only become relevant and revealed to the player when an agent or analyst is assigned a device. When an analyst / agent is hired / spawned, they are created with 6 storage slots by default (and two phone numbers for each of their phones, but phone numbers can and should be changed frequently and at any time).

1. strategic time must be allocated, a department technician (custodial staff) must be assigned to the device transfer and "device onboarding" and devices / agents / analysts must be in the same location.

Understood. Each analyst or agent receives six persistent storage slots at creation: two desktop hard-drive slots, two laptop hard-drive slots, and two PDA storage-card slots. Their identifiers remain hidden until the corresponding device assignment makes them relevant. Creating those slots does not itself give the person six devices.

Phones do not use these storage slots. Phone numbers are separately changeable identifiers, not permanent personnel or equipment identities.

Device transfer and onboarding are scheduled operations. They require strategic time, an assigned Department technician from custodial staff, and the technician, affected person, and devices at the same location. That gives the diagram’s custodial staffing role a specific operational responsibility.[^76_1]

For the next small batch, two clarifications.

First question: When you say “two phone numbers for each of their phones,” do you mean two numbers per phone, for up to four numbers across two active phones, or one number per phone, for two numbers total?

Second question: You previously allowed more devices to be assigned than can be used simultaneously. Do the six storage slots limit a person to six assigned computers and PDAs, or can additional assigned devices exist through extra storage slots or by using the existing storage identities one device at a time?

<div align="center">⁂</div>

[^76_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. one phone number per phone, in any combination of landline or mobile phones.

1. the same four hdds and two SCs will be shared between all their computers and devices. In theory, they "carry their data with them" and can swap hard drives themselves. Its the "safe transfer of data and reassignment of department equipment" that cannot be done by the analyst / agent alone (this requires a technician, as previously discussed). So while the four hdds are interchangeable, the analyst / agent can use up to two desktops and two laptops concurrently in the same location at the same time with their four owned HDDs - they cannot use four desktops simultaneously with their four HDDs

Understood. Each phone has one number, and the two active phones can be any combination of landline and mobile phones.

The storage arrangement is a personal pool of four interchangeable hard drives and two PDA storage cards, not storage permanently bound to six particular machines. Those storage identities can serve the person’s larger collection of assigned equipment.

There are two different operations. Moving their own storage between already assigned, compatible devices can be done by the analyst or agent. Safe data transfer, equipment onboarding, and reassignment of Department equipment require a technician and the scheduled, same-location procedure you established.

Storage compatibility does not change device-use limits. Four hard drives allow two desktops and two laptops to participate together, but not four desktops. The maximum remains eight active devices on one task, all at the person’s location.

This clarifies how personal storage connects to the diagram’s separate desktop, laptop, PDA, and phone families.[^77_1]

For the next small batch, two questions.

First question: Can the analyst or agent’s own hard-drive or storage-card swap happen immediately, or should it take a small amount of strategic time without requiring a technician?

Second question: If an active device becomes unavailable, does the task continue at reduced effectiveness when the remaining devices meet its requirements, and pause when they do not?

<div align="center">⁂</div>

[^77_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. takes small amount of strategic time

1. yes that is correct

Confirmed. An analyst or agent can swap their own compatible storage between already assigned devices, but it takes a small amount of strategic time. A technician is still required for safe data transfer, onboarding, and Department equipment reassignment.

If an active device becomes unavailable, the task continues with reduced effectiveness when the remaining equipment meets its requirements. Otherwise, the task pauses. Device unavailability alone does not automatically mean task failure or evidence destruction.

That completes the basic equipment-use rules for the desktop, laptop, and PDA families shown in the diagram.[^78_1]

Let’s move to Communications in the next small batch.

First question: Does investing in Communications increase its own branch points and contribute to the overall Tech Infrastructure total, just as Data Processing investment does?

Second question: Do new phone models follow the same sequence as computers: meet development thresholds, purchase a permanent contract, then purchase individual devices?

<div align="center">⁂</div>

[^78_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. yes

1. yes

Confirmed. Communications investment increases its branch points and contributes to cumulative Tech Infrastructure points. Phone models follow the same progression sequence: meet the development requirements, purchase a permanent contract, then purchase individual devices.

The diagram also includes communications methods such as fax, encrypted chat, and voice over internet, so we should distinguish phone equipment from the services or capabilities it supports.[^79_1]

For the next small batch, two questions.

First question: What benefits do phone models provide during a task? Do they mainly improve communication speed and reliability, unlock particular actions, modify task success, or support a combination?

Second question: Is Communications Bandwidth a Department-wide capacity, a capacity specific to each location, or a combination of both?

<div align="center">⁂</div>

[^79_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. communication speed, signal reliability, map coverage, ease of use (stress reducer)

1. location specific, but the higher the bandwidth per location, the higher the department wide bandwidth / transfer efficiency

Confirmed. Phone models affect communication speed, signal reliability, map coverage, and ease of use, with ease of use reducing stress.

Bandwidth is location-specific. Improving a location’s bandwidth also contributes to Department-wide bandwidth or transfer efficiency. We should keep those operational values separate from the cumulative Communications development points used to unlock contracts.

This clarifies the diagram’s Communications Bandwidth branch and its relationship to communications equipment.[^80_1]

For the next small batch, two questions.

First question: When data moves between two locations, should transfer speed depend on both locations’ bandwidth, with the slower connection limiting the transfer, or should Department-wide efficiency provide a broader bonus as well?

Second question: Are bandwidth improvements purchased and installed for each location separately after their contracts are unlocked, or does purchasing a bandwidth upgrade improve every Department location automatically?

<div align="center">⁂</div>

[^80_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. transfer speed should depend on both locations' bandwidth. This should be an exaggerating simulation of realtime data transfer of large data packets (exaggerated sizes to provide incentive for higher bandwidth modems)

Understood. Data-transfer speed depends on the bandwidth at both the sending and receiving locations. Transfer workloads will use deliberately exaggerated data sizes so higher-bandwidth modems provide a meaningful gameplay benefit.

The diagram’s modem tiers can therefore represent operational transfer capacity, separate from the development points that unlock their contracts.[^81_1]

I’ll leave the exact transfer formula and timing scale undecided. Department-wide efficiency should not silently bypass a location’s limited connection.

For the next small batch, two questions.

First question: Once a modem contract is purchased, must the player purchase and install modem equipment separately at each location?

Second question: Do transfers progress automatically in the background, allowing the analyst or agent to perform another task, or do they occupy that person’s single active-task slot until the transfer finishes?

<div align="center">⁂</div>

[^81_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. each location and each device must be separately connected. A modem is purchased for a location and routers are purchased to connect each device, but the device must support the new modem. For instance, a computer with maximum 14k modem support cannot support a 56k modem or T1 connection.

1. transfers occupy the agent / analyst and counts as on-duty active time. Technicians (custodial staff) can do this for the agent / analyst, freeing the agent / analyst to do other tasks that do not require the device performing the transfer i.e. analysis on their other assigned computer in another location

Understood. Network access requires both location infrastructure and individual device connections. The Department purchases a modem for a location and routers to connect devices, and each device must support that connection tier. Under your gameplay rule, an older computer limited to fourteen-kilobit modem support cannot use a fifty-six-kilobit or T-one connection.

Transfers are staffed tasks, not unattended background activity. They occupy the analyst or agent and count as active on-duty time. A technician can perform the transfer instead, freeing that person to work with other equipment, including equipment at another location. The device performing the transfer remains unavailable for that other work.

This gives the diagram’s modem tiers and custodial staffing roles distinct operational responsibilities.[^82_1]

Your example also establishes that technician-led transfer is different from physically swapping a person’s storage: data can be transferred while the owner works elsewhere. We still need to specify the technician’s required location.

For the next small batch, two questions.

First question: Must the technician be at the sending device’s location, and does the receiving device also require a person attending it? Or can one technician manage both ends from the sending location?

Second question: If several transfers use the same location’s modem simultaneously, do they share its available bandwidth, or does the modem permit only one transfer at a time?

<div align="center">⁂</div>

[^82_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. early game, technicians must be at the same location, but through upgrades and unlocking T1 connections, transfers can be done by remote technicians.

1. unlike real bandwidth, analyst / agent devices do not actually consume bandwidth, and all transfer at the same transfer rate. For example, a 56k modem allows all devices connected to it to transfer up to 56kb per second. This is simplified for the game and not representative of real world file transfer protocols

Confirmed. Bandwidth is a per-device transfer-rate limit, not a shared pool. Multiple connected devices can each transfer at the location’s supported rate without slowing one another down. Transfers still depend on both endpoint locations and device compatibility.

Technicians initially need to be at the transfer location. Later upgrades, including unlocking T-one connections, enable remote technician operation. This extends the diagram’s modem progression with a remote-operation capability.[^83_1]

I’ll preserve this as an intentional gameplay abstraction, not substitute real-world network behavior.

For the next small batch, two questions.

First question: Does remote technician operation require the technician’s location and both transfer endpoints to support T-one or better, or only the location being remotely operated?

Second question: Can each technician supervise multiple transfers simultaneously, or does one transfer occupy their single active-task slot, just as it does for an analyst or agent?

<div align="center">⁂</div>

[^83_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. scratch this rule - any bandwidth can transfer between each other, however it is not incentivized to use lower bandwidth connections to transfer large size data packets (I.e. 15GB over a 56k modem) - we can remove the T1 connection requirement.

1. one active task per technician at a time

Confirmed. We’ll remove the T-one requirement for remote transfers. Locations with different bandwidth tiers can transfer data between one another; lower bandwidth makes large transfers slower, rather than making them ineligible.

Each technician can perform only one active task at a time. Delegating a transfer therefore frees the analyst or agent, but occupies the technician and the device performing the transfer.

The diagram’s modem tiers remain useful as speed upgrades, not as restrictions on which locations can exchange data.[^84_1]

One distinction needs confirmation before we move on: this removes the bandwidth requirement for remote technician operation, but it does not necessarily remove your separate device-to-modem compatibility rule.

First question: Should remote technician operation now be available from the beginning, or still require a separate upgrade that is unrelated to bandwidth?

Second question: Does the earlier hardware rule remain—that a device limited to fourteen-kilobit modem support cannot connect directly to a fifty-six-kilobit modem—or should it be allowed to connect and simply transfer at its own lower maximum rate?

<div align="center">⁂</div>

[^84_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. separate upgrade requiring internet

1. lower bandwidth devices cannot connect to higher bandwidth modems, meaning the player must maintain multiple types of modems before they upgrade the devices or their bandwidths (not sure if players will be able to upgrade individual devices, TBD)

Confirmed. Remote technician operation requires a separate upgrade with an Internet prerequisite, but no T-one requirement.

Device compatibility remains strict. A lower-bandwidth device cannot connect directly to a higher-bandwidth modem. Locations can therefore retain multiple modem types to support their mix of older and newer equipment. Whether individual devices can receive bandwidth upgrades remains undecided.

The distinction is between a device connecting to its local modem and two locations exchanging data. Each device needs a compatible local connection, but transfers can cross between different bandwidth tiers. Higher-tier infrastructure does not replace the older connections still needed by existing devices. That preserves the additive development approach for the diagram’s modem families.[^85_1]

For the next small batch, two questions.

First question: Can a higher-bandwidth device connect to a lower-bandwidth modem and operate at that modem’s slower rate?

Second question: For remote technician operation, must both the technician’s location and the operated device’s location have Internet access, or is Internet access required only at the operated location?

<div align="center">⁂</div>

[^85_1]: DoDA_ProgressionTree.drawio.xml


---

# \<q>First question: Can a higher-bandwidth device connect to a lower-bandwidth modem and operate at that modem’s slower rate?\</q> 1) no, the device will be incompatible with modems that don't match it's network bandwidth exactly.

2\) yes, both locations require internet access

Confirmed. A device must match its local modem’s network-bandwidth tier exactly. Neither a faster nor a slower modem is compatible. That replaces the earlier description of device bandwidth as merely a maximum.

Different locations can still exchange data across different tiers. For example, a device matched to a fifty-six-kilobit modem can transfer to a device matched to another location’s higher-tier modem. The local connections must match their devices; the two locations’ tiers do not have to match each other.

Remote technician operation requires its separate upgrade and Internet access at both the technician’s location and the operated device’s location. There is no T-one prerequisite. The diagram’s modem families remain separate infrastructure options rather than replacements for every older connection.[^86_1]

For the next small batch, two questions.

First question: Do routers also need to match the device and modem bandwidth tier exactly, or are routers compatible across tiers?

Second question: When a location has several modem tiers installed, should each device use a player-selected compatible modem, an automatically selected matching modem, or support both options?

<div align="center">⁂</div>

[^86_1]: DoDA_ProgressionTree.drawio.xml


---

# Any bandwidth can be used for remote access, however the amount of data transfered during the remote access session will determine the time to complete the task. Remote access hard drive transfer for reassigning devices would take exceptionally long on a 56k connection, but becomes more viable on a 128k connection and T1 connection. Things like onboarding, remote tech support (to fix randomized computer bugs that disable the device), system updates (mandatory downtime at randomized intervals, system updates to not have any other effect on devices).

Understood. Remote access has no minimum bandwidth tier. Once the remote-operation upgrade and Internet access requirements are met, the session’s data volume and connection speed determine how long the task takes.

Large storage transfers for equipment reassignment are therefore possible over a fifty-six-kilobit connection, but deliberately time-consuming. Faster connections make them more practical without being mandatory.

Remote technician work now includes data transfer, device onboarding, and support for randomized computer bugs that disable a device. System updates introduce mandatory downtime at randomized intervals, but do not improve stats or otherwise change device capabilities. These maintenance tasks extend the diagram’s equipment and communications model.[^87_1]

The exact-match rule for a device’s local modem remains unchanged. Allowing remote access across different connection tiers does not make incompatible local hardware connectable.

For the next small batch, two questions.

First question: Does “disabled by a computer bug” mean the device cannot perform ordinary work but still permits technician remote access, or can some bugs also disable remote access and require an on-site technician?

Second question: Do mandatory system updates require an assigned technician, occupying their one active-task slot, or do updates run automatically while only the device is unavailable?

Router compatibility and modem selection remain unresolved; this clarification does not answer those earlier questions.

<div align="center">⁂</div>

[^87_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. disabled means it cannot perform ordinary work but still permits technician remote access AND some bugs can required an on-site technician.

1. system and device updates run automatically but must be triggered manually by the player or NPC.

Confirmed. A bug can disable ordinary device work while leaving technician remote access available. Some bug types require an on-site technician instead. We’ll therefore track ordinary usability, remote accessibility, and on-site repair requirements separately, rather than use one general disabled flag.

System and device updates must be initiated by the player or an NPC, but run automatically afterward. They cause downtime without changing device stats or capabilities. These maintenance rules extend the equipment model represented in your diagram.[^88_1]

For the next small batch, two questions.

First question: Once an update starts, is the person who triggered it free to perform another task using other equipment, while the updating device remains unavailable?

Second question: When a mandatory update becomes due, does the device immediately stop ordinary work until updated, or is there a grace period during which the player or NPC can choose when to start it?

<div align="center">⁂</div>

[^88_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. No, the person who triggered it has to be present and is occupied by the system update

1. the computer will nag the user to update constantly, and will gradually become more prone to task failure and computer bugs.

Confirmed. An update runs automatically after initiation, but it is not unattended: the person who triggers it must remain present and occupied for its duration. It therefore uses that person’s single active-task slot, while the device is unavailable for ordinary work.

When an update becomes due, the computer remains usable but repeatedly prompts its user. Delaying the update gradually increases task-failure risk and the likelihood of computer bugs.

This qualifies the earlier “no other effects” rule. Updates are maintenance, not equipment upgrades; overdue maintenance affects reliability, rather than permanently improving the device’s capabilities. This adds a maintenance state alongside the equipment families in your diagram.[^89_1]

For the next small batch, two questions.

First question: Does completing an update reset the overdue-update risks to their normal baseline, while leaving any existing bugs to be repaired separately?

Second question: Can the player assign a technician to initiate and attend the update instead of the device’s analyst or agent, freeing that owner to work with other equipment?

<div align="center">⁂</div>

[^89_1]: DoDA_ProgressionTree.drawio.xml


---

# 1. yes, update resets everything

1. yes, a technician can be assigned allowing the agent or analyst to use another device owned by them or tend to another task

Confirmed. A technician can perform the update, occupying their own active-task slot while the analyst or agent works on another owned device or performs another task. The updating device remains unavailable until the update finishes.

I’ll record that an update resets the device’s update-related maintenance state. However, “resets everything” needs one clarification because my previous question combined overdue-update risks with existing bugs.

These maintenance rules add detail to the equipment and custodial staffing relationships in the diagram.[^90_1]

For this batch, just one question: Does completing an update also clear existing computer bugs, including those normally requiring an on-site technician, or does it reset only the overdue-update risks while existing bugs still require their own repair task?

<div align="center">⁂</div>

[^90_1]: DoDA_ProgressionTree.drawio.xml


---

# Only technicians can remove computer bugs. If a technician does a system update, all bugs are removed as well along with the system update with no additional strategic time allocated - just the update time. This means that any bugs on the device remain after a system update if performed by an agent or analyst.

Confirmed. Only technicians remove computer bugs.

An update performed by an analyst or agent clears overdue-update risks, but leaves existing bugs intact. A technician-performed update clears those risks and all existing bugs together, using only the update’s strategic-time duration. No additional repair time is added.

The person performing the update remains occupied, and the device remains unavailable until completion. This gives custodial technicians a distinct maintenance benefit alongside their role in the diagram.[^91_1]

There is one remaining interaction to clarify before we close this batch.

If a device has a bug that normally requires an on-site technician, can a remote technician’s system update still remove that bug, or must the combined update and repair be performed on-site?

<div align="center">⁂</div>

[^91_1]: DoDA_ProgressionTree.drawio.xml


---

# \<q>If a device has a bug that normally requires an on-site technician, can a remote technician’s system update still remove that bug, or must the combined update and repair be performed on-site?\</q> remote system updating is an unlockable ability, not immediately granted with remote access. The type of bug determines whether the computer must be serviced on-site or can be serviced remotely (network card bug, display driver bug, corrupted hard drive, etc)

Understood. Remote access and remote system updating are separate unlockable abilities. Acquiring remote access does not automatically grant remote updating.

Each bug type determines whether service can occur remotely or requires an on-site technician. I won’t assign those rules to your network-card, display-driver, or corrupted-drive examples until you define them.

This qualifies the technician-update rule: an update can include bug removal without additional strategic time, but remote updating cannot bypass a bug’s on-site service requirement. These ability and maintenance distinctions extend the diagram’s technology progression.[^92_1]

For the next small batch, one question.

If a device has an on-site-only bug but still permits remote access, can a technician perform the update remotely and leave that bug for later on-site repair, or must the update itself wait for an on-site technician?

<div align="center">⁂</div>

[^92_1]: DoDA_ProgressionTree.drawio.xml


---

# The technician can perform the update remotely and leave the bug for later on-sire repair

Confirmed. A technician can complete a remote system update while leaving an on-site-only bug for later on-site repair, provided remote updating is unlocked and the device still permits remote access.

## Settled maintenance rules

| Update performed by | Update-related risks | Existing bugs | Strategic time |
| :-- | :-- | :-- | :-- |
| Agent or analyst | Reset | All remain | Update time only |
| Technician remotely | Reset | Remote-serviceable bugs removed; on-site-only bugs remain | Update time only; later on-site repair is separate |
| Technician on-site | Reset | All removed | Update time only, with no additional time for bundled bug removal |

Remote access does not automatically unlock remote system updating. Bug type determines the required service location, and only technicians can remove bugs.

This replaces the earlier blanket wording that “a technician update removes all bugs”: it removes all bugs that can be serviced from the technician’s current service location.

<span style="display:none">[^93_1][^93_2][^93_3]</span>

<div align="center">⁂</div>

[^93_1]: paste.txt

[^93_2]: DoDA_ProgressionTree.drawio-1.jpg

[^93_3]: DoDA_ProgressionTree.drawio.xml

