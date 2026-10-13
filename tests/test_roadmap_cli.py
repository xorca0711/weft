"""Offline CLI boundaries; synthetic judgments never qualify real screening."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from weft.__main__ import main
from weft import evaluation
from tests.test_evaluation import plan_fixture, judgment_fixture


class RoadmapCliTests(unittest.TestCase):
    def call(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(args)
        return status, json.loads(stdout.getvalue() or stderr.getvalue())

    def write(self, root, name, data):
        path = root / name
        path.write_text(json.dumps(data), encoding='utf-8')
        return str(path)

    @patch('weft.__main__.coverage.audit_profiles', return_value={'scope': 'configuration-coverage-only'})
    @patch('weft.__main__.build_context', return_value={'questions': ['all-pinned-questions']})
    def test_coverage_uses_full_pinned_context_without_rq_filter(self, context, audit):
        status, result = self.call(['profile-coverage', '--repo', 'fixture'])
        self.assertEqual(status, 0)
        self.assertEqual(len(context.call_args.args), 2)
        self.assertEqual(context.call_args.kwargs, {})
        self.assertEqual(audit.call_args.args[1], context.return_value)
        self.assertEqual(result['scope'], 'configuration-coverage-only')

    @patch('weft.__main__.evaluation.evaluate')
    def test_hash_mismatch_fails_before_judgments_are_read_or_evaluated(self, score):
        with tempfile.TemporaryDirectory() as directory:
            plan = self.write(Path(directory), 'plan.json', plan_fixture())
            status, result = self.call(['evaluation-score', '--plan', plan, '--plan-sha256', 'f'*64,
                                       '--predictions', 'absent.json', '--references', 'absent.json'])
        self.assertEqual(status, 1)
        self.assertIn('frozen canonical JSON hash', result['error'])
        score.assert_not_called()

    def test_synthetic_plan_and_score_end_to_end_without_overwriting_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = plan_fixture()
            plan_path = self.write(root, 'plan.json', plan)
            predictions = self.write(root, 'predictions.json', [judgment_fixture(plan)])
            references = self.write(root, 'references.json', [judgment_fixture(plan, True)])
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            status, frozen = self.call(['evaluation-plan', '--plan', plan_path])
            self.assertEqual(status, 0)
            self.assertEqual(frozen['plan_sha256'], evaluation.fingerprint(plan))
            status, result = self.call(['evaluation-score', '--plan', plan_path,
                                       '--plan-sha256', frozen['plan_sha256'],
                                       '--predictions', predictions, '--references', references])
            self.assertEqual(status, 0)
            self.assertEqual(result['metrics']['reading']['paired_items'], 1)
            self.assertEqual(list(result['exposure_strata']), ['synthetic'])
            for flag in evaluation.FLAGS:
                self.assertIs(result[flag], False)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_plan_command_rejects_missing_owner_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = plan_fixture()
            del plan['owner_review']
            path = self.write(Path(directory), 'plan.json', plan)
            status, result = self.call(['evaluation-plan', '--plan', path])
        self.assertEqual(status, 1)
        self.assertIn('fields', result['error'])
