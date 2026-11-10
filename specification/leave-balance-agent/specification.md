# Specification: leave-balance-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md`)
- [x] Bootstrap agent code in `assets/leave-balance-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/leave-balance-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> **Before proceeding**, read [guidelines-agent-skills.md](../guidelines-agent-skills.md) and decide whether runtime skills are needed.

The agent does not require runtime skills for v1 — all logic is straightforward tool-call orchestration with no complex multi-step decision trees. The system prompt handles intent classification.

---

## Project-Specific Tasks

## Agent System Prompt & Identity

- [x] Open `assets/leave-balance-agent/app/agent.py`, find the `@prompt_section` body (`get_system_prompt`), and set the agent's identity and purpose:
  - The agent is a conversational HR self-service assistant for employees
  - Its sole purpose is to answer questions about the authenticated employee's leave balance
  - It must never return data for any employee other than the one currently authenticated
  - It must never fabricate leave balance figures — all data must come from MCP tool results
  - If confidence in understanding the user's intent is low, ask the employee to clarify before calling any tool
  - Respond in a concise, friendly tone with clear formatted answers (e.g. bullet list of leave types and days)

## Leave Balance Query (REQ-001)

- [x] Implement a tool `get_leave_balance` that:
  - Calls the `Balances` MCP tool to retrieve the authenticated employee's total remaining leave balance
  - Accepts no input parameters beyond the employee identity (passed via session context)
  - Returns total remaining days

## Leave Balance Breakdown by Type (REQ-002)

- [x] Implement a tool `get_leave_types` that:
  - Calls the `AvailableTimeTypes` MCP tool to retrieve all available leave types for the employee
  - Returns a list of leave types with their names and remaining balances
- [x] Update `get_leave_balance` (or compose in the agent prompt) so that a full balance query returns both total days and per-type breakdown in a single response

## Upcoming Approved Leave (REQ-003)

- [x] Implement a tool `get_upcoming_leave` that:
  - Calls the `ECTimeOff` MCP tool (OData) to retrieve approved future leave requests for the authenticated employee
  - Filters for requests with approval status = Approved and start date >= today
  - Returns a list of upcoming leave entries with: leave type, start date, end date, number of days

## Employee Identity Scoping (REQ-004)

- [x] Ensure all three tools (`get_leave_balance`, `get_leave_types`, `get_upcoming_leave`) extract the authenticated employee's user ID from the session/request context and pass it to every MCP tool call
- [x] Add a guardrail in the system prompt: if the user's message references another employee by name or ID, the agent must decline and respond only with the requesting employee's own data
- [x] Add a guardrail: the agent must never perform any write operations (no POST, PUT, DELETE to any MCP tool)

## Graceful Error Handling (REQ-005)

- [x] For each tool, add try/except error handling:
  - On MCP tool call failure (timeout, API error), log the error and return a user-friendly message: "I was unable to retrieve your leave information right now. Please try again in a moment, or contact HR for assistance."
  - Do not expose raw error details or stack traces to the user
- [x] Ensure the agent does not fabricate or estimate leave balances when data is unavailable

## Data API Integrations

The following SuccessFactors APIs have been downloaded for MCP server generation:

- `sap.sf:apiResource:ECTimeOff:v1` → `specification/leave-balance-agent/api-specs/ECTimeOff.edmx` (OData)
- `sap.sf:apiResource:Balances:v1` → `specification/leave-balance-agent/api-specs/Balances.json` (REST)
- `sap.sf:apiResource:AvailableTimeTypes:v1` → `specification/leave-balance-agent/api-specs/AvailableTimeTypes.json` (REST)

```text
MCP API: sap.sf:apiResource:ECTimeOff:v1
MCP tool scope: read-only
Resources in scope: TimeOff, TimeOffItem

MCP API: sap.sf:apiResource:Balances:v1
MCP tool scope: read-only
Resources in scope: all

MCP API: sap.sf:apiResource:AvailableTimeTypes:v1
MCP tool scope: read-only
Resources in scope: all
```

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD using structured logging with the pattern `[MILESTONE_ID].[achieved|missed]: [description]` and OpenTelemetry custom spans:

  | Milestone | Achieved log | Missed log |
  |-----------|-------------|------------|
  | M1: Query Received | `M1.achieved: employee leave query received and intent classified successfully` | `M1.missed: intent classification failed or query not recognised as a leave inquiry` |
  | M2: API Authentication | `M2.achieved: SuccessFactors API authentication successful for employee` | `M2.missed: SuccessFactors API authentication failed` |
  | M3: Balance Retrieved | `M3.achieved: leave balance and type breakdown retrieved successfully` | `M3.missed: failed to retrieve leave balance or type breakdown from SuccessFactors` |
  | M4: Upcoming Leave Fetched | `M4.achieved: upcoming approved leave requests retrieved successfully` | `M4.missed: failed to retrieve upcoming leave requests from SuccessFactors` |
  | M5: Response Delivered | `M5.achieved: leave balance response delivered to employee within 30 seconds` | `M5.missed: response delivery failed or exceeded 30-second target` |

- [x] Extract business logic from `stream()` into a plain async helper to avoid `GeneratorExit` context errors (see [guidelines-agent-python.md](../guidelines-agent-python.md))
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) for complete MCP integration patterns.

- [x] Invoke `mcp-translation-file` skill for each downloaded API spec to generate MCP translation cards:
  - `specification/leave-balance-agent/api-specs/ECTimeOff.edmx` → MCP translation card for ECTimeOff (OData, `sap.sf:apiResource:ECTimeOff:v1`)
  - `specification/leave-balance-agent/api-specs/Balances.json` → MCP translation card for Balances (REST, `sap.sf:apiResource:Balances:v1`)
  - `specification/leave-balance-agent/api-specs/AvailableTimeTypes.json` → MCP translation card for AvailableTimeTypes (REST, `sap.sf:apiResource:AvailableTimeTypes:v1`)
- [x] Invoke `setup-solution` skill to create `solution.yaml` and `asset.yaml` files, registering the agent and all generated MCP server assets
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — see [guidelines-agent-python.md](../guidelines-agent-python.md) for the canonical pattern. NEVER import directly from `sap_cloud_sdk.agentgateway`. NEVER create direct HTTP clients for SAP APIs.
- [x] Add MCP server dependencies to `asset.yaml` under `requires` — one entry per generated MCP server (ECTimeOff, Balances, AvailableTimeTypes), using exact ORD IDs from generated assets
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill (required before tests can run)

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit tests in `assets/leave-balance-agent/tests/` — one per tool:
  - `test_get_leave_balance.py` — mock MCP tool response, assert total balance returned correctly
  - `test_get_leave_types.py` — mock MCP tool response, assert leave type list returned correctly
  - `test_get_upcoming_leave.py` — mock MCP tool response, assert approved future leave returned correctly; test filter for approved status and future dates
  - Run each test immediately after writing it
- [x] Write one integration test executing end-to-end agent flow:
  - Employee asks "How many vacation days do I have left?"
  - Mock LLM, mock all three MCP tools (Balances, AvailableTimeTypes, ECTimeOff)
  - Assert the agent returns a response containing balance summary and breakdown
  - Assert cross-employee guardrail: a query referencing another employee is declined
  - Assert error fallback: when an MCP tool fails, agent returns a graceful error message
- [x] Run `pytest` from `assets/leave-balance-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/leave-balance-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/leave-balance-agent/`
