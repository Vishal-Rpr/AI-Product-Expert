# Pod Priority Board — Codebase Context for Prototype Agent

This document provides the complete RFQ status lifecycle, shipment statuses, invoice linkage, and data model context from the Silq backend codebase. Use this to make the Pod Priority Board prototype realistic against production behavior.

---

## Entity Hierarchy

```
Organization (client)
  └── ClientRFQDefinition (CRD)
        ├── computed_internal_status (persisted, recalculated)
        ├── computed_external_status (persisted, client-facing)
        ├── service_types[] (SHIPPING, INSPECTION, CUSTOM, DELIVERY)
        ├── priority (HIGHEST=1, HIGH=2, MEDIUM=3, LOW=4)
        └── ClientRFQVersion (CRV) — one active CRV per CRD assumed
              ├── cargo_ready_date, target_delivery_date
              ├── origin_place, destination_place, origin_port, destination_port
              ├── incoterms
              ├── quoting_engine_status (PROCESSING, FAILED, INPUT_REQUIRED, etc.)
              ├── ClientRFQShippingServiceInfo
              │     ├── freight_modes[] (AIR, OCEAN_FCL, OCEAN_LCL, OCEAN_SCL, TRUCK, FTL, LTL)
              │     ├── shipping_service_coverage[] (P2P=1, P2D=2, D2D=3, D2P=4)
              │     └── customs_required
              ├── ClientRFQTradeLane[] (origin_port, destination_port, via_ports[])
              ├── Collaborator[] (via GenericFK, roles like ACCOUNT_MANAGER)
              └── SilqRFQ (1:1)
                    └── QuoteResponseDefinition[] (QRD)
                          ├── status, quote_valid_till, quote_sent_date, accepted_time
                          ├── freight_service_type (AIR, OCEAN_FCL, etc.)
                          ├── QuoteGroup
                          └── Shipment[] (via accepted_quote FK, multiple allowed for FCL)
                                ├── status (location), execution_status
                                ├── shipment_route → ShipmentRouteLeg[]
                                └── belongs_to_project → Task (PROJECT)

Project = Task (root, task_type=PROJECT)
  ├── silq_identifier (matches CRD.silq_identifier)
  ├── Collaborator[] (ACCOUNT_MANAGER, PROJECT_OWNER, etc.)
  ├── TaskSubject → ClientRFQVersion
  ├── TaskResult → Shipment(s)
  └── Subtasks (stages): Booking, Origin CX, Pickup, Dest CX, Delivery, Customer Invoicing
```

---

## RFQ Status Lifecycle (CRD `computed_internal_status`)

### All CRD Status Values

| Value | Status | Meaning |
|-------|--------|---------|
| 1 | `DRAFT` | RFQ created, not submitted |
| 2 | `ARCHIVED` | Archived (soft close) |
| 3 | `SUBMITTED_FOR_QUOTE` | Submitted; waiting for quotes. Also: all quotes declined/expired (stays here, does NOT go to REJECTED) |
| 4 | `OPERATOR_QUOTE_RECEIVED` | At least one QRD is IN_REVIEW (operator working) |
| 5 | `AWAITING_CLIENT_RESPONSE` | At least one QRD is SENT_TO_CLIENT |
| 6 | `DONE_ACCEPTED` | At least one QRD is ACCEPTED |
| 7 | `DONE_REJECTED` | Defined but NEVER computed by current logic — legacy/BI only |
| 8 | `DONE_CANCELLED` | RFQ cancelled |
| 9 | `UNKNOWN` | Invalid/inconsistent state |
| 11 | `ACCEPTED_REQUOTING` | Accepted RFQ has active requote (NEW or IN_PROGRESS) |
| 12 | `REQUOTED` | Requote completed, original RFQ superseded |

### External (Client-Facing) Status Mapping

