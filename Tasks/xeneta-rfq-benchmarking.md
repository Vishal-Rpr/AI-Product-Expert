# Task: Xeneta RFQ rate benchmarking integration

**Linked goal:** API integrations with rate providers

## Objective
Evaluate and integrate Xeneta's market rate API into our RFQ quoting workflow to benchmark every quote against independent market data before it reaches the client.

## Key goals
- Request a Xeneta demo and formal pricing quote for our org size and volume
- Build an MCP wrapper around Xeneta's API as Phase 1 proof of concept (4–8 hours of dev)
- Validate data quality against real RFQ lanes our team quotes on
- Design a caching strategy to stay within API quota limits
- Plan the Phase 2 production integration into the quoting UI

## Acceptance criteria
- [ ] Xeneta pricing confirmed and approved by leadership
- [ ] MCP wrapper deployed locally and tested against 10+ real RFQ lanes
- [ ] Benchmark data quality validated: rates make sense vs. our buy rates and existing market knowledge
- [ ] Caching strategy documented and API quota utilization projected
- [ ] Go/no-go decision made on Phase 2 production build
