# Client Credit Limit Table — Prototype Summary

## Location
`Prototypes/credit-limit-table.html` — standalone HTML file, opens in any browser, zero dependencies.

## What It Is
A clickable UI prototype for a Client Credit Limit Management screen within the Silq freight forwarding app. Built for internal Finance users (admin view) and external client users (client view) to view, manage, and request changes to credit terms. Styled to match the Silq design system (warm beige/amber palette, Inter font, left sidebar navigation with "silq" text logo).

## Two Views (toggle in top-right header)

### 1. Admin View (Finance / FinOps team)

**Summary cards** (row of 3 above the table):
| Card | Content | Notes |
|------|---------|-------|
| Clients by Status | Mini pie chart with total client count in center; slices for Within Limit (green), Near Limit (amber), Over Limit (red) with legend counts | Excludes DOR clients — only clients with assigned credit limits |
| Credit Exposure vs. Limit | Total exposure amount with progress bar against total assigned limit; shows utilization %, available amount | Clients with assigned credit limits only (excludes DOR) |
| Total A/R Receivable | Total outstanding invoices across ALL clients | Includes both credit-limit clients and DOR clients — full A/R view as of today |

**Table columns** (one row per client):
| # | Column | Notes |
|---|--------|-------|
| 1 | Client | Name (clickable → opens detail panel) + Client ID. Revision request rows show amber highlight + left-border accent + "Revision Requested" label |
| 2 | Account Manager | AM name with avatar initials |
| 3 | General Credit Terms | DOR, 7 Days, 10 Days, 15 Days, 30 Days, 45 Days, 60 Days. Hover tooltip shows the terms value |
| 4 | Assigned Limit | USD amount with utilization progress bar underneath (green <70%, amber 70-90%, red >90%). Shows "N/A" for DOR clients |
| 5 | Current Exposure | Computed from credit formula. Red text if over limit |
| 6 | Available Credit | Green if positive, red if negative. Shows "N/A" for DOR clients |
| 7 | Status | Badge: Within Limit / Near Limit / Over Limit / N/A (DOR clients) |
| 8 | Duties Outlay Option | Colour-coded badge: Silq Duty, Pre-Pay, ACH, Not Applicable |
| 9 | Actions | View Details (eye), Revise Terms (pencil), Documents (doc icon) |

**Sorting:** Client name, Assigned Limit, Current Exposure, Available Credit are sortable (ascending/descending toggle).

**Toolbar:**
- Search bar (filters by client name or account manager)
- Filter chips: All, Within Limit, Near Limit, Over Limit, Revision Requests
- Last synced timestamp ("Last synced with QuickBooks: ...")

**Row actions:**
- **View Details** → slide-out detail panel (see Detail Panel section below)
- **Revise Terms** → opens Revise Credit Terms modal
- **Documents** → opens detail panel focused on the Documents section

**"+ Add Credit Limit" button** → opens the Add Client Credit Limit modal

### 2. Client View (single client perspective)

**Summary cards** (5 cards, rendered dynamically for the logged-in client):
| Card | Value |
|------|-------|
| Assigned Limit | Limit amount + limit type + terms |
| Current Exposure | Sum of all outstanding |
| Available Credit | Green if positive, red if negative, shows % remaining |
| Current Bookings | Accepted shipment quotes not yet invoiced (count + amount) |
| Duties Outlay | Client's outlay option |

**Donut pie chart:**
- Shows credit utilization (consumed vs. available) as a ring chart
- Clickable — triggers a toast indicating navigation to the Invoices page
- "View Invoice Breakdown" link below the chart

**Action cards** (right-hand panel, no table):
| Card | Action |
|------|--------|
| View Full Details | Opens detail panel with exposure breakdown, terms, docs, revision history |
| View Invoice Breakdown | Navigates to Invoices page (simulated via toast) |
| Request Credit Limit Revision | Opens Request Revision modal |
| View Documents | Opens detail panel focused on documents |

**Exposure Breakdown** (inline below action cards):
- Outstanding Invoices (clickable → opens ageing breakdown popup)
- \+ Customer-Level Debit Notes
- − Customer-Level Credit Notes
- − Unadjusted Advances/Payments
- = Credit Exposure (bold total)

## Detail Side Panel (slides from right)
Triggered by View Details action (both views). Contains five sections:

