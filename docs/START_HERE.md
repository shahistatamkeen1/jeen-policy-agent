# Start here: build, run, understand, demonstrate

This repository contains the completed working demo for the Jeen AI Solution Engineer home assignment. The implementation has been tested with a live provider, executed end-to-end in n8n, and validated through automated and live-model evaluations. This guide explains how to reproduce, understand, and demonstrate the solution locally.

Your stated target is **September 16**. The email screenshot shows an interview on **September 23, 10–11 AM**, with no visible timezone. An interview date is not necessarily the submission deadline. Keep September 16 as your working deadline unless the recruiter confirms otherwise.

## 1. Understand what you will demonstrate

The customer is Cedarbridge Bank, a fictional financial-services organization. Operations staff need answers to internal AI-use and vendor policies and need to send requests to the correct review queue.

Your agent performs these steps:

1. An n8n form collects a request ID and policy question.
2. A Python HTTP endpoint retrieves the four best-matching policy sections with BM25.
3. An LLM selects evidence IDs and a queue, or reports insufficient evidence.
4. Python checks the response schema, source IDs and queue. It renders exact source text.
5. An n8n form pauses the workflow for a human to inspect the evidence and approve or reject.
6. The case endpoint persists an approved supported request in SQLite and records the decision.
7. The final form displays the case ID, or explains that no case was created.

The first live question will be: **May a team upload customer statements to a public AI chatbot for summarization?** Policy AI-01 says no and routes the question to SecurityReview. Approval creates a review case only; it does not authorize the upload.

## 2. Prepare your computer

Use Windows PowerShell and Docker Desktop with Linux containers. Docker Desktop must be installed, running, and show its engine as ready. If it asks to enable WSL2 or restart Windows, follow its normal setup.

Extract the ZIP into a convenient folder such as `C:\Projects\jeen-policy-agent`. Open that folder in VS Code. The folder you open must contain `compose.yaml`, `Dockerfile`, and `.env.example` directly.

Open **Terminal → New Terminal**, then verify:

```powershell
docker --version
docker compose version
```

If a command is not recognized, finish the Docker installation and reopen VS Code. Do not paste the commands into the Python interpreter.

## 3. Set the configuration locally

```powershell
Copy-Item .env.example .env
```

Open `.env` in VS Code. Set:

```dotenv
OPENAI_API_KEY=your-own-api-key
OPENAI_MODEL=gpt-4o-mini
DEMO_API_TOKEN=your-own-long-random-token
```

Replace the example values. Do not add these secrets to the workflow JSON, screenshots, slides, GitHub, or chat. An OpenAI API account with model access and billing is needed; follow the provider's key and billing settings. The key goes only into your local `.env` file.

Generate a random integration token in PowerShell if you need one:

```powershell
[guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
```

Copy that generated value into `DEMO_API_TOKEN`. You will also paste it into one n8n credential in step 6.

## 4. Start the services

```powershell
docker compose up --build -d
docker compose ps
```

The first build can take several minutes while Docker downloads images. Both services should show as running. Open `http://localhost:8010/health` in your browser. Expected fields:

```json
{"status":"ok","llm_configured":true,"chunks":8,"mode":"live_provider_only"}
```

`llm_configured: true` checks that a key is present, not that billing or access works. The live evaluation checks the actual provider connection.

Then open `http://localhost:5678`. Create the owner account for your local n8n installation. Keep that account's credentials private. This local setup does not need an n8n Cloud subscription.

## 5. Import the workflow

1. In n8n, create a new workflow.
2. Open the workflow menu (usually the three dots near the top right).
3. Choose **Import from File**.
4. Select `workflows/cedarbridge-policy-agent.json` from the extracted project.
5. Confirm you can see the request form, retrieval, LLM decision, review renderer, human approval, case action, and result form.
6. Save the workflow. UI wording can vary slightly between releases.

The assignment says LangFlow is preferable but explicitly allows n8n. This implementation uses n8n's native form pages and HTTP integrations to keep the workflow visible and the code easy to test.

## 6. Connect the integration credential

For each of these three HTTP Request nodes:

- Retrieve policy sections
- LLM evidence and routing decision
- Record decision and create case

Open the node. Authentication should be **Generic Credential Type → Header Auth**. Create a credential in the first node:

- Credential display name: `Cedarbridge local API`
- Header name: `X-Demo-Token`
- Header value: the exact `DEMO_API_TOKEN` from `.env`

Save it, and select the same credential in the other two nodes. The URLs should begin with `http://policy-api:8000`. Inside Docker, `policy-api` is the service hostname; `localhost` inside the n8n container would point back to n8n itself.

No OpenAI credential is required in n8n because the Python service calls the provider. The integration token and provider key are separate credentials.

## 7. Run the positive scenario

1. Click **Execute workflow** or open the first node and choose **Listen for test event**.
2. Open the **Test URL** shown in the Form Trigger node. Copy the URL displayed by your n8n instance; do not invent it.
3. Enter request ID `DEMO-001`.
4. Enter: `May a team upload customer statements to a public AI chatbot for summarization?`
5. Submit. The browser should advance to the human review form.
6. Confirm the evidence status is `supported`, the queue is `SecurityReview`, and citation `AI-01` appears with its original policy text.
7. Before clicking approve, explain that the workflow is paused and no case exists yet.
8. Choose `Approve`, enter a reviewer name and a reason such as `AI-01 directly covers customer statements in public AI tools; create a SecurityReview case.`
9. Submit. The completion screen should show `case_created`, a `CB-...` case ID, and `SecurityReview`.

For the demo, you play both requester and reviewer. This demonstrates a real human interaction, but not independently authenticated roles. State this clearly if asked about RBAC.

## 8. Verify persistence

Check the created case from PowerShell. Read the token from your own local file without putting it into the command text:

