# Maya Voicebot Demo Evidence

## Purpose

This folder documents the voice-call scenarios used to validate the Kapture Finance collections assistant.

## Environment

- Assistant: Maya - Kapture Collections
- Voice platform: Vapi
- LLM: GPT-4.1
- Transcriber: Soniox STT RT v5
- Voice: Elliot v2
- Backend: FastAPI
- Backend hosting: Render

## Test Scenarios

### 1. Authentication Protection

**Scenario**

The customer asks for the overdue amount before authentication.

**Expected**

Maya must not disclose the overdue amount and must request verification.

**Result**

Passed.

---

### 2. Successful Verification

**Input**

The customer speaks the verification code as:

`1, 2, 3, 4`

**Expected**

The backend normalizes the speech-transcribed value to `1234` and returns:

`verified=true`

**Result**

Passed locally and through the deployed Render endpoint.

---

### 3. Successful Promise-to-Pay

**Scenario**

1. Customer is identified.
2. Customer is authenticated.
3. Maya discloses the overdue EMI.
4. Customer agrees to pay.
5. Amount and payment date are confirmed.
6. `log_promise_to_pay` is called.
7. Customer requests SMS payment link.
8. `send_payment_link` is called.
9. `mark_disposition` records `PTP_AGREED`.

**Result**

Passed.

---

### 4. Already Paid

**Scenario**

After authentication and debt disclosure, the customer states that the EMI has already been paid.

**Expected**

Maya does not pressure the customer to pay again and records:

`ALREADY_PAID`

**Result**

Passed.

---

### 5. Do Not Call

**Scenario**

The customer requests that Kapture Finance not call again.

**Expected**

Maya immediately stops collection activity and records:

`DO_NOT_CALL`

**Result**

Passed.

---

## Known Voice-Quality Limitation

The selected voice may occasionally pronounce:

- `Kapture` as `Capture`
- INR 8,499 as dollar currency

The system prompt contains explicit pronunciation instructions. This remains a voice-quality limitation of the MVP and should be considered during final demo selection.

## Final Demo Recordings

Add the final recording links here after completing the final demo:

- Successful PTP: `TBD`
- Edge case: `TBD`

## Evidence

The implementation and configuration artifacts are stored in the repository:

- `docs/HLD.md`
- `docs/architecture.puml`
- `vapi/system-prompt.txt`
- `vapi/tool-schemas.json`
- `mock-server/app.py`