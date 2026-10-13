param([string]$Root = 'E:\Dev\uzdoom_src\doda-core')
$ErrorActionPreference = 'Stop'
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
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

payload = json.loads('{"guards": {"doda_row_selection.py": "f70ef6a09fca470ba84425a09a36f1720955b10ddf4819ac0373fe994810863b", "doda_inline_bulk_edit.py": "d235bb6f8c4285980b290e40f6db007ccf53cb1aef56d865646d10b87ffa6708", "tests/test_inline_bulk_edit.py": "69893b43ca1fdb852b1669bc82079434979434d9d944df43061ea6ab36d50efc", "doda_bulk_edit.py": "8e149daccbfb03106dfb4c3f16491286c8d58fcf30bf7bb4b4ab0bd493221595", "doda_multiselect.py": "76594c79c8728425f768877ba6b134cf17be24978b5a47a561e0b093fc8aa757", "doda_network_editor.py": "2f764a4f126d9be5714b97d88d986dba12841b2f77f045b5f1fe4b823203d6f6", "tests/test_row_selection.py": "5966f9998027672d386968e48267ccdebdc03cfa7065c7a1f84b0cab9f428070", "doda_task_templates_editor.py": "e1fee1e861fd1c2c9b6c8d1d89002b723c19dbcc6d1565858b0a600cbb72b4f4"}, "changes": [["doda_row_selection.py", "def selection_display(rows, field):\\n    return MULTIPLE_VALUES if any(row.get(field, \\"\\") for row in rows) else \\"\\"", "def selection_display(rows, field, show_common=False):\\n    values = [row.get(field, \\"\\") for row in rows]\\n    if show_common and values and all(value == values[0] for value in values):\\n        return values[0]\\n    return MULTIPLE_VALUES if any(values) else \\"\\""], ["doda_inline_bulk_edit.py", "self.editor.vars[name].set(selection_display(selected, name))", "self.editor.vars[name].set(selection_display(selected, name, show_common=True))"], ["tests/test_inline_bulk_edit.py", "def test_same_and_different_populated_fields_show_placeholder(self):", "def test_mixed_fields_show_placeholder_and_common_fields_show_value(self):"], ["tests/test_inline_bulk_edit.py", "self.assertEqual(self.editor.vars[\\"active\\"].get(), \\"Multiple values\\")", "self.assertEqual(self.editor.vars[\\"active\\"].get(), \\"false\\")"], ["tests/test_inline_bulk_edit.py", "self.assertEqual(self.editor.vars[\\"blank\\"].get(), \\"Multiple values\\")", "self.assertEqual(self.editor.vars[\\"blank\\"].get(), \\"new\\")"]], "new_files": {"tests/test_common_value_display.py": "import unittest\\nfrom unittest.mock import Mock\\nfrom types import SimpleNamespace as NS\\n\\nimport doda_row_selection as selection\\nimport doda_inline_bulk_edit as inline\\n\\n\\nclass Variable:\\n    def __init__(self):\\n        self.value = \\"\\"\\n        self.callbacks = []\\n    def get(self):\\n        return self.value\\n    def set(self, value):\\n        self.value = value\\n        for callback in self.callbacks:\\n            callback()\\n    def trace_add(self, mode, callback):\\n        self.callbacks.append(callback)\\n        return str(len(self.callbacks))\\n\\n\\nclass Widget:\\n    def __init__(self):\\n        self.state = \\"normal\\"\\n    def cget(self, name):\\n        return () if name == \\"values\\" else self.state\\n    def configure(self, **kwargs):\\n        self.state = kwargs.get(\\"state\\", self.state)\\n    def bind(self, *args, **kwargs):\\n        pass\\n\\n\\nclass CommonValueDisplayTests(unittest.TestCase):\\n    def display(self, values):\\n        return selection.selection_display([{\\"x\\": v} for v in values], \\"x\\", show_common=True)\\n\\n    def test_same_integer_text_shows_actual_value(self):\\n        self.assertEqual(self.display([\\"1\\", \\"1\\", \\"1\\"]), \\"1\\")\\n\\n    def test_same_text_shows_actual_value(self):\\n        self.assertEqual(self.display([\\"AGENT\\", \\"AGENT\\"]), \\"AGENT\\")\\n\\n    def test_same_boolean_shows_actual_value(self):\\n        self.assertEqual(self.display([\\"false\\", \\"false\\"]), \\"false\\")\\n\\n    def test_all_blank_remains_blank(self):\\n        self.assertEqual(self.display([\\"\\", \\"\\", \\"\\"]), \\"\\")\\n\\n    def test_different_values_show_multiple(self):\\n        self.assertEqual(self.display([\\"1\\", \\"2\\"]), \\"Multiple values\\")\\n\\n    def test_mixed_blank_and_populated_show_multiple(self):\\n        self.assertEqual(self.display([\\"\\", \\"1\\"]), \\"Multiple values\\")\\n\\n    def test_empty_selection_is_blank(self):\\n        self.assertEqual(self.display([]), \\"\\")\\n\\n    def test_legacy_task_template_display_is_unchanged(self):\\n        self.assertEqual(selection.selection_display([{\\"x\\": \\"1\\"}, {\\"x\\": \\"1\\"}], \\"x\\"), \\"Multiple values\\")\\n\\n    def test_missing_and_blank_are_equivalent(self):\\n        self.assertEqual(selection.selection_display([{}, {\\"x\\": \\"\\"}], \\"x\\", show_common=True), \\"\\")\\n\\n    def test_distinct_authored_representations_are_not_normalized(self):\\n        self.assertEqual(self.display([\\"1\\", \\"01\\"]), \\"Multiple values\\")\\n\\n\\nclass CommonValueInlineTests(unittest.TestCase):\\n    def setUp(self):\\n        fields=tuple(NS(name=n,label=n,kind=\\"text\\",required=False,multiline=False) for n in (\\"id\\",\\"minimum\\",\\"preferred\\",\\"maximum\\",\\"blank\\"))\\n        self.editor=NS(\\n            spec=NS(table=\\"example\\",fields=fields,key_columns=(\\"id\\",)),\\n            rows=[dict(id=i,minimum=\\"1\\",preferred=\\"1\\",maximum=\\"2\\",blank=\\"\\") for i in (\\"A\\",\\"B\\",\\"C\\")],\\n            vars={f.name:Variable() for f in fields}, widgets={f.name:Widget() for f in fields},\\n            tree=Mock(), app=NS(project_root=\\"root\\",log=Mock()),\\n            dirty=False,_set_status=Mock(),_ref_choices=Mock(),\\n        )\\n        self.editor.tree.selection.return_value=(\\"0\\",\\"1\\",\\"2\\")\\n        self.controller=inline.install_inline(self.editor)\\n        self.controller.begin((\\"0\\",\\"1\\",\\"2\\"))\\n\\n    def test_common_staffing_counts_display_without_becoming_edits(self):\\n        self.assertEqual([self.editor.vars[n].get() for n in (\\"minimum\\",\\"preferred\\",\\"maximum\\")], [\\"1\\",\\"1\\",\\"2\\"])\\n        self.assertEqual(self.controller.changes,{})\\n        self.assertFalse(self.editor.dirty)\\n\\n    def test_apply_without_edit_preserves_rows_and_skips_validation(self):\\n        before=[dict(r) for r in self.editor.rows]\\n        validate=Mock()\\n        self.assertFalse(inline.apply_inline(self.editor,validate,None))\\n        self.assertEqual(self.editor.rows,before)\\n        validate.assert_not_called()\\n\\n    def test_edit_other_field_preserves_common_counts(self):\\n        self.editor.vars[\\"blank\\"].set(\\"note\\")\\n        validate=Mock(return_value=NS(valid=True,errors=[]))\\n        self.assertTrue(inline.apply_inline(self.editor,validate,None))\\n        self.assertEqual([r[\\"minimum\\"] for r in self.editor.rows],[\\"1\\",\\"1\\",\\"1\\"])\\n        self.assertEqual([r[\\"maximum\\"] for r in self.editor.rows],[\\"2\\",\\"2\\",\\"2\\"])\\n        self.assertEqual(self.editor.vars[\\"blank\\"].get(),\\"note\\")\\n        self.assertEqual(self.controller.changes,{})\\n\\n    def test_explicit_clear_of_common_value_is_tracked(self):\\n        self.editor.vars[\\"minimum\\"].set(\\"\\")\\n        self.assertEqual(self.controller.changes,{\\"minimum\\":\\"\\"})\\n        validate=Mock(return_value=NS(valid=True,errors=[]))\\n        self.assertTrue(inline.apply_inline(self.editor,validate,None))\\n        self.assertEqual([r[\\"minimum\\"] for r in self.editor.rows],[\\"\\",\\"\\",\\"\\"])\\n        self.assertEqual(self.editor.vars[\\"minimum\\"].get(),\\"\\")\\n\\n    def test_protected_common_key_component_stays_disabled(self):\\n        self.editor.spec.key_columns=(\\"id\\",\\"preferred\\")\\n        self.controller.begin((\\"0\\",\\"1\\",\\"2\\"),force=True)\\n        self.assertEqual(self.editor.vars[\\"preferred\\"].get(),\\"1\\")\\n        self.assertEqual(self.editor.widgets[\\"preferred\\"].state,\\"disabled\\")\\n        self.assertEqual(self.controller.changes,{})\\n"}}')
root=Path(sys.argv[1]).resolve()
module=root / "tools" / "doda_content_workbench"
source=root / "data_authoring" / "source"
if not module.is_dir() or not source.is_dir():
    raise SystemExit("Project directories missing; nothing installed.")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def guard():
    errors=[]
    for name,expected in payload["guards"].items():
        actual=sha(module / name)
        if actual != expected:
            errors.append(f"{name}: expected {expected}, actual {actual}")
    for name in payload["new_files"]:
        if (module / name).exists():
            errors.append(name + ": target already exists")
    if errors:
        raise RuntimeError("GUARD FAILED. Inspect current local files; do not bypass.\n" + "\n".join(errors))

