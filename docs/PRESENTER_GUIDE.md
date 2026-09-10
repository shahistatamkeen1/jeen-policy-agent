# Presenter guide: explain the customer problem and defend the design

Use these notes to prepare, then explain the solution in your own words. The interviewer may ask you to change a policy or walk through a failed request. Make sure you can find the corresponding code without memorizing a script.

## A 7–10 minute presentation and demonstration

**Opening, 45 seconds:**

“Cedarbridge is a fictional bank used for this demo. I focused on operations staff asking AI-use and vendor-policy questions. Today, those requests can involve manual document searches and uncertain routing. The workflow retrieves the relevant policy evidence, recommends a review queue, and creates a case only after a human reviews the recommendation.”

**Business value, 45 seconds:**

“The proposed value is faster policy lookup, more consistent routing and traceable handoff. I would validate those benefits against a manual baseline. I have not measured customer ROI. I deliberately chose case creation as a limited, reversible action suitable for a short proof of concept.”

**Architecture, 90 seconds:**

“n8n orchestrates the request and approval forms. The Python integration loads three policy documents and splits them by section. BM25 retrieves four candidate sections. The LLM selects relevant evidence IDs and a review queue, or abstains. The server checks the schema, verifies that the cited IDs came from the retrieved context, and checks that the selected queue matches policy metadata. The answer displays exact policy excerpts and references. The workflow pauses at a human review form. Approval creates a durable SQLite case and audit record.”

**Live demo, 3–4 minutes:**

1. Show the n8n canvas.
2. Submit the customer-statements/public-chatbot question.
3. Read the cited AI-01 excerpt and explain the proposed SecurityReview queue.
4. Pause before approval. Show that recommendation alone creates no case.
5. Approve case creation, then show the resulting case ID and persisted record.
6. Run the retention-period question. Show insufficient evidence and no new case.
7. If time permits, demonstrate rejection or the VendorRisk route.

**Controls and next steps, 1–2 minutes:**

“Exact excerpts reduce invented policy prose, but the model can still select an irrelevant section. That is why we evaluate relevance and retain human review. This demo includes integration-token authentication, persisted decisions, document versions and hashes, proposal expiry and duplicate-approval protection. Production would require authenticated reviewer roles, document ACLs, protected audit storage, monitoring and a connection to the customer's case system.”

## Customer discovery questions

- Who asks these questions today, and who owns the final policy decision?
- Which policies are authoritative, how are they versioned, and how often do they change?
- What is the current time to find evidence and route a request?
- Which requests must never become automated actions?
- What information must a reviewer see to make a decision?
- Which case system and identity provider should the pilot integrate with?
- What are the data residency, retention and provider restrictions?
- What would count as a successful two-week pilot?

## Technical questions you should be ready to answer

### Why n8n when LangFlow was preferable?

The assignment allows both. n8n makes the form interaction, approval pause and HTTP action visible. The Python service keeps retrieval and action validation independently testable. If the customer standardizes on LangFlow, the same APIs can be exposed as components; that migration is not included in this demo.

### Is this really RAG without a vector database?

Yes. Retrieval-augmented generation can use lexical retrieval. Here BM25 retrieves document sections, and the model consumes that retrieved context to produce a structured decision. The displayed answer is assembled from the selected source text. This is deliberately extractive RAG, not free-form synthesis. It does not use embeddings, semantic search or a vector database.

### Why not let the model write the answer?

The use case prioritizes exact policy wording and traceability. The model selects evidence and a queue, while the server renders the original excerpts. This reduces invented policy facts. The tradeoff is a less conversational answer and continued dependence on the model to judge evidence relevance.

### Where is the LLM-powered decision?

In `call_llm` and `propose`: the model chooses `supported` versus `insufficient`, one to three evidence IDs, and a queue. The queue determines the case destination after approval. This is more than cosmetic text generation.

### What actually happens when the human approves?

`POST /decisions` loads the server-stored proposal, checks expiry and source hashes, starts a SQLite transaction, and writes a case only for an approved supported proposal. A unique proposal ID constraint and transaction prevent duplicate cases when the same approval is replayed. A separate new request can still create another case; there is no semantic duplicate detection across new requests.

