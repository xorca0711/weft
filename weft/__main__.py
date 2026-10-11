from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .validation import ValidationError, read_json, validate_project, verify_ravel


def main():
    parser = argparse.ArgumentParser(description="Weft offline project and Ravel connection checks")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Check the local scaffold; no network or scientific runs")
    verify = sub.add_parser("verify-ravel", help="Verify pinned committed blobs without writing to Ravel")
    verify.add_argument("--repo", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "validate":
            result = validate_project(root)
        else:
            lock = read_json(root / "integration/ravel.lock.json")
            result = verify_ravel(args.repo, lock)
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
