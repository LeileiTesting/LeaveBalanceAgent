# Product Requirements Document (PRD)

**Title:** Leave Balance Query Agent  
**Date:** 2026-11-10  
**Owner:** HR / Employee Experience  
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Employees waste 10+ minutes logging into SAP SuccessFactors just to check how many vacation days they have left. This AI agent lets them ask in plain language and get an answer in under 30 seconds — no login, no navigation required.

**Business Need:**  
There is no conversational self-service channel for employees to quickly check their leave balance. The current process requires navigating multiple screens in SAP SuccessFactors, creating unnecessary friction for a routine, read-only inquiry. This drives avoidable HR helpdesk load and erodes the employee experience.

**Expected Value:**  
- Reduce time-to-answer for leave balance queries from 10+ minutes to under 30 seconds
- Decrease HR helpdesk inquiries related to leave balance checks
- Improve employee satisfaction with self-service HR tooling

**Product Objectives (Prioritized):**
1. Enable employees to retrieve their full leave balance via a conversational interface in under 30 seconds
2. Provide a breakdown of remaining leave by type (annual, sick, etc.) and show upcoming approved leave
3. Ensure the agent only returns data scoped to the authenticated employee (no cross-employee data exposure)

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to retrieve leave balance | ~10+ minutes (manual login to SuccessFactors) | Under 30 seconds via conversational interface | — | Manage Time & Attendance / Absence Management | user |

---

## User Profiles & Personas

### Primary Persona: Alex — Employee

Alex is a 34-year-old office worker who uses SAP SuccessFactors for HR tasks but rarely logs in proactively. When planning a holiday or coordinating time off with the team, Alex needs a quick answer to "how many days do I have left?" — but dreads logging into the HR portal just for that. Alex is comfortable with chat interfaces and messaging tools, and expects information to be available instantly, the same way they'd ask a colleague. The 10+ minute login and navigation process feels disproportionate to a simple question.

**Goals:**
- Quickly find out remaining vacation and leave balance without navigating SuccessFactors
- Understand which types of leave are available (annual, sick, special, etc.)
- See upcoming approved leave to plan ahead

**Key Tasks:**
- Ask "How many vacation days do I have left?"
- Ask "What leave types do I have and how many days each?"
- Ask "When is my next approved leave?"

---

## Goals and Non-Goals

### Goals (In Scope)

- Answer natural language questions about an employee's remaining leave balance
- Return a breakdown of leave balance by leave type
- Return a list of upcoming approved leave requests for the employee
- Authenticate the employee and scope all data responses to that individual only
- Respond within 30 seconds

### Non-Goals (Out of Scope)

- Submitting or cancelling leave requests on behalf of the employee
- Displaying team or manager-level leave views
- Providing leave policy advice or entitlement rules
- Integration with calendaring tools (e.g. Outlook, Google Calendar)
- Any write operations to SAP SuccessFactors

---

## Requirements

### Must-Have Requirements

**REQ-001**: Natural Language Leave Balance Query

- **Problem to Solve**: Employees have no quick, low-friction way to check their leave balance; they must log into SuccessFactors and navigate multiple screens.
- **User Story**: As an employee, I need to ask in plain language how many leave days I have remaining, so that I can get an instant answer without logging into SuccessFactors.
- **Acceptance Criteria**:
  - Given the employee asks any natural language variant of "how many days do I have left?", when the agent processes the query, then it returns the total remaining leave balance.
  - Given the agent receives the query, when the response is returned, then it is delivered within 30 seconds.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 1

---

**REQ-002**: Leave Balance Breakdown by Type

- **Problem to Solve**: Employees need to know not just the total balance, but how it is split across different leave types (e.g. annual leave, sick leave, special leave).
- **User Story**: As an employee, I need a breakdown of my leave balance by leave type, so that I can understand exactly what leave I have available.
- **Acceptance Criteria**:
  - Given the employee asks about their leave balance, when the agent retrieves data from SuccessFactors, then it returns remaining days per leave type.
  - Given the employee asks specifically about one leave type, then the agent returns the balance for that type only.
