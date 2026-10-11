"""Bounded, content-addressed synthetic receipts. Hash anchors come from the ledger."""
import hashlib
import json
from pathlib import Path
import stat
import zipfile

from .jobs import JobError, canonical

MAX_BYTES = 2 * 1048576
MAX_MEMBER = 1048576


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return canonical(value).encode()


def decode(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise JobError("Duplicate JSON key")
            result[key] = value
        return result
    try:
        value = json.loads(data, object_pairs_hook=pairs)
        if encoded(value) != data:
            raise JobError("Noncanonical receipt")
        return value
    except (ValueError, TypeError, UnicodeError) as exc:
        raise JobError("Invalid canonical JSON") from exc


def record(name, data):
    return {"path": name, "bytes": len(data), "sha256": sha(data)}


def make_bundle(identity, outcome, observation, result=None):
    files = {} if result is None else {"result.json": encoded(result)}
    manifest = {"schema_version": 1, "identity": identity,
                "files": [record(name, data) for name, data in sorted(files.items())]}
    files["output-manifest.json"] = encoded(manifest)
    terminal = {"schema_version": 1, "identity": identity, "outcome": outcome,
                "observation": observation,
                "output_manifest_sha256": sha(files["output-manifest.json"])}
    files["terminal.json"] = encoded(terminal)
    return files


def verify_bundle(files, *, identity, terminal_sha256):
    if not isinstance(files, dict) or set(files) not in (
            {"terminal.json", "output-manifest.json"},
            {"terminal.json", "output-manifest.json", "result.json"}):
        raise JobError("Missing/unexpected bundle members")
    if sum(map(len, files.values())) > MAX_BYTES or any(len(x) > MAX_MEMBER for x in files.values()):
        raise JobError("Bundle expansion excess")
    if sha(files["terminal.json"]) != terminal_sha256:
        raise JobError("Terminal content hash mismatch")
    terminal = decode(files["terminal.json"])
    if set(terminal) != {"schema_version", "identity", "outcome", "observation", "output_manifest_sha256"}:
        raise JobError("Invalid terminal fields")
    if type(terminal["schema_version"]) is not int or terminal["schema_version"] != 1 or encoded(terminal["identity"]) != encoded(identity):
        raise JobError("Terminal identity drift")
    if terminal["outcome"] not in {"local_verified", "failed", "cancelled"}:
        raise JobError("Unknown is not a terminal receipt")
    o = terminal["observation"]
    if (set(o) != {"container_id", "status", "running", "pid", "exit_code", "oom_killed", "processes_absent", "timed_out", "cancel_requested"}
            or o["container_id"] != identity["container_id"] or o["status"] != "exited"
            or o["running"] is not False or type(o["pid"]) is not int or o["pid"] != 0
            or o["processes_absent"] is not True or type(o["exit_code"]) is not int
            or type(o["oom_killed"]) is not bool or type(o["timed_out"]) is not bool or type(o["cancel_requested"]) is not bool):
        raise JobError("Unverified terminal observation")
    outcome = terminal["outcome"]
    if ((outcome == "local_verified" and (o["exit_code"] != 0 or o["oom_killed"] or o["timed_out"] or o["cancel_requested"]))
            or (outcome == "cancelled" and (not (o["timed_out"] or o["cancel_requested"]) or o["exit_code"] != 137 or o["oom_killed"]))
            or (outcome == "failed" and (o["exit_code"] == 0 or o["timed_out"] or o["cancel_requested"]))):
        raise JobError("Outcome contradicts observation")
    if sha(files["output-manifest.json"]) != terminal["output_manifest_sha256"]:
        raise JobError("Manifest content hash mismatch")
    manifest = decode(files["output-manifest.json"])
    expected = [record("result.json", files["result.json"])] if "result.json" in files else []
    if encoded(manifest) != encoded({"schema_version": 1, "identity": identity, "files": expected}):
        raise JobError("Output manifest drift")
    if (outcome == "local_verified") != ("result.json" in files):
        raise JobError("Success requires exactly one deterministic output")
    if "result.json" in files:
        decode(files["result.json"])
    return terminal


def write_archive(path, files):
    """Exclusive creation; deterministic ZIP metadata; never overwrites evidence."""
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_STORED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o444) << 16
            z.writestr(info, data)


def restore_archive(archive, destination, *, identity, terminal_sha256, archive_sha256):
    """Verify every byte before creating a fresh directory. Never executes members."""
    archive = Path(archive)
    if archive.is_symlink() or archive.stat().st_size > MAX_BYTES:
        raise JobError("Unsafe/oversized archive")
    raw = archive.read_bytes()
    if sha(raw) != archive_sha256:
        raise JobError("Archive content hash mismatch")
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            infos = z.infolist()
            names = [i.filename for i in infos]
            if len(names) > 3 or len(names) != len(set(names)):
                raise JobError("Duplicate/excess archive members")
            total = 0
            for i in infos:
                mode = i.external_attr >> 16
                if (i.filename not in {"terminal.json", "output-manifest.json", "result.json"}
                        or i.is_dir() or stat.S_ISLNK(mode)
                        or (stat.S_IFMT(mode) not in {0, stat.S_IFREG})
                        or i.flag_bits & 1 or i.file_size > MAX_MEMBER):
                    raise JobError("Unsafe archive member")
                total += i.file_size
            if total > MAX_BYTES:
                raise JobError("Archive expansion excess")
            files = {i.filename: z.read(i) for i in infos}  # read verifies CRC
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise JobError("Invalid ZIP/CRC") from exc
    terminal = verify_bundle(files, identity=identity, terminal_sha256=terminal_sha256)
    destination = Path(destination)
    if any(p.is_symlink() for p in [destination, *destination.parents]):
        raise JobError("Symlink destination rejected")
    destination.mkdir()  # existing paths/symlinks are rejected, even if empty
    for name, data in files.items():
        with (destination / name).open("xb") as stream:
            stream.write(data)
    return terminal
