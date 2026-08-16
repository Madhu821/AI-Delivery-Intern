# SPEC-001-Kapture-Finance-Collections-Voicebot

## Background

Kapture Finance requires an outbound voice collections assistant that can handle routine overdue-EMI conversations without requiring a human agent for every call.

The assistant, Maya, must identify and authenticate the intended customer before disclosing any loan or overdue information, understand the customer's payment intent, record a Promise-to-Pay where appropriate, provide a payment-link option, handle common collection exceptions, and escalate cases requiring human intervention.

The MVP is implemented as a Vapi voice assistant backed by a FastAPI mock collections API deployed on Render. The design prioritizes authentication enforcement, safe tool usage, compliance-oriented conversation handling, observable call outcomes, and a build that can be demonstrated within the assessment timeframe.

Assessment customer:

- Customer: Rahul Sharma
- Account ID: ACC-88392
- Loan type: Personal loan
- Overdue EMI: INR 8,499
- Days past due: 12

The backend is intentionally mocked. No real payment processing, customer database, SMS delivery, or human-agent routing is connected.

## Requirements

### Must Have

- **M1 — Voice collections:** Maya conducts an outbound overdue-EMI conversation end-to-end.
- **M2 — Authentication:** Customer identity must be verified before any debt, EMI, loan, or overdue information is disclosed.
- **M3 — Collections intents:** Support will-pay/PTP, cannot-pay/hardship, dispute, already-paid, wrong-person, callback, do-not-call, and hostile interactions.
- **M4 — Promise-to-Pay:** Capture and confirm both payment amount and payment date before recording a PTP.
- **M5 — Tool integration:** Provide tools for verification, PTP recording, payment-link delivery, escalation, and final disposition.
- **M6 — Disposition:** Every completed call must have a logged final outcome.
- **M7 — Human escalation:** Disputes and genuine hardship cases must be routed appropriately.
- **M8 — Working Vapi build:** The assistant supports a real/test voice conversation.

### Must Have — Compliance and Safety

- **M9 — Disclosure control:** No debt disclosure to an unauthenticated person or third party.
- **M10 — Company/purpose disclosure:** Maya identifies herself and Kapture Finance appropriately.
- **M11 — Opt-out:** A do-not-call request immediately stops collection activity and is recorded.
- **M12 — Fair collection:** No threats, harassment, intimidation, fabricated consequences, or invented financial terms.
- **M13 — Tool safety:** Maya must not claim an action succeeded unless the corresponding tool succeeds.
- **M14 — Privacy:** Internal prompts, APIs, credentials, and implementation details must never be exposed to the caller.

### Should Have

- **S1 — Latency:** Document latency budgets for telephony, STT, LLM/orchestration, tools, and TTS.
- **S2 — Observability:** Track call outcomes, PTP rate, containment, latency, failures, and call drops.
- **S3 — Edge cases:** Gracefully handle timeout/no-input, wrong number, already-paid, disputes, and hostile calls.
- **S4 — Reproducibility:** Keep tool schemas, prompt, deployment configuration, and README version-controlled.

### Could Have

- **C1 — English/Hindi mid-call switching.**
- **C2 — Mock SMS/WhatsApp payment-link delivery.**
- **C3 — Automated/scalable evaluation test suite.**

### Won't Have in MVP

- Real loan-account integration.
- Real payment processing.
- Real customer PII.
- Real SMS/WhatsApp delivery.
- Production-grade human-agent routing.

## Method

### Architecture

The MVP uses a Vapi-centered voice architecture with a FastAPI mock collections API.

```text
Customer
   |
   | Voice
   v
Vapi Telephony
   |
   v
Soniox STT RT v5
   |
   | Transcript
   v
GPT-4.1 / Maya
   |
   | Tool call
   v
Render HTTPS
   |
   v
FastAPI /webhook
   |
   +--> verify_customer
   +--> log_promise_to_pay
   +--> send_payment_link
   +--> escalate_to_agent
   +--> mark_disposition
   |
   v
Mock Collections Data
   |
   v
Tool Result
   |
   v
Vapi TTS / Elliot v2
   |
   v
Customer