# Codebase Exploration Guide

Once the company repo is connected, this is the structured exploration plan to build deep context for product work.

## Phase 1: Architecture overview (first pass)

### Repo structure
- [ ] Map the folder structure — identify backend, frontend, shared libs, config
- [ ] Identify the Python framework in use (Django, Flask, FastAPI, or other)
- [ ] Locate the GraphQL schema (Strawberry or Graphene based on org forks)
- [ ] Find the database models / ORM layer
- [ ] Identify the API layer — REST endpoints, GraphQL resolvers, or both
- [ ] Locate environment/config files to understand third-party service dependencies

### Tech stack confirmation
- [ ] Python backend framework
- [ ] GraphQL library (Strawberry / Graphene)
- [ ] Frontend framework (ReScript with Vite, based on org forks)
- [ ] Database (Postgres, MySQL, etc.)
- [ ] Task queue / background jobs (Celery, etc.)
- [ ] Deployment setup (Docker, K8s, etc.)

---

## Phase 2: Business domain mapping (tied to GOALS.md)

### Rate provider integrations
- [ ] Find existing rate provider integration code (Shipco, Flockfreight, Draymaster)
- [ ] Map the data flow: how rates come in → how they're stored → how they're surfaced in quoting
- [ ] Identify the quoting/pricing engine — where rate comparisons happen
- [ ] Check for API client abstractions — is there a common pattern or is each provider ad-hoc?
- [ ] Look for rate caching, staleness handling, error/retry logic

### Client credit limit system
- [ ] Check if any credit-related models/tables already exist
- [ ] Find the QuickBooks integration code — sync logic, API client, data mapping
- [ ] Locate invoice models and payment tracking
- [ ] Identify where shipment booking happens — this is where credit limit enforcement would plug in
- [ ] Look for existing customer financial data (balances, outstanding amounts)

### Pod priority board
- [ ] Find the RFQ (Request for Quote) model and workflow
- [ ] Map the shipment lifecycle stages in code (unquoted → quoted → booked → delivered → invoiced)
- [ ] Identify pod/team assignment logic
- [ ] Check if there's an existing dashboard or reporting layer

---

## Phase 3: Customer-facing behavior analysis

### Booking flow
- [ ] Trace the end-to-end booking flow from customer request to confirmed booking
- [ ] Identify validation rules, business logic, and edge cases
- [ ] Find notification triggers (emails, alerts)

### Customer portal
- [ ] What can customers see and do in the app?
- [ ] Where are permissions/roles defined?
- [ ] What data is exposed via API to the frontend?

### Reporting and analytics
- [ ] What Metabase queries exist? (cross-reference with Metabase MCP)
- [ ] Any in-app reporting or dashboards?
- [ ] Data export capabilities

---

## Phase 4: Code quality and patterns

### For feature suggestion context
- [ ] How are new features typically structured? (folder conventions, service layer patterns)
- [ ] Testing coverage — what's tested, what's not?
- [ ] Migration patterns — how are DB schema changes handled?
- [ ] Error handling patterns — how are errors surfaced to users?

---

## Key questions to answer from the codebase

1. What's the current state of the QuickBooks integration — is it polling or webhook-based?
2. How are rates currently fetched and cached from providers?
3. What does the shipment booking validation logic look like — where would credit limit checks fit?
4. What's the RFQ lifecycle in code — does it match the Pod Priority Board stages?
5. Are there any feature flags or A/B testing infrastructure?
6. What background jobs exist and what do they do?
7. Where are the pain points in the code — complex files, high churn areas, TODO comments?
