# Silq Codebase Architecture Map

Generated from exploration on May 14, 2026. Repos cloned to Desktop.

## Backend (`C:\Users\visha\OneDrive\Desktop\silq`)

### Stack
- **Framework:** Django 5.2, ASGI via Channels
- **Database:** PostgreSQL + PostGIS (primary + read replica + BI DB)
- **GraphQL:** Dual — legacy Graphene (`/graphql/`) being migrated to Strawberry (`/strawberry/`, `/public/`)
- **REST:** DRF external API at `/api/v1/` (shipments, rates, invoices)
- **Background jobs:** Celery (queues: default, high, low, long_running, agent, auto_quote) + django-celery-beat + Kafka consumers
- **Search:** OpenSearch (via django-opensearch-dsl)
- **Auth:** Session + Token auth, API keys for external, impersonation support
- **Feature flags:** Waffle + custom Gandalf rules engine
- **Monitoring:** Silk (profiling), Datadog, Sentry (on-prem Azure)

### Key Domain Apps (45+ Django apps)
| App | Domain |
|-----|--------|
| `quoting` | RFQ lifecycle, quote generation, auto-quoting orchestration |
| `rates` | Rate sheets, rate line items, Rate model for AQ matching |
| `shipments` | Shipment lifecycle, status tracking, execution states |
| `invoicing` | Invoice model, QB sync bridge, payment status |
| `integrations` | QuickBooks, Shipco, VesselFinder, Google Apps, BeProduct |
| `financing` | CreditLimit model (new), Payment, CreditMemo |
| `organization` | Client/vendor organizations, memberships |
| `app_platform` | Work management (Tasks/Projects as Task tree), artifacts, tours |
| `bookings` | Supplier booking forms → RFQ conversion |
| `network` | Network/partner management |
| `atlas` | AI agent framework, chat sessions, SSE streaming |
| `skynet` | LLM/template lab |
| `notifications` | Notification delivery (being overhauled — External Notification Reliability project) |
| `sauron` | Event sourcing/publishing |
| `api` | GraphQL schemas (Graphene + Strawberry), external REST API |

### Rates & Auto Quoting Architecture
- **RateSheet** → uploaded file with vendor, validity, type (Ocean/Trucking/Air/etc.)
- **RateLineItem** (abstract) → OceanRateLineItem, AirRateLineItem, Origin/Destination/CustomsRateLineItem
- **Rate** → denormalized query-optimized model used by AQ matching. GenericFK back to originating line item.
- **Trucking:** RateSheetTruckingLane → DrayageRateSheetLineItem / CartageRateSheetLineItem
- **AQ Engine:** Atlas agent-based (3 delegates: trade lane setup → lane processing → Shipco rates). Fetches via `RatesService.list_rates_given_mode_route_and_charges` with CRD-based validity matching.
- **Shipco:** Full integration under `integrations/shipco/` — API calls via Atlas AgentTools.API_CALL, rate ingestion service, benchmark DTOs
- **Flockfreight/Draymaster:** Not yet implemented in code

### QuickBooks & Credit Limits
- **QB Gateway:** `integrations/quickbooks/quickbooks_gateway.py` — OAuth, invoice/payment/customer CRUD
- **QB Service:** `quickbooks_service.py` — sync_invoice, sync_organization, webhook processing
- **Models:** QuickbooksCustomer (1:1 Organization), QuickbooksProject (1:1 QuoteResponseDefinition), QuickbooksInvoice, QuickbooksCreditMemo
- **Invoice bridge:** `invoicing.Invoice` has 1:1 to QuickbooksInvoice. Sync updates balance, paid status.
- **CreditLimit model:** `financing/models.py` — organization, version, amount, general_credit_terms, duties_outlay_option, revision_reason. Schema exists but NOT yet wired into app logic.
- **Payment/CreditMemo models:** Exist in `financing/` but not yet wired into production sync paths

### RFQ → Shipment Lifecycle
1. **Booking submission** (optional) → converts to ClientRFQDefinition/Version via BookingService
2. **ClientRFQDefinition** → ClientRFQVersion → SilqRFQ (deprecated mirror) → QuoteResponseDefinition
3. **QRD accepted** → `create_shipment_from_quote` → Shipment created with accepted_quote FK
4. **Shipment statuses:** Location-based (seller → origin port → transit → destination → consignee) + Execution-based (NEW → IN_PROGRESS → DONE)
5. **Projects:** No separate model — root Task with task_type=PROJECT. RFQs attach as TaskSubject, Shipments as TaskResult.

### No "Pod" Model in Code
- Pod assignment is a BI/analytics concept (UserTeams in business_intelligence), not a runtime model
- Collaboration via generic Collaborator model on tasks

---

## Frontend (`C:\Users\visha\OneDrive\Desktop\silq-frontend`)

### Stack
- **Language:** ReScript 11 (legacy/core) + TypeScript strict (new features)
- **UI:** React 18, Tailwind CSS 3, MUI 7
- **Data:** Relay 15 (dual compiler — main + public schemas)
- **Bundler:** Vite 4
- **State:** MobX for complex state, React context for lightweight
- **Routing:** ReScript Relay Router (not react-router-dom)
- **Testing:** Playwright E2E

### Entry Flow
Main.res → App.res (auth, layout) → Routes.res (URL matching → route variants → page components)

### Key Pages
| URL | Module |
|-----|--------|
| `/projects` | ProjectDashboard |
| `/rfqs` | RequestForQuotesDashboard |
| `/shipments` | Shipments |
| `/rates` | Rates (upload, config, client sheets) |
| `/invoices` | Invoices (admin-gated) |
| `/network` | Network |
| `/tasks` | Tasks |
| `/bookings` | BookingsDashboard |
| `/agents` | AgentsDashboard |
| `/console` | Console (internal ops) |

### Dual Language Policy
- New features → TypeScript
- New ReScript only for icon patterns
- TS pages need thin `.res @module` wrappers for the router
