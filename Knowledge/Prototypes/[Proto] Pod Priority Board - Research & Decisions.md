# Pod Priority Board — Research & Decisions

## Concept
A swim lane / kanban-style dashboard that lets a Pod (Account Managers, Origin Ops, Destination Ops) manage daily priorities at the RFQ level. Inspired by deal-tracking pipelines — RFQs move through stages with key data points and action items highlighted on each card.

## Lifecycle Scope — AM Quoting Pipeline Only
The board tracks RFQs exclusively through the **quoting lifecycle**, aligned with the real CRD (ClientRFQDefinition) `computed_internal_status` from the Silq backend. Once a quote is accepted (`DONE_ACCEPTED`), the row exits the board — operational stages (transit, delivery, invoicing) are not tracked here.

### Active Stages
1. **Submitted for Quote** (`SUBMITTED_FOR_QUOTE`) — RFQ submitted, awaiting quote preparation. Also: all quotes declined/expired loop back here (CRD stays open).
2. **Awaiting Client Response** (`AWAITING_CLIENT_RESPONSE`) — Quote sent to client, waiting on their decision.
3. **Quote Expired** (derived from QRD status) — Quote validity lapsed. This is NOT a CRD status — the CRD stays at `SUBMITTED_FOR_QUOTE`. Derived by checking QRD `status = EXPIRED` or `quote_valid_till < today`.
4. **Accepted Requoting** (`ACCEPTED_REQUOTING`) — Original quote was accepted, but a requote is in progress (scope change, rate change, etc.).

### Exit Conditions (row leaves the board)
| Trigger | CRD Status | What happens |
|---|---|---|
| Quote accepted | `DONE_ACCEPTED` | AM's job done, handed off to Ops |
| RFQ cancelled | `DONE_CANCELLED` | Explicitly closed |
| RFQ archived | `ARCHIVED` | Soft-closed |
| Requote completed | `REQUOTED` | Original CRD exits; new requote CRD takes over under same `silq_identifier` |

### Critical Behavior: No "Rejected" Terminal State
When all quotes on an RFQ are declined or expired, the CRD loops back to `SUBMITTED_FOR_QUOTE`. The RFQ stays open for the operator to create new quotes. An RFQ only exits via acceptance, cancellation, or archiving.

### Re-quote Handling
- Original CRD shows `ACCEPTED_REQUOTING` while requote is in progress — stays visible on the board
- When requote completes, original CRD becomes `REQUOTED` (exits) and the new CRD takes over
- Same `silq_identifier` throughout — board shows the latest active CRD for a project
- The `Qx` badge and quote history trail on the table show revision history

## Key Design Decisions
- **Primary user:** Pod Lead (overview of all RFQs across the team)
- **Actions on the board:** View and filter only — no inline status updates
- **Navigation:** Each card hyperlinks directly to the project/RFQ in the main app
- **Data freshness:** Real-time (live queries, not batch/refresh)
- **Lifecycle boundary:** Quoting pipeline only (up to acceptance). Post-acceptance stages belong to a separate Ops board.

## Build Path
**Decision: Build natively** — Retool was evaluated and rejected (poor past experience). Building as a standalone prototype first, then integrating natively into the Silq app.

**Prototype:** `Prototypes/pod-priority-board.html` — single-file HTML prototype using the Silq design system, same tech approach as the credit limit table prototype.

### Paths evaluated
| Path | Decision | Notes |
|---|---|---|
| **A. ClickUp / Monday.com** | Rejected | Data duplication, no live sync |
| **B. Retool / Appsmith** | Rejected | Bad experience with Retool |
| **C. Build natively** | Selected | Full control, consistent UX, direct DB integration |

## Researched Platforms & Links

### Freight-Specific Platforms
- **Portmasters** — Flow-based kanban ops workspace for freight forwarders
  https://www.portmasters.net/
- **UPilot** — CRM for logistics with customizable pipelines and quotation engine
  https://upilot.com/upilot-crm-for-logistics/
- **Navix** — AI-powered freight CRM, lead-to-invoice tracking
  https://navixai.co/
- **Meriq** — Freight operating system with multi-carrier RFQ management
  https://www.meriq.app/
- **Beacon** — Supply chain visibility with live shipment boards
  https://www.beacon.com/platform

### General CRM / Project Tools with Logistics Templates
- **ClickUp — Shippers Kanban Board Template**
  https://clickup.com/templates/kanban-board/shippers
- **ClickUp — Freight Forwarders CRM Template**
  https://clickup.com/templates/crm/freight-forwarders
- **Monday.com — Logistics Operations Management CRM**
  https://monday.com/crm/marketplace/template/logistics-operations-management-crm
