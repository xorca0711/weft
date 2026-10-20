"""Verified material reuse and explicit local intake. No URL retrieval or inspection attestation."""
import hashlib
import json
from pathlib import Path

from . import batches, qualification, screening
from .identity import digest
from .reading_locations import check_files


def reusable(store, bid, cid):
    rows = store.db.execute('''SELECT bi.candidate_id,bi.reading_json FROM batch_items bi
        JOIN candidates donor ON donor.id=bi.candidate_id JOIN candidates target ON target.id=?
        WHERE bi.batch_id=? AND bi.candidate_id!=? AND donor.current=1
        AND donor.paper_key=target.paper_key AND donor.evidence_sha=target.evidence_sha
        AND bi.reading_json IS NOT NULL ORDER BY bi.candidate_id''', (cid, bid, cid)).fetchall()
    prepared = [(r['candidate_id'], json.loads(r['reading_json'])) for r in rows
                if json.loads(r['reading_json']).get('status') == 'prepared']
    if len({r['source_sha256'] for _, r in prepared}) > 1:
        raise ValueError('Conflicting cached XML versions; explicit source reconciliation required')
    return prepared[0][0] if prepared else None


def cached_xml(store, target_id, bid, donor_id):
    if target_id == donor_id:
        raise ValueError('Cannot use material reuse to retry the same reading')
    items = {}
    candidates = {}
    for cid in (target_id, donor_id):
        item = store.db.execute('SELECT * FROM batch_items WHERE batch_id=? AND candidate_id=?', (bid, cid)).fetchone()
        if not item or not item['packet_json']:
            raise ValueError('Reuse requires two issued packets in the same batch')
        candidates[cid] = screening.live_candidate(store, screening.stored_packet(item))
        items[cid] = item
    target, donor = candidates[target_id], candidates[donor_id]
    if (target['paper_key'], target['evidence_sha']) != (donor['paper_key'], donor['evidence_sha']):
        raise ValueError('Cached material differs from the target paper/evidence snapshot')
    read = json.loads(items[donor_id]['reading_json'] or '{}')
    if read.get('status') != 'prepared':
        raise ValueError('Prepared cached source required')
    directory = check_files(store, read)
    body = (directory / 'source.xml').read_bytes()
    if hashlib.sha256(body).hexdigest() != read['source_sha256']:
        raise ValueError('Cached source changed during reuse')
    return body, {'kind': 'cached_xml', 'batch_id': bid, 'donor_candidate_id': donor_id,
                  'source_sha256': read['source_sha256'], 'evidence_sha256': donor['evidence_sha'],
                  'shared_source': True, 'assessment_reused': False}


def _local_file(root, relative):
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
            or relative.startswith('/') or any(p in {'', '.', '..'} for p in relative.split('/'))):
        raise ValueError('Artifact path must be a contained relative path')
    path = root
    for component in relative.split('/'):
        path = path / component
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError('Linked material paths are not allowed')
    if not path.resolve(strict=True).is_relative_to(root) or not path.is_file():
        raise ValueError('Regular contained material required')
    return path


