import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from weft import author_canary as canary


class AuthorCanaryTests(unittest.TestCase):
    def test_default_all_modes_only_plan(self):
        with patch.object(canary, 'execute', side_effect=AssertionError('No default execution')):
            for mode in canary.MODES:
                output = io.StringIO()
                with contextlib.redirect_stdout(output): self.assertEqual(canary.main([mode]), 0)
                self.assertFalse(json.loads(output.getvalue())['runtime_qualified'])

    def test_success_fixture_is_exclusive_and_not_enforcement_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            result = canary.execute('success', temp)
            self.assertTrue((Path(temp)/'canary.json').is_file())
            self.assertIsNone(result['error']); self.assertFalse(result['enforcement_verified'])
            self.assertEqual(canary.execute('success', temp)['error']['type'], 'FileExistsError')

    def test_failure_has_distinct_exit_code(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(canary.main(['failure', '--execute']), 17)

    def test_byte_probe_handles_enospc_without_claiming_quota(self):
        with tempfile.TemporaryDirectory() as temp, patch('os.fsync', side_effect=OSError(28, 'fixture')):
            result = canary.execute('output', temp)
        self.assertEqual(result['error']['errno'], 28)
        self.assertFalse(result['enforcement_verified'])


if __name__ == '__main__': unittest.main()