- **Pipeline CRM (Logistics)**
  https://www.pipelinecrm.com/industries/logistics-crm/

### Low-Code / Build-Your-Own Platforms
- **Retool — Pipeline Management Template**
  https://retool.com/templates/project-pipeline-management
- **Retool — Shipment Processing Dashboard**
  https://retool.com/use-case/shipment-processing-dashboard
- **Appsmith** (open-source, self-hostable alternative)
  https://www.appsmith.com/

### Power BI Kanban Visuals
- **Kanban Tasks Viewer PRO**
  https://appsource.microsoft.com/en-us/product/power-bi-visuals/softcial1741389388075.kanban-tasks-viewer-pro-chart?tab=overview
- **PowerGraph Task Board**
  https://marketplace.microsoft.com/en-us/product/power-bi-visuals/stratada.taskboard?tab=overview

## Card Layout (Per RFQ)
Each card shows:
- **Client name**
- **Origin → Destination**
- **Mode** (FCL / LCL / Air)
- **Days in current stage**
- **Assigned to** (team member)
- **Stage-specific data point:**
  - *Submitted for Quote* → Date RFQ received
  - *Awaiting Client Response* → Quote validity date
  - *Quote Expired* → Days since expiry
  - *Accepted Requoting* → Date originally accepted, with "requoting" indicator