| Internal | External |
|----------|----------|
| DRAFT | DRAFT |
| SUBMITTED_FOR_QUOTE, OPERATOR_QUOTE_RECEIVED | SUBMITTED_FOR_QUOTE |
| AWAITING_CLIENT_RESPONSE | AWAITING_RESPONSE |
| DONE_ACCEPTED | ACCEPTED |
| DONE_CANCELLED | CANCELLED |
| ACCEPTED_REQUOTING | ACCEPTED_REQUOTING |
| REQUOTED | REQUOTED |
| ARCHIVED | ARCHIVED |
| DONE_REJECTED | UNKNOWN (never surfaces) |

### CRD Status Computation Logic (priority order, first match wins)

```
1. CRV status is CANCELLED → DONE_CANCELLED
2. CRV status is ARCHIVE → ARCHIVED
3. RequoteTransaction exists on original CRV:
   - requote_status COMPLETED → REQUOTED
   - requote_status NEW or IN_PROGRESS → ACCEPTED_REQUOTING
4. No SilqRFQ exists:
   - CRV DRAFT → DRAFT
   - CRV CANCELLED → DONE_CANCELLED
   - else → UNKNOWN
5. SilqRFQ exists, no QRDs with quote_group:
   - SRFQ DRAFT/DRAFT_VALIDATED/SUBMITTED → SUBMITTED_FOR_QUOTE
   - SRFQ ARCHIVED → ARCHIVED
   - SRFQ CANCELLED → DONE_CANCELLED
6. SilqRFQ exists + QRDs with quote_group:
   - SRFQ CANCELLED → DONE_CANCELLED
   - Any QRD ACCEPTED → DONE_ACCEPTED
   - Any QRD IN_REVIEW → OPERATOR_QUOTE_RECEIVED
   - Any QRD SENT_TO_CLIENT → AWAITING_CLIENT_RESPONSE
   - All QRDs declined/expired/skipped → SUBMITTED_FOR_QUOTE (NOT rejected)
```

### CRD State Machine

```
[Start] → DRAFT
DRAFT → SUBMITTED_FOR_QUOTE (submit RFQ)
SUBMITTED_FOR_QUOTE → OPERATOR_QUOTE_RECEIVED (QRD created/received)
SUBMITTED_FOR_QUOTE → AWAITING_CLIENT_RESPONSE (QRD shared with client)
SUBMITTED_FOR_QUOTE → DONE_ACCEPTED (QRD accepted directly)
SUBMITTED_FOR_QUOTE → DONE_CANCELLED (cancel)
SUBMITTED_FOR_QUOTE → ARCHIVED (archive)

OPERATOR_QUOTE_RECEIVED → AWAITING_CLIENT_RESPONSE (share quote)
OPERATOR_QUOTE_RECEIVED → DONE_ACCEPTED (accept)
OPERATOR_QUOTE_RECEIVED → SUBMITTED_FOR_QUOTE (all declined/expired — loops back)
OPERATOR_QUOTE_RECEIVED → DONE_CANCELLED (cancel)

AWAITING_CLIENT_RESPONSE → DONE_ACCEPTED (client accepts)
AWAITING_CLIENT_RESPONSE → SUBMITTED_FOR_QUOTE (declined/expired — loops back for re-quote)
AWAITING_CLIENT_RESPONSE → DONE_CANCELLED (cancel)
AWAITING_CLIENT_RESPONSE → ARCHIVED (archive)

DONE_ACCEPTED → ACCEPTED_REQUOTING (requote initiated)
DONE_ACCEPTED → DONE_CANCELLED (cancel)
DONE_ACCEPTED → ARCHIVED (archive)

ACCEPTED_REQUOTING → REQUOTED (requote accepted)
ACCEPTED_REQUOTING → DONE_ACCEPTED (requote cancelled — reverts)

REQUOTED → ACCEPTED_REQUOTING (another requote on the chain)

DONE_CANCELLED → ARCHIVED (archive)
```

### Terminal / Conclusive CRD States

| Status | Terminal? | Notes |
|--------|-----------|-------|
| DONE_ACCEPTED | Terminal for quoting phase | Shipment execution continues downstream |
| DONE_CANCELLED | Terminal | |
| ARCHIVED | Terminal | Can archive from AWAITING_CLIENT_RESPONSE, DONE_ACCEPTED, DONE_CANCELLED |
| REQUOTED | Terminal for original RFQ | Requote RFQ is now the active one |

