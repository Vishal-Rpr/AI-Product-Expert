# FBX Benchmark Rate Integration

**Goal link:** API integrations with rate providers (GOALS.md)

## Objective
Display FBX market median and market low benchmark rates from FreightOS/Freightos Terminal alongside quotes in our B2B freight forwarding app, so quoting teams can see how their rates compare to the market in real time.

## Key goals
- Identify the right data access path (Terminal API vs Baltic Exchange API vs embeddable widget)
- Secure API access and data licence for FBX benchmark data
- Build integration to pull market median and market low rates by trade lane
- Surface benchmark data in the quoting UI alongside live quotes

## Acceptance criteria
- [ ] Data access agreement signed with Freightos Terminal or Baltic Exchange
- [ ] API integration returns market median and market low rates per trade lane
- [ ] Benchmark data displays in the quoting screen when a user is quoting
- [ ] Data refreshes at least daily (FBX publishes daily at 14:00 UTC)
