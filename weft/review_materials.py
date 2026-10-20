"""Bounded local source bundles and route receipts for assisted review.

No retrieval, rendering, inspection attestation, permission inference or dispatch.
PDF/image locators describe supplied inspection records; only bytes are verified.
"""
import hashlib
import json
import re
from urllib.parse import urlsplit

from . import evaluation as e
from .materials import _local_file
from .qualification import MAX_ARTIFACT, MAX_TOTAL, _format

RECORD_ROLES = {'authority', 'access_receipt', 'review_record'}
ROLES = {'full_text', 'derived_text', 'figure', 'supplement'} | RECORD_ROLES
ROUTES = {'public_http', 'institutional_browser', 'publisher_api', 'manual_local'}
OUTCOMES = {'retrieved', 'blocked', 'rate_limited', 'redirect_failed', 'metadata_only',
            'download_failed', 'unavailable', 'unknown'}
RESERVED = {'packet.json', 'human-response-template.json', 'report.json', 'human-response.json',
            'review.md', 'index.html', 'manifest.json'}


def portable(name, paths):
    if not isinstance(name, str):
        raise ValueError('Portable relative source path required')
    parts = name.split('/')
    devices = {'con', 'prn', 'aux', 'nul'} | {p + str(n) for p in ('com', 'lpt') for n in range(1, 10)}
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._#-]*', p) or p != p.rstrip(' .')
           or p.split('.')[0].casefold() in devices for p in parts):
        raise ValueError('Canonical portable source path components required')
    if parts[0].casefold() in RESERVED:
        raise ValueError('Source path collides with a reserved export filename')
    alias = name.casefold()
    for previous, spelling in paths.items():
        if alias == previous and name != spelling:
            raise ValueError('Source path aliases another source')
        if alias.startswith(previous + '/') or previous.startswith(alias + '/'):
            raise ValueError('Source file/directory paths collide')
    paths[alias] = name


def public_url(value):
    e._text(value, 'public source URL')
    url = urlsplit(value)
    if url.scheme != 'https' or not url.hostname or url.username or url.password:
        raise ValueError('Explicit public HTTPS source URL required')


