"""Retained synthetic visual example; uses test builders, never author code."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_science_pipeline import SciencePipelineTests
from weft import evidence as ev, science_review as review


def create(directory):
    directory = ev.unlinked(directory)
    if not directory.is_absolute() or directory.exists() or not directory.parent.is_dir():
        raise ValueError('Fresh absolute demo directory with existing parent required')
    directory.mkdir()
    fixture = SciencePipelineTests()
    fixture.base = directory.resolve()
    fixture.inputs, fixture.sources, fixture.protected = [directory / x for x in ('inputs', 'sources', 'protected-fixture')]
    for path in (fixture.inputs, fixture.sources, fixture.protected): path.mkdir()
    (fixture.inputs / 'counts.csv').write_bytes(b'sample,value\ns1,10\ns2,12\n')
    (fixture.inputs / 'adapter.py').write_bytes(b'# Synthetic placeholder; never executed\n')
    (fixture.inputs / 'environment.txt').write_bytes(b'Synthetic offline fixture specification\n')
    (fixture.sources / 'paper.txt').write_bytes(b'SYNTHETIC ONLY: s1 and s2 are distinct units. Illustrative reference quantity 11.\n')
    (fixture.sources / 'review.txt').write_bytes(b'Synthetic supplied review fixture, not a human approval.\n')
    (fixture.protected / 'historical.txt').write_bytes(b'PRESERVE')
    fixture.ws = ev.Workspace.create(directory / 'workspace', inputs=fixture.inputs,
                                     sources=fixture.sources, protected_roots=[fixture.protected])
    fixture.aid, fixture.cid = 'wa-' + 'a' * 32, 'wc-' + 'b' * 32
    measurements = fixture.measurement()
    measurements['metrics'][0]['value'] = 10.5  # Deliberate discrepancy, not a computed scientific result.
    receipt = fixture.finish(measurements)
    critique = fixture.critique(receipt)
    critique['issues'][0]['comment'] = 'Returned fixture mean 10.5 differs from the frozen illustrative target 11. Investigate the calculation before interpreting it.'
    critique['issues'][0]['severity'] = 'blocking'
    critique['issues'][0]['evidence'] = [fixture.ws.file(receipt, parse=True)['outputs'][0]['file']]
    critique_ref = fixture.put(critique)
    page = review.view(fixture.ws, receipt, critique_ref)['view']
    export = review.dry_export(fixture.ws, receipt, critique_ref, 'Inspect the provisional fixture workflow only')['export']
    result = {'status': 'synthetic-example-created', 'view': str(fixture.ws.file(page)),
              'workspace': str(fixture.ws.root), 'receipt': receipt, 'review': critique_ref,
              'qc': review.qc(fixture.ws, receipt), 'export': export,
              'verification': review.verify_export(fixture.ws.file(export), export['sha256']),
              'author_code_executed': False, **ev.FLAGS}
    ev.write_new(directory / 'demo-result.json', ev.encoded(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path)
    args = parser.parse_args()
    result = create(args.directory)
    print(json.dumps({k: result[k] for k in ('status', 'view', 'workspace', 'author_code_executed', *ev.FLAGS)}, indent=2))
