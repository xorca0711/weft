"""Offline B5 evaluation accounting, not scientific certification or dispatch.

Inputs are frozen, externally supplied judgments. Hashes bind bytes and actor,
independence, exposure and approval fields remain attestations. This module does
not select papers, invent reference labels, set release thresholds or use a model.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
import re

LABELS = {
    'reading': ('read_next', 'hold', 'reject'),
    'data': ('review_required', 'hold', 'not_suitable'),
    'rq': ('review_required', 'hold', 'not_suitable'),
}
EXPOSURES = {'none', 'exposed', 'unknown'}
FLAGS = {'scientific_execution_allowed': False, 'claim_validated': False,
         'release_qualified': False, 'actor_identity_verified': False,
         'model_invoked': False}


def fingerprint(value):
    """Canonical JSON hash; reject non-JSON and nonfinite values."""
    try:
        body = json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError) as exc:
        raise ValueError('Finite JSON values required') from exc
    return hashlib.sha256(body).hexdigest()


def _keys(value, fields, where):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError('Unexpected or missing fields: ' + where)


def _text(value, where):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        raise ValueError('Nonempty bounded text required: ' + where)


def _sha(value, where):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA-256 required: ' + where)


def _time(value, where):
    _text(value, where)
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.utcoffset() is None:
            raise ValueError('Time zone missing')
        return result
    except ValueError as exc:
        raise ValueError('Time-zone-aware ISO timestamp required: ' + where) from exc


def validate_plan(plan):
    _keys(plan, {'schema_version', 'evaluation_id', 'kind', 'frozen_at', 'owner_review',
                 'sampling', 'reference_reviewers', 'sample'}, 'plan')
    if type(plan['schema_version']) is not int or plan['schema_version'] != 1:
        raise ValueError('Unsupported evaluation schema')
    _text(plan['evaluation_id'], 'evaluation_id')
    if not isinstance(plan['kind'],str) or plan['kind'] not in {'synthetic', 'development', 'prospective'}:
        raise ValueError('Evaluation kind required')
    _time(plan['frozen_at'], 'frozen_at')
    review = plan['owner_review']
    _keys(review, {'actor', 'locator', 'record_sha256'}, 'owner_review')
    _text(review['actor'], 'owner actor'); _text(review['locator'], 'owner review locator')
    _sha(review['record_sha256'], 'owner review hash')
    sampling = plan['sampling']
    _keys(sampling, {'universe_locator', 'universe_sha256', 'selection_method', 'coverage_limits'}, 'sampling')
    _sha(sampling['universe_sha256'], 'sampling universe')
    for key in ('universe_locator', 'selection_method', 'coverage_limits'):
        _text(sampling[key], key)
    reviewers = plan['reference_reviewers']
    if not isinstance(reviewers, list) or not reviewers:
        raise ValueError('Named reference reviewers required')
    for reviewer in reviewers:
        _text(reviewer, 'reference reviewer')
    if len(set(reviewers)) != len(reviewers):
        raise ValueError('Duplicate reference reviewers')
    sample = plan['sample']
    if not isinstance(sample, list) or not sample:
        raise ValueError('Explicit nonempty frozen sample required')
    seen = set()
    for item in sample:
        _keys(item, {'item_id', 'paper_key', 'lineage_group', 'packet_sha256', 'source_sha256',
                     'source_version', 'source_locator', 'prior_exposure', 'selection_probability',
                     'selection_probability_note'}, 'sample item')
        for key in ('item_id', 'paper_key', 'lineage_group', 'source_version', 'source_locator',
                    'selection_probability_note'):
            _text(item[key], key)
        if item['item_id'] in seen:
            raise ValueError('Duplicate sample item')
        seen.add(item['item_id'])
        for key in ('packet_sha256', 'source_sha256'):
            _sha(item[key], key)
        _keys(item['prior_exposure'], {'agent', 'evaluator'}, 'prior_exposure')
        if any(not isinstance(value,str) or value not in EXPOSURES for value in item['prior_exposure'].values()):
            raise ValueError('Exposure must be none, exposed or unknown')
        probability = item['selection_probability']
        if probability is not None and (type(probability) not in {int, float}
                or not math.isfinite(probability) or not 0 < probability <= 1):
            raise ValueError('Selection probability must be null or in (0, 1]')
    return {'plan_sha256': fingerprint(plan), 'sample_size': len(sample), **FLAGS}


def _records(plan, records, reference):
    if not isinstance(records, list):
        raise ValueError('Judgment records must be a list')
    items = {x['item_id']: x for x in plan['sample']}
    result = {}; frozen = _time(plan['frozen_at'], 'frozen_at')
    for record in records:
        _keys(record, {'schema_version', 'evaluation_id', 'plan_sha256', 'item_id', 'packet_sha256',
                       'actor', 'actor_kind', 'created_at', 'independent_reference',
                       'blind_to_agent', 'prior_exposure', 'judgments'}, 'judgment record')
        if (type(record['schema_version']) is not int or record['schema_version'] != 1
                or record['evaluation_id'] != plan['evaluation_id']
                or record['plan_sha256'] != fingerprint(plan)):
            raise ValueError('Judgment differs from frozen plan')
        item_id = record['item_id']
        if not isinstance(item_id, str) or item_id not in items:
            raise ValueError('Unmatched judgment item; never silently discard records')
        item = items[item_id]
        if record['packet_sha256'] != item['packet_sha256']:
            raise ValueError('Judgment packet differs from frozen sample')
        _text(record['actor'], 'judgment actor')
        if _time(record['created_at'], 'judgment created_at') < frozen:
            raise ValueError('Judgment predates frozen plan; retain as development evidence elsewhere')
        if (type(record['independent_reference']) is not bool or type(record['blind_to_agent']) is not bool
                or not isinstance(record['prior_exposure'],str) or record['prior_exposure'] not in EXPOSURES):
            raise ValueError('Explicit independence, blinding and exposure attestations required')
        if reference:
            if (record['actor_kind'] != 'human' or record['actor'] not in plan['reference_reviewers']
                    or not record['independent_reference']):
                raise ValueError('Reference needs a declared independent named human reviewer')
        elif record['actor_kind'] != 'agent' or record['independent_reference'] or record['blind_to_agent']:
            raise ValueError('Agent response cannot be its own independent reference')
        key = (item_id, record['actor']) if reference else item_id
        if key in result:
            raise ValueError('Duplicate judgment; preserve amendments separately before freezing inputs')
        _keys(record['judgments'], LABELS, 'separate reading/data/RQ judgments')
        for dimension, labels in LABELS.items():
            judgment = record['judgments'][dimension]
            _keys(judgment, {'label', 'reason', 'citations'}, dimension)
            label = judgment['label']
            if label is not None and (not isinstance(label, str) or label not in labels):
                raise ValueError('Invalid label for ' + dimension)
            _text(judgment['reason'], dimension + ' reason or missingness explanation')
            citations = judgment['citations']
            if not isinstance(citations, list) or (label is not None and not citations):
                raise ValueError('Known judgments require evidence citations')
            for citation in citations:
                _keys(citation, {'locator', 'source_sha256'}, dimension + ' citation')
                _text(citation['locator'], 'citation locator')
                if citation['source_sha256'] != item['source_sha256']:
                    raise ValueError('Citation source differs from frozen sample')
        result[key] = record
    return result


def _metrics(rows, dimension):
    labels = LABELS[dimension]; matrix = {r: {p: 0 for p in labels} for r in labels}
    counts = Counter()
    for row in rows:
        counts['sample_items'] += 1
        predicted = row['agent'][dimension] if row['agent'] else None
        references = row['references'][dimension]
        available = [label for label in references if label is not None]
        if predicted is None: counts['missing_agent_labels'] += 1
        counts['expected_reference_labels'] += len(references)
        counts['missing_reference_labels'] += sum(label is None for label in references)
        if not available: counts['items_without_reference_label'] += 1
        if len(set(available)) > 1:
            counts['reference_disagreements'] += 1
        # Missing reviewers and disputes stay unresolved; never pick a favorable reviewer.
        agreed = available[0] if available and len(available) == len(references) and len(set(available)) == 1 else None
        if agreed is None: counts['unresolved_reference_items'] += 1
        if predicted is None or agreed is None:
            continue
        counts['paired_items'] += 1
        matrix[agreed][predicted] += 1
        if predicted != agreed: counts['disagreements_with_reference'] += 1
        if predicted == agreed == 'hold': counts['concordant_holds'] += 1
        if predicted == labels[0]:
            counts['positive_agent_labels_with_resolved_reference'] += 1
            if agreed != labels[0]: counts['unsupported_positive_relative_to_reference'] += 1
    keys = ('sample_items', 'missing_agent_labels', 'expected_reference_labels', 'missing_reference_labels',
            'items_without_reference_label', 'reference_disagreements', 'unresolved_reference_items',
            'paired_items', 'disagreements_with_reference', 'concordant_holds',
            'positive_agent_labels_with_resolved_reference', 'unsupported_positive_relative_to_reference')
    result = {key: counts[key] for key in keys}
    result['disagreement_rate'] = counts['disagreements_with_reference'] / counts['paired_items'] if counts['paired_items'] else None
    denominator = counts['positive_agent_labels_with_resolved_reference']
    result['unsupported_positive_rate'] = counts['unsupported_positive_relative_to_reference'] / denominator if denominator else None
    result['confusion_reference_rows_agent_columns'] = matrix
    return result


def evaluate(plan, predictions, references):
    """Validate exact frozen inputs and return dimension-specific descriptive metrics.

    Invalid, unmatched or duplicate records fail explicitly, producing no misleading
    partial score. Missing labels/reviewers remain in sample denominators. No threshold
    or pass decision is computed. Reference consensus is not verified scientific truth.
    """
    result = validate_plan(plan)
    agents = _records(plan, predictions, False); humans = _records(plan, references, True)
    agent_names = {record['actor'] for record in agents.values()}
    if agent_names.intersection(plan['reference_reviewers']):
        raise ValueError('Agent and independent reference reviewer identities overlap')
    rows = []
    for item in plan['sample']:
        agent = agents.get(item['item_id'])
        reviews = [humans.get((item['item_id'], reviewer)) for reviewer in plan['reference_reviewers']]
        exposures = list(item['prior_exposure'].values()) + [r['prior_exposure'] for r in [agent, *reviews] if r]
        if any(r and not r['blind_to_agent'] for r in reviews):
            exposures.append('exposed')
        # "Unseen" is an attestation and excludes synthetic/development runs entirely.
        stratum = ('exposed' if 'exposed' in exposures else 'unknown' if 'unknown' in exposures
                   or agent is None or any(r is None for r in reviews) else 'declared_unseen')
        if plan['kind'] != 'prospective' and stratum == 'declared_unseen': stratum = plan['kind']
        rows.append({'item_id': item['item_id'], 'stratum': stratum,
                     'agent': {d: agent['judgments'][d]['label'] for d in LABELS} if agent else None,
                     'references': {d: [r['judgments'][d]['label'] if r else None for r in reviews] for d in LABELS}})
    result.update(schema_version=1, evaluation_id=plan['evaluation_id'], kind=plan['kind'],
                  predictions_sha256=fingerprint(predictions), references_sha256=fingerprint(references),
                  sample_lineage_groups=len({x['lineage_group'] for x in plan['sample']}),
                  independent_study_count=None, valid_prediction_records=len(agents),
                  valid_reference_records=len(humans), missing_prediction_records=len(rows)-len(agents),
                  missing_reference_records=len(rows)*len(plan['reference_reviewers'])-len(humans),
                  unblinded_reference_records=sum(not r['blind_to_agent'] for r in humans.values()),
                  metrics={dimension: _metrics(rows, dimension) for dimension in LABELS},
                  exposure_strata={stratum: {dimension: _metrics([r for r in rows if r['stratum']==stratum], dimension)
                                             for dimension in LABELS}
                                   for stratum in sorted({r['stratum'] for r in rows})},
                  item_accounting=rows,
                  limits=['Actor, owner approval, independence, exposure and timestamps are supplied attestations.',
                          'Citation hashes bind source identity, not semantic support or inspection.',
                          'Unweighted sample proportions; no literature recall or population accuracy estimate.',
                          'Reviewer disagreement and missing judgments are unresolved, not negative labels.',
                          'No release threshold, scientific eligibility or automatic execution is established.'])
    return result
