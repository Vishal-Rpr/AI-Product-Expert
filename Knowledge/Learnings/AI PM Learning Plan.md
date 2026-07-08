# AI Product Management Plan — v2 (Sprint to a Vertical AI PM Role)

**Last re-evaluated:** July 8, 2026
**Who you are now:** A practicing B2B product manager in freight forwarding who already operates as an AI-native PM — and who has now **shipped two public AI tools**. You run a working PM co-pilot daily (Linear + Google Workspace MCPs, RAG-style PRD/user-story generation, automated task files, prototype workflows). You have direct access to a real production AI codebase (`atlas/` agents, dual GraphQL, Kafka, Celery, auto-quoting, document processing). You ship real AI-adjacent features: client credit limits + QuickBooks, auto-quoting (Spring Tide), rates automation, and a Sync Document Processing framework.

**What you've publicly shipped (as of Jul 8, 2026):**
- [Co-Pilot-build-v1](https://github.com/Vishal-Rpr/Co-Pilot-build-v1) — RAG-powered PM CLI: PRD generation, opt-in eval (5-dimension rubric), PRD→tickets (Linear/Jira), prototype generation, Excalidraw diagrams, Confluence publishing. ChromaDB vector store, Click CLI, 13 pytest tests, product-brief README with documented design tradeoffs.
- [logistics-pm](https://github.com/Vishal-Rpr/logistics-pm) — a domain-specific Cowork plugin: 4 auto-firing skills (freight-domain-knowledge, logistics-prd-generation, eval-framework, style-matching), 2 slash commands (`/write-spec`, `/user-stories`), real freight reference PRDs. Follows Anthropic's plugin spec; differentiates on domain + evals + style matching.
**Goal:** Land a **vertical / domain AI PM role** (logistics, supply chain, or adjacent B2B) — **actively applying now, target offer in ~8-10 weeks.**
**Positioning:** *Domain AI PM for logistics & supply chain* — the person who has actually shipped AI-adjacent features on messy, multi-stakeholder freight workflows.
**Time budget:** 8-10+ hrs/week. ~6-week build sprint, with the application + interview loop running in parallel from Week 1.
**Central principle:** You have already built the capability. This plan converts capability into **public evidence, interviews, and offers.** Ship > study. Reading is now the reference layer, not the work.

> Linked goals: `GOALS.md → Personal → AI upskilling` and (new) `AI PM role transition`.

---

## What you've already banked (stop re-doing these)

Give yourself credit and do not repeat this work. The old tracker said Weeks 3-8 were "not started" — in reality you did the substance out of order:

| Old plan item | Status | Evidence |
|---|---|---|
| LLM fundamentals (Karpathy, AI stack) | ✅ Done | Marked complete; you work in an AI codebase daily |
| PM Co-pilot v0/v1 (build from scratch) | ✅ Done & in daily use | Linear + Google Workspace MCPs, RAG PRD generation, task automation |
| Product teardown / competitive landscape | ✅ Researched | `PM Copilot Landscape & Architecture.md` (May 31) |
| Technical depth (RAG vs fine-tune, embeddings, cost) | ✅ Done | Architecture-decision table + Claude pricing analysis |
| Capstone strategy / repositioning | ✅ Done | `Capstone Repositioning - Cowork Plugin Strategy.md` (Jun 1) |
| Prompt engineering for PMs | ✅ Done in practice | Your daily co-pilot usage |
| RAG in practice | ✅ Done & shipped | ChromaDB RAG in Co-Pilot-build-v1 |
| Ship the co-pilot (Pillar 3) | ✅ SHIPPED & public | Co-Pilot-build-v1 repo, product-brief README, tests |
| Ship the domain plugin (Pillar 3) | ✅ SHIPPED & public | logistics-pm repo (4 skills, 2 commands) |
| Eval framework (rubric) | 🟡 Partially done | 5-dim rubric in both repos — but LLM-judge on *generation quality*, not dataset-driven feature evals |

**Still open (this is the whole game now):** deepen evals from rubric → **one rigorous, metrics-based eval on a real AI feature**; write 3 **real-work case studies**; **distribute** what you've shipped (posts + portfolio, not just repos); nail **positioning**; and run **interview reps + applications** hard.

---

## Your positioning (nail this before anything else)

For a vertical hunt, positioning is the highest-leverage asset. Everything else hangs off it.

**One-liner:** "I'm a product manager who ships AI features on real, messy freight-forwarding workflows — auto-quoting, document processing, and credit risk — and I measure them with evals, not vibes."

**Why it wins:** Generalist AI PMs are common; domain AI PMs who have *actually shipped* against unstructured B2B data are rare and in higher demand. Your freight domain + production AI codebase + real evals is a combination almost no candidate can match.

**Proof stack (what you point to):** two shipped open-source tools ([Co-Pilot-build-v1](https://github.com/Vishal-Rpr/Co-Pilot-build-v1) + [logistics-pm](https://github.com/Vishal-Rpr/logistics-pm)) ✅, a rigorous eval on a real feature (Pillar 1), 3 real-work case studies (Pillar 2), and a strategy memo on AI-native freight (Pillar 4). The build exists; now it needs **distribution and narrative**.

**Action:** Write this as a 3-sentence positioning statement + a one-line LinkedIn headline in Week 1. Everything public flows from it.

---

## The 5 Pillars (run in parallel, not in sequence)

### Pillar 1 — Evals, level 2 (deepen from rubric → rigorous, metrics-based)
You already have a **5-dimension rubric (LLM-as-judge)** in both shipped repos — that covers *generation quality* ("is this PRD good?"). Good, but that's the entry-level version every eval-aware candidate has. The interview-differentiating artifact is a **dataset-driven, quantitative eval on a real AI feature**, anchored to the **"LLM output evaluations"** project on your Q2 board.

- Pick one real AI feature — recommend **document extraction accuracy** (Sync Doc Processing) or **auto-quoting output quality** (Spring Tide). Both are domain-rich and demonstrable.
- Build a **labeled test set** (ground-truth examples), then measure quantitatively: extraction **precision/recall/F1** per field, groundedness/hallucination rate, plus a **guardrail metric** that must not regress.
- Add a **failure taxonomy** (categorize *why* it fails) and show how you'd track it across model/prompt changes (regression view).
- Contrast it with your existing rubric eval — that comparison ("when to use LLM-judge vs. dataset metrics") is itself a strong interview and post topic.
- Output: extend one of your repos (or a new one) + a writeup: "Two kinds of AI evals, and when to use each — a freight case study."

### Pillar 2 — Real-work case studies (your moat — you're now free to use these)
These beat any toy capstone. Anonymize company specifics; keep the product thinking. Write **three**, each 2-3 pages, structured: Problem → Discovery/evidence → Approach & tradeoffs → Metrics (outcome vs output) → AI opportunity + eval + risks.

1. **Human-in-the-loop document processing** (Sync Doc Processing framework) — the cleanest "AI PM" story: AI parses, human reviews/corrects, system learns. Perfect for interviews.
2. **Agentic auto-quoting** (Spring Tide) — multi-step, tool-calling, guardrails; use the charge-dedup and carrier/service-selection work to show reasoning about reliability.
3. **AI-assisted credit risk / exposure** (Credit Limit + QuickBooks, incl. the CON-7133 data spike) — data integration + risk + workflow; shows you connect AI to business outcomes (overdue receivables, faster credit decisions).

### Pillar 3 — Ship the co-pilot / plugin ✅ DONE
Both are public: [Co-Pilot-build-v1](https://github.com/Vishal-Rpr/Co-Pilot-build-v1) and [logistics-pm](https://github.com/Vishal-Rpr/logistics-pm). READMEs already read like product briefs with documented tradeoffs. **Do not re-architect these.** Remaining effort is limited to small, high-ROI polish *driven by feedback and interview needs* only:

- Add a short **demo** (asciinema/GIF or a 2-min Loom) to each README so a recruiter/hiring manager sees it work in 30 seconds.
- Add a **results section** once Pillar 1's rigorous eval exists (numbers > claims).
- Fold the Pillar 1 metrics-based eval into `logistics-pm`'s `eval-framework` skill so it's not rubric-only.
- Otherwise: **stop building, start distributing** (Pillar 4).

### Pillar 4 — Distribution & narrative (now your highest-leverage open item)
You've made the classic builder mistake: two solid repos, **zero distribution.** Public repos with 0-1 stars aren't evidence until someone sees them. Convert build → narrative. Five posts, each drawn from Pillars 1-3, authenticity > polish. **Start with #1 this week** — you can post it today.

1. **Open-source launch** (do first): "I built two AI tools for logistics PMs — a RAG co-pilot and a domain Cowork plugin. Here's the product thinking." Link both repos, show the domain + eval + style-matching differentiators vs. generic PM plugins.
2. **Eval framework for AI in freight** (Pillar 1) — the two-kinds-of-evals angle. Signals the exact skill they hire for.
3. **"AI in B2B Freight, 2026" landscape** (you already have the research).
4. **Case study: human-in-the-loop document processing** (Pillar 2).
5. **Strategy memo:** "If I were building an AI-native freight platform from scratch."

### Pillar 5 — Positioning + interviews + applications (parallel from Week 1)
This is what the old plan fatally back-loaded. Start now.

- **Week 1:** positioning statement, updated LinkedIn + resume, target list of ~25 vertical companies.
- **Every week:** 5-10 applications, 3-5 targeted outreach DMs (reference something specific they shipped), 1 mock interview.
- Interview frameworks preserved below (Rounds 1-5).

---

## 5-Week Execution Grid (compressed — build is done)

Pillar 3 (ship) is complete, so this is now a **distribution + evals-depth + case-study + interview sprint**. Applications run from Day 1.

| Week | Pillar 1 (Evals depth) | Pillar 2 (Case studies) | Pillar 4 (Distribution) | Pillar 5 (Apply/Interview) |
|------|------------------------|--------------------------|--------------------------|-----------------------------|
| 1 | Pick feature; build labeled test set | Draft case study #1 (doc processing) | **Post #1: launch both repos**; positioning + LinkedIn/resume live | Build 25-target list; 5 applications |
| 2 | Metrics harness (P/R/F1); first scores | Finish #1; start #2 (auto-quoting) | Add demo GIF/Loom to both READMEs | 8 applications; 3 outreach; mock (product sense) |
| 3 | Failure taxonomy; fold into logistics-pm | Finish #2; start #3 (credit risk) | Post #2: two-kinds-of-evals writeup | 8 applications; 3 outreach; mock (technical/evals) |
| 4 | Add results section to repos | Finish #3 | Post #3: freight AI landscape | 8 applications; mock (metrics) |
| 5 | Maintain | Assemble 3 into portfolio site | Post #4: strategy memo; portfolio live | 10 applications; 2 mocks (strategy + STAR) |
| 6+ | Maintain | Refresh as you interview | Post #5 (case study); 1 post/2 wks | Rolling applications + interviews until offer |

**Portfolio site (Week 5):** packaging, not creating — repos are live, posts are out. The site just brings it together. Link it in every application and DM.

---

## Interview Prep (kept — vertical AI interviews still use these rounds)

For vertical/logistics AI roles, expect **more weight on domain + evals + your real case studies**, and somewhat less on abstract "design an AI product for Google Maps." Still, master all five round types.

### Round 1: Product Sense / Product Design
**Asked:** "Design an AI feature for [product]." **Testing:** Can you find a real problem, scope an AI solution, reason about tradeoffs, define success?
**Framework:** (1) clarify user/context, (2) pick one of 2-3 pains, (3) why AI is the *right* tool, (4) high-level AI architecture (classification? generation? retrieval? agentic?), (5) failure modes/edge cases, (6) leading + lagging success metrics.
**Your edge:** "When I shipped auto-quoting, the key decision was how much autonomy to give the agent vs. human review, because a wrong quote has real revenue consequences…"

### Round 2: Strategy
**Asked:** "Should [company] build an AI-native [X]?" "A competitor just shipped an AI feature — what do you do?" **Testing:** markets, competitive dynamics, where AI is a moat vs. commodity.
**Framework:** (1) strategic context, (2) 2-3 options + tradeoffs, (3) recommendation + reasoning, (4) risks + mitigation.
**Your edge:** your "AI-native freight platform" memo + real landscape research.

### Round 3: Technical / AI Depth
**Asked:** "RAG vs fine-tuning?" "How do you reduce hallucinations in a customer-facing feature?" **Testing:** can you collaborate with ML engineers and scope well?
**Must explain clearly:** RAG vs fine-tune vs prompt engineering (when each); evals (define + run, why > benchmarks); the latency/cost/quality triangle; hallucination detection/prevention/graceful degradation; context windows; embeddings + vector search (high level); human-in-the-loop; responsible AI.
**Your edge:** you built a RAG pipeline, an eval harness, and MCP integrations — use specifics (chunking, similarity thresholds, model routing, ChromaDB tradeoffs).

### Round 4: Metrics / Analytical
**Asked:** "Measure success for an AI writing assistant." "Accuracy dropped 92%→87% — what do you do?" **Testing:** connect AI metrics to business outcomes.
**Vocabulary:** ML (precision, recall, F1, accuracy); product (task completion, time-to-value, retention); AI-specific (hallucination rate, eval pass rate, cost/query, latency p50/p95); business (revenue, ticket deflection, NPS).
**Framework:** (1) define user success, (2) leading + lagging, (3) AI quality metrics, (4) guardrail metrics, (5) A/B or staged rollout.

### Round 5: Execution / Behavioral (STAR)
**Prepare 5 stories:**
1. Shipping auto-quoting / doc processing under ambiguity (execution + AI).
2. Applying AI to messy freight workflows (domain × AI).
3. Building + shipping the eval framework (initiative, technical learning).
4. Influencing without authority (stakeholder management — e.g., FinOps on credit limits).
5. A hard tradeoff / saying no (prioritization, data-driven).

**Company-specific notes** (if you also apply to Big Tech as a hedge): Google = product sense + structured creativity; Meta = metrics + experimentation; Microsoft = technical depth + enterprise empathy; Amazon = Leadership Principles + Working Backwards; Apple = design + privacy.

**Interview prep resources:** Exponent (AI PM mocks), Lewis Lin "Decode and Conquer," Lenny "How to get into AI PM," "Cracking the PM Interview" (Gayle McDowell), IGotAnOffer.

**Prep cadence (runs across the sprint):** frameworks first → 2 product-sense Qs/day for a stretch → 2 technical/metrics Qs/day → STAR out loud (record yourself) → 2-3 full mocks before real onsites.

---

## Ongoing Habits (trimmed)

- **Daily (15 min):** Simon Willison's blog / Lenny's AI posts / HN AI threads.
- **Weekly:** ship *something* public (post, repo update, or case study). Consistency > polish.
- **Weekly:** teardown one AI feature *as a PM* (Linear AI, Notion AI, Perplexity, a freight-tech tool).
- **Session ritual (per AGENTS.md):** pull progress from the `AI-Product-Expert` repo at start; push completed learnings/artifacts at the end.

---

## Reference Appendix

### Book list (demoted to reference — you're past "learn the basics")
Read only what fills a specific gap; don't let reading crowd out shipping.

| Priority for you now | Book | Why |
|---|---|---|
| Skim for interview framing | The AI Product Playbook — Nika & Granados | Shipping AI features end-to-end; guardrails, failure modes |
| Skim, B2B/ops cases | Reimagined: Building Products with GenAI — Shi et al. | Case-study patterns |
| Optional refresh | Continuous Discovery Habits — Torres | Outcome/discovery muscle (you already practice it) |
| Optional | Obviously Awesome — Dunford | Positioning (relevant to your vertical hunt) |
| Optional | Co-Intelligence — Mollick | Org adoption of AI |
| Lower priority | The Mom Test; Inspired; AI Snake Oil | Foundational; only if a gap shows up |

### Industry snapshot (mid-2026)
- **Strongest AI PM hiring:** vertical SaaS (logistics, fintech, healthcare, legal), dev tools/infra, enterprise AI platforms, AI-native startups (Series A-B).
- **Your advantage:** complex multi-stakeholder B2B workflows, messy real-world shipping data, ROI/outcome fluency, and shipped AI features — domain AI PMs > generalist AI PMs.
- **What they test:** can you define/run evals; know when AI is/ isn't right; scope idea→shipped; work with ML engineers on cost/latency/quality; have you shipped; do you think in outcomes.

### Vertical target list (starter — build to ~25 in Week 1)
Flexport, Freightos, Project44, FourKites, Vizion, Terminal49, Altana, e2open, Stord, Shippeo, Motive, Samsara (logistics AI), plus fintech-logistics and vertical-AI startups surfacing on Lenny's / YC / a16z lists. Prioritize ones with public AI feature launches you can reference in outreach.

### Key people to follow
Lenny Rachitsky, Shreyas Doshi, Teresa Torres, Marty Cagan, Simon Willison, Ethan Mollick, Chip Huyen, Hamel Husain (evals), Eugene Yan, Maggie Appleton, April Dunford, Andrew Ng, Ben Thompson, Marily Nika.

### Newsletters & blogs
**PM:** Lenny's Newsletter, SVPG, Product Talk, First Round Review, Reforge, Department of Product.
**AI product:** Simon Willison's Weblog, One Useful Thing (Mollick), The Batch (Ng), Stratechery, a16z AI, Anthropic/OpenAI/DeepMind blogs, hamel.dev, eugeneyan.com.
**Logistics:** FreightWaves, Supply Chain Dive, The Logistics of Logistics podcast (AI episodes).

### Communities
Lenny's Slack, Mind the Product Slack, Hacker News (AI threads), r/ProductManagement, X/Twitter (build a list), LinkedIn AI PM groups, AI tool Discords (Anthropic, LangChain).

### Interview/practice sites
Exponent, IGotAnOffer, Product School, Pragmatic Institute, Mind the Product.

---

## Progress Tracker (updated Jul 8, 2026)

**Banked / done:** ✅ Co-pilot shipped (Co-Pilot-build-v1) · ✅ Domain plugin shipped (logistics-pm) · ✅ Rubric eval (both repos) · ✅ Landscape research · 🟡 Positioning (draft this week)

| Week | Evals depth | Case studies | Distribution | Apply/Interview | Status |
|------|-------------|--------------|--------------|-----------------|--------|
| 1 | Labeled test set | Draft #1 | Post #1: launch repos; positioning + LinkedIn live | 25 targets; 5 apps | Not started |
| 2 | Metrics harness (P/R/F1) | Finish #1; start #2 | Demo GIF/Loom in READMEs | 8 apps; mock (product sense) | Not started |
| 3 | Failure taxonomy → logistics-pm | Finish #2; start #3 | Post #2: two-kinds-of-evals | 8 apps; mock (technical) | Not started |
| 4 | Results section in repos | Finish #3 | Post #3: freight AI landscape | 8 apps; mock (metrics) | Not started |
| 5 | Maintain | Portfolio site | Post #4: strategy memo; portfolio live | 10 apps; mocks (strategy+STAR) | Not started |
| 6+ | Maintain | Refresh | Post #5 (case study); 1 post/2wks | Rolling until offer | Not started |