## Filters
- By **team member** (see one person's workload)
- By **client**
- By **mode** (FCL / LCL / Air)
- By **trade lane** (origin/destination)
- By **RFQ ID** (free-text search)

## Data Source
- All required data points are available within the existing system via `ClientRFQDefinition` and `QuoteResponseDefinition` models
- Stage bucketing is derived from CRD `computed_internal_status` + QRD status/validity
- Assignee resolved from Project-level `Collaborator` model (role: `ACCOUNT_MANAGER`)
- "Quote Expired" is derived (QRD-level check, not a CRD status)
- "First-time client" is derived (count of prior `DONE_ACCEPTED` CRDs for the organization)
- No external carrier tracking integration needed — post-acceptance stages are out of scope

## Visual Indicators / Flags
Priority flags on cards:
1. **CRD passed** — highlight cards where cargo ready date has passed and RFQ is still in Submitted
2. **First-time client** — flag RFQs where the client is shipping with us for the first time
3. **Re-quoting** — flag RFQs currently in the `ACCEPTED_REQUOTING` cycle

Additionally:
- **Count badge on each swim lane header** (e.g., "Submitted for Quote: 6")
- **Pipeline Value in summary strip** (total $ across all active RFQs)
- **Expired count** and **CRD Passed count** as attention pills in the summary strip

## Three-View Architecture
The board has three togglable views:

### Table View (default, leftmost toggle)
A flat, tabular view of all RFQs for quick scanning and ground-level testing.
- **De-duplicated rows:** Each RFQ/Project ID appears exactly once, even if it belongs to multiple stages
- **Stage pills column:** Colored pills showing all stages an RFQ belongs to
- **Columns:** Assignee (editable dropdown), Client, Contact, Silq ID + RFQ Date (combined), Shipper/PO #, Route, Mode, Stage(s), CRD, Quote Sent (with Qx badge for revisions), Total $ (with "was $X" for previous value), Attn (needs attention toggle), Notes (inline editable)
- **Re-quote trail:** Quote Sent and Total $ columns show `Qx` badges for revision count, "was $X" for previous values, and full history on hover
- **Needs Attention:** Clickable "!" button per row that toggles a red highlight on the entire row
- **Inline editing:** Notes field (click to edit textarea) and Assignee (dropdown)
- **Filters:** Team member, client, mode, stage, free-text search (RFQ ID, client, route)
- **Clickable rows:** Each row opens the RFQ detail (same as card click in Action View)

#### Custom Views
Users can customize the Table View and save personalized configurations:
- **Column picker:** Dropdown to show/hide individual columns, with Select All / Deselect All
- **Save View:** Save current column visibility + active filters as a named custom view (stored in localStorage)
- **View tabs:** "All Columns" (default) + saved custom views appear as clickable tabs above the filter bar
- **Delete views:** Each saved view has an "x" to remove it
- Switching views restores both column visibility and filter state

### Action View
The kanban swim lane board for day-to-day RFQ management. Pod labeled by **Revenue Account Manager**.
- 4 swim lanes: Submitted for Quote → Awaiting Client Response → Quote Expired → Accepted Requoting
- Each lane shows: count, total shipments, total quoted value
- Cards show: client, route with Air/Ocean icon, mode chip, shipment count, stage data, assignee, urgency badge
- Filters: team member, client, mode, trade lane, free-text search
- Summary pills: Active RFQs, Pipeline Value ($), Expired count, CRD Passed count, First-Time Clients

### Pod Health View
A high-level performance dashboard for the Pod Lead to assess pipeline health over time.
- **Timeline filter:** Preset ranges (This Week / Month / Quarter / Year) + custom date picker
- **Client and RFQ ID filters**
- **Summary stats (5 cards)** — $ figures led:
  1. Total Revenue (invoiced $, hero metric)
  2. Pipeline Value (total $ in funnel)
  3. Avg Deal Size ($ per invoiced RFQ)
  4. Conversion Rate (% approved, showing $ converted of $ submitted)
  5. Quote TAT Avg (days, with active client count)

- **Pipeline Overview (2 primary sections, each with RFQ/Quote + status sub-grids):**

  #### 1. Shipping
  Top-level grouping for all shipment-related pipeline data. Includes a **mode filter** (All / Air / Ocean / Trucking).

  **RFQs & Quotes** (sub-section) — $ values are the hero numbers, counts shown as secondary badges
  - RFQ Pipeline Value — $ total, with count badge
  - Quoted Value — $ quoted, with count badge
  - Won Value — $ converted + value conversion % bar + count badge
  - Lost Value — $ lost + win rate % + count badge

  **Shipment Tracking** (sub-section) — historical outcomes, $ led
  - Shipment Value — $ total
  - Booked Value — $ awaiting pickup
  - In Transit Value — $ currently moving
  - Delivered Value — $ fulfilled + fulfillment % bar

  #### 2. Inspections
  Top-level grouping for RFQs that require quality/compliance checks.

  **RFQs & Quotes** (sub-section) — $ led, same pattern as Shipping

  **Inspection Status** (sub-section) — $ led
  - Scheduled Value, In Progress Value, Passed Value, At Risk Value

## Codebase Context
Detailed backend data model and status lifecycle documentation is maintained in:
`Knowledge/Reference files/Pod Priority Board - Codebase Context for Prototype.md`

Key references:
- **Entity hierarchy:** Organization → CRD → CRV → SilqRFQ → QRD → Shipment
- **CRD status computation:** Priority-ordered logic (first match wins) based on CRV status, RequoteTransaction, SilqRFQ, and QRD statuses
- **Assignee model:** `Collaborator` with `collaboration_role` (ACCOUNT_MANAGER, ASSOCIATE_ACCOUNT_MANAGER, etc.) attached to Project via GenericFK
- **Mode:** `ClientRFQShippingServiceInfo.freight_modes[]` (AIR, OCEAN_FCL, OCEAN_LCL, etc.)
- **Route:** `CRV.origin_place`, `CRV.destination_place` for pre-acceptance; shipment-level for post-acceptance
- **Date fields:** CRD.created_at (submission), QRD.quote_valid_till (expiry), QRD.accepted_time (acceptance), CRV.cargo_ready_date (CRD)

## Hosting
The prototype is hosted on **GitHub Pages** via a dedicated `silq-prototypes` repository:
- Repo folder: `Knowledge/silq-prototypes/`
- Landing page: `index.html` (links to all prototypes)
- Deployed via GitHub Pages (source: `main` branch, root `/`)
- Collaborators can add new prototypes by following the `README.md` in the repo

## Live Integration Plan (Phased)
Discussed plan to make the board read real data from the existing Postgres backend:

### Phase 1 — Read-Only API
- Create SQL views in Postgres for stage bucketing (Submitted for Quote, Awaiting Client Response, Quote Expired via QRD check, Accepted Requoting) and health metrics (pipeline $, conversion rates)
- Expose read-only REST endpoints via the existing Python/Django backend (e.g. `/api/pod-board/lanes`, `/api/pod-board/health`)
- Swap the hardcoded `RFQS` and `HEALTH_DATA` arrays in the prototype with `fetch()` calls to these endpoints
- Link each card's RFQ ID to the main app URL (e.g. `https://app.onesilq.com/projects/{encoded_project_id}/quotes`, noting Base64 encoding for IDs)

### Phase 2 — Embed in App
- Mount the board as a route inside the main Silq application
- Use the app's existing auth/SSO so only logged-in users can access it
- Replace raw HTML with the app's frontend framework

### Phase 3 — Full Native Feature
- Real-time updates (WebSockets or polling)
- Pod-level permissions and role-based filtering
- Write actions (assign, flag, update status) directly from the board

## Next Steps
- Review prototype and iterate on all three views
- Draft a proper spec / PRD for this feature
- Plan DB views and queries for stage bucketing + health metrics (see Live Integration Plan above)
- Create engineering handoff doc for Phase 1
- Integrate into the Silq app as a native feature
