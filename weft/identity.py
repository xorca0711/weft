"""Conservative bibliographic identity; versions and study independence stay separate."""
from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import unquote


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def doi_key(value):
    if not isinstance(value, str):
        return None
    value = unquote(value.strip()).lower()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)", "", value)
    return value if re.fullmatch(r"10\.\d{4,9}/\S+", value) else None


def integrity_relation(kind) -> bool:
    """Nominate integrity review; do not interpret direction or scientific effect."""
    kind = re.sub(r"[^a-z]+", " ", str(kind).lower())
    return any(word in kind for word in
               ("retract", "erratum", "corrig", "correction", "expression of concern"))


def _items(raw, container, member):
    value = raw.get(container)
    if value is None:
        return []
    if not isinstance(value, dict):
        raise ValueError(f"Malformed provider {container}")
    items = value.get(member)
    if items is None:
        return []
    if not isinstance(items, list):
        raise ValueError(f"Malformed provider {container}")
    return items


def normalize(raw: dict) -> dict:
    if (not isinstance(raw.get("source"), str)
            or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,15}", raw["source"])
            or type(raw.get("id")) not in (str, int)
            or not str(raw["id"]).strip() or len(str(raw["id"])) > 256):
        raise ValueError("Malformed provider identity")
    source, external = str(raw["source"]), str(raw["id"])
    doi = doi_key(raw.get("doi"))
    pmid = str(raw.get("pmid") or (external if source == "MED" else ""))
    pmid = pmid if pmid.isdigit() else None
    pmcid = str(raw.get("pmcid", "")).upper()
    pmcid = pmcid if re.fullmatch(r"PMC\d+", pmcid) else None
    identifiers = [f"epmc:{source}:{external}"]
    identifiers += [f"{kind}:{value}" for kind, value in (("doi", doi), ("pmid", pmid), ("pmcid", pmcid)) if value]
    if source == "MED" and external.isdigit():
        identifiers.append("pmid:" + external)
    if source == "PMC" and re.fullmatch(r"PMC\d+", external):
        identifiers.append("pmcid:" + external)
    corrections = _items(raw, "commentCorrectionList", "commentCorrection")
    pubtypes = _items(raw, "pubTypeList", "pubType")
    if any(not isinstance(c, dict) for c in corrections) or any(not isinstance(p, str) for p in pubtypes):
        raise ValueError("Malformed provider correction/publication metadata")
    warnings = []
    if raw.get("doi") and not doi:
        warnings.append("malformed-doi")
    if raw.get("pmid") and not pmid:
        warnings.append("malformed-pmid")
    if raw.get("pmcid") and not pmcid:
        warnings.append("malformed-pmcid")
    if source == "MED" and (not external.isdigit() or pmid != external):
        warnings.append("provider-pmid-conflict")
    if source == "PMC" and (not re.fullmatch(r"PMC\d+", external) or (pmcid and pmcid != external)):
        warnings.append("provider-pmcid-conflict")
    concerns = [c for c in corrections if integrity_relation(c.get("type"))]
    related = [{"kind": c.get("type", "unspecified"), "source": c.get("source"),
                "id": c.get("id"), "reference": c.get("reference")}
               for c in corrections]
    journal = (raw.get("journalInfo") or {}).get("journal") or {}
    return {"provider_id": f"epmc:{source}:{external}", "identifiers": sorted(set(identifiers)),
            "doi": doi, "pmid": pmid, "pmcid": pmcid, "title": raw.get("title") or "",
            "journal": journal.get("title") or raw.get("journalTitle"),
            "journal_issn": journal.get("issn"), "journal_essn": journal.get("essn"),
            "first_publication_date": raw.get("firstPublicationDate"),
            "first_index_date": raw.get("firstIndexDate"), "revision_date": raw.get("dateOfRevision"),
            "publication_types": pubtypes, "related_records": related,
            "provider_versions": raw.get("versionList"),
            "abstract_sha256": hashlib.sha256((raw.get("abstractText") or "").encode()).hexdigest(),
            "access": {k: raw.get(k) for k in ("isOpenAccess", "inEPMC", "hasPDF", "license")},
            "identity_warning": ";".join(warnings) or None,
            "integrity_flags": ["provider-correction-or-retraction-link"] if concerns or
                any(integrity_relation(p) for p in pubtypes) else [],
            "integrity_scope": "provider-metadata-only; absence of flags is not clearance",
            "study_independence": "not-assessed"}


