# AI-Delivery-Intern Voicebot

An MVP outbound voice collections assistant built for the AI Delivery Intern assessment.

Maya is a voice-based collections assistant that authenticates the intended customer before disclosing overdue information, handles common payment intents, records Promise-to-Pay commitments, sends a mock payment link, escalates disputes/hardship cases, and records a final call disposition.

## Architecture

```text
Customer
   |
   v
Vapi Telephony
   |
   +--> Soniox STT RT v5
   |
   v
GPT-4.1 / Maya
   |
   +--> verify_customer
   +--> log_promise_to_pay
   +--> send_payment_link
   +--> escalate_to_agent
   +--> mark_disposition
            |
            v
     Render HTTPS
            |
            v
     FastAPI /webhook
            |
            v
     Mock Collections Data

## Technology Stack
Python
FastAPI
Vapi
GPT-4.1
Soniox STT RT v5
Elliot v2 / Vapi voice
Render
GitHub
Backend

The backend exposes:

POST /webhook

Public assessment endpoint:

https://ai-delivery-intern.onrender.com/webhook

The backend implements:

verify_customer
log_promise_to_pay
send_payment_link
escalate_to_agent
mark_disposition

The backend uses deterministic mock customer data for the assessment.

Test Customer
Customer: Rahul Sharma
Account ID: ACC-88392
Loan: Personal loan
Overdue EMI: INR 8,499
Days past due: 12

This is assessment/mock data and is not connected to a real lending system.

Authentication

Authentication is a mandatory gate.

Maya must call verify_customer before disclosing:

overdue amount
EMI information
loan information
payment status
debt information

The backend normalizes speech-transcribed verification codes.

Examples:

1234
1, 2, 3, 4

These are normalized before validation.

Tools
verify_customer

Verifies the customer's identity.

log_promise_to_pay

Records a confirmed Promise-to-Pay after both amount and date have been explicitly confirmed.

send_payment_link

Sends a mock payment link through SMS, WhatsApp, or both.

This does not process a payment.

escalate_to_agent

Handles dispute and financial-hardship cases requiring human intervention.

mark_disposition

Records the final outcome of every completed call.

Supported outcomes:

PTP_AGREED
ALREADY_PAID
DISPUTED
HARDSHIP_ESCALATED
WRONG_PERSON
DO_NOT_CALL
NO_RESPONSE
Conversation Safety

The assistant is designed to:

authenticate before debt disclosure
avoid threats or harassment
respect do-not-call requests
avoid exposing information to third parties
avoid inventing account information
avoid claiming tool actions succeeded when they failed
escalate disputes and genuine hardship
record a final disposition before ending a completed call

Test Results
Scenario	Result
Authentication before disclosure	Passed
Voice verification	Passed
Successful Promise-to-Pay	Passed
Payment-link flow	Passed
Already-paid case	Passed
Do-not-call case	Passed
Final disposition	Passed

Additional test evidence is documented in demo/README.md.


Repository Structure

Delivery-Intern/
├── mock-server/
│ ├── app.py
│ └── requirements.txt
├── docs/
│ ├── HLD.md
│ └── architecture.puml
├── vapi/
│ ├── system-prompt.txt
│ └── tool-schemas.json
├── tests/
├── demo/
│ └── README.md
├── README.md
└── .gitignore


Running the Mock Server

Install dependencies:

pip install -r mock-server/requirements.txt

Run:

uvicorn mock-server.app:app --host 0.0.0.0 --port 8000

Local webhook:

http://127.0.0.1:8000/webhook


Example Verification Test

curl -X POST http://127.0.0.1:8000/webhook
-H "Content-Type: application/json"
-d '{"message":{"type":"tool-calls","toolCallList":[{"id":"test-1","type":"function","function":{"name":"verify_customer","arguments":{"account_id":"ACC-88392","verification_code":"1, 2, 3, 4"}}}]}}'

Expected result:

{
"verified": true
}


Deployment

The backend is deployed through GitHub to Render.

Deployment flow:

Local code
|
v
GitHub
|
v
Render
|
v
Public HTTPS webhook
|
v
Vapi


Known Limitations

This is an assessment MVP rather than a production collections platform.

mock/static customer data
mock payment-link delivery
mock human escalation
Render free-tier cold-start latency
English-first conversation
voice pronunciation may require further tuning for "Kapture" and INR amounts
no real payment processing
no real SMS/WhatsApp integration


What I Would Improve for Production
Connect to a secure collections/account service.
Add production authentication and service-to-service authorization.
Add a persistent database and audit trail.
Add production human-agent routing.
Integrate approved messaging providers.
Add Hindi/English language switching.
Add automated conversation evaluation.
Add dashboards and alerting.
Add load and latency testing.
Perform jurisdiction-specific compliance review.


Documentation
High-Level Design: docs/HLD.md
Architecture Diagram: docs/architecture.puml
Maya System Prompt: vapi/system-prompt.txt
Vapi Tool Schemas: vapi/tool-schemas.json
Demo Evidence: demo/README.md