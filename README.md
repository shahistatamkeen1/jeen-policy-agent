# Cedarbridge Bank — Governed AI Policy Review Agent

A governed enterprise AI proof of concept that combines **RAG, LLM-powered decision support, policy citations, human-in-the-loop review, and controlled action execution**.

The agent retrieves relevant internal policy evidence, determines whether the evidence is sufficient, recommends the appropriate review queue, presents the exact supporting citations to a human reviewer, and creates a durable review case only after explicit approval.

> **Note:** Cedarbridge Bank and all policy documents in this repository are fictional and synthetic. No real customer, banking, or confidential data is used.

---

## Assessment Summary

This project was built as an **AI Solution Engineer working demo** focused on a financial-services policy-review use case.

The core design principle is:

> **Retrieve → Ground → Recommend → Review → Validate → Act**

The LLM is used for evidence selection and routing recommendation, but it is **not treated as an autonomous authority**.

A case can be created only when:

1. relevant policy evidence is available,
2. the LLM recommendation is grounded in that evidence,
3. the recommendation passes server-side validation, and
4. a human explicitly approves the action.

If evidence is insufficient, the workflow abstains and prevents downstream case creation.

---

## Customer Context & Business Problem

**Customer:** Cedarbridge Bank, a fictional financial-services organization.

Operations teams regularly need to answer internal questions related to:

- AI usage
- customer-data handling
- vendor onboarding
- vendor assurance
- procurement routing

A manual process can require employees to search multiple policy documents, identify the correct section, determine which review team owns the request, and manually create a case.

This creates several risks:

- slow policy interpretation,
- inconsistent routing,
- unsupported answers,
- missing evidence,
- incorrect escalation,
- and over-reliance on AI-generated responses.

The goal of this solution is to accelerate policy triage while keeping the final action **grounded, reviewable, and human-controlled**.

---

## Key Capabilities

- **Retrieval-Augmented Generation (RAG)** using BM25 retrieval
- Evidence-grounded LLM decision making
- Exact policy citations with document and section metadata
- Structured review-queue recommendations
- Explicit `supported` and `insufficient` evidence states
- Human-in-the-loop approval and rejection
- Durable case creation only after approval and validation
- Server-side guardrails
- Prompt-injection resistance testing
- Fabricated-citation rejection
- Duplicate/replay protection
- Policy-change validation
- Proposal-expiry handling
- Persistent audit records
- Dockerized local environment
- n8n workflow orchestration
- Automated application testing
- Live-model evaluation

---

## Architecture

```text
                       ┌─────────────────────┐
                       │   Policy Question   │
                       │      n8n Form       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Retrieve Relevant  │
                       │  Policy Sections    │
                       │     BM25 RAG        │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    LLM Evidence     │
                       │ + Routing Decision  │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Validate & Prepare  │
                       │    Cited Review     │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Human Review     │
                       │  Approve / Reject   │
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
          │   Create Case   │           │  Close With     │
          │ Supported +     │           │   No Action     │
          │ Approved Only   │           │                 │
          └─────────────────┘           └─────────────────┘