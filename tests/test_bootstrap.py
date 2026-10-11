import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from weft.validation import ValidationError, read_json, validate_manifest, validate_project, verify_ravel

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.lock = read_json(ROOT / "integration/ravel.lock.json")

    def test_manifest_is_valid(self):
        validate_manifest(self.lock)

    def test_abbreviated_commit_rejected(self):
        self.lock["commit"] = "bfe26b8"
        with self.assertRaises(ValidationError):
            validate_manifest(self.lock)

    def test_traversal_and_windows_paths_rejected(self):
        for path in ("../secret", "/absolute", "C:/secret", "a\\b", "a/../b"):
            with self.subTest(path=path):
                lock = copy.deepcopy(self.lock)
                lock["files"][0]["path"] = path
                with self.assertRaises(ValidationError):
                    validate_manifest(lock)

    def test_duplicate_source_rejected(self):
        self.lock["files"].append(copy.deepcopy(self.lock["files"][0]))
        with self.assertRaises(ValidationError):
            validate_manifest(self.lock)


class ProjectTests(unittest.TestCase):
    def test_real_scaffold(self):
        self.assertFalse(validate_project(ROOT)["scientific_execution_enabled"])

    def test_activation_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "weft"
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "runs"))
            policy = read_json(dest / "configs/policy.json")
            policy["scientific_execution_enabled"] = True
            (dest / "configs/policy.json").write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_project(dest)

    def test_exposure_erasure_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "weft"
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "runs"))
            pilot = read_json(dest / "configs/pilot.json")
            pilot["exposure"] = "unseen"
            (dest / "configs/pilot.json").write_text(json.dumps(pilot), encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_project(dest)


class GitVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        path = self.repo / "analysis/research/registry.json"
        path.parent.mkdir(parents=True)
        blob = b'{"questions":[{"id":"A0"}]}'
        path.write_bytes(blob)
        self.git("add", ".")
        self.git("-c", "user.name=Weft fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        self.lock = {"schema_version":1, "repository":"https://github.com/xorca0711/ravel.git",
                     "commit":self.git("rev-parse", "HEAD").strip(), "question_ids":["A0"],
                     "files":[{"path":"analysis/research/registry.json", "sha256":hashlib.sha256(blob).hexdigest()}]}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True)

    def test_working_changes_are_ignored_and_preserved(self):
        path = self.repo / "analysis/research/registry.json"
        path.write_text("local work", encoding="utf-8")
        before = self.git("status", "--porcelain")
        self.assertTrue(verify_ravel(self.repo, self.lock)["ok"])
        self.assertEqual(before, self.git("status", "--porcelain"))
        self.assertEqual(path.read_text(), "local work")

    def test_hash_tamper_rejected(self):
        self.lock["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValidationError):
            verify_ravel(self.repo, self.lock)

    def test_absent_question_rejected(self):
        self.lock["question_ids"] = ["A99"]
        with self.assertRaises(ValidationError):
            verify_ravel(self.repo, self.lock)

    def test_unavailable_commit_rejected(self):
        self.lock["commit"] = "0" * 40
        with self.assertRaises(ValidationError):
            verify_ravel(self.repo, self.lock)


if __name__ == "__main__":
    unittest.main()
