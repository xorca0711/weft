import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from weft import evidence, scientific
from weft.__main__ import main
from weft.jobs import validate_packet, JobError


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.inputs, self.sources, self.protected = [self.base / x for x in ('inputs', 'sources', 'ravel')]
        for path in (self.inputs, self.sources, self.protected): path.mkdir()
        (self.inputs / 'counts.csv').write_bytes(b'sample,value\ns1,10\ns2,12\n')
        (self.inputs / 'adapter.py').write_bytes(b'# synthetic code fixture; never executed\n')
        (self.inputs / 'environment.txt').write_bytes(b'synthetic immutable environment specification\n')
        (self.sources / 'paper.txt').write_bytes(b'SYNTHETIC: s1 and s2 are distinct units; both in control.\n')
        (self.sources / 'review.txt').write_bytes(b'SYNTHETIC design review fixture, not a human approval.\n')
        (self.protected / 'historical.txt').write_bytes(b'PRESERVE')
        self.ws = evidence.Workspace.create(self.base / 'workspace', inputs=self.inputs,
                                           sources=self.sources, protected_roots=[self.protected])
        self.aid, self.cid = 'wa-' + 'a' * 32, 'wc-' + 'b' * 32

    def file_ref(self, root, name):
        return {**evidence.reference(getattr(self, root), name), 'root': root}

    def base_record(self, kind):
        return {'schema_version': evidence.VERSION, 'kind': kind,
                'workspace_id': self.ws.binding['workspace_id'], 'article_id': self.aid,
                'revision': 1, 'previous': None, 'amendment_reason': None,
                'created_at': '2026-10-21T00:00:00Z',
                'actor': {'id': 'synthetic-test', 'kind': 'fixture', 'identity_basis': 'self-reported'},
                **evidence.FLAGS}

    def put(self, obj):
        return self.ws.put(evidence.encoded(obj))['record']

    def source(self):
        return {**self.base_record('source-manifest'),
                'bibliography': {'identifiers': ['fixture:paper'], 'title': 'Synthetic paper', 'integrity_status': 'synthetic-fixture'},
                'origin': None, 'resources': [{'resource_id': 'paper', 'version': 'fixture-v1',
                'locator': 'paper.txt:1', 'access': 'retained', 'inspection': 'inspected',
                'file': self.file_ref('sources', 'paper.txt'), 'limits': 'Synthetic bytes only'}]}

    def case(self, source_ref):
        return {**self.base_record('case-revision'), 'case_id': self.cid, 'source_manifest': source_ref,
                'purpose': 'description', 'analysis_mode': 'exploration', 'question': 'Describe synthetic values',
                'comparison': 's1 versus s2 descriptively', 'endpoint': 'Synthetic value',
                'inference_scope': 'descriptive', 'exposure': {'mode': 'synthetic-fixture',
                'note': 'Fictional source, units, code and review for software checks', 'evidence': []}, 'holds': []}

    def data(self, case_ref):
        citation = {'resource_id': 'paper', 'locator': 'paper.txt:1',
                    'file_sha256': self.file_ref('sources', 'paper.txt')['sha256']}
        return {**self.base_record('data-feasibility'), 'case_id': self.cid, 'case': case_ref,
                'files': [{'file': self.file_ref('inputs', 'counts.csv'), 'accession': 'fixture:counts',
                           'sample_ids': ['s1', 's2'], 'access_terms': 'Synthetic fixture', 'inspection': 'inspected'}],
                'units': [{'sample_id': s, 'unit_id': s, 'unit_kind': 'individual', 'condition': 'control',
                           'lineage': 'fixture:study', 'citations': [citation]} for s in ('s1', 's2')],
                'controls': [], 'replication_justification': None,
                'resources': {'memory_bytes': 1024, 'disk_bytes': 1024, 'wall_seconds': 1},
                'interpretation_limits': ['Synthetic description only'], 'unknowns': []}

    def plan(self, case_ref, data_ref):
        return {**self.base_record('analysis-contract'), 'case_id': self.cid, 'case': case_ref,
                'feasibility': data_ref, 'plan': {'comparison': 's1 versus s2 descriptively',
                'endpoint': 'Synthetic value', 'biological_unit': 'Synthetic individual', 'baseline': 'Fixture baseline',
                'methods': 'No execution; illustrative contract', 'reproduction_target': 'Not applicable: synthetic exploration',
                'uncertainty': 'No population claim', 'sensitivity': 'Illustrative sensitivity plan',
                'stop_rules': 'Stop at missing input', 'interpretation_limits': ['Synthetic description only']},
                'code_files': [self.file_ref('inputs', 'adapter.py')],
                'environment': self.file_ref('inputs', 'environment.txt'),
                'design_review': self.file_ref('sources', 'review.txt'),
                'outputs': [{'path': 'outputs/table.csv', 'role': 'table', 'description': 'Planned synthetic output'}],
                'limits': {'wall_seconds': 1, 'memory_bytes': 1024, 'disk_bytes': 1024,
                           'download_bytes': 0, 'max_attempts': 1, 'spend_usd': 0}}

    def prepare(self):
        sr = self.put(self.source())
        cr = self.put(self.case(sr))
        dr = self.put(self.data(cr))
        return sr, cr, dr

    def test_frozen_plan_and_preflight_never_execute(self):
        _, cr, dr = self.prepare()
        contract = self.plan(cr, dr)
        ref = self.put(contract)
        with patch('subprocess.run', side_effect=AssertionError('No process launch')):
            result = scientific.preflight(self.ws, ref)
        self.assertEqual(result['status'], 'hold')
        self.assertFalse(result['dispatch_authorized'])
        self.assertFalse((self.ws.root / 'control').exists())
        with self.assertRaises(JobError): validate_packet(contract)

    def test_same_bytes_idempotent_and_overwrite_rejected(self):
        obj = self.source(); self.put(obj)
        self.assertTrue(self.ws.put(evidence.encoded(obj))['idempotent'])
        obj['bibliography']['title'] = 'Replacement'
        with self.assertRaises(ValueError): self.put(obj)

    def test_tampered_input_and_code_fail_at_use(self):
        _, cr, dr = self.prepare()
        ref = self.put(self.plan(cr, dr))
        for filename in ('counts.csv', 'adapter.py'):
            path = self.inputs / filename; original = path.read_bytes()
            path.write_bytes(original + b'TAMPER')
            with self.assertRaises(ValueError): scientific.preflight(self.ws, ref)
            path.write_bytes(original)

    def test_new_source_holds_dependent_case(self):
        sr, _, _ = self.prepare()
        obj = self.source(); obj.update(revision=2, previous=sr, amendment_reason='Synthetic correction')
        self.put(obj)
        self.assertEqual(self.ws.status()['status'], 'hold')
        with self.assertRaises(ValueError): self.put(self.case(sr))

    def test_revision_fork_and_exposure_erasure_rejected(self):
        sr, cr, _ = self.prepare()
        obj = self.case(sr); obj.update(revision=2, previous=cr, amendment_reason='Fixture amendment')
        obj['exposure']['mode'] = 'prospective-test'
        with self.assertRaises(ValueError): self.put(obj)
        obj['exposure']['mode'] = 'synthetic-fixture'; obj['revision'] = 3
        with self.assertRaises(ValueError): self.put(obj)

    def test_current_revision_supersedes_without_historical_hold(self):
        sr = self.put(self.source()); obj = self.source()
        obj.update(revision=2, previous=sr, amendment_reason='Fixture revision')
        self.put(obj)
        status = self.ws.status()
        self.assertEqual(status['status'], 'recorded')
        self.assertEqual(status['records'][0]['assessment']['status'], 'historical')

    def test_canonical_and_execution_flags_and_id_rejected(self):
        sr = self.put(self.source())
        for field, value in [('dispatch_authorized', True), ('canonical_acceptance', True), ('case_id', 'A12'), ('status', 'integrated')]:
            obj = self.case(sr); obj[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.put(obj)

    def test_protected_or_existing_root_untouched(self):
        for path in (self.protected / 'new', self.protected, self.ws.root):
            with self.assertRaises(ValueError):
                evidence.Workspace.create(path, inputs=self.inputs, sources=self.sources, protected_roots=[self.protected])
        self.assertEqual((self.protected / 'historical.txt').read_bytes(), b'PRESERVE')
        self.assertFalse((self.protected / 'new').exists())

    def test_paths_links_and_aliases_rejected(self):
        for name in ('../paper.txt', 'C:/paper.txt', '/paper.txt', 'a\\paper.txt', 'CON', 'a./file', 'PAPER.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError): evidence.contained(self.sources, name)
        try: (self.sources / 'alias.txt').symlink_to(self.sources / 'paper.txt')
        except OSError: return  # Path/link cases still run on hosts without link permission.
        with self.assertRaises(ValueError): evidence.reference(self.sources, 'alias.txt')

    def test_same_sample_or_file_not_counted_twice(self):
        sr = self.put(self.source()); cr = self.put(self.case(sr))
        for field in ('files', 'units'):
            obj = self.data(cr); obj[field].append(copy.deepcopy(obj[field][0]))
            with self.assertRaises(ValueError): self.put(obj)

    def test_pooled_description_limited_and_replicated_claim_held(self):
        sr = self.put(self.source()); obj = self.case(sr); cr = self.put(obj)
        data = self.data(cr)
        for unit in data['units']: unit['unit_kind'] = 'pool'
        self.assertEqual(self.ws.validate(data)['status'], 'limited')
        obj.update(revision=2, previous=cr, amendment_reason='Fixture change of inference', inference_scope='replicated-population')
        cr2 = self.put(obj); data['case'] = cr2
        result = self.ws.validate(data)
        self.assertEqual(result['status'], 'held')
        self.assertIsNone(result['permitted_inference'])

    def test_reused_units_are_not_replicates(self):
        sr = self.put(self.source()); obj = self.case(sr); obj['inference_scope'] = 'replicated-population'
        cr = self.put(obj); data = self.data(cr); data['replication_justification'] = 'Fixture assertion'
        for unit in data['units']: unit['unit_id'] = 'same-donor'
        result = self.ws.validate(data)
        self.assertEqual(result['distinct_units_by_condition'], {'control': 1})
        self.assertEqual(result['status'], 'held')

    def test_missing_metadata_or_inspection_holds_freeze(self):
        sr = self.put(self.source()); cr = self.put(self.case(sr)); data = self.data(cr)
        data['files'][0]['inspection'] = 'metadata-only'
        dr = self.put(data)
        self.assertEqual(self.ws.validate(data)['status'], 'held')
        with self.assertRaises(ValueError): self.put(self.plan(cr, dr))

    def test_false_source_citation_and_sample_omission_rejected(self):
        sr = self.put(self.source()); cr = self.put(self.case(sr))
        obj = self.data(cr); obj['units'][0]['citations'][0]['file_sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.put(obj)
        obj = self.data(cr); obj['units'].pop()
        with self.assertRaises(ValueError): self.put(obj)

    def test_contract_cannot_drop_limits_or_expand_claim(self):
        _, cr, dr = self.prepare()
        for field, value in [('comparison', 'Different contrast'), ('interpretation_limits', [])]:
            obj = self.plan(cr, dr); obj['plan'][field] = value
            with self.assertRaises(ValueError): self.put(obj)
        for field, value in [('memory_bytes', 512), ('spend_usd', 1)]:
            obj = self.plan(cr, dr); obj['limits'][field] = value
            with self.assertRaises(ValueError): self.put(obj)

    def test_copy_is_readable_but_inactive(self):
        self.prepare(); dest = self.base / 'copy'; shutil.copytree(self.ws.root, dest)
        copied = evidence.Workspace(dest)
        self.assertFalse(copied.status()['writable_here'])
        with self.assertRaises(ValueError): copied.put(evidence.encoded(self.source()))

    def test_interrupted_write_is_retained_not_replaced(self):
        obj = self.source(); target = self.ws.root / evidence.record_path(obj)
        target.parent.mkdir(parents=True); target.write_bytes(b'{partial')
        with self.assertRaises(ValueError): self.put(obj)
        self.assertEqual(target.read_bytes(), b'{partial')

    def test_strict_json_and_timestamp(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.assertRaises(ValueError): evidence.decode(raw)
        obj = self.source(); obj['created_at'] = '2026-10-21T00:00:00'
        with self.assertRaises(ValueError): self.put(obj)

    def test_tampered_predecessor_holds_current_revision(self):
        sr = self.put(self.source()); obj = self.source()
        obj.update(revision=2, previous=sr, amendment_reason='Fixture amendment')
        self.put(obj)
        path = self.ws.root / sr['path']
        changed = self.source(); changed['bibliography']['title'] = 'Tampered predecessor'
        path.write_bytes(evidence.encoded(changed))
        self.assertEqual(self.ws.status()['status'], 'hold')

    def test_hardlinked_lock_cannot_write_outside_workspace(self):
        outside = self.protected / 'empty'; outside.write_bytes(b'')
        os.link(outside, self.ws.root / '.workflow.lock')
        with self.assertRaises(ValueError): self.put(self.source())
        self.assertEqual(outside.read_bytes(), b'')

    def test_cli_and_read_only_status(self):
        _, cr, dr = self.prepare(); ref = self.put(self.plan(cr, dr))
        path = self.base / 'ref.json'; path.write_bytes(evidence.encoded(ref))
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.ws.root.rglob('*') if p.is_file()}
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = main(['evidence-preflight', '--root', str(self.ws.root), '--contract-reference', str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['status'], 'hold')
        after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.ws.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
