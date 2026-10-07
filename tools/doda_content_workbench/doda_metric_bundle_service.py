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