- **Maps to Objective**: Objective 2
- **Priority Rank**: 2

---

**REQ-003**: Upcoming Approved Leave Requests

- **Problem to Solve**: Employees want to cross-reference their remaining balance with leave they have already booked.
- **User Story**: As an employee, I need to see my upcoming approved leave requests, so that I can plan future time off accurately.
- **Acceptance Criteria**:
  - Given the employee asks about upcoming leave, when the agent queries SuccessFactors, then it returns a list of approved future leave requests with dates and leave type.
- **Maps to Objective**: Objective 2
- **Priority Rank**: 3

---

**REQ-004**: Employee Identity Scoping

- **Problem to Solve**: The agent must never return another employee's leave data, regardless of how the query is phrased.
- **User Story**: As an employee, I need confidence that the agent only shows my own leave data, so that my personal information is protected.
- **Acceptance Criteria**:
  - Given any leave balance query, when the agent calls SuccessFactors APIs, then it only passes the authenticated employee's identity.
  - Given a query that references another employee by name or ID, then the agent declines and responds only with the requesting employee's own data.
- **Maps to Objective**: Objective 3
- **Priority Rank**: 4

---

**REQ-005**: Graceful Handling of Unavailable Data

- **Problem to Solve**: API calls may fail or return incomplete data; the agent must not silently return wrong information.
- **User Story**: As an employee, I need a clear message when my leave data cannot be retrieved, so that I know to try again or contact HR.
- **Acceptance Criteria**:
  - Given an API call to SuccessFactors fails, when the agent processes the error, then it returns a friendly message explaining the issue and suggests contacting HR.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 5

---

## Solution Architecture

**Architecture Overview:**  
A pro-code Python AI agent built on the A2A protocol. The agent receives natural language queries from employees, reasons over the intent, and calls SAP SuccessFactors REST/OData APIs to retrieve leave data. All API calls are scoped to the authenticated employee's identity.

**Key Components:**

- **AI Agent (Python, A2A)**: Core reasoning and orchestration layer; handles natural language understanding, tool selection, and response formatting
- **SuccessFactors Balances API** (`sap.sf:apiResource:Balances:v1`): Retrieves total and per-type leave balance
- **SuccessFactors AvailableTimeTypes API** (`sap.sf:apiResource:AvailableTimeTypes:v1`): Retrieves available leave types for the employee
- **SuccessFactors ECTimeOff API** (`sap.sf:apiResource:ECTimeOff:v1`): Retrieves approved leave requests (OData)

**Integration Points:**

- SAP SuccessFactors Employee Central: read-only, REST/OData, called on demand per user query
- Employee identity provider: used to scope all SuccessFactors API calls to the authenticated user

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The agent is designed with extension points to support future capabilities without rebuilding the core:
  - Future tool: Submit leave requests (write operation — out of scope for v1)
  - Future tool: Manager team leave view
  - Future tool: Leave policy Q&A (knowledge base integration)
- The tool registry should be modular so new SuccessFactors API tools can be added independently

**Business Step Instrumentation:**
- All key business steps must emit structured log statements for observability and debugging in production
- Log pattern: `[MILESTONE_ID].[achieved|missed]: [description]`
- See Milestones section for the full definition

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent

**Actions the system performs without human approval:**
- Querying leave balance from SAP SuccessFactors
- Querying leave type breakdown
- Querying upcoming approved leave requests
- Formatting and returning the response to the employee

**Actions that require human review or approval:**
- None in scope for v1 (all actions are read-only)

**Model or engine used:** SAP Generative AI Hub (LLM for natural language understanding and response generation)

**Knowledge & data sources accessed:**
- SAP SuccessFactors Employee Central: leave balances, leave types, approved time-off requests (read-only)

