param([string]$Root = 'E:\Dev\uzdoom_src\doda-core')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$picker = New-Object System.Windows.Forms.OpenFileDialog
$picker.Title = 'Select the ORIGINAL failed v125a installer (read as data only)'
$picker.Filter = 'PowerShell installer (*.ps1)|*.ps1'
$picker.FileName = 'DoDA_v125a_task_template_drafts.ps1'
try {
    if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw 'Cancelled; nothing installed.'
    }
    $original = $picker.FileName
} finally {
    $picker.Dispose()
}
$module = Join-Path $Root 'tools\doda_content_workbench'
$python = @(
    (Join-Path $module '.venv\Scripts\python.exe'),
    (Join-Path $Root '.venv\Scripts\python.exe')
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $python) {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if (-not $command) { throw 'Python not found. Use the existing Workbench Python; do not install another environment.' }
    $python = $command.Source
}
$code = @'
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

original=Path(sys.argv[1])
root=sys.argv[2]
data=original.read_bytes()
expected="6ae6d4b3e40f5a8561d565c1d9b3afffbc6321725b19c2bc6d9a9259b0bc7ee3"
if hashlib.sha256(data).hexdigest() != expected:
    raise SystemExit("Original installer hash mismatch. Stop and inspect; do not bypass.")
text=data.decode("utf-8-sig").replace("\r\n","\n")
match=re.search(r"(?ms)^\$code = @'\n(.*?)\n'@\s*$",text)
if match is None:
    raise SystemExit("Installer code block not found. Nothing changed.")
code=match.group(1)
tree=ast.parse(code)
nodes=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="payload" for t in n.targets)]
if len(nodes) != 1:
    raise SystemExit("Installer payload is ambiguous. Nothing changed.")
node=nodes[0]
if not isinstance(node.value,ast.Call) or not isinstance(node.value.func,ast.Attribute) or not isinstance(node.value.func.value,ast.Name) or node.value.func.value.id != "json" or node.value.func.attr != "loads" or len(node.value.args) != 1:
    raise SystemExit("Unexpected payload shape. Nothing changed.")
payload=json.loads(ast.literal_eval(node.value.args[0]))
changed=[]
for item in payload["patches"]:
    name,old,new=item
    if name == "doda_content_gui.py" and old in (
        "    def run_export(self) -> None:\n",
        "    def run_validation(self) -> None:\n",
    ):
        needle="        if task_draft_dirty(self):\n"
        if new.count(needle) != 1:
            raise SystemExit("Warning-code content guard failed. Nothing changed.")
        item[2]=new.replace(needle,
            '        task_editor = getattr(self, "task_templates_editor", None)\n'
            '        if task_editor is not None and getattr(task_editor, "dirty", False):\n')
        changed.append(old.strip())
if len(changed) != 2:
    raise SystemExit("Expected two orchestration warning patches. Nothing changed.")
payload["guards"]["tests/test_export_chain.py"]="c189452d9487bd2098099be0823c12fd32e14f7d7e6c5be73f3331d91bdbbeb0"
payload["new_files"]["tests/test_task_draft_export_context.py"]='import unittest\nfrom types import SimpleNamespace\nimport test_export_chain as chain\n\n\nclass TaskDraftExportContextTests(unittest.TestCase):\n    def setUp(self):\n        fixture=chain.ExportChainTests()\n        fixture.setUp()\n        self.fn=fixture.fn\n        self.app=fixture.app\n        self.dialog=fixture.dialog\n\n    def test_dirty_task_draft_warns_but_preserves_saved_source_export_chain(self):\n        self.app.task_templates_editor=SimpleNamespace(dirty=True)\n        self.fn(self.app)\n        self.app.log.assert_any_call("Task Templates note: applied drafts are not included; this action uses saved source. Save to Source first to include them.")\n        self.app.run_command.assert_called_once()\n        self.app.run_network_rules.assert_called_once_with("export",announce=False)\n        self.dialog.showinfo.assert_called_once()\n\n    def test_clean_task_editor_adds_no_draft_warning(self):\n        self.app.task_templates_editor=SimpleNamespace(dirty=False)\n        self.fn(self.app)\n        self.assertFalse(any("Task Templates note:" in str(call.args[0]) for call in self.app.log.call_args_list))\n        self.app.run_command.assert_called_once()\n        self.app.run_network_rules.assert_called_once_with("export",announce=False)\n'
lines=code.splitlines(keepends=True)
lines[node.lineno-1:node.end_lineno]=["payload = json.loads(" + repr(json.dumps(payload)) + ")\n"]
code="".join(lines)
for old,new in (
    ('baseline + 34','baseline + 36'),
    ('"v125a_task_drafts_"','"v125a_r1_task_drafts_"'),
    ('V125A INSTALLED:','V125A-R1 INSTALLED:'),
):
    if code.count(old) != 1:
        raise SystemExit("Installer correction guard failed: " + old)
    code=code.replace(old,new)
ast.parse(code)
print("Running corrected v125a-r1 package. Original PowerShell installer is not executed.",flush=True)
print("Export-chain tests remain unchanged; two draft-warning regressions added.",flush=True)
sys.argv=[str(original),root]
exec(compile(code,str(original) + " [corrected Python package]","exec"),{"__name__":"__main__","__file__":str(original)})

'@
$temporary = Join-Path $env:TEMP ('doda_v125a_r1_' + [guid]::NewGuid().ToString('N') + '.py')
try {
    [IO.File]::WriteAllText($temporary, $code, (New-Object System.Text.UTF8Encoding($false)))
    & $python $temporary $original $Root
    if ($LASTEXITCODE -ne 0) { throw "Corrected v125a-r1 stopped with exit code $LASTEXITCODE. Inspect the reported log/backup before retrying." }
} finally {
    Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
}
