"""Offline feasibility and frozen-plan checks; no scientific execution authority."""
from __future__ import annotations

from .evidence import COMMON, FLAGS, keys, text, string_list, relative


def _case(workspace, record):
    case = workspace.bound_record(record['case'], 'case-revision', case=record)
    workspace.validate(case)
    source = workspace.bound_record(case['source_manifest'], 'source-manifest', case=case)
    workspace.validate(source)
    return case, source


def _positive(value, *, zero=False):
    if type(value) is not int or not (0 if zero else 1) <= value <= 2**63 - 1:
        raise ValueError('Finite nonnegative/positive integer bound required')


def feasibility(workspace, record):
    keys(record, COMMON | {'article_id', 'case_id', 'case', 'files', 'units',
                          'controls', 'replication_justification', 'resources',
                          'interpretation_limits', 'unknowns'})
    case, source = _case(workspace, record)
    holds = list(case['holds'])
    if source['bibliography']['integrity_status'] in {'unknown', 'concern-recorded'}:
        holds.append('Source integrity review unresolved')
    if not isinstance(record['files'], list) or not 1 <= len(record['files']) <= 256:
        raise ValueError('Bounded actual input inventory required')
    sample_ids, identities = set(), set()
    for entry in record['files']:
        keys(entry, {'file', 'accession', 'sample_ids', 'access_terms', 'inspection'})
        text(entry['accession'])
        string_list(entry['sample_ids'], nonempty=True)
        sample_ids.update(entry['sample_ids'])
        workspace.file(entry['file'])
        identity = (entry['file']['root'], entry['file']['path'].casefold())
        if identity in identities: raise ValueError('Duplicate input file')
        identities.add(identity)
        if entry['access_terms'] is None: holds.append('Input access terms unresolved')
        else: text(entry['access_terms'])
        if entry['inspection'] not in {'metadata-only', 'inspected'}:
            raise ValueError('Unknown data inspection state')
        if entry['inspection'] != 'inspected': holds.append('Actual input contents not inspected')
    if not isinstance(record['units'], list) or not 1 <= len(record['units']) <= 10000:
        raise ValueError('Bounded sample/unit map required')
    resources = {r['resource_id']: r for r in source['resources']}
    samples, groups, unit_lineages = set(), {}, {}
    restricted_units = False
    for unit in record['units']:
        keys(unit, {'sample_id', 'unit_id', 'unit_kind', 'condition', 'lineage', 'citations'})
        text(unit['sample_id'])
        if unit['sample_id'] in samples: raise ValueError('Duplicate sample mapping')
        samples.add(unit['sample_id'])
        for key in ('unit_id', 'condition', 'lineage'):
            if unit[key] is not None: text(unit[key])
        if unit['unit_kind'] not in {'individual', 'pool', 'cell', 'section', 'unknown'}:
            raise ValueError('Unknown biological-unit kind')
        if not isinstance(unit['citations'], list): raise ValueError('Source citations required')
        if not unit['citations']: holds.append('Unit metadata lacks source evidence')
        for citation in unit['citations']:
            keys(citation, {'resource_id', 'locator', 'file_sha256'})
            text(citation['locator'])
            resource = resources.get(citation['resource_id'])
            if (not resource or resource['file'] is None or
                    citation['file_sha256'] != resource['file']['sha256']):
                raise ValueError('Unit citation is not bound to retained source bytes')
        if unit['condition'] is None or unit['lineage'] is None:
            holds.append('Condition or shared-data lineage unresolved')
        if unit['unit_kind'] != 'individual' or unit['unit_id'] is None:
            restricted_units = True
        if (unit['unit_id'] is None or unit['unit_kind'] == 'unknown') and not record['unknowns']:
            holds.append('Unknown biological-unit identity lacks an explicit limitation')
        if unit['unit_id'] is not None:
            previous = unit_lineages.setdefault(unit['unit_id'], unit['lineage'])
            if previous != unit['lineage']:
                raise ValueError('Same biological unit has conflicting lineage')
            groups.setdefault(unit['condition'], set()).add(unit['unit_id'])
    if samples != sample_ids: raise ValueError('Unit map must cover exactly the input sample IDs')
    string_list(record['controls'])
    if case['purpose'] == 'perturbation-effect' and not record['controls']:
        holds.append('Perturbation-effect comparison lacks documented controls')
    if record['replication_justification'] is not None: text(record['replication_justification'])
    if case['inference_scope'] == 'replicated-population':
        if restricted_units or any(len(units) < 2 for units in groups.values()) or not groups:
            holds.append('Requested replicated inference lacks identifiable replicated individual units')
        if not record['replication_justification']:
            holds.append('Design-specific independence/precision justification absent')
    keys(record['resources'], {'memory_bytes', 'disk_bytes', 'wall_seconds'})
    for value in record['resources'].values():
        if value is None: holds.append('Resource estimate unresolved')
        else: _positive(value)
    string_list(record['interpretation_limits'], nonempty=True)
    string_list(record['unknowns'])
    if case['inference_scope'] == 'unresolved': holds.append('Intended inference unresolved')
    status = 'held' if holds else ('limited' if restricted_units or record['unknowns'] else 'eligible')
    return {'status': status, 'holds': sorted(set(holds)),
            'permitted_inference': case['inference_scope'] if not holds else None,
            'distinct_units_by_condition': {str(k): len(v) for k, v in groups.items()},
            'metadata_attested_not_authenticated': True, 'scientific_validity_established': False,
            **FLAGS}


