# Task: Credit Limit Management Table — UI Prototype

**Linked goal:** Client credit limit feature (GOALS.md)

---

## Objective
Build a clickable UI prototype of the Client Credit Limit Management table so Finance users can visualize the interface for maintaining, viewing, and updating client credit terms and exposure.

## Key goals
- Display all core credit fields: client name, account manager, general credit terms, assigned limit, current exposure, available credit, credit documentation
- Implement the credit exposure formula: `Sum of outstanding invoices (net of payments & adjustments) + customer-level debit notes − customer-level credit notes − unadjusted advances/payments`
- Include standard additional fields: credit rating, payment score, utilization bar, limit type, validity period, approval status, currency
- Support key Finance workflows: add new credit limit, revise credit terms, view detailed breakdown, upload documentation
- Show summary-level KPIs: total clients, total credit allocated, total exposure, over-limit count, expiring-soon count

## Acceptance criteria
- [ ] Prototype opens in any browser with no dependencies
- [ ] Table shows all 8 sample clients with realistic freight forwarding data
- [ ] Credit exposure is computed correctly per the PRD formula
- [ ] Status badges reflect: Within Limit, Near Limit (< 10% remaining), Over Limit, Expired
- [ ] "Add Client Credit Limit" modal captures all required fields including document uploads
- [ ] "Revise Credit Terms" modal allows updating limit, terms, and attaching justification
- [ ] Detail side panel shows full exposure breakdown, terms, documentation list, and revision history
- [ ] Search and filter (by status) work correctly
- [ ] Summary cards display accurate aggregated metrics
- [ ] Expiring-soon flag appears for limits expiring within 30 days