def provider_relations(raw: dict) -> list[dict]:
    """Exact provider links, including their qualification notes; never union edges."""
    record = normalize(raw)
    result = []
    for container, member in (("commentCorrectionList", "commentCorrection"), ("versionList", "version")):
        for index, value in enumerate(_items(raw, container, member)):
            if not isinstance(value, dict):
                raise ValueError("Malformed provider relation")
            source, external = value.get("source"), value.get("id")
            targets = []
            if (isinstance(source, str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,15}", source)
                    and type(external) in (str, int) and str(external).strip()
                    and len(str(external)) <= 256):
                external = str(external)
                targets.append(f"epmc:{source}:{external}")
                if source == "MED" and external.isdigit():
                    targets.append("pmid:" + external)
                if source == "PMC" and re.fullmatch(r"PMC\d+", external):
                    targets.append("pmcid:" + external)
            kind = value.get("type") if container == "commentCorrectionList" else "provider-version"
            relation = {"source_provider_id": record["provider_id"],
                        "source_identifiers": record["identifiers"],
                        "kind": kind or "unspecified", "target_identifiers": sorted(targets),
                        "integrity_review_required": integrity_relation(kind),
                        "locator": f"/{container}/{member}/{index}", "provider_assertion": value,
                        "scope": "provider-reported; direction and validity not independently assessed"}
            relation["relation_sha256"] = digest(relation)
            result.append(relation)
    return result


def deduplicate(raw_records: list[dict]) -> dict:
    # Collapse byte-equivalent metadata snapshots, then connect only strong identifiers.
    normalized = [normalize(r) for r in raw_records]
    snapshots = {digest(r): r for r in normalized}
    values = list(snapshots.values())
    parent = list(range(len(values)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_identifier = {}
    for i, record in enumerate(values):
        for identity in record["identifiers"]:
            if identity in by_identifier:
                parent[root(i)] = root(by_identifier[identity])
            else:
                by_identifier[identity] = i
    components = {}
    for i, record in enumerate(values):
        components.setdefault(root(i), []).append(record)
    groups, conflicts = [], []
    for component in components.values():
        contradictions = {kind: sorted({identifier.split(":", 1)[1] for r in component
                          for identifier in r["identifiers"] if identifier.startswith(kind + ":")})
                          for kind in ("doi", "pmid", "pmcid")}
        conflict = any(len(v) > 1 for v in contradictions.values())
        # Conflicting strong IDs stay visible as a held group, never silently accepted.
        identifiers = sorted({v for r in component for v in r["identifiers"]})
        preference = ("doi:", "pmid:", "pmcid:", "epmc:")
        key = next(i for prefix in preference for i in identifiers if i.startswith(prefix))
        group = {"paper_key": key, "identifiers": identifiers,
                 "records": sorted(component, key=lambda r: (r["provider_id"], digest(r))),
                 "identity_status": "conflict" if conflict else "resolved",
                 "study_independence": "not-assessed"}
        group["evidence_sha256"] = digest(group["records"])
        groups.append(group)
        if conflict:
            conflicts.append({"paper_key": key, "reason": "conflicting-strong-identifiers",
                              "values": contradictions})
    title_buckets = {}
    for group in groups:
        title = re.sub(r"\W+", " ", group["records"][0]["title"].lower()).strip()
        if title:
            title_buckets.setdefault(title, []).append(group["paper_key"])
    possible_versions = sorted(sorted(keys) for keys in title_buckets.values() if len(keys) > 1)
    relations = {r["relation_sha256"]: r for raw in raw_records for r in provider_relations(raw)}
    for relation in relations.values():
        relation["source_paper_keys"] = sorted(g["paper_key"] for g in groups
            if set(g["identifiers"]) & set(relation["source_identifiers"]))
        relation["target_paper_keys"] = sorted(g["paper_key"] for g in groups
            if set(g["identifiers"]) & set(relation["target_identifiers"]))
        relation["reconciliation"] = ("target-not-identified" if not relation["target_identifiers"] else
            "target-not-in-result" if not relation["target_paper_keys"] else "explicit-link-needs-review")
    return {"observations": len(raw_records), "unique_metadata_snapshots": len(values),
            "resolved_work_count": sum(g["identity_status"] == "resolved" for g in groups),
            "groups": sorted(groups, key=lambda g: g["paper_key"]),
            "identity_conflicts": sorted(conflicts, key=lambda c: c["paper_key"]),
            "possible_versions_by_title": possible_versions,
            "provider_relations": sorted(relations.values(), key=lambda r: r["relation_sha256"]),
            "version_policy": "Different identifiers remain separate editions; title similarity only nominates review",
            "independent_study_count": None}