**Tools or connectors invoked:**
- `Balances` (SuccessFactors REST API): retrieves remaining leave balance per employee — read-only
- `AvailableTimeTypes` (SuccessFactors REST API): retrieves available leave types per employee — read-only
- `ECTimeOff` (SuccessFactors OData API): retrieves approved time-off requests — read-only

**Guardrails & fail-safes:**
- The agent must never perform write operations on SuccessFactors (no leave creation, modification, or deletion)
- All API calls must be scoped to the authenticated employee's identity; cross-employee data access is prohibited
- If the agent cannot retrieve data (API error, timeout), it returns a graceful fallback message and does not fabricate leave balances
- If confidence in intent classification is low, the agent asks the employee to clarify before calling any API

---

## Milestones

### M1: Query Received

- **Description**: The agent has received and understood the employee's leave-related query
- **Achieved when**: Intent is classified as a leave balance inquiry and the employee's identity is confirmed
- **Log on achievement**: `M1.achieved: employee leave query received and intent classified successfully`
- **Log on miss**: `M1.missed: intent classification failed or query not recognised as a leave inquiry`

### M2: API Authentication

- **Description**: The agent has successfully authenticated with SAP SuccessFactors using the employee's identity
- **Achieved when**: SuccessFactors API connection is established and the employee's user context is confirmed
- **Log on achievement**: `M2.achieved: SuccessFactors API authentication successful for employee`
- **Log on miss**: `M2.missed: SuccessFactors API authentication failed`

### M3: Balance Retrieved

- **Description**: The agent has retrieved the employee's total leave balance and breakdown by leave type
- **Achieved when**: A valid response is received from the Balances and AvailableTimeTypes APIs
- **Log on achievement**: `M3.achieved: leave balance and type breakdown retrieved successfully`
- **Log on miss**: `M3.missed: failed to retrieve leave balance or type breakdown from SuccessFactors`

### M4: Upcoming Leave Fetched

- **Description**: The agent has retrieved the employee's upcoming approved leave requests
- **Achieved when**: A valid response is received from the ECTimeOff OData API
- **Log on achievement**: `M4.achieved: upcoming approved leave requests retrieved successfully`
- **Log on miss**: `M4.missed: failed to retrieve upcoming leave requests from SuccessFactors`

### M5: Response Delivered

- **Description**: The agent has returned a complete, formatted response to the employee within the target time
- **Achieved when**: The response is delivered to the employee within 30 seconds of the original query
- **Log on achievement**: `M5.achieved: leave balance response delivered to employee within 30 seconds`
- **Log on miss**: `M5.missed: response delivery failed or exceeded 30-second target`

---

## Risks, Assumptions, and Dependencies

### Risks

- **SuccessFactors API authentication complexity**: OAuth/SAML scoping to the requesting employee must be implemented correctly to prevent data leakage
- **API rate limits**: High usage could trigger SuccessFactors throttling; caching strategies may be needed for v2
- **Leave data accuracy**: The agent reflects what is in SuccessFactors; if data is stale, responses will be inaccurate

### Assumptions

- SAP SuccessFactors Employee Central is the system of record for all leave data
- The `Query Time Account Balances` SOAP API is not available in this landscape and will not be used
- Employees are authenticated prior to interacting with the agent; identity can be passed securely to SuccessFactors API calls

### Dependencies

- SAP SuccessFactors Employee Central — live and accessible via REST/OData APIs
- SAP Generative AI Hub — available for LLM-based intent understanding and response generation
- Employee identity / authentication provider — must supply identity context consumable by SuccessFactors APIs

---

## Appendix

### References

- SAP SuccessFactors Time Off API: `sap.sf:apiResource:ECTimeOff:v1`
- SAP SuccessFactors Balances API: `sap.sf:apiResource:Balances:v1`
- SAP SuccessFactors Available Time Types API: `sap.sf:apiResource:AvailableTimeTypes:v1`
- SAP Reference Business Architecture: Recruit to Retire — Manage time and attendance (BPS-393)
