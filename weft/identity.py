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


def normalize(raw: dict) -> dict:
    source, external = str(raw["source"]), str(raw["id"])
    doi = doi_key(raw.get("doi"))
    pmid = str(raw.get("pmid") or (external if source == "MED" else ""))
    pmid = pmid if pmid.isdigit() else None
    pmcid = str(raw.get("pmcid", "")).upper()
    pmcid = pmcid if re.fullmatch(r"PMC\d+", pmcid) else None
    identifiers = [f"epmc:{source}:{external}"]
    identifiers += [f"{kind}:{value}" for kind, value in (("doi", doi), ("pmid", pmid), ("pmcid", pmcid)) if value]
    corrections = (raw.get("commentCorrectionList") or {}).get("commentCorrection", []) or []
    pubtypes = (raw.get("pubTypeList") or {}).get("pubType", []) or []
    concerns = [c for c in corrections if any(word in str(c.get("type", "")).lower()
                for word in ("retract", "erratum", "corrig", "correction", "expression of concern"))]
    related = [{"kind": c.get("type", "unspecified"), "source": c.get("source"),
                "id": c.get("id"), "reference": c.get("reference")}
               for c in corrections]
    journal = (raw.get("journalInfo") or {}).get("journal") or {}
    return {"provider_id": f"epmc:{source}:{external}", "identifiers": sorted(identifiers),
            "doi": doi, "pmid": pmid, "pmcid": pmcid, "title": raw.get("title") or "",
            "journal": journal.get("title") or raw.get("journalTitle"),
            "journal_issn": journal.get("issn"), "journal_essn": journal.get("essn"),
            "first_publication_date": raw.get("firstPublicationDate"),
            "first_index_date": raw.get("firstIndexDate"), "revision_date": raw.get("dateOfRevision"),
            "publication_types": pubtypes, "related_records": related,
            "provider_versions": raw.get("versionList"),
            "abstract_sha256": hashlib.sha256((raw.get("abstractText") or "").encode()).hexdigest(),
            "access": {k: raw.get(k) for k in ("isOpenAccess", "inEPMC", "hasPDF", "license")},
            "identity_warning": "malformed-doi" if raw.get("doi") and not doi else None,
            "integrity_flags": ["provider-correction-or-retraction-link"] if concerns or
                any("retract" in str(p).lower() for p in pubtypes) else [],
            "integrity_scope": "provider-metadata-only; absence of flags is not clearance",
            "study_independence": "not-assessed"}


def deduplicate(raw_records: list[dict]) -> dict:
    # Collapse byte-equivalent metadata snapshots, then connect only strong identifiers.
    snapshots = {digest(normalize(r)): normalize(r) for r in raw_records}
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
        contradictions = {kind: sorted({r[kind] for r in component if r[kind]})
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
    possible_versions = [keys for keys in title_buckets.values() if len(keys) > 1]
    return {"observations": len(raw_records), "unique_metadata_snapshots": len(values),
            "resolved_work_count": sum(g["identity_status"] == "resolved" for g in groups),
            "groups": sorted(groups, key=lambda g: g["paper_key"]), "identity_conflicts": conflicts,
            "possible_versions_by_title": possible_versions,
            "version_policy": "Different identifiers remain separate editions; title similarity only nominates review",
            "independent_study_count": None}
