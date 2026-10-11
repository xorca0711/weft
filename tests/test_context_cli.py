import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from weft.context import build_context
from weft.identity import digest
from weft.__main__ import main


class ContextTests(unittest.TestCase):
    def source(self, repo, *args):
        self.assertTrue(args[-1].startswith("a" * 40 + ":"))
        if args[-1].endswith("registry.json"):
            return json.dumps({"questions":[{"id":q,"card":"QUESTIONS.md#" + q,"dossier":"docs/" + q + ".md"} for q in ["A0","A1"]]}).encode()
        return b"### A0. First question\nFirst evidence.\n### A1. Second question\nOther evidence.\n"

    @patch("weft.context.verify_ravel")
    def test_all_questions_bound_to_committed_sections(self, verify):
        with patch("weft.context.git_read", side_effect=self.source) as read:
            result = build_context(Path("fixture"), {"commit":"a"*40,"repository":"fixture"})
        self.assertEqual(read.call_count, 2)  # registry plus one cached card blob
        self.assertEqual(len(result["questions"]), 2)
        self.assertNotIn("Second evidence", result["questions"][0]["canonical_section"])
        self.assertEqual(result["catalog_sha256"], digest(result["questions"]))
        verify.assert_called_once()

    @patch("weft.context.verify_ravel")
    def test_unknown_question_fails(self, verify):
        with patch("weft.context.git_read", side_effect=self.source):
            with self.assertRaises(ValueError):
                build_context(Path("fixture"), {"commit":"a"*40,"repository":"fixture"}, ["A99"])

    @patch("weft.context.verify_ravel", side_effect=ValueError("hash mismatch"))
    def test_pin_failure_cannot_build_context(self, verify):
        with self.assertRaises(ValueError):
            build_context(Path("fixture"), {"commit":"a"*40})


class CliTests(unittest.TestCase):
    def call(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(args)

    @patch("weft.__main__.build_context")
    def test_cap_rejected_before_context_or_network(self, context):
        self.assertEqual(self.call(["discover","--repo","unused","--profile","choi-pilot",
                                   "--until","2026-10-11","--max-records","201"]), 1)
        context.assert_not_called()

    @patch("weft.__main__.build_context")
    def test_unknown_profile_rejected_before_context_or_network(self, context):
        self.assertEqual(self.call(["discover","--repo","unused","--profile","unknown", "--until","2026-10-11"]), 1)
        context.assert_not_called()

    @patch("weft.__main__.discover")
    @patch("weft.__main__.build_context", return_value={"catalog_sha256":"fixture"})
    def test_priority_search_needs_completed_broad_window(self, context, discover):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self.call(["discover","--repo","unused","--profile","alveolar-transitions",
                                       "--stream","priority_journals","--since","2026-01-01","--until","2026-10-11",
                                       "--store",str(Path(root)/"store")]), 1)
        discover.assert_not_called()