try:
    guard()
except Exception as error:
    print(error)
    raise SystemExit(1)
csv_bytes={p.relative_to(source).as_posix():p.read_bytes() for p in source.rglob("*.csv")}
if not csv_bytes:
    raise SystemExit("No source CSVs found; nothing installed.")

def csv_guard():
    now={p.relative_to(source).as_posix():p.read_bytes() for p in source.rglob("*.csv")}
    if now != csv_bytes:
        changed=sorted(name for name in set(now) | set(csv_bytes) if now.get(name) != csv_bytes.get(name))
        raise RuntimeError("Source CSV changed during installation: " + ", ".join(changed))

stamp=datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
backup=module / "backups" / ("v124_common_value_display_" + stamp)
backup.mkdir(parents=True)
originals={name:(module / name).read_bytes() for name in sorted(set(change[0] for change in payload["changes"]))}
for name,data in originals.items():
    dest=backup / "modified_files" / name
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
for name,data in csv_bytes.items():
    dest=backup / "source_csv_snapshot" / name
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
(backup / "source_manifest.json").write_text(json.dumps({name:hashlib.sha256(data).hexdigest() for name,data in csv_bytes.items()},indent=2),encoding="utf-8")
print("Backup and logs:",backup,flush=True)

def suite(label,minimum):
    env=dict(os.environ)
    env["PYTHONPATH"]=str(module) + os.pathsep + env.get("PYTHONPATH","")
    env["PYTHONDONTWRITEBYTECODE"]="1"
    done=subprocess.run([sys.executable,"-m","unittest","discover","-s",str(module / "tests"),"-p","test_*.py"],
        cwd=root,env=env,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
    (backup / (label + ".log")).write_text(done.stdout,encoding="utf-8")
    print(done.stdout,flush=True)
    counts=re.findall(r"Ran (\d+) tests? in",done.stdout)
    count=int(counts[-1]) if counts else 0
    if done.returncode != 0 or count < minimum:
        raise RuntimeError(f"{label} failed: exit {done.returncode}, tests {count}, required >= {minimum}.")
    csv_guard()
    return count

written={}
try:
    baseline=suite("baseline",759)
    guard()
    candidates={}
    for name,data in originals.items():
        text=data.decode("utf-8-sig").replace("\r\n","\n")
        for target,old,new in payload["changes"]:
            if name != target:
                continue
            if text.count(old) != 1:
                raise RuntimeError("Content guard failed: " + name + ". Inspect current file.")
            text=text.replace(old,new)
        ast.parse(text)
        newline="\r\n" if b"\r\n" in data else "\n"
        encoded=text.replace("\n",newline).encode("utf-8")
        if data.startswith(b"\xef\xbb\xbf"):
            encoded=b"\xef\xbb\xbf" + encoded
        candidates[name]=encoded
    for name,text in payload["new_files"].items():
        ast.parse(text)
        candidates[name]=text.encode("utf-8")
    guard()
    csv_guard()
    for name,data in candidates.items():
        path=module / name
        tmp=path.with_name("." + path.name + "." + uuid4().hex + ".tmp")
        try:
            tmp.write_bytes(data)
            if name in originals and path.read_bytes() != originals[name]:
                raise RuntimeError("File changed before write: " + name)
            if name not in originals and path.exists():
                raise RuntimeError("New target appeared before write: " + name)
            os.replace(tmp,path)
            written[name]=data
        finally:
            tmp.unlink(missing_ok=True)
    after=suite("post_install",baseline + 15)
    csv_guard()
    for name,data in written.items():
        if (module / name).read_bytes() != data:
            raise RuntimeError("Patched file changed during tests: " + name)
    for name,expected in payload["guards"].items():
        if name not in written and sha(module / name) != expected:
            raise RuntimeError("Unmodified guarded file changed: " + name)
    hashes={name:sha(module / name) for name in written}
    (backup / "installed_hashes.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    print(f"V124 INSTALLED: baseline {baseline}, post-install {after}; {len(csv_bytes)} source CSVs unchanged.")
    print("Shared Record fields show common values; mixed fields show Multiple values. Task Templates unchanged.")
    print(json.dumps(hashes,indent=2))
except BaseException as error:
    failures=[]
    for name,data in reversed(list(written.items())):
        path=module / name
        try:
            if not path.is_file() or path.read_bytes() != data:
                raise RuntimeError("Current file differs from patch output; refusing to overwrite external edits.")
            if name in originals:
                tmp=path.with_name("." + path.name + ".rollback." + uuid4().hex)
                try:
                    tmp.write_bytes(originals[name])
                    os.replace(tmp,path)
                finally:
                    tmp.unlink(missing_ok=True)
                if path.read_bytes() != originals[name]:
                    raise RuntimeError("Rollback verification failed.")
            else:
                path.unlink()
        except Exception as rollback_error:
            failures.append(name + ": " + str(rollback_error))
    print("INSTALLATION STOPPED:",str(error))
    print("Patched files rolled back." if not failures else "ROLLBACK NEEDS INSPECTION:\n" + "\n".join(failures))
    try:
        csv_guard()
        print("Source CSVs unchanged.")
    except Exception as source_error:
        print(source_error)
        print("Source snapshot retained in backup. No CSV is overwritten automatically; inspect before restoration.")
    print("Backup and logs:",backup)
    raise SystemExit(1)

'@
$temporary = Join-Path $env:TEMP ('doda_v124_' + [guid]::NewGuid().ToString('N') + '.py')
try {
    [IO.File]::WriteAllText($temporary, $code, (New-Object System.Text.UTF8Encoding($false)))
    & $python $temporary $Root
    if ($LASTEXITCODE -ne 0) { throw "v124 stopped with exit code $LASTEXITCODE. Inspect the reported log/backup before retrying." }
} finally {
    Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
}
