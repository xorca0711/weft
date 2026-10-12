"""Prepare private review proposals, never publish to or authorize work in Ravel."""
import hashlib
import json
from pathlib import Path

from . import batches, qualification
from .identity import digest


FLAGS = {'claim_validated': False, 'scientific_execution_allowed': False,
         'automatic_integration_allowed': False, 'publication_authorized': False}


def _bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _contents(store, batch_id, candidate_id, scope):
    if scope not in {'data_review', 'rq_review'}:
        raise ValueError('Choose data_review or rq_review explicitly')
    summary = qualification.summary(store, batch_id, candidate_id)
    proposal = 'data_proposal' if scope == 'data_review' else 'rq_proposal'
    if not summary or not summary['current'] or summary.get(proposal) != 'review_required' or summary.get('coverage_holds'):
        raise ValueError('Current scope-specific review-required proposal needed; held/unreviewed evidence cannot transfer')
    row = store.db.execute('SELECT record_json,packet_sha FROM evidence_reviews WHERE record_sha=?',
                           (summary['record_sha256'],)).fetchone()
    saved = store.db.execute('SELECT packet_json FROM evidence_packets WHERE packet_sha=?', (row['packet_sha'],)).fetchone()
    packet = json.loads(saved[0])
    spec = batches.specification(store, batch_id)
    provenance = {key: packet[key] for key in ['batch_id', 'candidate_id', 'paper_key',
                  'context_sha256', 'evidence_sha256', 'source_sha256',
                  'reading_packet_sha256', 'reading_assessment_sha256',
                  'coverage_scope', 'compatibility_scope']}
    provenance.update(packet_sha256=row['packet_sha'], ravel_commit=spec['context']['ravel_commit'])
    # No source text/figures, catalog database, private recovery records or arbitrary files.
    # Free-text reviewer fields may still be private: this is NOT privacy-cleared output.
    files = {'review.json': _bytes(json.loads(row['record_json'])),
             'summary.json': _bytes(summary), 'provenance.json': _bytes(provenance)}
    files['README.md'] = (
        '# Weft intake proposal — private staging\n\n'
        f'Review scope: `{scope}`. Status: awaiting publication and Ravel review.\n\n'
        'A review-required proposal is not eligibility approval, scientific acceptance,\n'
        'an execution permit or a new canonical RQ. All other scope holds remain.\n'
        'Review free-text fields for privacy and source-text redistribution before export.\n'
        'No full text, figure, supplement, dataset or analysis output is bundled.\n'
    ).encode('utf-8')
    manifest = {'schema_version': 1, 'kind': 'weft-private-intake-proposal',
                'scope': scope, 'status': 'awaiting_publication_review',
                'batch_id': batch_id, 'candidate_id': candidate_id,
                'record_sha256': summary['record_sha256'], 'packet_sha256': row['packet_sha'],
                'proposed_ravel_path': 'weft_intake/paper-' + digest(packet['paper_key'])[:16]
                    + '/' + summary['record_sha256'] + '/' + scope + '/',
                'files': {name: {'bytes': len(body), 'sha256': _sha(body)} for name, body in files.items()},
                **FLAGS}
    files['manifest.json'] = _bytes(manifest)
    if sum(map(len, files.values())) > 2_000_000:
        raise ValueError('Proposal exceeds 2 MB staging bound')
    directory = store.root / 'intake-staging' / summary['record_sha256'] / scope
    return directory, files


def _safe_path(store, directory):
    relative = directory.relative_to(store.root)
    current = store.root
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ValueError('Intake staging cannot traverse links/junctions')
    if not directory.resolve().is_relative_to(store.root):
        raise ValueError('Intake staging escaped catalog')


def prepare(store, batch_id, candidate_id, scope):
    with batches.exclusive(store):
        directory, files = _contents(store, batch_id, candidate_id, scope)
        _safe_path(store, directory)
        directory.mkdir(parents=True, exist_ok=False)
        for name, body in files.items():
            with (directory / name).open('xb') as target:
                target.write(body)
        return {'status': 'private_staging_only', 'directory': str(directory),
                'manifest_sha256': _sha(files['manifest.json']), 'members': len(files), **FLAGS}


def verify(store, batch_id, candidate_id, scope, directory, manifest_sha256):
    with batches.exclusive(store):
        expected, files = _contents(store, batch_id, candidate_id, scope)
        directory = Path(directory).absolute()
        if directory != expected:
            raise ValueError('Not the current proposal staging path')
        _safe_path(store, directory)
        if set(p.name for p in directory.iterdir()) != set(files):
            raise ValueError('Unexpected or missing intake members')
        if _sha(files['manifest.json']) != manifest_sha256:
            raise ValueError('Manifest anchor does not match current review')
        for name, body in files.items():
            path = directory / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size != len(body) or path.read_bytes() != body:
                raise ValueError('Changed intake member: ' + name)
        return {'status': 'verified_private_proposal', 'members': len(files),
                'manifest_sha256': manifest_sha256, **FLAGS}