def contract(workspace, record):
    keys(record, COMMON | {'article_id', 'case_id', 'case', 'feasibility', 'plan',
                          'code_files', 'environment', 'outputs', 'limits', 'design_review'})
    case, _ = _case(workspace, record)
    data = workspace.bound_record(record['feasibility'], 'data-feasibility', case=record)
    if data['case'] != record['case']: raise ValueError('Feasibility uses another case revision')
    assessment = feasibility(workspace, data)
    if assessment['status'] == 'held': raise ValueError('Held feasibility cannot freeze a contract')
    keys(record['plan'], {'comparison', 'endpoint', 'biological_unit', 'baseline',
                          'methods', 'reproduction_target', 'uncertainty', 'sensitivity',
                          'stop_rules', 'interpretation_limits'})
    for key, value in record['plan'].items():
        if key == 'interpretation_limits': string_list(value, nonempty=True)
        else: text(value)
    if record['plan']['comparison'] != case['comparison'] or record['plan']['endpoint'] != case['endpoint']:
        raise ValueError('Contract comparison/endpoint differs from case')
    if not set(data['interpretation_limits']).issubset(record['plan']['interpretation_limits']):
        raise ValueError('Contract drops feasibility interpretation limits')
    if not isinstance(record['code_files'], list) or not 1 <= len(record['code_files']) <= 256:
        raise ValueError('Bounded pinned code snapshot required')
    seen = set()
    for ref in record['code_files']:
        workspace.file(ref)
        identity = (ref['root'], ref['path'].casefold())
        if identity in seen: raise ValueError('Duplicate code file')
        seen.add(identity)
    workspace.file(record['environment'])
    workspace.file(record['design_review'])
    if not isinstance(record['outputs'], list) or not 1 <= len(record['outputs']) <= 256:
        raise ValueError('Bounded planned output inventory required')
    seen = set()
    for output in record['outputs']:
        keys(output, {'path', 'role', 'description'})
        relative(output['path']); text(output['description'])
        if not output['path'].startswith('outputs/') or output['path'].casefold() in seen:
            raise ValueError('Outputs must be unique under fresh attempt outputs/')
        if output['role'] not in {'figure', 'table', 'qc', 'log'}:
            raise ValueError('Unknown planned output role')
        seen.add(output['path'].casefold())
    keys(record['limits'], {'wall_seconds', 'memory_bytes', 'disk_bytes', 'download_bytes', 'max_attempts', 'spend_usd'})
    for key, value in record['limits'].items():
        _positive(value, zero=key in {'download_bytes', 'spend_usd'})
    if record['limits']['spend_usd'] != 0:
        raise ValueError('This offline contract route does not authorize paid execution')
    for key, estimate in data['resources'].items():
        if record['limits'][key] < estimate:
            raise ValueError('Contract bound below declared resource estimate')
    return {'status': 'contract-recorded', 'immutable_plan': True,
            'design_review_is_supplied_evidence_not_authenticated_approval': True,
            'scientific_execution_implemented': False, **FLAGS}


def validate(workspace, record):
    if record['kind'] == 'data-feasibility': return feasibility(workspace, record)
    if record['kind'] == 'analysis-contract': return contract(workspace, record)
    from .science_review import validate as validate_review
    return validate_review(workspace, record)


def preflight(workspace, contract_ref):
    """Validate bindings without mistaking offline adapter checks for isolation."""
    record = workspace.bound_record(contract_ref, 'analysis-contract')
    workspace.validate(record)
    return {'status': 'hold', 'contract': contract_ref,
            'offline_adapter_available': True,
            'reasons': ['Author-code isolation and live scientific dispatch are not qualified',
                        'No supported qualified runtime evidence is bound to this contract',
                        'Scientific execution policy remains disabled'], **FLAGS}