### How is the human-in-the-loop implemented?

An n8n Form node waits for a person to select Approve or Reject, enter a reviewer name, and provide a reason. In this local demo the name is self-declared and the same browser can play both roles. Production must enforce reviewer identity, authorization, and separation of duties through an identity provider or a case-system approval mechanism.

### Can it still hallucinate?

The model cannot introduce new policy prose into the rendered answer because it returns only IDs and a queue. However, it can choose a real but irrelevant citation or incorrectly judge evidence as sufficient. Metadata checks do not prove semantic entailment. Evaluate unsupported, ambiguous and adversarial questions; use human review to catch remaining errors. Never claim a zero-hallucination guarantee.

### What happens when the policy is missing or changes?

No lexical matches skip the model and return a limitation. When there are matches but the question is not answered, the model is instructed to abstain. Unsupported proposals cannot create cases. At approval time, the server checks document hashes. A changed file blocks the action and requires a fresh retrieval after restart. More mature document lifecycle/version handling would be needed at scale.

### How do you defend against prompt injection?

The prompt marks the request and context as untrusted data. The model cannot call arbitrary tools or choose arbitrary endpoints. The server rejects unknown citation IDs, extra output keys and unsupported queue values. A reviewer sees the original question and evidence. These reduce risk but do not prove immunity; the live evaluation includes malicious instructions and fabricated policy references.

### How would this run on AWS or Azure?

Treat this as a proposed production design: privately host n8n and an application service; put secrets in the cloud secret manager; use private document storage and a managed database; integrate the customer's identity and case systems; restrict provider egress; add telemetry and backups. Use the customer's existing deployment standard. Kubernetes and Terraform are reasonable enterprise options, but they are not needed for this local proof of concept and are not implemented here.

### What about air-gapped environments?

The current demo calls OpenAI over the internet, so it is not air-gapped. A disconnected deployment would require a locally hosted model, locally available dependencies and images, offline document ingestion, and an evaluation of that model's schema compliance and evidence selection. Do not claim that changing a URL alone makes the system air-gap ready.

### What about RBAC, data lineage and audit trails?

Implemented: an integration token, source title/section/version/hash, persisted retrieval context, persisted model metadata, human decision and case records. Not implemented: per-user RBAC, document ACL filtering, authenticated reviewer identity, immutable/WORM audit storage, full enterprise data lineage, encryption key lifecycle or regulatory certification.

### Why standard-library Python and SQLite?

The assignment limits time and asks for a small working workflow. The service has no Python package installation dependency. SQLite provides real persistence and transaction semantics for a single-machine demo. The HTTP server and SQLite database are deliberately local-demo infrastructure; production would use a production application server, operational controls and a suitable managed store.

### What have you measured?

Automated application tests verify control behavior. Live evaluation results must come from your own actual provider run; use `evidence/live-evaluation.json` after generating it. The live runner checks expected status, queue and required citations, with recorded latency and provider usage. It does not replace manual relevance review or a larger evaluation set. There are no measured business savings in this demo.

## Use your resume carefully

The supplied resume emphasizes RAG, agent orchestration, financial-services compliance, Python, Java and cloud deployment. Connect this demo to those topics only through work you personally performed and can explain. Do not borrow the resume's percentage improvements as results of this assessment. Be prepared to distinguish what you implemented here, what a previous team built, and what you are proposing as a production extension.

## Suggested schedule to September 16

- September 10: run the stack, inspect the documents and complete the positive scenario.
- September 11: run rejection, unsupported questions and the live evaluation; fix concrete failures.
- September 12: capture genuine screenshots and export the tested workflow.
- September 13: rehearse the five slides and a 3-minute demo; inspect the code paths above.
- September 14: practice customer discovery and technical follow-up questions.
- September 15: check the repository/ZIP for secrets, broken instructions and missing deliverables.
- September 16: submit using the recruiter's requested channel and preserve the final version.

This schedule spreads setup and rehearsal across days; it is not a recommendation to expand the implementation beyond the assignment's 4–5 hour scope.