1. **Credit Position** — Assigned Limit, Current Exposure, Available Credit, Utilization % with status badge
2. **Exposure Breakdown** — Full formula view with:
   - Outstanding Invoices (net of payments)
   - **Invoice Ageing Breakdown** (inline sub-section): Current, 1–30, 31–60, 61–90, 90+ day buckets — each showing total amount and invoice count
   - \+ Customer-Level Debit Notes
   - − Customer-Level Credit Notes
   - − Unadjusted Advances/Payments
   - = Credit Exposure
3. **Credit Terms** — General Terms, Limit Type (Revolving only for now), Duties Outlay Option, Approval Status. Pending revision requests shown in amber highlight
4. **Documents** — Clickable chips showing filename and file type
5. **Revision History** — Timeline of all past credit limit changes (date + description)

## Invoice Ageing Breakdown Popup
Triggered by clicking "Outstanding Invoices" in the client-view exposure breakdown. Shows a modal with:
- Client name in the title
- Five buckets: Current, 1–30, 31–60, 61–90, 90+
- Each bucket displays: label, total amount (USD), invoice count
- Total outstanding shown at the bottom

## Modals / Forms

### Add Client Credit Limit (Admin)
| Field | Type | Mandatory |
|-------|------|-----------|
| Client Name | Dropdown | Yes |
| Account Manager | Dropdown | Yes |
| Credit Limit Amount (USD) | Number input — **auto-set to $0 and disabled when DOR is selected** | Yes |
| General Credit Terms | Dropdown (DOR, 7 Days, 10 Days, 15 Days, 30 Days, 45 Days, 60 Days) — selecting DOR disables the limit amount field | Yes |
| Credit Limit Type | Dropdown (Revolving only for now) | Yes |
| Duties Outlay Option | Dropdown (Silq Duty, Pre-Pay, ACH, Not Applicable) | No |
| Credit Limit Application (upload) | File upload (.pdf, .doc, .docx, .xlsx) | Yes |
| Credit Limit Allocation Document (upload) | File upload (.pdf, .doc, .docx, .xlsx) | Yes |
| Internal Notes / Justification | Textarea | No |

### Revise Credit Terms (Admin)
| Field | Type | Mandatory |
|-------|------|-----------|
| Client | Text (read-only, pre-filled) | — |
| Current Limit | Text (read-only, pre-filled) | — |
| New Credit Limit (USD) | Number input | Yes |
| Credit Terms | Dropdown (DOR, 7 Days, 10 Days, 15 Days, 30 Days, 45 Days, 60 Days) — auto-populated with existing value | Yes |
| Revision Reason | Dropdown (Periodic review, Improved payment history, Deteriorated payment history, Business volume increase, Business volume decrease, Client request, Risk re-assessment, Other) | Yes |
| Supporting Documentation (upload) | File upload | No |
| Justification Notes | Textarea | No |

### Request Credit Limit Revision (Client)
| Field | Type | Mandatory |
|-------|------|-----------|
| Reason for Revision Request | Dropdown (Need higher limit for upcoming orders, Business volume has increased, Current terms are too restrictive, Seasonal demand increase, Other) | Yes |
| Detailed Description | Textarea | Yes |
| Requested New Limit (USD) | Number input | No |
| Supporting Documents (upload) | File upload | No |

All forms mark mandatory fields with a red asterisk (*). Info banner on the client form explains that requests go to Finance for review.

## Credit Exposure Formula (implemented in JS)
```
Credit Exposure = Outstanding Invoices (net of payments & adjustments)
               + Customer-Level Debit Notes
               − Customer-Level Credit Notes
               − Unadjusted Advances/Payments

Available Credit = Assigned Limit − Credit Exposure
```

## Status Logic
| Status | Condition |
|--------|-----------|
| Within Limit | Available Credit > 20% of Assigned Limit |
| Near Limit | Available Credit < 20% of Assigned Limit (but >= 0) |
| Over Limit | Available Credit < 0 |

## Sample Data
8 sample clients with full data including:
- Client IDs (CLT-1001 through CLT-1008)
- 3 Account Managers: Sarah Kim, James Chen, Maria Lopez
- Credit terms: DOR, 15 Days, 30 Days, 45 Days, 60 Days
- Limits from $200,000 to $1,000,000 (CLT-1007 is DOR with no credit limit)
- Ageing bucket data per client
- Current bookings data per client
- Documents (1–4 per client)
- Revision history entries
- 2 clients with pending revision requests (CLT-1002, CLT-1008)

