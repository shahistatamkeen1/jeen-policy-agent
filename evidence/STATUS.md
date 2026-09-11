# Test results

## Application tests

**27/27 passed**, recorded September 11, 2026. Full output: [automated-tests.txt](automated-tests.txt).

The suite uses fixed model responses to test BM25 retrieval, output validation, source citations, approval and rejection, insufficient-evidence blocking, persistence, proposal expiry, audit records and HTTP authentication. It also covers repeated and concurrent approvals.

Two regression tests cover Windows source files: unchanged CRLF policies allow approval, while an actual file edit after retrieval blocks it. Approval checks the same document directory used for ingestion.

## Live model evaluation

**10/10 passed**, recorded September 10, 2026. Provider: OpenAI. Recorded model: `gpt-5.6-sol`. Full results: [live-evaluation.json](live-evaluation.json).

| Supported question | Selected section | Queue |
|---|---|---|
| Customer statements in a public AI chatbot | AI-01 | SecurityReview |
| New vendor missing a SOC 2 report | VR-01 | VendorRisk |
| Existing vendor renewal quotation | VR-03 | Procurement |
| Public marketing material in an approved internal AI tool | AI-02 | AIEnablement |

The selected excerpts match the source policies and address these four questions. The remaining six cases return insufficient evidence, covering missing retention periods, thresholds, country approvals, a turnaround guarantee, malicious instructions and a fabricated policy reference.

The runner checks expected status, queue and citation IDs. It uses a temporary database and does not call the case-creation endpoint. These results predate the September 11 hashing correction; they are not a new provider run against that revision. Ten cases provide useful examples, but are too few to estimate general accuracy or resistance to prompt injection.

## Workflow runs

| Scenario | Result | Screenshot |
|---|---|---|
| Supported evidence, human approval | Case created in SecurityReview | [Approved](02_supported_approved_case_created.png) |
| Supported evidence, human rejection | No case created | [Rejected](03_supported_rejected_no_case.png) |
| Insufficient evidence, approval attempted | `closed_no_action`; no case created | [Blocked](04_insufficient_approval_blocked.png) |

Additional captures: [workflow canvas](01_workflow_architecture.png), [cited review form](06_cited_policy_evidence.png), [retrieval candidates](07_retrieval_candidate_chunks_insufficient.png), and [live evaluation summary](05_live_evaluation_10_of_10.png).

## Open verification items

The portable workflow passed the import/export check recorded in [n8n-import-export.txt](n8n-import-export.txt). An export from the configured demonstration instance still needs to be checked. A fresh approval run on Windows is also pending after the file-hashing correction.

The existing canvas screenshot predates the documentation cleanup and contains an old setup-note reference. A new capture should accompany the configured workflow export. Other run screenshots remain records of the earlier executions.