### Critical Behavior: Declined/Expired Quotes Do NOT End the RFQ

When all quotes on an RFQ are declined or expired, the CRD status goes back to `SUBMITTED_FOR_QUOTE` — NOT to any terminal state. The RFQ stays open for the operator to create new quotes. There is no `DONE_REJECTED` computed state in production.

This means **an RFQ only reaches a conclusive end via**: acceptance, explicit cancellation, or archiving. Quote rejection alone does not close it.

---

## Quote (QRD) Status Lifecycle

### All QRD Status Values

| Value | Status | Meaning |
|-------|--------|---------|
| 11 | NEW | V2 initial state |
| 12 | DRAFT | V2 draft |
| 1 | IN_REVIEW | Operator reviewing |
| 2 | SENT_TO_CLIENT | Shared with client |
| 3 | ACCEPTED | Client accepted |
| 4 | DECLINED | Client rejected |
| 5 | ALTERNATIVE_ACCEPTED | Another offering in group accepted |
| 6 | CANCELLED | Cancelled |
| 7 | EXPIRED | Quote validity expired |
| 8 | SKIPPED | Another quote group accepted |
| 9 | REQUOTED | Original accepted quote superseded by requote |
| 10 | ARCHIVED | Archived with RFQ |

### Quote Validity and Expiry

- `quote_valid_till` is a DateField on QRD (required)
- Expiry is NOT automatic/scheduled — it's a manual status transition triggered via `UpdateQuoteGroupStatusV2` mutation
- Before sharing a quote, validation blocks if `quote_valid_till <= today`
- Expired QRDs keep the CRD at SUBMITTED_FOR_QUOTE (ready for new quote)

### What Happens on Each QRD Action

| Action | QRD Status | CRD Impact | Side Effects |
|--------|-----------|------------|--------------|
| Quote created by engine | NEW/IN_REVIEW | → OPERATOR_QUOTE_RECEIVED | |
| Quote shared with client | SENT_TO_CLIENT | → AWAITING_CLIENT_RESPONSE | Sets quote_sent_date |
| Client accepts | ACCEPTED | → DONE_ACCEPTED | Creates shipment(s), sets accepted_time, publishes event |
| Client declines | DECLINED | → SUBMITTED_FOR_QUOTE (if all declined) | Requires rejection reason |
| Quote expired | EXPIRED | → SUBMITTED_FOR_QUOTE (if all expired) | Cancels quote review tasks |
| Another group accepted | SKIPPED / ALTERNATIVE_ACCEPTED | Unchanged (already DONE_ACCEPTED) | |
| RFQ cancelled | CANCELLED | → DONE_CANCELLED | Cascades to all QRDs |
| RFQ archived | ARCHIVED | → ARCHIVED | Cascades to all QRDs |
| Requote accepted | REQUOTED (on original accepted QRD) | Original → REQUOTED | Shipments moved to new QRD |

---

## Shipment Status Lifecycle

### Location Status (`ShipmentStatuses` — physical position)

| Value | Status | Meaning |
|-------|--------|---------|
| 0 | UNKNOWN | Default on creation |
| 2 | SELLER_LOCATION | At factory/seller |
| 4 | IN_TRANSIT_TO_ORIGIN_PORT | Moving to origin port |
| 6 | AT_ORIGIN_PORT | At origin port |
| 8 | IN_TRANSIT_TO_DESTINATION_PORT | Main leg transit (ocean/air) |
| 10 | AT_DESTINATION_PORT | At destination port |
| 12 | IN_TRANSIT_TO_CONSIGNEE_LOCATION | Final mile |
| 14 | AT_CONSIGNEE_LOCATION | Delivered to consignee |

Derived from route leg actual dates, not manually set. When location reaches AT_CONSIGNEE_LOCATION, execution status auto-sets to DONE.

### Execution Status (`ShipmentExecutionStatuses` — lifecycle state)

