# B3 cloud qualification and bounded B4 review

**12 October 2026: B3 and new-worker checkpoint recovery passed; B4 source
acquisition was interrupted by platform safety filtering. Final state is unverified.** This is an exposed development check of the existing
candidate, not an independent assessment of screening accuracy.

[Check record](../records/b3-cloud-b4-boundary-20261012.json) ·
[B3 interface](EVIDENCE_QUALIFICATION.md) ·
[Current state](../PROGRESS.md) · [Backend roadmap](DISCOVERY_SCREENING_BACKEND.md)

## Original worker qualification and recovery

The existing screening worker checked PR #7 at
`d95d55868ea42561d89112ef5dc7bf060fba46ca` in a separate clean source checkout.
The environment setup remains `d031cef`; the existing Ravel context remains
`bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`. These are different pins with different
roles. No environment publication or Choi action occurred during qualification.

- All **55 targeted tests** passed: qualification 16, batches 22, reading 7 and
  reading locations 10. Documentation checks passed 119 links and 15 Ravel blobs.
- The previously verified 522,632-byte after-screening archive passed exact
  SHA-256, ZIP CRC, safe-path, 42-member, SQLite integrity and count checks.
- A disposable copy issued the same source-bound packet and an all-uninspected
  review with separate data-use and RQ holds. Only two B3 events were appended;
  the original 20-event prefix, five screening decisions and source bytes remain.
- Another-path recovery returned the identical packet and `already_recorded`,
  with zero HTTP calls, unchanged database rows and no duplicate events.

At that original-worker checkpoint, the designated B4 review store was a separate,
unchanged restore; no B4 proposal was issued there. Those stores were quiesced,
and qualification copies remain inactive. The new worker has a different review
store; its later interrupted state is described below. Root reviewed worker tool outputs and receipts; this is not a second
independent cloud execution. Receipt hashes are in the public record; private
paths and worker identifiers remain under ignored `runs/b3-cloud-b4-review-20261012`.

## Bounded review scope and actual coverage

