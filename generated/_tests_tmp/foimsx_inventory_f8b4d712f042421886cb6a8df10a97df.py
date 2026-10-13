import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
repo = root.parent

print("--- FOIMS-X and preview files ---", flush=True)
for folder in ("DoDA/UI/FOIMSX", "DoDA/Preview"):
    base = root / folder
    if not base.is_dir():
        print("(missing) " + folder, flush=True)
        continue
    for path in sorted(base.rglob("*")):
        if path.is_file():
            print("%s  %d bytes" % (path.relative_to(root).as_posix(), path.stat().st_size), flush=True)

print("--- all ZScript files mentioning FOIMS ---", flush=True)
for path in sorted(root.rglob("*.zs")):
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        continue
    if "FOIMS" in text:
        print(path.relative_to(root).as_posix(), flush=True)

print("--- native DoDA function names used by ZScript ---", flush=True)
names = set()
pattern = re.compile(r"DoDA\.([A-Za-z0-9_]+)\(")
for path in root.rglob("*.zs"):
    try:
        names.update(pattern.findall(path.read_text(encoding="utf-8-sig", errors="replace")))
    except OSError:
        pass
for name in sorted(names):
    print(name, flush=True)

print("--- where the native implementation lives ---", flush=True)
skip = {".git", "build", "node_modules", "backups", "_tests_tmp", "generated"}
needle = "GetPersonnelSnapshotRevision"
hits = []
for dirpath, dirnames, filenames in os.walk(repo):
    dirnames[:] = [d for d in dirnames if d not in skip]
    for filename in filenames:
        if not filename.lower().endswith((".cpp", ".h", ".hpp", ".zs", ".md", ".txt")):
            continue
        path = Path(dirpath) / filename
        try:
            if path.stat().st_size > 2_000_000:
                continue
            if needle in path.read_text(encoding="utf-8-sig", errors="ignore"):
                hits.append(path)
        except OSError:
            pass
    if len(hits) >= 25:
        break
for path in hits:
    print(path.relative_to(repo).as_posix(), flush=True)
if not hits:
    print("No file mentioning " + needle + " was found under " + str(repo), flush=True)

print("--- wiki and docs mentioning FOIMS ---", flush=True)
for folder in ("wiki", "docs"):
    base = root / folder
    if base.is_dir():
        for path in sorted(base.rglob("*.md")):
            try:
                if "FOIMS" in path.read_text(encoding="utf-8-sig", errors="replace"):
                    print(path.relative_to(root).as_posix(), flush=True)
            except OSError:
                pass

print("--- generated WorkbenchCatalog.zs (first 70 lines) ---", flush=True)
catalog = next(iter(root.rglob("WorkbenchCatalog.zs")), None)
if catalog is None:
    print("WorkbenchCatalog.zs was not found.", flush=True)
else:
    print(catalog.relative_to(root).as_posix(), flush=True)
    for number, line in enumerate(catalog.read_text(encoding="utf-8-sig", errors="replace").splitlines()[:70], 1):
        print("%d: %s" % (number, line[:150]), flush=True)