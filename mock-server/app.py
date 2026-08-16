from datetime import datetime, timezone
from typing import Any
import json
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Kapture Finance Mock Collections API",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kapture-collections")

# ---------------------------------------------------------
# Mock customer/account data
# ---------------------------------------------------------

CUSTOMER = {
    "account_id": "ACC-88392",
    "customer_name": "Rahul Sharma",
    "loan_type": "Personal Loan",
    "overdue_amount": 8499,
    "days_past_due": 12,
}

# Reference material explicitly provides these mock
# verification values.
VALID_VERIFICATION_CODES = {"1234", "1995"}


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Current Vapi format:
      message.toolCallList

    Reference/older examples may use:
      message.toolCalls

    We support both.
    """
    tool_calls = message.get("toolCallList")

    if tool_calls is None:
        tool_calls = message.get("toolCalls", [])

    return tool_calls or []


def get_tool_name(tool_call: dict[str, Any]) -> str | None:
    """
    Current Vapi:
      { "name": "verify_customer", ... }

    Some older payloads may contain:
      { "function": { "name": "verify_customer", ... } }
    """
    if tool_call.get("name"):
        return tool_call["name"]

    function = tool_call.get("function", {})
    return function.get("name")


def get_tool_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
    """
    Current Vapi uses `arguments` / `parameters`
    depending on payload representation.
    """
    arguments = tool_call.get("arguments")

    if arguments is None:
        arguments = tool_call.get("parameters")

    if arguments is None:
        function = tool_call.get("function", {})
        arguments = function.get("arguments")

    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except json.JSONDecodeError:
            return {}

    return arguments or {}


def get_tool_call_id(tool_call: dict[str, Any]) -> str:
    return tool_call.get("id", "unknown-tool-call")


def tool_result(tool_call_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """
    Vapi expects the result itself as a string.
    """
    return {
        "toolCallId": tool_call_id,
        "result": json.dumps(result, separators=(",", ":")),
    }


# ---------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------

def verify_customer(args: dict[str, Any]) -> dict[str, Any]:
    account_id = args.get("account_id")
    verification_code = str(args.get("verification_code", "")).strip()

    if account_id != CUSTOMER["account_id"]:
        return {
            "verified": False,
            "message": "Customer account could not be verified.",
        }

    if verification_code in VALID_VERIFICATION_CODES:
        return {
            "verified": True,
            "customer_name": CUSTOMER["customer_name"],
            "message": "Identity verified successfully.",
        }

    return {
        "verified": False,
        "message": "Verification failed. Incorrect verification code.",
    }


def log_promise_to_pay(args: dict[str, Any]) -> dict[str, Any]:
    account_id = args.get("account_id")
    ptp_date = args.get("ptp_date")
    amount = args.get("amount")

    if account_id != CUSTOMER["account_id"]:
        return {
            "success": False,
            "message": "Unknown account.",
        }

    if not ptp_date or amount is None:
        return {
            "success": False,
            "message": "PTP date and amount are required.",
        }

    # Mock ID. No real database/payment operation is performed.
    ptp_id = f"PTP-{datetime.now().strftime('%H%M%S')}"

    return {
        "success": True,
        "ptp_id": ptp_id,
        "confirmed_date": ptp_date,
        "amount": amount,
    }


def send_payment_link(args: dict[str, Any]) -> dict[str, Any]:
    account_id = args.get("account_id")
    channel = args.get("channel")

    if account_id != CUSTOMER["account_id"]:
        return {
            "success": False,
            "message": "Unknown account.",
        }

    if channel not in {"SMS", "WhatsApp", "BOTH"}:
        return {
            "success": False,
            "message": "Unsupported payment-link channel.",
        }

    return {
        "success": True,
        "channel": channel,
        "message": (
            f"Mock payment link sent successfully via {channel} "
            "to the registered mobile number."
        ),
    }


def escalate_to_agent(args: dict[str, Any]) -> dict[str, Any]:
    account_id = args.get("account_id")
    reason = args.get("reason")

    if account_id != CUSTOMER["account_id"]:
        return {
            "success": False,
            "message": "Unknown account.",
        }

    allowed_reasons = {
        "DISPUTE",
        "HARDSHIP_REQUEST",
    }

    if reason not in allowed_reasons:
        return {
            "success": False,
            "message": "Unsupported escalation reason.",
        }

    escalation_id = f"ESC-{datetime.now().strftime('%H%M%S')}"

    return {
        "success": True,
        "escalation_id": escalation_id,
        "reason": reason,
        "message": "Customer escalation recorded successfully.",
    }


def mark_disposition(args: dict[str, Any]) -> dict[str, Any]:
    account_id = args.get("account_id")
    status = args.get("status")
    notes = args.get("notes", "")

    if account_id != CUSTOMER["account_id"]:
        return {
            "success": False,
            "message": "Unknown account.",
        }

    allowed_statuses = {
        "PTP_AGREED",
        "ALREADY_PAID",
        "DISPUTED",
        "HARDSHIP_ESCALATED",
        "WRONG_PERSON",
        "DO_NOT_CALL",
        "NO_RESPONSE",
    }

    if status not in allowed_statuses:
        return {
            "success": False,
            "message": "Unsupported disposition status.",
        }

    return {
        "success": True,
        "disposition_logged": status,
        "notes": notes,
        "timestamp": utc_now(),
    }


# ---------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------

def execute_tool(
    name: str,
    args: dict[str, Any],
) -> dict[str, Any]:

    logger.info("Tool call: %s | args=%s", name, args)

    if name == "verify_customer":
        return verify_customer(args)

    if name == "log_promise_to_pay":
        return log_promise_to_pay(args)

    if name == "send_payment_link":
        return send_payment_link(args)

    if name == "escalate_to_agent":
        return escalate_to_agent(args)

    if name == "mark_disposition":
        return mark_disposition(args)

    return {
        "success": False,
        "message": f"Unknown tool: {name}",
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/")
def health_check():
    return {
        "service": "Kapture Finance Mock Collections API",
        "status": "ok",
    }


# ---------------------------------------------------------
# Vapi webhook
# ---------------------------------------------------------

@app.post("/webhook")
async def vapi_webhook(request: Request):

    body = await request.json()

    logger.info("Incoming Vapi request: %s", body)

    message = body.get("message", {})
    message_type = message.get("type")

    # Vapi sends many informational events to server URLs.
    # Only tool-calls require a tool result response.
    if message_type != "tool-calls":
        return JSONResponse(
            status_code=200,
            content={"status": "acknowledged"},
        )

    tool_calls = get_tool_calls(message)

    results = []

    for tool_call in tool_calls:
        tool_call_id = get_tool_call_id(tool_call)
        tool_name = get_tool_name(tool_call)
        arguments = get_tool_arguments(tool_call)

        if not tool_name:
            result = {
                "success": False,
                "message": "Tool name was missing from Vapi request.",
            }
        else:
            result = execute_tool(tool_name, arguments)

        results.append(
            tool_result(
                tool_call_id,
                result,
            )
        )

    # IMPORTANT:
    # Vapi expects HTTP 200 and this exact results structure.
    return JSONResponse(
        status_code=200,
        content={
            "results": results,
        },
    )