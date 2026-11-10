# Leave Balance Query Agent

## Business challenge

Employees want a quick, conversational way to check their remaining vacation and leave balance without having to manually log into SAP SuccessFactors. The current process takes 10+ minutes and creates unnecessary friction for a simple self-service need.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to retrieve leave balance | ~10+ minutes (manual login to SuccessFactors) | Under 30 seconds via conversational interface | — | Manage Time & Attendance / Absence Management | user |

## Key Milestones

1. **Query received** — Agent receives and understands the employee's natural language leave query
2. **API authentication** — Agent authenticates and connects to SAP SuccessFactors
3. **Balance retrieved** — Agent fetches total remaining leave balance and breakdown by leave type
4. **Upcoming leave fetched** — Agent retrieves upcoming approved leave requests
5. **Response delivered** — Agent returns a clear, formatted answer to the employee within 30 seconds

## Business Architecture (RBA)

### End-to-End Process

Recruit to Retire

### Process Hierarchy

```
Recruit to Retire
└── Manage Workforce (generic)
    └── Manage time and attendance (generic) (BPS-393)
        └── Manage attendance and absence quotas (BA-2724)
        └── Record absences (BA-2651)
```

### Summary

The challenge of querying remaining vacation days maps to "Manage time and attendance" within the Recruit to Retire E2E, specifically covering absence quota management and absence recording activities in SAP SuccessFactors Employee Central.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Query total leave balance by employee | SAP SuccessFactors Employee Central — Absence Management (SC4500) | `sap.sf:apiResource:Balances:v1` | — | — | — | — | No | Direct REST API call; no MCP server available |
| Breakdown of leave by type | SAP SuccessFactors Employee Central — Absence Management | `sap.sf:apiResource:AvailableTimeTypes:v1` | — | — | — | — | No | Time types available via SuccessFactors REST API |
| View upcoming approved leave requests | SAP SuccessFactors Employee Central — Time Sheet Management (SC1334) | `sap.sf:apiResource:ECTimeOff:v1` | — | — | — | — | No | OData API covers time-off requests |
| Conversational self-service interface for employees | None — no pre-built conversational UI in SuccessFactors | — | — | — | — | — | Yes | Custom AI agent required |

### Key findings

- SAP SuccessFactors Employee Central provides full standard coverage for absence and leave management via REST and OData APIs.
- Three relevant APIs identified: `Balances`, `AvailableTimeTypes`, and `ECTimeOff` — all available; no MCP servers exist for them, so direct API calls will be used.
- The only gap is the conversational interface layer, which requires a custom AI agent.
- The `Query Time Account Balances` SOAP API is marked unavailable in this landscape and must not be used.
- The agent will serve employees in a self-service capacity, requiring secure identity-aware API calls scoped to the requesting employee.
- SuccessFactors Mobile apps provide optional native absence access but do not fulfill the conversational/chat requirement.

## Recommendations

### Conversational Leave Balance AI Agent

#### Executive Summary

Python AI agent answering employee leave queries via SuccessFactors APIs.

#### Recommended Solution

Build a pro-code Python AI agent (A2A protocol) that connects to SAP SuccessFactors via its REST/OData APIs. The agent handles natural language questions such as "How many vacation days do I have left?" and responds with the employee's total remaining balance, a breakdown by leave type, and any upcoming approved leave — all within 30 seconds.

#### Problem Statement

Employees currently must log into SAP SuccessFactors and navigate multiple screens to find their leave balance, a process taking 10+ minutes. This creates unnecessary friction for a simple self-service need and increases HR helpdesk inquiries.

#### Affected User Roles

- Employees (primary users — self-service leave balance queries)

#### Important factors

##### Saves employee time through conversational self-service

Employees can ask in plain language and receive an instant, structured answer — no navigation required.

##### Direct API integration with SAP SuccessFactors

The agent uses standard SuccessFactors REST/OData APIs (Balances, AvailableTimeTypes, ECTimeOff), ensuring data accuracy and alignment with the system of record.

#### Potential risks

##### API authentication and employee identity scoping

The agent must ensure it only returns leave data for the authenticated requesting employee. Proper OAuth/SAML scoping with SuccessFactors is required.

##### SuccessFactors API availability and rate limits

Production usage must account for SuccessFactors API throttling policies.

#### Recommended solution category

AI Agent

#### Intent fit

92%