| Value | Status | Meaning |
|-------|--------|---------|
| 5 | NEW | Just created |
| 1 | IN_PROGRESS | Active execution |
| 2 | ON_HOLD | Paused |
| 3 | DONE | Complete |
| 4 | CANCELLED | Cancelled |
| 6 | ARCHIVED | Archived |

### Shipment Categories (used for dashboard grouping — not a stored field)

| Category | Condition |
|----------|-----------|
| IN_TRANSIT | execution_status = IN_PROGRESS |
| ON_HOLD | execution_status = ON_HOLD |
| DELIVERED | execution_status = DONE + location = AT_CONSIGNEE + invoicing task still active |
| COMPLETED | execution_status = DONE + location = AT_CONSIGNEE + invoicing task DONE (or none) |
| CANCELLED | execution_status = CANCELLED |

**DELIVERED vs COMPLETED is the "pending invoicing" distinction.** It's driven by whether the project's "Customer Invoicing" subtask is still active or done.

### "Arriving Soon" — Not a Backend Concept

There is no "arriving soon" status, category, or flag in the codebase. The prototype must compute this from `ShipmentRouteLeg.estimated_arrival_date` (e.g., arrival within N days AND not yet at consignee).

### "First-Time Client" — Not a Backend Flag

No production field for this. Must be derived (e.g., count of prior DONE_ACCEPTED CRDs for the organization).

---

## Invoice Linkage

### How Invoicing Connects

```
QuoteResponseDefinition (accepted)
  → QuickbooksProject (1:1)
    → QuickbooksInvoice[]
      → invoicing.Invoice (1:1 bridge)
```

### Invoice Statuses (`QuickbooksInvoiceStatuses`)

CURRENT=1, OVERDUE=2, PAID=3, CANCELLED=4, PARTIALLY_PAID=5

### "Delivered but Not Invoiced" Detection

Not a single flag. Requires checking:
1. Shipment execution_status = DONE AND location = AT_CONSIGNEE_LOCATION
2. Project's "Customer Invoicing" subtask status is active (TO_DO or IN_PROGRESS), not DONE

Invoicing does NOT change CRD status. CRD stays DONE_ACCEPTED throughout shipment execution and invoicing.

---

## Assignee / Team / Pod

### No Runtime Pod Model

"Pod" only exists in BI: `UserTeams.EAST_ASIA`, `SOUTH_ASIA`. Not used in RFQ/shipment runtime.

### How Assignment Works — Collaborator Model

```python
Collaborator.subject → Project (Task) | CRV | Shipment
Collaborator.collaborator → Person
Collaborator.collaboration_role → CollaborationRoles
```

Key roles for the board:
- ACCOUNT_MANAGER (7) — primary AM on project
- ASSOCIATE_ACCOUNT_MANAGER (28)
- PROJECT_OWNER (8)
- ORIGIN_SHIPPING_COORDINATOR (11)
- DESTINATION_SHIPPING_COORDINATOR (12)

Account manager is resolved from the Project-level collaborator, not CRD directly. Filtering by AM uses `ProjectService.list_project_silq_identifiers_for_people_collaborating_on_projects()`.

---

## Date Fields Available for Stage Display

| Stage | Key Date | Source |
|-------|----------|--------|
| Draft / Unquoted | RFQ creation date | CRD.created_at |
| Awaiting Quote | Days since submission | CRV.created_at (when ACTIVE) |
| Awaiting Client | Quote validity deadline | QRD.quote_valid_till |
| Quote Expired | Expiry date | QRD.quote_valid_till (when status=EXPIRED) |
| Accepted | Acceptance date | QRD.accepted_time |
| In Transit | ETA | ShipmentRouteLeg.estimated_arrival_date (last leg) |
| Arriving Soon | Arrival date | ShipmentRouteLeg.estimated_arrival_date (last leg) |
| Delivered | Delivery date | ShipmentRouteLeg.actual_arrival_date (last leg) |
| Pending Invoicing | Days since delivery | ShipmentRouteLeg.actual_arrival_date (last leg) |
| CRD/cargo level | Cargo ready date | CRV.cargo_ready_date |
| CRD/target | Target delivery | CRV.target_delivery_date |

