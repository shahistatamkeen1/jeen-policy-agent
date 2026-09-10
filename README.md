# Cedarbridge Bank — Governed AI Policy Review Agent

A production-oriented proof of concept for a governed enterprise AI workflow that retrieves policy evidence, uses an LLM to make evidence-grounded routing recommendations, presents citations to a human reviewer, and creates a durable review case only after explicit approval.

> **Note:** Cedarbridge Bank and all included policy documents are fictional and synthetic. No real customer or confidential banking data is used.

---

## Overview

Enterprise AI systems should not make consequential decisions solely because an LLM generated a plausible answer.

This project demonstrates a safer pattern:

**Retrieve → Ground → Recommend → Review → Validate → Act**

A user submits a policy question. The system retrieves relevant policy sections, asks an LLM to determine whether the evidence is sufficient, proposes the appropriate review queue, and presents the supporting citations to a human reviewer.

A durable review case is created only when:

1. relevant policy evidence exists,
2. the LLM recommendation is grounded in that evidence, and
3. a human explicitly approves the action.

If evidence is insufficient, downstream case creation is blocked even when approval is attempted.

---

## Key Capabilities

- Policy retrieval using BM25-based search
- Evidence-grounded LLM reasoning
- Policy citations with document and section metadata
- Structured routing recommendations
- Explicit `supported` / `insufficient` evidence states
- Human-in-the-loop approval
- Durable case creation only after validation
- Rejection path with no downstream action
- Insufficient-evidence safety guardrail
- Prompt-injection resistance testing
- Fabricated-policy / citation resistance
- Auditable workflow execution
- Dockerized local environment
- n8n workflow orchestration
- Automated application tests
- Live LLM evaluation

---

## Architecture

```text
                       ┌─────────────────────┐
                       │   Policy Question   │
                       │     n8n Form        │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Retrieve Policy   │
                       │      Sections       │
                       │      BM25 RAG       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    LLM Evidence     │
                       │  + Routing Decision │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Prepare Cited Review│
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Human Review     │
                       │ Approve / Reject    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Validate Decision & │
                       │   Evidence Status   │
                       └──────────┬──────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
                   ▼                             ▼
          ┌─────────────────┐           ┌─────────────────┐
          │   Create Case   │           │ Closed / No     │
          │ Supported +     │           │ Action          │
          │ Approved Only   │           │                 │
          └─────────────────┘           └─────────────────┘