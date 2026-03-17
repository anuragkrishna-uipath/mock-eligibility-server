#!/usr/bin/env python3
"""
Mock MCP HTTP Server — Employee Eligibility Check

A lightweight HTTP REST API that exposes the check_employee_eligibility tool.
Zero dependencies — uses only Python stdlib.

Endpoints:
  GET  /health                        → Health check
  GET  /tools                         → List available tools
  POST /tools/check_employee_eligibility → Check eligibility

Deploy anywhere: Render, Railway, Fly.io, or use ngrok for quick testing.
"""

import json
import os
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

# ──────────────────────────────────────────────────────────────────────
# Eligibility logic
# ──────────────────────────────────────────────────────────────────────

ELIGIBLE_REASONS = [
    "Employee has been with the company for over 2 years and is in good standing.",
    "Employee's current laptop is past its 3-year refresh cycle.",
    "Employee recently received a promotion and qualifies for upgraded equipment.",
    "Employee's role requires high-performance hardware per IT policy.",
    "Employee is part of the engineering team with an approved hardware budget.",
    "Employee's existing device has been flagged for multiple hardware failures.",
    "Employee relocated to a new office and qualifies for equipment refresh.",
]

NOT_ELIGIBLE_REASONS = [
    "Employee received a new laptop within the last 12 months.",
    "Employee is currently on a performance improvement plan (PIP).",
    "Employee's department has exhausted its hardware budget for this quarter.",
    "Employee's role does not meet the minimum hardware tier requirement.",
    "Employee has an open request that is still being processed.",
    "Employee's probation period has not yet ended (minimum 6 months required).",
    "Employee's manager has not submitted the required pre-approval.",
]


def check_employee_eligibility(employee_name, employee_id=None, request_type="laptop", reason_for_request=""):
    is_demo = "demo" in reason_for_request.lower()

    if is_demo:
        is_eligible = True
        reason = "Request is for a customer demo — automatically approved per company policy."
    else:
        is_eligible = random.choice([True, False])
        if is_eligible:
            reason = random.choice(ELIGIBLE_REASONS)
        else:
            reason = random.choice(NOT_ELIGIBLE_REASONS)

    return {
        "employee_name": employee_name,
        "employee_id": employee_id or "EMP-" + str(random.randint(10000, 99999)),
        "request_type": request_type,
        "status": "eligible" if is_eligible else "not_eligible",
        "eligible": is_eligible,
        "reason": reason,
    }


TOOL_DEFINITION = {
    "name": "check_employee_eligibility",
    "description": (
        "Check whether an employee is eligible for a requested item "
        "(e.g., new laptop, hardware upgrade). Returns eligibility status and a reason. "
        "Requests for a customer demo are always approved."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "employee_name": {
                "type": "string",
                "description": "Full name of the employee raising the request.",
            },
            "employee_id": {
                "type": "string",
                "description": "Optional employee ID (e.g., EMP-12345).",
            },
            "request_type": {
                "type": "string",
                "description": "Type of request: laptop, monitor, keyboard, etc.",
                "default": "laptop",
            },
            "reason_for_request": {
                "type": "string",
                "description": "Reason for the request (e.g., 'customer demo', 'hardware failure').",
            },
        },
        "required": ["employee_name"],
    },
}


# ──────────────────────────────────────────────────────────────────────
# HTTP Handler
# ──────────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _send_json(self, status, data):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {})

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "server": "mock-eligibility-server", "version": "1.0.0"})

        elif self.path == "/tools":
            self._send_json(200, {"tools": [TOOL_DEFINITION]})

        elif self.path == "/":
            self._send_json(200, {
                "name": "Mock MCP Server — Employee Eligibility",
                "version": "1.0.0",
                "endpoints": {
                    "GET /health": "Health check",
                    "GET /tools": "List available tools",
                    "POST /tools/check_employee_eligibility": "Check employee eligibility",
                },
            })

        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/tools/check_employee_eligibility":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                params = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON"})
                return

            result = check_employee_eligibility(
                employee_name=params.get("employee_name", "Unknown"),
                employee_id=params.get("employee_id"),
                request_type=params.get("request_type", "laptop"),
                reason_for_request=params.get("reason_for_request", ""),
            )
            self._send_json(200, result)

        else:
            self._send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


# ──────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────

def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Mock MCP HTTP Server running on http://0.0.0.0:{port}")
    print(f"  GET  /              → Server info")
    print(f"  GET  /health        → Health check")
    print(f"  GET  /tools         → List tools")
    print(f"  POST /tools/check_employee_eligibility → Check eligibility")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