## Design System
- **Palette:** Warm beige/amber — `--bg: #faf9f7`, `--primary: #c8842e`, `--card: #ffffff`
- **Font:** Inter (Google Fonts)
- **Status colours:** Green (within), Amber/Yellow (near), Red (over)
- **Layout:** Left sidebar (220px) with Silq logo + nav items, main content area
- **Responsive:** Collapses to 3-column summary grid at smaller widths

## Key Design Decisions
- **No expiry/validity dates** — removed from all views, forms, and data
- **No currency selector** — all values implicitly USD
- **No Payment Terms Detail field** — removed from forms, detail panel, and data
- **Client view has no table** — dashboard-only with pie chart, action cards, and inline exposure breakdown
- **Ageing breakdown** appears both as an inline section in the detail panel (under Exposure Breakdown) and as a popup modal in the client view
- **DOR (Due on Receipt) clients** — shown in the table but with N/A for Assigned Limit, Available Credit, and Status. DOR clients are excluded from the pie chart and exposure/limit summary cards, but included in Total A/R. DOR = no credit limit applicable by definition

## Related Files
- `Tasks/credit-limit-table-prototype.md` — task file with objective, key goals, acceptance criteria
- `Knowledge/Reference files/PRD - Client Credit Limit and QuickBooks Integration.md` — local PRD
- [Google Doc PRD](https://docs.google.com/document/d/1W3NVapRu6lVhc6o299bcbx1wE3LBaJY9W9Mukw_-rNw/edit)
- [Form Field Definitions (Google Sheet)](https://docs.google.com/spreadsheets/d/1JE4Uz6i5imzkRJ3CjfluczghTarO5p7nj4ma98H4swg)
- `Exports/` — CSV exports of form field definitions (Add, Revise Admin, Request Client)

## Linear Tickets
- **CON-7194** — [User Story 1] - [Admin View] Credit Limit Table Setup — Columns, Summary Cards, Filters & Manual Sync
- **CON-7195** — [User Story 2] - [Admin View] Export Credit Limit Table to Excel
- **CON-7196** — [User Story 3] - [Admin View] Create Credit Limit Form
- **CON-7197** — [User Story 4] - [Admin View] Revise Credit Limit Form
- **CON-7198** — [User Story 5] - [Admin View] Actions Bar — Detail Panel, Ageing Breakdown & Revision History
- **CON-7199** — [User Story 6] - [Admin View] Success Metrics Definition (Placeholder)
- ~~**CON-7162**~~ — Canceled (superseded by the stories above)

## Change Log
| Date | Change |
|------|--------|
| Initial build | Table with admin/client views, modals, detail panel, all 8 sample clients |
| Update 1 | Added invoice drilldown from client view (pie chart + action card → Invoices page navigation toast) |
| Update 2 | Removed Expiry/Valid From dates from entire prototype |
| Update 3 | Removed "Total Credit Allocated" summary card from admin view; added "Revision Requests" card |
| Update 4 | Added invoice ageing breakdown popup (Current, 1–30, 31–60, 61–90, 90+) triggered from Outstanding Invoices click |
| Update 5 | Added inline ageing breakdown in the detail panel under Exposure Breakdown |
| Update 6 | Removed Currency dropdown from all forms (all USD) |
| Update 7 | Added mandatory field indicators (red asterisk) on all forms |
| Update 8 | Added "Current Bookings" summary card in client view |
| Update 9 | Removed "Payment Terms Detail" field from forms, detail panel, table tooltip, and data |
| Update 10 | Aligned prototype with PRD + Google Sheet as source of truth: General Credit Terms dropdown changed to DOR/7/10/15/30/45/60 Days; Duties Outlay made non-mandatory with values Silq Duty/Pre-Pay/ACH/Not Applicable; Credit Limit Type restricted to Revolving only; CL Allocation Document made mandatory; Revise form Justification Notes made non-mandatory; Revise form field renamed from "New Credit Terms" to "Credit Terms"; Near Limit threshold changed from 10% to 20%; all sample data updated to match |
| Update 11 | Replaced 4 admin summary cards with 3: (1) Clients by Status pie chart showing Within/Near/Over breakdown, (2) Credit Exposure vs. Limit progress bar, (3) Total A/R Receivable across all clients. DOR clients now show N/A for Assigned Limit, Available Credit, and Status columns. DOR excluded from pie and exposure cards but included in A/R total. CLT-1007 (Silk Road Logistics) assigned limit set to $0 as DOR. |
| Update 12 | Add Credit Limit form: selecting DOR in General Credit Terms now auto-sets Credit Limit Amount to $0 and disables the field. Re-selecting any other term re-enables the field. |
