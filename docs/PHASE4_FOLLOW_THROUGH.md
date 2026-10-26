# Full-text review and remaining qualification

The [evidence-generation revision](EVIDENCE_GENERATION_ROADMAP.md#phase-4-and-the-scientists-role)
adds the proposed scientific-development work: a bounded analysis pilot with
actual results, critique and consequential owner decisions. It does not replace
or pass the frozen reading evaluation. Any new evaluation plan needs its own
prospective amendment and appropriate independent references. W01–W09 describe
the implementation gap; L1–L4 below retain their technical meaning and holds.

Phase 4 now carries retained full texts, critic findings and separate human
decisions through the existing private exporter. Transfer verification checks
the source bundle and recomputes its accounting without resuming a job. These
are software capabilities. Independent scientific-quality evaluation remains
pending, and the existing L0–L4 deployment sequence is unchanged.

Current evaluation status, checked 25 October: the 20 October 12-item development
package and criteria were frozen after owner approval (10/12 reading agreement,
12 completed claim audits, zero critical errors as a pilot continuation rule).
The 21 October owner amendment delegated routine source auditing to AI and changed
the active workflow to assisted reading review. Twelve bounded AI source audits
exist; they are not independent human reference judgments. Individual reading
decisions remain private; unresolved field/source interpretation issues remain
in the retained evaluation records. The original evaluation remains unpassed; any
assisted agreement is descriptive, not a retroactive blind score. No routine claim
audit form is required from the owner under the amended workflow.

The immediate Phase 4 gap is adjudicated scientific/evaluation evidence with an
appropriate reference and exposure record. It does not require the missing cloud
runtime-status interface to continue offline source review or software development.
The R01 scientific pilot and its separate runtime/isolation prerequisites belong
to W08/W10. A new evidence-generation evaluation needs prospective criteria rather
than silently repurposing the original reading-preference benchmark.

## Multi-source review contract

`quality-review-export` accepts the existing schema v1 and an additive schema v2.
Each v2 case retains the exact DOI metadata source and adds `materials` and
`access_attempts`. The executable synthetic example is in
[`test_review_materials.py`](../tests/test_review_materials.py).

Each material names its local portable path, SHA-256, byte count, format, role,
paper key, origin, version, coverage, inspection record and derivation parents.
Supported formats are UTF-8 text, JSON, PDF, PNG and JPEG. Roles distinguish main
text, derived text, figures, supplements, review annotations, human authority and
access receipts. Derived text must name a retained main text or supplement in
the same case. JSON records are capped at 1 MB; individual materials at 32 MiB;
the source bundle at 256 MiB and 256 material records. Existing case/finding caps
remain unchanged. Oversized generated JSON is rejected before export begins.

Inspection records attribute `not_reviewed`, `text_reviewed`, `pixels_reviewed`
or `text_and_selected_pixels` to the declared actor and explicit scope. Text or
captions cannot be labelled pixel inspection. Retaining a whole PDF does not mean
all its figures were inspected. The format check establishes a file signature,
not a valid parsed PDF/image or safe rendering environment.

V2 locators use `/metadata/...` for the original metadata and
`/materials/<material_id>/content/...` for JSON records or zero-based text lines.
Binary content is not parsed. A binary material's `/inspection/scope` locator
identifies an attestation, never a page-level entailment check. A review-record
locator cites an annotation rather than primary evidence. Paper bindings,
versions, inspection, authority, exposure and timestamps remain attestations;
hashes and pointers cannot establish their truth or scientific support.

Access attempts identify the route (`public_http`, `institutional_browser`,
`publisher_api` or `manual_local`), source URL, observation time, outcome, known
HTTP status, retained material IDs and a locator into an acquisition receipt.
`retrieved` needs actual retained paper material and a compatible status;
metadata-only HTTP 200 is not full-text retrieval. A failed route does not imply
irrelevance, missing institutional entitlement, or successful cloud access.
Receipt contents are supplied evidence, not independently authenticated transport
logs. Local intake of an earlier download must say so explicitly.

The original critic findings and human response remain separate. Import only
the decision actually supplied. A reading keep maps to `read_next`; it does not
fill data-use/RQ labels, declare technical agreement, or attest completed reading.
An import timestamp dates the new record; retain the original decision authority
and date inside its source record. Assisted responses cannot become independent
references. No live store, held disposition or Ravel record is changed.

## Export, transfer and inactive readback

```powershell
python -m weft quality-review-export --packet private/input/packet.json --adjudication private/input/human-response.json --output private/review-001
python -m weft quality-review-verify --directory private/review-001 --expected-manifest-sha256 <hash-returned-by-export>
```

Use a new output directory each time. Export returns the manifest hash; retain it
separately before copying the directory. Verification checks the complete file
inventory, rejects linked/escaped paths and missing/tampered files, reloads source
bindings and recomputes the report and blank response template. A partial export
without its final manifest fails verification. Without a separately retained
hash, verification establishes internal consistency only; even with one, it does
not authenticate an actor or scientifically validate a claim. No restore copy
is activated and no model, provider, retrieval or resume is invoked.

The view is static, private HTML/Markdown. Material links, declared coverage,
route outcomes and unresolved decisions remain visible. This work does not
qualify local-file browser support or add an alternative browser-access route.

## Remaining stages and completion evidence

The descriptions below map to the existing roadmap; they introduce no new phase
numbering, schedule or deployment authorization.

| Stage | Work completed locally | Evidence still required |
|---|---|---|
| Phase 4 / B5 | Review/export/transfer software; frozen 12-item development package; later AI-assisted source audits and R01 owner reading keep | Qualified reference judgments, resolution of retained issues and scored outcomes consistent with recorded exposure. Broader recall claims also need an independent bibliography; new evidence-generation endpoints need prospective criteria |
| L1: native runtime qualification | Existing exact-occurrence launch journal and preserved runtime-HOLD evidence | New platform evidence resolving missing runtime-status capability; then the permitted same-occurrence bounded test and verified result. No replacement launch/retry is justified now |
| L2: durable remote recovery | Existing local duplicate/lost-acknowledgement/restore controls; new review-bundle transfer checks | Supported authoritative remote writer or enforced fencing, remote cancellation/recovery and operation without a PC callback |
| L3: bounded integrated operation | Local coordinator, listing gates, material intake, status/review export | Qualified launcher plus independently evaluated search/screening and source-access routes; operational denominators including failures and holds |
| L4 / M6: recurrence | Existing configuration remains disabled | Technical and quality qualification, then separate owner configuration of cadence, time zone, scope, finite limits, destinations and stop/notification rules |

The next local component is implemented in the
[cloud-return intake](CLOUD_RETURN_INTAKE.md): read-only task/spec/contract binding,
artifact verification and explicit incomplete/held result accounting. It adds no
new live-cloud qualification evidence.

Institutional-browser full-text access and automated cloud-runtime availability
are different dependencies. Improving file handoff resolves a local integration
gap; it does not establish the cause of the app/CLI launch failure or repair a
missing runtime capability. Keep the existing
[native runtime diagnosis](qualification/NATIVE_RUNTIME_HOLD.md) and support
request (submitted and escalated on 21 October); no repeated probe, alternate environment or new service follows
from this implementation. The [remote architecture](REMOTE_AUTOMATION_ARCHITECTURE.md)
owns the eventual qualification sequence.

## Historical draft independent evaluation design

The draft below predates the accepted 20 October design/frozen development package
and the 21 October assisted-review amendment summarized above. Its statements that
sample size and numerical criteria are unset describe that earlier checkpoint,
not the current state. The original frozen private artifacts remain unchanged.

Purpose: assess Weft's reading-selection errors, unsupported statements, false
data/RQ readiness and appropriate uncertainty on a bounded future paper sample.
The comparison is the frozen agent output versus separately collected independent
human judgments and an independently assembled bibliography. The accounting unit
is the frozen paper/context item; repeated papers, cohorts and source data must
remain linked rather than counted as independent scientific replication.

Keep the owner as primary reviewer. For a genuinely independent reference subset,
the owner must record judgments before seeing AI decisions or critique for those
items. The critic can then review disagreements and prepare the same compact
biology/mechanism/relevance cards, preserving the original human and agent labels.
Items exposed to critique first remain in the assisted development stratum.
Existing exposed decisions are useful development feedback, not unseen labels.

Freeze the eligible universe and selection method before collecting outcomes.
Include relevant positives, contrary studies, adjacent/ineligible studies,
low-ranked/rejected candidates and access failures. Keep a separately scoped
contrary-evidence audit even when the primary reading list prioritizes named
journals; journal prestige is not a reference relevance label. Record each item's
prior exposure and the limits of bibliography coverage. A returned search set
alone supplies no population-recall denominator.

Use separate reading, data-use and RQ endpoints. Retain exact evidence locators,
uncertainty, unresolved units/lineage and missing materials. Assess citation
support using the actual inspected source, not hash agreement. The largest
validity threats are reviewer anchoring from AI exposure, purposive favorable
selection, access-dependent missingness and shared-source pseudo-replication.
Report them rather than claiming they were eliminated by schema checks.

Sample size, numerical acceptance criteria, independently authored bibliography,
reviewer authority and operational qualification remain **unset**. This draft
must not be submitted as an approved/frozen `evaluation-plan`. Once prerequisites
are met, the owner reviews those concrete choices before outcomes; the existing
[B5 plan/scorer](B5_EVALUATION_PREPARATION.md) then provides accounting without
granting scientific acceptance or dispatch authority. No extra keep/reject answer
is required for previously recorded reading choices.

B4 remains excluded and held, Choi closed, M6 disabled, automatic cloud launch
unqualified and Ravel unchanged. No dataset, author-code execution, support
message, deployment or schedule was introduced.