def import_manifest(store, bid, cid, manifest_path):
    """Validate the entire manifest before intake; exact retries reuse attachment IDs.

    A partial import may retain valid immutable attachments. No inspection or
    review disposition is changed, including after an interrupted acknowledgement.
    """
    path = Path(manifest_path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
        raise ValueError('Regular material manifest below 1 MB required')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    fields = {'schema_version', 'batch_id', 'candidate_id', 'packet_sha256', 'artifacts'}
    if (not isinstance(manifest, dict) or set(manifest) != fields or type(manifest['schema_version']) is not int
            or manifest['schema_version'] != 1 or manifest['batch_id'] != bid or manifest['candidate_id'] != cid
            or not isinstance(manifest['artifacts'], list) or not 1 <= len(manifest['artifacts']) <= 64):
        raise ValueError('Invalid bounded material manifest identity')
    root = path.resolve().parent
    prepared = []
    with batches.exclusive(store):
        packet = qualification._packet(store, bid, cid)
        if manifest['packet_sha256'] != digest(packet):
            raise ValueError('Material manifest refers to a different evidence packet')
        resources = {r['resource_id'] for r in packet['resources']}
        seen = set()
        total = 0
        existing = {r['id']: json.loads(r['metadata_json']) for r in store.db.execute(
            'SELECT id,metadata_json FROM evidence_artifacts WHERE packet_sha=?', (digest(packet),))}
        for item in manifest['artifacts']:
            if not isinstance(item, dict) or set(item) != {'resource_id', 'path', 'sha256', 'bytes', 'origin'}:
                raise ValueError('Artifact manifest fields differ from the contract')
            qualification._text(item['origin'], 'origin')
            if item['resource_id'] not in resources:
                raise ValueError('Unknown material resource')
            local = _local_file(root, item['path'])
            with local.open('rb') as handle:
                body = handle.read(qualification.MAX_ARTIFACT + 1)
            if (not body or len(body) > qualification.MAX_ARTIFACT or type(item['bytes']) is not int
                    or len(body) != item['bytes'] or hashlib.sha256(body).hexdigest() != item['sha256']):
                raise ValueError('Material bytes/hash differ from manifest or exceed cap')
            fmt = qualification._format(body, local.suffix)
            meta = {'packet_sha256': digest(packet), 'resource_id': item['resource_id'], 'sha256': item['sha256'],
                    'bytes': len(body), 'format': fmt, 'origin': item['origin']}
            aid = digest(meta)
            if aid in seen:
                raise ValueError('Duplicate artifact in manifest')
            seen.add(aid)
            if aid not in existing:
                total += len(body)
            prepared.append((item, local, aid))
        if len(set(existing) | seen) > 64 or sum(m['bytes'] for m in existing.values()) + total > qualification.MAX_TOTAL:
            raise ValueError('Material manifest exceeds existing per-packet evidence cap')
    results = []
    # Existing attach owns its lock and revalidates source and file bytes. A
    # second digest check below prevents a changed file being accepted as this manifest.
    for item, local, expected_id in prepared:
        result = qualification.attach(store, bid, cid, item['resource_id'], local, item['origin'],
                                      expected_sha256=item['sha256'])
        if result['artifact_id'] != expected_id:
            raise ValueError('Material changed after manifest validation')
        results.append(result)
    return {'status': 'imported', 'manifest_sha256': digest(manifest), 'artifacts': results,
            'inspection_attested': False, 'scientific_execution_allowed': False, 'claim_validated': False}


def inventory(store, bid, cid):
    """Read-only resource/attachment view with source and inspection scope separate."""
    packet = qualification._packet(store, bid, cid)
    summary = qualification.summary(store, bid, cid)
    record = None
    if summary and summary.get('record_sha256'):
        row = store.db.execute('SELECT record_json FROM evidence_reviews WHERE record_sha=?', (summary['record_sha256'],)).fetchone()
        record = json.loads(row[0])
    coverage = {r['resource_id']: r for r in record['coverage']} if record else {}
    resources = []
    for resource in packet['resources']:
        assets = []
        for row in store.db.execute('SELECT id FROM evidence_artifacts WHERE packet_sha=? AND resource_id=? ORDER BY id',
                                    (digest(packet), resource['resource_id'])):
            try:
                meta = qualification._artifact(store, digest(packet), resource['resource_id'], row['id'])
                assets.append({'artifact_id': row['id'], 'status': 'verified_bytes', **meta})
            except (ValueError, OSError, KeyError, TypeError) as exc:
                assets.append({'artifact_id': row['id'], 'status': 'hold', 'reason': str(exc)})
        resources.append({**resource, 'coverage': coverage.get(resource['resource_id'], {
            'resource_id': resource['resource_id'], 'status': 'not_inspected', 'artifact_id': None,
            'inspection_note': 'No recorded inspection assessment'}), 'attachments': assets})
    read_row = store.db.execute('SELECT reading_json,reading_result_json FROM batch_items WHERE batch_id=? AND candidate_id=?', (bid, cid)).fetchone()
    return {'schema_version': 1, 'batch_id': bid, 'candidate_id': cid, 'packet_sha256': digest(packet),
            'packet': packet, 'resources': resources, 'summary': summary, 'assessment': record,
            'reading_assessment': json.loads(read_row['reading_result_json']),
            'source_acquisition': json.loads(read_row['reading_json']).get('source_acquisition', {'kind': 'historical_receipt'}),
            'private': True, 'claim_validated': False, 'scientific_execution_allowed': False,
            'inspection_is_actor_attested': True, 'semantic_support_verified': False}