def load(case, root, paths, budget, pointer):
    entries = case['materials']
    if not isinstance(entries, list) or not 1 <= len(entries) <= 64:
        raise ValueError('One to 64 explicit local materials required per case')
    view, retained = {}, []
    for item in entries:
        e._keys(item, {'material_id', 'path', 'sha256', 'bytes', 'format', 'role', 'paper_key',
                      'origin', 'version', 'coverage', 'inspection', 'derived_from'}, 'review material')
        mid = item['material_id']
        if not isinstance(mid, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', mid) or mid in view:
            raise ValueError('Unique bounded material ID required')
        if item['paper_key'] != case['paper_key']:
            raise ValueError('Material paper binding differs from its case')
        for key in ('role', 'format', 'origin', 'version', 'coverage'):
            e._text(item[key], 'material ' + key)
        if item['role'] not in ROLES or item['format'] not in {'txt', 'json', 'pdf', 'png', 'jpeg'}:
            raise ValueError('Unsupported review material role/format')
        if item['role'] not in RECORD_ROLES:
            public_url(item['origin'])
        if item['role'] in RECORD_ROLES and item['format'] != 'json':
            raise ValueError('Authority, review and access records require JSON')
        if item['role'] == 'figure' and item['format'] not in {'png', 'jpeg', 'pdf'}:
            raise ValueError('Figure pixels require an image/PDF material')
        if item['role'] == 'derived_text' and item['format'] != 'txt':
            raise ValueError('Derived text must be an explicit UTF-8 text file')
        inspection = item['inspection']
        e._keys(inspection, {'status', 'actor', 'scope'}, 'material inspection')
        e._text(inspection['status'], 'inspection status'); e._text(inspection['scope'], 'inspection scope')
        allowed = {'not_reviewed', 'text_reviewed', 'pixels_reviewed', 'text_and_selected_pixels'}
        if inspection['status'] not in allowed:
            raise ValueError('Unknown inspection status')
        if inspection['status'] == 'not_reviewed':
            if inspection['actor'] is not None:
                raise ValueError('Unreviewed material cannot name an inspecting actor')
        else:
            e._text(inspection['actor'], 'declared inspecting actor')
        if ('pixels' in inspection['status'] and item['format'] not in {'pdf', 'png', 'jpeg'}):
            raise ValueError('Text/captions cannot establish pixel inspection')
        if item['format'] in {'png', 'jpeg'} and inspection['status'] == 'text_reviewed':
            raise ValueError('Image pixels are not a text source')
        portable(item['path'], paths)
        local = _local_file(root, item['path'])
        e._sha(item['sha256'], 'material hash')
        if type(item['bytes']) is not int or not 0 < item['bytes'] <= MAX_ARTIFACT:
            raise ValueError('Material byte size must be within the existing 32 MiB cap')
        with local.open('rb') as handle:
            body = handle.read(MAX_ARTIFACT + 1)
        if len(body) != item['bytes'] or hashlib.sha256(body).hexdigest() != item['sha256']:
            raise ValueError('Material bytes/hash differ from the record')
        budget['bytes'] += len(body); budget['count'] += 1
        if budget['bytes'] > MAX_TOTAL or budget['count'] > 256:
            raise ValueError('Review bundle exceeds 256 MiB / 256 material records')
        if item['format'] == 'json':
            if len(body) > 1_000_000:
                raise ValueError('Review JSON record exceeds 1 MB')
            content = json.loads(body)
            e.fingerprint(content)  # rejects nonfinite values
        else:
            if _format(body, local.suffix) != item['format']:
                raise ValueError('Material signature/format mismatch')
            content = body.decode('utf-8-sig').splitlines() if item['format'] == 'txt' else None
        parents = item['derived_from']
        if not isinstance(parents, list) or any(not isinstance(p, str) for p in parents) or len(parents) != len(set(parents)):
            raise ValueError('Explicit distinct derivation parents required')
        if bool(parents) != (item['role'] == 'derived_text'):
            raise ValueError('Only derived text must declare its original material')
        view[mid] = {'content': content, 'inspection': inspection, 'coverage': item['coverage'],
                     'version': item['version'], 'sha256': item['sha256'], 'role': item['role']}
        retained.append((item, body))
    by_id = {item['material_id']: item for item, _ in retained}
    for item, _ in retained:
        for parent in item['derived_from']:
            if parent not in by_id or by_id[parent]['role'] not in {'full_text', 'supplement'}:
                raise ValueError('Derived text must bind an original full text or supplement in the same case')
    document = {'materials': view}
    attempts = case['access_attempts']
    if not isinstance(attempts, list) or len(attempts) > 64:
        raise ValueError('Bounded access-attempt list required')
    seen = set()
    for attempt in attempts:
        e._keys(attempt, {'attempt_id', 'route', 'source_url', 'observed_at', 'outcome',
                         'http_status', 'material_ids', 'receipt_locator', 'notes'}, 'access attempt')
        for key in ('attempt_id', 'route', 'outcome', 'notes', 'receipt_locator'):
            e._text(attempt[key], key)
        if attempt['attempt_id'] in seen or attempt['route'] not in ROUTES or attempt['outcome'] not in OUTCOMES:
            raise ValueError('Invalid or duplicate source-access attempt')
        seen.add(attempt['attempt_id'])
        public_url(attempt['source_url']); e._time(attempt['observed_at'], 'access observation')
        status = attempt['http_status']
        if status is not None and (type(status) is not int or not 100 <= status <= 599):
            raise ValueError('HTTP status must be unknown or an actual status code')
        mids = attempt['material_ids']
        if (not isinstance(mids, list) or any(not isinstance(mid, str) or mid not in by_id for mid in mids)
                or len(mids) != len(set(mids))):
            raise ValueError('Access attempt must name retained material IDs')
        if attempt['outcome'] == 'retrieved' and (not mids or status is not None and status != 200):
            raise ValueError('Retrieved outcome needs retained bytes and a compatible HTTP status')
        if attempt['outcome'] == 'retrieved' and any(by_id[mid]['role'] in RECORD_ROLES for mid in mids):
            raise ValueError('A receipt or human decision is not retrieved paper material')
        match = re.match(r'^/materials/([^/]+)/content(?:/|$)', attempt['receipt_locator'])
        if not match or match[1] not in by_id or by_id[match[1]]['role'] != 'access_receipt':
            raise ValueError('Access attempt needs a bound receipt locator')
        pointer(document, attempt['receipt_locator'])
    return view, retained


def summary(case):
    return {'material_count': len(case['materials']),
            'declared_inspected_materials': sum(m['inspection']['status'] != 'not_reviewed' for m in case['materials']),
            'access_attempts': [{k: a[k] for k in ('attempt_id', 'route', 'outcome', 'http_status', 'material_ids')}
                                for a in case['access_attempts']],
            'inspection_is_attested': True, 'semantic_support_verified': False,
            'access_failure_is_relevance_rejection': False,
            'institutional_permission_failure_inferred': False,
            'automatic_cloud_access_qualified': False}