The sole candidate is [DOI 10.1002/advs.77773](https://doi.org/10.1002/advs.77773),
PMC13634473, linked to A0 in the existing batch. No new discovery or other-paper
review is included. The proposed use is to assess a future descriptive comparison
of human AT2 expansion/intermediate states and its compatibility with A0.
Dataset review means availability, accession/file inventory, conditions,
biological units, pooling, controls and source lineage. It does not download
matrices/FASTQ, run author code or perform numerical analysis.

| XML inventory | Actual retained-material coverage | Limit |
|---|---|---|
| Six main figures, referenced as WEBP | Source-archive acquisition started; completion unverified; no pixel inspection established | Captions and partial bytes do not establish figure coverage |
| One supplementary wrapper without a file href | No independent file identified | Two XML supplement entries do not imply two retrievable files |
| One referenced DOCX supplement | Archive completion and member availability unverified; no content review established | Direct DOCX intake is unsupported; available renderer has not been qualified by rendering |
| Data-availability statement | Previously cached XML only | No accession or external dataset URL identified in that cached statement; this is not proof that no dataset exists |

Existing Pillow/ImageMagick can potentially decode WEBP into PNG. A derived
viewing artifact would need retained originals, hashes, dimensions and decoded
pixel-equivalence verification before B3 attachment. **No conversion was run.**
Existing DOCX text/table/image extraction could support a partial review, but
would not certify layout, pagination or complete supplement inspection. The old
worker had no verified renderer. The new worker found an existing LibreOffice
executable and obtained its version; no document was rendered or inspected.
No renderer was installed, and B3 format checks were not changed.

The proposed caps remain 32 MiB/item, 128 MiB total including expanded and derived
files, at most 12 distinct source requests and at most two attempts per request.
Archive contents must be inventoried before bounded extraction; reject unsafe
paths and linked/encrypted members. Redirect hosts require policy verification
before following. BioRender attribution links are not retrieval targets.

## Access boundary and precise resume point

The worker made two documentation GETs through its inherited proxy/TLS:

| URL | Result | Retained response bytes | Attempts |
|---|---|---:|---:|
| `https://www.ebi.ac.uk/europepmc/webservices/rest/` | HTTP 404 | 116 | 1 |
| `https://www.ebi.ac.uk/europepmc/webservices/rest/application.wadl` | HTTP 404 | 132 | 1 |

No redirects were followed. These 248 bytes are documentation error responses,
not figure or supplement downloads. They do not establish that the candidate
`PMC13634473/supplementaryFiles` API route is invalid; its official documentation
has not yet been verified. The worker allows `www.ebi.ac.uk` but excludes
`europepmc.org`, the official documentation host identified for the next check.

The owner approved adding only `europepmc.org` and publishing that amendment.
The root browser permission layer then denied `chatgpt.com` access, so the edit
was not performed. A retry after renewed owner authorization confirmed a saved
site permission block. Browser-permission enablement was requested so the agent
can make the approved edit. Do not describe the grant as
published or effective until read back. The worker exposes status inspection,
but no supported in-place policy-refresh tool was found.

Follow-up inspection confirmed the owner's UI and saved origin configuration both
allow chatgpt.com. The same browser API nevertheless reports a saved block.
The cause is unconfirmed; desktop-app restart is the next troubleshooting step.
No permission configuration was edited, and no alternate browser route was used.
Verify browser access after restart before attempting the approved amendment;
the cloud worker must remain preserved.

### Published-amendment follow-up

The owner subsequently reported publication and explicitly requested a same-worker
check, with a stop if a new worker is needed. Fresh managed observations show the
existing worker running/connected with an enforced restricted policy, desired and
observed revision 24, and its original configuration version. The effective policy
still excludes `europepmc.org`; explicit hosts remain `ftp.ncbi.nlm.nih.gov` and
`www.ebi.ac.uk` alongside the existing preset. Only read-only environment status
is exposed, with no supported in-place adoption mechanism. Publication is
owner-reported, not independent readback of the reusable environment settings.

The worker stopped without making a network request or changing materials or
proposals. All stores remain quiesced. Receipt SHA-256:
`cb35697a67aa8c229725685270246203af7d0aaa9b68a689d77ca980321d1e0f`.
No replacement worker, restart or Choi action occurred.

The owner then explicitly authorized one new screening-only worker in updated
weft-pilot. Browser control of chatgpt.com still rejects access; the available
task-creation tool cannot choose this named environment. A private, copyable launch
prompt is prepared under ignored `runs/b3-cloud-b4-review-20261012`, including
the exact archive identity, hashes, source pins, coverage limits and stop rules.
The owner was asked to start that task and return its link. No task was created
in an unspecified environment; no new worker has been launched by root.

### Initial new-worker gate — resolved by the later check

The owner created the authorized screening-only task and supplied its link.
Its first two managed-status checks report running state, current observations,
matching desired/observed revision 2 and a changed configuration version. The
three explicit hosts and Package managers preset are present. However,
`network_policy.state` is `unknown`, so the runtime has not established policy
enforcement. The requested environment name is owner-attested; the status
response does not expose a display name for independent confirmation.

The worker stopped before source acquisition, checkpoint restoration, tests or
material inspection. Its initial receipt hash is
`4f7fd71a07e9575b15be6c1eb05697196a7e30919ead258c92b99586cf86275f`;
the private inventory hash is
`c05eb62eb0f8d5daa472bbe85d0f875882196551e9efbdf36ae7378508ddf4c7`.
A bounded read-only post-startup follow-up was requested. At this initial stop,
no new acquisition requests had been made. The later result is recorded below;
the initial receipt remains unchanged.

### Follow-up passed; review interrupted

The same new worker subsequently reported current observations, running/connected
state, restricted policy **enforced**, matching desired/observed revision 4 and
no runtime failure. Required hosts and the existing preset are intact. No policy
change or restart was performed during the check. The reason for the initial
unknown observation is not reported; it resolved on the later status read.
The user's environment selection and historical setup provenance corroborate
identity; independent current display-name verification remains unavailable.
Readiness receipt SHA-256:
`77bc6492455c97fdb4f1d991853786ae6b4fb532b0c48dae72f43e43144a4df5`.

The setup checkout remained at d031cef. A separate clean checkout at PR #7
d95d558 restored the exact 522,632-byte after-screening archive. The archive
hash, CRC, safe paths, 42 manifest members, catalog hash, SQLite integrity,
foreign keys and expected initial counts passed. Restore receipt SHA-256:
`0fe771919d693be9b187b7a0ea77882ba0e005910b800aff0e63bf18d78a645e`.
All 55 targeted tests, 119 documentation links and 15 pinned Ravel files passed.
The same B3 packet was issued without network access or reading relocation;
no new data-use/RQ assessment was submitted in the observed execution.
These are new-worker results reviewed through its tool outputs, not a second
independent root execution. Prior full-suite CI was reused.

Three additional documentation requests returned the official REST page (200),
its linked Swagger route (404, retained) and a reference PDF (200). The worker
recorded the acquisition method as documented. A sixth request began retrieving
the source archive; the last observed ledger reported HTTP 200 and 65,536 bytes,
with state `started`. Last observed counted usage is **1,004,901 bytes / six
distinct requests**, one attempt each, including the original two requests.
These are an in-progress snapshot; they are not final transfer totals or proof
of a complete, safe or inspected archive.

The review turn then failed with an explicit platform safety error citing
potential dual-use biology. No triggering passage or exact rejected operation
was identified. A subsequent administrative preservation-only request was also
rejected before any tool ran. No bypass, alternate task or repeated source
request was attempted. This outcome does not establish that the paper itself is
unsuitable or identify a network, credential or resource failure.

Final acquisition status, archive hash, database event counts and process/store
quiescence are **unverified**. No complete figure/supplement inspection, scientific
assessment, new private export or recovery checkpoint is established. The old
worker and Choi remain unchanged. Private task identifiers, original error and
receipt paths stay in the ignored handoff directory.

Next steps are conditional on resolution through the platform's normal review
route. Do not rephrase or move the blocked task to evade the restriction. Before
any permitted continuation, reconcile existing processes, partial/complete bytes,
request accounting and store state without overwriting receipts. Preserve the
original scope and bounds; a new private export still requires its own known
payload approval. No additional host grant is indicated by the reported error.

## Ravel interpretation boundary

Root read the pinned A0 [current result](https://github.com/xorca0711/ravel/blob/bfe26b876221cf6c6fa6f9b16a90cfb516b5998d/RQ_Specified/A0_conserved_epithelial_transition_program/reports/PILOT_V1_RESULTS.md),
[dossier](https://github.com/xorca0711/ravel/blob/bfe26b876221cf6c6fa6f9b16a90cfb516b5998d/docs/research_dossiers/A0.md)
and current folder framing before considering fit. These A0 paths and its
conditional package have no committed changes between that pin and inspected
local Ravel HEAD `cc5ce7e09bc03df49a982569236d572407ecb195`; this is not a claim
that the latest remote Ravel state was reviewed for scientific admission.

The frozen 50-gene programme failed the specified intestinal
intermediate-versus-mature comparison. `STOP_PRIMARY_TRANSFER_NOT_SUPPORTED`
remains in force. The current task is construct correspondence, not signature
retuning or a demonstrated conserved fate mechanism. Human AT2 culture may
provide adjacent model context; it is not automatically a comparable cross-tissue
transition, independent replication or evidence of fate control. No new RQ,
scientific acceptance, Ravel write or analysis is authorized by B3 completion.

B4 is incomplete; B5 still needs a separately frozen, independently reviewed
paper set, including contrary and low-ranked candidates. Choi publication,
artifacts and its held scientific reservation remain a separate unchanged track.
