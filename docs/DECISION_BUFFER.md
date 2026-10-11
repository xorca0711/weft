# Paper-to-question decision buffer

Ravel questions should guide **discovery**, while a separate review buffer owns
proposed connections. Directly attaching a search hit to an RQ as supporting
evidence would confuse lexical relevance with an observed result, and encourage
confirmation bias. The buffer allows contrary, adjacent and ultimately unrelated
papers to remain visible without rewriting the question register.

| Layer | What a link means | Implemented authority |
|---|---|---|
| Discovery context | A versioned RQ helped formulate this query | Read-only Git blobs and section hashes for all registered RQs |
| Candidate buffer | This paper appeared in that query | Persistent unvalidated proposal; `supports_rq` is unknown |
| Reading priority | Read next, hold or reject for a recorded reason | Agent/human self-attribution, matching metadata and context hashes; no authenticated scientific authority |
| Reading assessment | A proposed statement cites an inspected source segment | Hash/locator checking only; semantic support still needs review |
| Claim compatibility | Finding and RQ match in population, comparison, endpoint, unit, timing and lineage | Planned scientific review; not implemented by a keyword score |
| Ravel integration | A reviewed evidence package is proposed against the current base | Future scoped PR; no automatic merge, accepted claim or A-ID |

## Implemented transitions

`pending_review -> read_next | held | rejected`. Changed retrieved metadata or
changed RQ context invalidates a prior link (`stale`); reappearing old snapshots
reopen review rather than reviving a decision. Identity contradictions and provider
correction/retraction flags hold routine reading dispatch. Held papers remain
inspectable for targeted investigation. A read-next decision never validates a claim.

Identity uses strong bibliographic identifiers, not title similarity. Different
identifiers remain separate editions; possible title matches and provider version
links nominate reconciliation. Cross-run identifier changes hold related links.
Publication identity is not dataset lineage or independent replication. Repeated
searches can add receipts without adding another candidate for an unchanged pair.

## Review before joining evidence

For each proposed connection, inspect the primary result and methods, its exact
locator, measured endpoint, biological unit, context and access limits. Separately
read the current Ravel result and amendments. State whether the relation is direct,
contrary, adjacent, methodological, shared-source or unsupported. Similar RNA labels
do not establish the same state, mechanism or regulatory competence.

Preserve both the published claim and the reviewer's narrower interpretation.
Record shared cohorts and accessions before counting studies. Missing matches are
holds or rejected links, not reasons to reshape an RQ to fit a paper. A useful
unmatched finding can remain article-local; it need not receive a canonical ID.

## Operational limits

The SQLite event API appends decisions, but this is a local trusted-user store,
not a tamper-proof audit service or identity provider. Hash checks detect changed
artifacts against retained receipts; they do not prove truth or authenticated review.
Discovery is manually dispatched. Later job leases, semantic reviews, resource
accounting and export checks belong to M2/M3/M5. No plan wording substitutes for
those runtime checks.
