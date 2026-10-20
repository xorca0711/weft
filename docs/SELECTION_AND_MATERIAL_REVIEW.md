# Selection and material review

This extension connects bounded candidate nomination, reusable XML, explicitly
supplied local materials and a source-linked review view. It uses the existing
store, screening, reading and B3 validators. It does not invoke an agent, fetch
source-proposed URLs, certify inspection or change scientific admission rules.

## Versioned nomination

New `workflow-create` batches default to `paper-stream-v1`. `batch-discover`
retains its legacy default; either command accepts `--selection-policy legacy`
or `--selection-policy paper-stream-v1`. Existing frozen specifications and
pilot catalogs retain their original policy. No existing batch is upgraded.

The versioned policy is part of the batch specification hash. After discovery
completes, Weft freezes the candidate/source provenance and nomination order:

1. Retain identity/integrity holds, excluding them from nominal nominations.
2. Admit one RQ link per paper per round, using the existing paper identity.
3. Rotate across `rq_contrary`, `adjacent_context` and `broad` query streams.
4. Within a stream, use paper-key order. For a paper's RQ links, prefer the RQ
   with fewer links already nominated, then RQ ID and candidate ID.
5. Repeat paper rounds for remaining RQ links. Never duplicate a candidate.

Missing streams are skipped. A paper found by several streams is still admitted
only once per round. A screening cap smaller than the available streams cannot
guarantee representation of every stream. Stream membership describes retrieval
provenance, not the paper's actual stance or relevance. Identifier tie-breaking
remains arbitrary; this is a transparent diversity policy, not a trained ranker.
Existing version/edition identity handling and holds are unchanged.

The saved order survives review decisions and reopening the process. Changed
candidate identity, source provenance, integrity holds or plan bytes cause an
explicit hold/error; there is no implicit reranking. New selection policy
versions require new batches and review.

```powershell
python -m weft selection-report --store PRIVATE_STORE --batch BATCH_ID --include-plan
python -m weft selection-report --store PRIVATE_STORE --batch BATCH_ID --reference private/bibliography.json
```

The read-only report compares the new and legacy nominal orders under the same
screening-link cap, excluding known integrity holds. Actual packet issuance is
reported separately because validation failures and interruptions can change it.
Counts include links, unique paper keys, RQ allocation and query-stream coverage.
Stream counts overlap. Paper counts never imply independent studies.

Optional bibliography input uses exact stored paper keys, without fuzzy matching:

```json
{
  "schema_version": 1,
  "provenance": "Describe how this comparison bibliography was assembled",
  "prior_exposure": "Record prior exposure to the candidates and outcomes",
  "paper_keys": ["doi:10.9999/synthetic-example"]
}
```

Use 1–10,000 unique keys. The report retains the reference hash and denominator,
matched counts and missing keys for discovery, both nominal orders and actual
issuance. It measures coverage of that supplied bibliography only. Reference
independence, population recall, semantic accuracy and real-world selection
quality remain unqualified. Independent quality evaluation is a separate phase.

## Reuse XML while retaining separate RQ judgments

For a current `read_next` link, the coordinator may reuse verified XML prepared
for another current link to the same paper/evidence snapshot in the same batch.
The donor's source bytes, receipt and live packet are checked, and the new packet
retains its own RQ context and requires its own reading and B3 assessments.

Receipts identify the donor, source hash and shared-source status. No assessment
is copied; reused material is not independent replication. XML parsing and source
identity checks still run. Reuse consumes the existing full-read attempt budget
and performs no network call. Conflicting cached versions, stale/tampered inputs
and unknown prior attempts do not trigger a fetch fallback or retry. Donor and
target review holds remain independent and are never released by reuse.

## Manifest-based local intake

Prepare an exact manifest for the current evidence packet. Paths use forward
slashes relative to the manifest directory; traversal, absolute and linked
artifact paths are rejected. Hashes are SHA-256 of the actual file bytes.

```json
{
  "schema_version": 1,
  "batch_id": "BATCH_ID",
  "candidate_id": "CANDIDATE_ID",
  "packet_sha256": "CURRENT_EVIDENCE_PACKET_SHA256",
  "artifacts": [{
    "resource_id": "CURRENT_RESOURCE_ID",
    "path": "figures/figure-1.png",
    "bytes": 1234,
    "sha256": "FILE_SHA256",
    "origin": "Describe the supplied source and locator"
  }]
}
```

```powershell
python -m weft workflow-import-materials --store PRIVATE_STORE --batch BATCH_ID --candidate CANDIDATE_ID --manifest private/intake/manifest.json
python -m weft workflow-materials --store PRIVATE_STORE --batch BATCH_ID --candidate CANDIDATE_ID
```

The coordinator requires its active binding and an unheld evidence-review stage.
Intake validates all manifest entries before attaching, then rechecks each file
hash at attachment. Existing format and size limits apply: PNG/JPEG/PDF/UTF-8
TXT/CSV/TSV, 32 MiB per file, 64 artifacts and 256 MiB per evidence packet.
Format signatures are not a rendering or inspection guarantee.

Exact retries reuse attachment IDs. An interrupted import can retain a valid
partial set; retrying the same manifest completes the remainder. Intake does not
mark files inspected or change coverage/proposal records. Existing explicit
assessment submission remains necessary. The manifest command does not download
files, follow source URLs, extract archives or execute author code.

## Private review view

```powershell
python -m weft workflow-review-export --store PRIVATE_STORE --batch BATCH_ID --candidate CANDIDATE_ID --output private/review-001
```

The new directory contains `review.json`, a static `index.html`, and a last-written
hash manifest. The view separates data-use and RQ compatibility proposals; shows
comparison, endpoint, unit, controls, access, dataset lineage, limitations and
actor exposure; and links recorded citations to exact XML text locators. Resource
coverage, captions, file provenance and byte verification remain distinct from
recorded inspection. Invalid attachment bytes remain visible as holds.

Add `--include-materials` only to copy explicitly supplied, verified local files
and enable their local links. Without it, attachment files are not copied. The
bundle contains source text and private review metadata, even without attachments;
do not publish it as a public report. It has no scripts or remote asset loading,
does not upload anything, and opening it never changes an inspection record.
Interrupted exports have no completion manifest; use a new directory to retry.
Database reads are consistent; source files must remain quiescent during export.

## Reproducible synthetic demonstration

```powershell
python -m weft workflow-demo --output runs/selection-material-demo
```

Use a new output directory. This command injects every metadata/XML transport,
creates synthetic RQs without reading Ravel, and runs a finite fixture workflow.
It writes the catalog, supplied fixture, status view, review view, selection audit
and `demo.json`. Expected behavior: four reading packets across three papers,
three XML fixture calls and one cached reuse. The nominal legacy order reaches
two papers under that fixture's four-link cap. Both B3 proposals remain held;
the supplied one-pixel fixture is not recorded as inspected. These numbers test
software mechanics only, not retrieval quality or semantic review accuracy.

Tests: `tests/test_selection.py`, `tests/test_materials.py` and the coordinator's
existing integration/recovery tests. Run repository validation and the full suite
as documented in the [coordinator guide](WORKFLOW_COORDINATOR.md).

Choi remains closed, B4 held, M6 disabled and Ravel unchanged. App/CLI environment
mapping and runtime capability access remain unqualified. This implementation
does not retry held launches or substitute another platform.