---

## Mode and Route on RFQ

### How Mode Is Stored

- RFQ request: `ClientRFQShippingServiceInfo.freight_modes[]` (FCL, LCL, AIR, SCL, FTL, LTL, etc.)
- Accepted quote: `QRD.freight_service_type` (AIR, OCEAN_FCL, OCEAN_LCL, etc.)
- Shipment: `shipment_route.primary_transportation_mode` (AIR, OCEAN, TRUCKING, RAIL)

### How Route Is Stored

- RFQ level: `CRV.origin_place`, `CRV.destination_place` (Place model with name, country, port code)
- Trade lane level: `ClientRFQTradeLane.origin_port`, `destination_port`
- Quote level: `QRD.port_of_loading`, `port_of_discharge`, `place_of_receipt`, `place_of_delivery`
- Shipment level: `Shipment.origin_place`, `destination_place`

For the board, use CRV-level origin/destination for pre-acceptance stages, and shipment-level for post-acceptance.

---

## Multiple Shipments Per RFQ

Normal for FCL. One accepted QRD can have N shipments (one per container). All share the same `accepted_quote_id`. Each shipment has independent location status and execution status.

For the board: aggregate shipment status per RFQ/project. Show the "worst" status (e.g., if 3 of 4 shipments are delivered but 1 is still in transit, show "In Transit" as the active stage).

---

## Requote Impact on Board

- Original CRD shows ACCEPTED_REQUOTING while requote is active
- Original CRD shows REQUOTED when requote completes
- Requote CRD goes through its own full lifecycle (DRAFT → SUBMITTED → AWAITING → ACCEPTED)
- Same project/silq_identifier throughout
- Board should show the latest active CRD for a project, not the superseded original

---

## Suggested Board Column → Backend Signal Mapping

| Board Column | Primary Signal | Additional Data |
|--------------|---------------|-----------------|
| Unquoted | CRD status = SUBMITTED_FOR_QUOTE, OPERATOR_QUOTE_RECEIVED | Days since submission |
| Awaiting Client Response | CRD status = AWAITING_CLIENT_RESPONSE | QRD.quote_valid_till for expiry countdown |
| Quote Expired | QRD status = EXPIRED (not CRD status — CRD stays SUBMITTED_FOR_QUOTE) | quote_valid_till date |
| In Transit | CRD = DONE_ACCEPTED + any shipment IN_PROGRESS + location between ports | ShipmentRouteLeg ETA |
| Arriving Soon | CRD = DONE_ACCEPTED + shipment estimated_arrival_date within N days + not AT_CONSIGNEE | Arrival date |
| Pending Invoicing | CRD = DONE_ACCEPTED + shipment DONE + AT_CONSIGNEE + invoicing task active | Days since delivery |
| Cancelled | CRD = DONE_CANCELLED | |
| Archived | CRD = ARCHIVED | |

### Important: Quote Expired is a QRD-Level State

Quote expiry does NOT change the CRD status. The CRD stays at SUBMITTED_FOR_QUOTE. To bucket an RFQ as "Quote Expired" for the board, you must check QRD status = EXPIRED (or quote_valid_till < today) while CRD is still SUBMITTED_FOR_QUOTE or AWAITING_CLIENT_RESPONSE.

### Important: An RFQ Can Appear in Multiple Board Columns

One project with multiple shipments can have some in transit and some arriving soon simultaneously. The board should handle this — either show the RFQ in the most urgent column, or show it in multiple columns with per-shipment context.

---

## Data Fetch Pattern for the Board

1. Quote-stage items: Query `ClientRFQDefinition` filtered by computed_internal_status + accountManagerIds (via project collaborator join)
2. Execution-stage items: Query Shipments filtered by execution_status + account_manager on project + categories
3. Join on `silq_identifier` to create unified rows
4. Compute derived states: "arriving soon" from route leg dates, "first-time client" from org history, "quote expired" from QRD status/validity