```powershell
$demoToken = (Get-Content .env | Where-Object { $_ -match '^DEMO_API_TOKEN=' }) -replace '^DEMO_API_TOKEN=', ''
$demoHeaders = @{ 'X-Demo-Token' = $demoToken }
Invoke-RestMethod -Uri 'http://localhost:8010/cases' -Headers $demoHeaders | ConvertTo-Json -Depth 12
Invoke-RestMethod -Uri 'http://localhost:8010/audit' -Headers $demoHeaders | ConvertTo-Json -Depth 12
```

You should see the case, evidence, queue, reviewer and decision record. This is the workflow's real action: an HTTP tool writes a durable case. It is not a mock email or a chat response.

## 9. Run rejection and insufficient-evidence scenarios

Start a fresh test execution for each scenario, with a new request ID.

**Rejection:** repeat the positive question, select `Reject`, and explain why. Expected result: `rejected`, with no new case.

**Missing knowledge:** ask `How many years must customer statements be retained?` Expected result: `insufficient`, a limitation message, and no queue. Select Reject to close the review. Even if you select Approve, the server must return `closed_no_action` and create no case.

**Vendor route:** ask `A new analytics vendor is missing a SOC 2 Type II report. Which team should review this before onboarding?` Expected result: VR-01, VendorRisk, and a case only after approval.

## 10. Run the automated checks

The Docker container includes Python, so you do not need a local Python installation:

```powershell
docker compose exec policy-api python -m unittest discover -s tests -v
```

These are application tests with fixture model responses. To evaluate the actual provider, run:

```powershell
docker compose exec policy-api python -m tests.evaluate_live
docker compose cp policy-api:/app/evidence/live-evaluation.json ./evidence/live-evaluation.json
```

The live suite makes approximately ten provider calls. It uses a temporary database and creates no review cases. Inspect each result manually; a passing queue/citation check alone does not prove every answer is sufficient. If a live check fails, examine its retrieved evidence and decision before changing prompts. Do not replace a failed result with a fixture.

## 11. Review the captured evidence

The repository includes genuine screenshots from the tested workflow:

1. `evidence/01_workflow_architecture.png`  
   Full n8n workflow and successful execution.

2. `evidence/02_supported_approved_case_created.png`  
   Supported request approved by the reviewer with a durable case created.

3. `evidence/03_supported_rejected_no_case.png`  
   Supported recommendation rejected by the reviewer with no case creation.

4. `evidence/04_insufficient_approval_blocked.png`  
   Insufficient-evidence request safely blocked even when approval was attempted.

5. `evidence/05_live_evaluation_10_of_10.png`  
   Live-provider evaluation showing 10/10 checks passed.

6. `evidence/06_cited_policy_evidence.png`  
   Human-review screen showing the source policy citation and proposed queue.

7. `evidence/07_retrieval_candidate_chunks_insufficient.png`  
   Candidate retrieval example demonstrating why retrieval similarity alone is not sufficient evidence.

Detailed live-model results are stored in:

`evidence/live-evaluation.json`

A short recording can substitute for screenshots under the assignment instructions. A recording of the happy path plus abstention is a useful backup. Do not submit illustrated screens or fixture results as a live LLM run.

## 12. Prepare the submission and presentation

Read `PRESENTER_GUIDE.md` and rehearse using the five-slide deck. Update slide 5 with your actual live results only after you have them. Export the workflow again from n8n after configuring it so the submission reflects your tested canvas. Check that the export contains no raw secrets or pinned private execution data.

Follow `SUBMISSION_CHECKLIST.md`. Do not push `.env`, the local database, personal documents or secrets. It is fine to include synthetic policy documents, source code, the workflow, slides, and sanitized run evidence.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Docker command not recognized | Install/start Docker Desktop and reopen the terminal. |
| Docker engine unavailable | Start Docker Desktop; check WSL2 setup and any required reboot. |
| Port 5678 or 8010 already in use | Stop the conflicting local app, or edit only the host-side port in compose.yaml and use the new browser URL. |
| HTTP node says credential missing | Select the Header Auth credential in all three HTTP nodes. |
| HTTP 401 from policy API | Header must be X-Demo-Token and must exactly match `.env`. |
| Host policy-api cannot be found | Run both services with this Compose file; keep the service hostname in node URLs. |
| /health shows llm_configured false | Set the key and run `docker compose up -d --force-recreate policy-api`. |
| Provider HTTP 401 | Check your provider key locally. |
| Provider HTTP 429 | Check provider billing, quota and rate limits. |
| Provider HTTP 400 or 404 | Confirm the configured model supports Chat Completions and JSON output and is available to the account. |
| Test form stops responding | Start a fresh test execution and use the newly displayed test URL. |
| Proposal expired | Proposals expire after one hour; submit a fresh request. |
| Policy changed | Rebuild/restart the service and submit a fresh request. |
| Unexpected live answer | Reject the case; inspect the retrieved chunks and prompt. Do not claim zero hallucinations. |

Logs:

```powershell
docker compose logs --tail=60 policy-api
docker compose logs --tail=60 n8n
```

Stop when finished:

```powershell
docker compose down
```

This keeps named volumes. Do not add `-v` unless you deliberately want to delete the stored n8n setup and case data.

## What I implemented and why

Read the code in this order: `load_documents` → `retrieve` → `Agent.search` → `call_llm` → `validate` → `propose` → `decide`. Then read the workflow node parameters. The functions follow the demo sequence. The application uses no Python third-party libraries, minimizing setup and making the core decisions inspectable.

Source references: [n8n Form node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.form/), [Form Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.formtrigger/), [n8n 2.38.6 release](https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.6), [OpenAI Chat API](https://developers.openai.com/api/reference/resources/chat).
