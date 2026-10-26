"""R01 descriptive comparison mechanics, independent of missing author recipes.

Consumes already frozen/aggregated expression profiles. No normalization, cell
selection, label inference, target/tolerance invention or biological CI. Real
profiles must be produced by the qualified worker under the reviewed contract.
"""
from __future__ import annotations

import hashlib
import math

from . import evidence as ev

VERSION = 'weft-r01-descriptive-mechanics-v1'
SAMPLES = {'GSM9136218': 'uninjured', 'GSM9136219': 'D2', 'GSM9136220': 'D5',
           'GSM9136221': 'D10', 'GSM9136222': 'D40'}


def _profile(value):
    ev.keys(value, {'sample', 'population', 'representation', 'recipe_sha256',
                    'membership_sha256', 'cell_count', 'genes', 'values'})
    if value['sample'] not in SAMPLES: raise ValueError('Unregistered deposited pool')
    ev.text(value['population']); ev.text(value['representation'])
    ev.sha(value['recipe_sha256']); ev.sha(value['membership_sha256'])
    if type(value['cell_count']) is not int or value['cell_count'] < 1:
        raise ValueError('Positive observed cell denominator required')
    genes, values = value['genes'], value['values']
    if not isinstance(genes, list) or not 2 <= len(genes) <= 100000:
        raise ValueError('Bounded common feature list required')
    for gene in genes: ev.text(gene)
    if len(set(genes)) != len(genes): raise ValueError('Duplicate feature identity')
    if not isinstance(values, list) or len(values) != len(genes): raise ValueError('Feature/value alignment mismatch')
    if any(type(x) not in {int, float} or not math.isfinite(x) for x in values):
        raise ValueError('Finite numeric profile required')
    return value


def pearson(left, right):
    """Stable centered cosine; undefined constant vectors stay unavailable."""
    if len(left) != len(right) or len(left) < 2: raise ValueError('Matched feature vectors required')
    centered = []
    for values in (left, right):
        if any(type(x) not in {int, float} or not math.isfinite(x) for x in values):
            raise ValueError('Finite numeric profile required')
        scale = max(abs(x) for x in values)
        if scale == 0: return None
        scaled = [x / scale for x in values]
        mean = math.fsum(scaled) / len(values)
        delta = [x - mean for x in scaled]
        norm = math.sqrt(math.fsum(x*x for x in delta))
        if norm == 0: return None
        centered.append([x / norm for x in delta])
    return max(-1.0, min(1.0, math.fsum(a*b for a, b in zip(*centered))))


def compare(left, right):
    left, right = _profile(left), _profile(right)
    if left['genes'] != right['genes']: raise ValueError('Identical frozen feature order required')
    if left['representation'] != right['representation'] or left['recipe_sha256'] != right['recipe_sha256']:
        raise ValueError('A comparison requires one frozen processing recipe')
    if left['sample'] != 'GSM9136218' or right['sample'] != 'GSM9136222':
        raise ValueError('This pilot comparison is uninjured versus D40')
    value = pearson(left['values'], right['values'])
    return {'schema_version': VERSION, 'kind': 'descriptive-pool-correlation',
            'representation': left['representation'], 'recipe_sha256': left['recipe_sha256'],
            'pearson_r': value, 'undefined_reason': 'constant-profile' if value is None else None,
            'gene_count': len(left['genes']), 'gene_order_sha256': hashlib.sha256(ev.encoded(left['genes'])).hexdigest(),
            'pools': [{'sample': p['sample'], 'population': p['population'],
                       'membership_sha256': p['membership_sha256'], 'cell_count': p['cell_count']}
                      for p in (left, right)],
            'biological_replicates_established': False, 'biological_confidence_interval': None,
            'published_reproduction_verdict': 'not-assessed', **ev.FLAGS}


def sensitivity(baseline_left, baseline_right, alternate_left, alternate_right):
    baseline, alternate = compare(baseline_left, baseline_right), compare(alternate_left, alternate_right)
    if baseline['representation'] == alternate['representation']:
        raise ValueError('Distinct processing representations required')
    if baseline_left['genes'] != alternate_left['genes'] or baseline['pools'] != alternate['pools']:
        raise ValueError('Sensitivity must preserve every feature, cell membership and denominator')
    a, b = baseline['pearson_r'], alternate['pearson_r']
    return {'schema_version': VERSION, 'baseline': baseline, 'alternate': alternate,
            'delta_r': b - a if a is not None and b is not None else None,
            'selection_bias_resolved': False, 'causal_or_lineage_evidence': False, **ev.FLAGS}
