# Mechanism-focused primary paper list

The owner's 20 October 2026 direction supersedes percentile-only admission with
a named CNS journal allowlist. [The frozen policy](../configs/listing_policy.json)
contains 21 biology-relevant research titles, including Nature Communications,
Science Immunology and Cell Stem Cell. No publisher-family prefix or fuzzy title
match admits additional journals. Clinical exceptions are empty; a named addition
requires a reviewed new policy version. No JIF or percentile was verified or
invented. Journal rank alone cannot admit a paper.

## Reading admission

Every admitted candidate needs:

1. A consistent journal identity matching an exact normalized allowlisted title.
2. Primary research in at least one relevant field: stem cells, cancer, immunology,
   chronic-disease biology, lung biology, IPF or bronchiectasis.
3. A biological mechanism central to the question and comparison, such as
   immune-niche crosstalk, metabolic rewiring or cell-fate regulation. These are
   examples, not an exhaustive vocabulary or a requirement for favorable results.
4. Explicit biological-system, measured-endpoint and mechanism descriptions, with
   exact retained-abstract citations. A shared title word is insufficient.
5. A current `read_next` response and no superseding disposition or integrity hold.

Material/device performance as the primary contribution is excluded even if it
mentions repair or signaling. Incidental material use in a mechanism-focused
biological study is not an automatic exclusion. Reviews and other non-primary
publications do not enter this list. Unknown journal identity, article type or
mechanism focus remains a hold. Null and contrary findings face the same criteria
as favorable findings. These are reading preferences, not proof of causal validity,
data usability, scientific merit or compatibility with a canonical Ravel question.

The tooth paper `10.1002/adma.75042` has an explicit owner-directed exclusion. The
materials-led lung hydrogel `10.1002/adhm.71751` is also excluded from this list.
These decisions do not declare the studies invalid or rewrite historical A0/A1
decisions. The separate private assisted human response records the tooth reading
rejection and broad pulmonary-context mismatch only; data-use and specific critic
findings remain unanswered. It is not independent B5 reference evidence.

## Implemented routes

New CLI `discover`, `batch-discover` and `workflow-create` calls add journal, field
and mechanism query constraints after validating the original source-bound
profile. All streams, including contrary and adjacent, operate within this explicit
scope. Queries are prefilters: they can miss relevant papers and return spurious
matches. Prospective retrieval quality has not been evaluated. This restricted
reading list is not a comprehensive literature review or recall estimate.

New CLI batches freeze the complete policy and constrained query profile in their
batch hash. Screening packets carry the policy, and `read_next` requires separate
source-cited listing assessments. Deterministic exclusions remain in the audit.
The manual reader cannot bypass a scoped batch's assessment. Standalone discovery
receipts bind the policy; those candidates also require scoped-batch screening
before full reading. No model, scheduler or cloud launcher is added. Citation
checks establish source/locator integrity, not semantic correctness; an agent can
still misinterpret a source.

```powershell
python -m weft paper-list --store PRIVATE_STORE --batch BATCH_ID
python -m weft workflow-export --store PRIVATE_STORE --batch BATCH_ID --output NEW_DIRECTORY
```

JSON separates `primary_list` from the retained `audit`. Workflow status/export
shows primary recommendations separately from the complete audit queue.
`buffer-list` remains a raw audit command, including exclusions and unreviewed
records. Existing specifications, catalogs, exports and holds are not upgraded;
historical batches do not acquire primary-list admission retroactively. Low-level
Python callers must supply `listing_policy=listing.policy()` to create a scoped
batch; the legacy API remains for recovery and tests. These are application gates,
not controls over arbitrary tools.

Ravel, the closed Choi run, B4 hold and disabled M6 remain unchanged. Independent
scientific-quality qualification and cloud-launch capability remain unresolved.
