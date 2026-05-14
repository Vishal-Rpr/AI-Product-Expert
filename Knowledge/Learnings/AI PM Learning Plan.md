# AI Product Management Learning Plan

**Who you are:** B2B freight forwarding PM. Currently ops/internal-focused (credit limit systems, rate provider APIs, internal dashboards in Retool). Strong in process/systems thinking and efficiency metrics. Gaps in customer-facing product skills and AI/ML technical fluency.
**Goal:** Land an AI PM role within 2 months.
**Duration:** 8 weeks, ~5-7 hours/week (evenings + weekends).
**Structure:** Each week has two tracks (AI + PM fundamentals), a build task for the PM Co-pilot, and a practice task tied to your real freight forwarding work.
**Central project:** PM Co-pilot Agent, built from scratch, evolving each week as you learn.

---

## The PM Co-pilot: Your Portfolio Anchor

This is the project that threads through the entire plan. Each week you learn something new and apply it directly to the co-pilot.

**Concept:** An AI agent that acts as a working partner for product managers. Core capabilities: RAG-powered PRD generation that matches your writing style using reference documents, and MCP-integrated ticket creation that actions directly into project management tools.

**Why this works as a portfolio piece:**
- Directly relevant to AI PM roles (you're building a product for your own profession)
- Demonstrates real architectural decisions: RAG for style consistency, MCPs for tool integration
- Every interviewer is a PM or works with PMs, so they instantly understand the value
- It evolves in complexity as your skills grow, showing progression

**What you showcase (the system, not the outputs):**
- **Architecture story:** Why RAG for style matching, why MCP for Linear/project tools, what tradeoffs you hit
- **Framework as product:** Open-source the agent structure, prompt design, RAG setup, MCP config. Other PMs plug in their own docs and tools.
- **Demo scenarios:** Use fictional but realistic product contexts. Write sample PRDs for a public or made-up product. Show before (manual) vs. after (AI-assisted).
- **Eval story:** How you measured quality (style accuracy, completeness, time saved)

**Important:** This is a clean, personal rebuild. No company-specific data, processes, or IP. Frame it as a general PM productivity framework inspired by common PM pain points.

---

## Build in Public Timeline

Start publishing from Week 2. By the time you assemble the portfolio in Week 7, it's already 80% live. Week 7 becomes polish and package, not create from scratch.

| Week | What goes public | Where | Framing |
|------|-----------------|-------|---------|
| 1 | Nothing (build privately, v0 won't be polished enough) | - | - |
| 2 | Product teardown of your own co-pilot | LinkedIn post | "I built a PM co-pilot. Here's what I learned about AI product quality." |
| 3 | "AI in B2B Shipping, 2026" landscape brief | LinkedIn or Substack | "I mapped the AI landscape in freight forwarding. Here's where the gaps are." |
| 4 | Eval framework for AI-assisted rate quoting | LinkedIn post | "How do you know if an AI feature is good enough to ship? I designed an eval framework." |
| 5 | PM Co-pilot + domain project repos | GitHub (open source) | "I open-sourced two AI tools I built. Here's the product thinking behind them." |
| 6 | Strategy memo: "Building an AI-native shipping platform" | LinkedIn/Substack | "If I were building an AI-native freight platform from scratch, here's what I'd build." |
| 7 | Capstone case study on a real feature | Portfolio site | "How I'd redesign a B2B feature I shipped, using AI and outcome-driven thinking." |
| 8 | Full portfolio site live + outreach blitz | Personal site/Notion | Portfolio link in every application and outreach message. |

**Content principles:** Early posts are observations and learnings, not polished product launches. Authenticity beats polish. Each post should teach the reader something, not just announce what you did.

---

## Phase 1: Sharpen the Foundation (Weeks 1-2)

### Week 1: How LLMs Work + Discovery Fundamentals

**AI Track:**
- [x] Watch: Andrej Karpathy, "Intro to Large Language Models" (YouTube, 1hr)
- [x] Read: The Complete AI Agent Stack in 2026 (optijara.ai/en/blog/ai-agent-stack-2026-complete-guide)
- [ ] Optional: Andrew Ng's "AI for Everyone" on Coursera (3hrs, free)
- [x] Read: Anthropic "Develop Tests" docs (platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [ ] Read: Anthropic prompt engineering docs (docs.anthropic.com)

**PM Track:**
- [ ] * Read: The Mom Test by Rob Fitzpatrick (~2hrs). Learn how to have useful customer conversations without leading the witness. This is the #1 gap for ops-focused PMs transitioning to customer-facing roles.
- [ ] Reflect: Think about your last 3 features (credit limits, pod board, rate APIs). Did you validate the problem with users before building? What would you do differently?

**Build (PM Co-pilot v0):**
- [ ] Set up the project from scratch on your personal PC
- [ ] Write the AGENTS.md with a clear identity, rules, and scope
- [ ] Define 2-3 core capabilities: PRD generation with RAG style matching, ticket creation via MCP
- [ ] Get it working for at least one workflow end-to-end

**Practice Task:**
Write down 5 questions you'd ask a client about their credit limit pain points, following Mom Test principles. No leading questions, no pitching solutions. Then write a 1-page product brief for the PM Co-pilot.

### Week 2: The AI Product Stack + Outcome Metrics

**AI Track:**
- [x] Read: 2026 AI Product Strategy Guide by Mind the Product (mindtheproduct.com)
- [x] Read: AI Product Manager Roadmap 2026 (nextbyrahul.tech/blog/ai-product-manager-roadmap-2026)
- [ ] Read: Chip Huyen, "Building LLM Applications for Production" (blog)

**PM Track:**
- [ ] * Read: Continuous Discovery Habits by Teresa Torres, Chapters 1-6. Covers opportunity solution trees, continuous interviewing, assumption mapping. This is the framework that bridges your ops thinking to customer-outcome thinking.
- [ ] Exercise: For your credit limit feature, map the outcome metrics you'd track if this were an external product (adoption rate, time-to-decision, error rate, revenue impact) vs. the internal efficiency metrics you're currently tracking.

**Build (PM Co-pilot v1):**
- [ ] Define eval criteria for the co-pilot: how do you know its output is actually good?
- [ ] Create 5+ test scenarios and evaluate systematically
- [ ] Identify where it fails or gives generic output, improve those areas
- [ ] Add a Knowledge folder with PM frameworks (RICE, ICE, user story templates, opportunity solution tree template)

**Practice Task:**
Build an opportunity solution tree for the credit limit feature. What's the desired outcome? What are the opportunities? What solutions map to each?

**PUBLIC (Week 2):** Write a product teardown of your co-pilot and post on LinkedIn. Frame it as "I built a PM co-pilot and here's what I learned about AI product quality." Be honest about what fails. Authenticity > polish.

---

## Phase 2: Deepen + Second Project (Weeks 3-5)

### Week 3: RAG and Retrieval Systems + Product Strategy

**AI Track:**
- [ ] * Read: Building RAG & AI Agents: From Embeddings to Autonomous Systems (tutorialq.com/ai/ml/rag-and-ai-agents)
- [ ] Explore: Try building a simple RAG demo using your rate provider documentation (or similar non-proprietary docs) as the knowledge base
- [ ] Read: a16z, "Emerging Architectures for LLM Applications"

**PM Track:**
- [ ] * Read: Continuous Discovery Habits, Chapters 7-14. Covers assumption testing, experiment design, making discovery a weekly habit.
- [ ] Watch: Marty Cagan talks on YouTube about product strategy vs. feature teams

**Build (PM Co-pilot v2):**
- [ ] Add a shipping/logistics knowledge layer so the co-pilot can help with domain-specific PM work
- [ ] Improve the RAG pipeline based on what you learned this week

**Practice Task:**
Write a 1-page product strategy brief for your rate provider integration. Include: the problem, who it serves, how you'd measure success (outcome metrics, not output), and what "good" looks like in 6 months.

**PUBLIC (Week 3):** Write the competitive landscape brief: "AI in B2B Shipping, 2026." Map 5-7 products (Flexport, Freightos, Project44, FourKites, etc.), their AI capabilities, and white space. Post on LinkedIn or Substack. This positions you as someone who thinks strategically about AI in your domain.

**Resources for landscape:**
- McKinsey, "AI in Supply Chain" reports (free summaries)
- Flexport, Project44, FourKites product pages and changelogs
- "The Logistics of Logistics" podcast (AI episodes)

### Week 4: AI Evals + Customer Segmentation

**AI Track:**
- [ ] * Read: Complete Guide to LLM & AI Agent Evaluation 2026 (adaline.ai/blog/complete-guide-llm-ai-agent-evaluation-2026)
- [ ] Understand the difference between: accuracy, precision, recall, F1 for retrieval systems; and hallucination rate, groundedness, relevance for generation quality
- [ ] Optional: Maven's "AI Evals for Engineers & PMs" by Hamel Husain

**PM Track:**
- [ ] * Read: Inspired by Marty Cagan. Focus on the discovery and strategy sections. Skip what you already know.
- [ ] Exercise: Segment your company's clients by their credit limit needs. Are there distinct personas? Different workflows? This is the "scalability thinking" muscle.

**Build: Capstone Project 2 (pick one domain-specific project):**

1. **Shipping Document AI Agent** - Takes unstructured shipping documents (BOLs, invoices, customs forms) and extracts structured data. Your domain knowledge lets you handle edge cases generic tools miss.
2. **Logistics Exception Handler** - Takes shipment status updates, flags anomalies, suggests resolution paths, and drafts customer communications.
3. **AI-Powered RFQ Analyzer** - Reads RFQ documents and produces a structured comparison.

**Practice Task:**
Design an eval framework for an AI feature relevant to your work. Example: "AI-assisted rate quoting." What would you measure? How would you know the AI output is good enough to show a client? Define rubrics, edge cases, and failure modes.

**PUBLIC (Week 4):** Post the eval framework on LinkedIn. Frame it as "How do you know if an AI feature is good enough to ship? Here's the eval framework I designed." Evals are the #1 differentiator for AI PMs right now, so this post signals exactly the right skill.

### Week 5: Agentic AI + Competitive Analysis and Shipping

**AI Track:**
- [ ] * Read: AI PM Career Guide 2026 by IdeaPlan (ideaplan.io/guides/ai-pm-career-guide)
- [ ] Deep dive on agentic AI: copilot patterns (human-in-the-loop) vs. autonomous agent patterns (multi-step, tool-calling). Read Anthropic's and OpenAI's blog posts on agent design.
- [ ] Study how AI is used in logistics/freight: automated quoting, document processing, predictive ETAs, anomaly detection

**PM Track:**
- [ ] Do a competitive teardown of 2-3 freight tech platforms (Flexport, Freightos, Project44). How do they position? What metrics do they highlight?
- [ ] Read: Obviously Awesome by April Dunford (positioning) OR watch her YouTube talks (free, 30-45 min)

**Build:**
- [ ] Finish domain capstone prototype with 3-5 realistic test cases

**Practice Task:**
Write a 1-pager: "Where could AI add the most value in our freight forwarding workflow?" Evaluate 3 candidate use cases. For each: problem, who has it, why AI is the right tool, what the eval framework looks like, what risks exist.

**PUBLIC (Week 5):**
- [ ] Push both projects (PM Co-pilot + domain project) to GitHub with READMEs that read like product briefs: problem, solution, architecture, results, limitations
- [ ] Write a LinkedIn post walking through your decision-making. Frame it as "I open-sourced two AI tools I built. Here's the product thinking behind them."

---

## Phase 3: AI Product Strategy + Interview Prep (Weeks 6-7)

### Week 6: Prompt Engineering for PMs + Strategy and Business Models

**AI Track:**
- [ ] * Practice prompt engineering seriously. Spend 2-3 hours using Claude/ChatGPT to:
  - Draft a PRD using structured prompts
  - Extract insights from a customer feedback dataset (real or simulated)
  - Build a decision matrix for a technical tradeoff
- [ ] Read about function calling, tool use, and structured outputs for product design
- [ ] Read: Ben Thompson, Stratechery (AI strategy essays)

**PM Track:**
- [ ] Learn outcome-based roadmapping: Read Teresa Torres or watch her talks on "outcomes over outputs"
- [ ] Exercise: Take your current work roadmap. Rewrite each item as an outcome, not a feature. "Build credit limit enforcement" becomes "Reduce overdue receivables by X% through automated credit controls."
- [ ] Read selectively: Ethan Mollick, "Co-Intelligence" (chapters on working with AI + organizational adoption)
- [ ] Optional: Arvind Narayanan & Sayash Kapoor, "AI Snake Oil" (skim for BS-detection framework)

**Build (PM Co-pilot v3 - final):**
- [ ] Polish the agent based on everything you've learned
- [ ] Add any final capabilities that make it genuinely useful
- [ ] Write a "product roadmap" for the co-pilot as if pitching to a team

**Practice Task:**
Rewrite your credit limit PRD (or a section of it, anonymized) to include: discovery evidence, outcome metrics, an eval plan for any AI-assisted components, and user segments.

**PUBLIC (Week 6):** Write and publish the strategy memo: "If I were building an AI-native shipping platform from scratch, here's what I'd build and why." 2-3 pages. Post on LinkedIn or Substack. This is your strongest written piece because it combines domain expertise with AI product vision.

### Week 7: Shipping AI Features + Interview Prep + Portfolio Assembly

**AI Track:**
- [ ] * Read: The AI Product Playbook by Dr. Marily Nika & Diego Granados. Covers the full lifecycle of shipping AI features.
- [ ] Study failure modes: hallucination, drift, latency, cost blowout. Understand product guardrails (fallbacks, confidence thresholds, human-in-the-loop).

**PM Track:**
- [ ] Learn B2B go-to-market basics: internal launch (training, documentation, rollout plan) and external launch (positioning, enablement, adoption tracking)
- [ ] Exercise: Design a rollout plan for your credit limit feature. Phased rollout? Pilot clients? What metrics trigger full launch vs. rollback?

**Build:**
- [ ] Complete the Big Tech Interview Prep section below
- [ ] Prepare 5 STAR stories

**Practice Task:**
Create a launch checklist for a hypothetical AI-assisted feature at your company (e.g., AI rate suggestions). Include: eval criteria, rollout phases, success metrics, failure handling, and a feedback loop.

**PUBLIC (Week 7):** Assemble the portfolio site (personal site, Notion page, or GitHub Pages). This is packaging, not creating. Everything is already live from Weeks 2-6. The site brings it together:
- [ ] PM Co-pilot: product brief + repo + evolution story (v0 to v3)
- [ ] Product teardown (already posted Week 2)
- [ ] Industry landscape (already posted Week 3)
- [ ] Domain capstone project (already on GitHub Week 5)
- [ ] Strategy memo (already posted Week 6)
- [ ] Capstone case study (write fresh this week)
- [ ] Start applying to roles with portfolio link

---

## Phase 4: Accelerate and Position (Week 8)

### Week 8: Synthesis + Go Public

**AI Track:**
- [ ] Revisit the AI PM Roadmap 2026. Self-assess against the skill stack. Where are you now vs. Week 1?
- [ ] Optional: Start a Maven cohort course (AI PM Certification, Agentic AI PM) for continued structured learning

**PM Track:**
- [ ] * Read: Reimagined: Building Products with Generative AI by Shyvee Shi et al. Skim for B2B and operations case studies.
- [ ] Reflect on your 8 weeks. What changed in how you approach your current features?

**Actions:**
- [ ] Publish your strategy memo on LinkedIn or Substack
- [ ] Reach out to 5 AI PMs for informational chats (cold DMs work, reference a specific thing they shipped)
- [ ] Apply to 10+ roles with your portfolio link in every application
- [ ] Share the PM Co-pilot publicly, invite other PMs to try it and give feedback

**Capstone Practice Task:**
Write a case study (2-3 pages) on one of your real features (credit limits, rate APIs, or pod board):
1. Problem: who has it, how you discovered it, evidence
2. Approach: how you designed the solution, tradeoffs, what you'd do differently
3. Metrics: what you measured, outcome vs. output metrics
4. AI opportunity: where AI could enhance this feature, eval framework, risks

This becomes a portfolio piece and proof-of-work for AI PM roles.

---

## Big Tech AI PM Interview Prep

Big tech interviews are structured rounds, not portfolio reviews. Your portfolio gets you past the resume screen. The interview itself tests live problem-solving. Here's how each round works and how to prepare.

### Round 1: Product Sense / Product Design

**What they ask:** "Design an AI feature for Google Maps." "How would you improve Alexa's shopping experience using AI?" "Build an AI product for small business owners."

**What they're testing:** Can you identify a real user problem, scope an AI solution, reason about tradeoffs, and define success?

**Framework to use:**
1. Clarify the user and context (who, when, why)
2. Identify 2-3 pain points, pick one
3. Propose a solution. Explain specifically why AI is the right tool (not just "it could use AI")
4. Define the AI architecture at a high level (is this a classification problem? generation? retrieval?)
5. Address failure modes and edge cases
6. Define success metrics (leading and lagging)

**Practice questions:**
- Design an AI feature for LinkedIn that helps recruiters write better outreach
- How would you add AI to Shopify's inventory management?
- Design an AI co-pilot for customer support agents at a B2B company
- How would you improve Google Docs with AI? What would you NOT add?

**Your edge:** Use your PM Co-pilot as a reference. "When I built my own PM co-pilot, I learned that the key decision was whether to generate from scratch or use RAG for style matching. I chose RAG because..."

### Round 2: Strategy

**What they ask:** "Should Microsoft build an AI-native CRM?" "How would you prioritize AI investments for YouTube?" "A competitor just launched an AI feature. What do you do?"

**What they're testing:** Can you think about markets, competitive dynamics, and resource allocation? Do you understand where AI creates real moats vs. commodity features?

**Framework to use:**
1. Define the strategic context (market, competition, company strengths)
2. Identify 2-3 options with tradeoffs
3. Make a recommendation with clear reasoning
4. Address risks and how to mitigate

**Practice questions:**
- Should Amazon build an AI-powered freight brokerage? (Use your shipping knowledge)
- A startup with 10 engineers wants to add AI to their B2B SaaS. How do you prioritize what to build first?
- Your AI feature is 80% accurate. Do you ship it? Under what conditions?
- How would you evaluate build vs. buy for an LLM component in your product?

### Round 3: Technical / AI Depth

**What they ask:** "Walk me through how you'd build a recommendation system." "How would you reduce hallucinations in a customer-facing AI product?" "Explain the tradeoffs between fine-tuning and RAG."

**What they're testing:** Can you collaborate with ML engineers? Do you understand enough to make good scoping decisions? They don't expect you to write code, but you need to reason about architecture.

**Key concepts you must be able to explain clearly:**
- RAG vs. fine-tuning vs. prompt engineering: when to use each
- Evals: how to define and run them, why they matter more than benchmarks
- Latency/cost/quality triangle: every AI product is a tradeoff between these three
- Hallucination management: detection, prevention, graceful degradation
- Context windows and their practical limits
- Embeddings and vector search (high level)
- Human-in-the-loop: when and how to insert human review
- Responsible AI: bias, safety, fairness considerations

**Practice questions:**
- You're building a document summarization feature. Walk me through the technical approach.
- Your AI feature's latency is 8 seconds. Users drop off after 3 seconds. What do you do?
- How would you evaluate whether your AI-generated PRDs are actually good?
- An ML engineer says fine-tuning will take 3 months. RAG can ship in 3 weeks. How do you decide?

**Your edge:** You've built RAG pipelines and MCP integrations. Use specific examples: "When I set up RAG for style-consistent PRD generation, I had to decide how to chunk reference documents and what similarity threshold to use. I learned that..."

### Round 4: Metrics / Analytical

**What they ask:** "How would you measure success for an AI writing assistant?" "Your model accuracy dropped from 92% to 87%. What do you do?" "Define a metric framework for AI-powered search."

**What they're testing:** Can you connect AI performance metrics to business outcomes? Do you understand both ML metrics and product metrics?

**Key metrics vocabulary:**
- **ML metrics:** Precision, recall, F1, accuracy, perplexity (know what they mean, not how to calculate)
- **Product metrics:** Task completion rate, time-to-value, user satisfaction, retention
- **AI-specific metrics:** Hallucination rate, eval pass rate, cost per query, latency p50/p95
- **Business metrics:** Revenue impact, support ticket deflection, NPS change

**Framework to use:**
1. Define what "success" means for the user (task completed faster? better outcome?)
2. Define leading metrics (engagement, task completion) and lagging metrics (retention, revenue)
3. Define AI quality metrics (eval pass rate, error rate)
4. Define guardrail metrics (things that should NOT get worse)
5. Explain how you'd set up an A/B test or staged rollout

### Round 5: Execution / Behavioral

**What they ask:** STAR format. "Tell me about a time you shipped something under ambiguity." "Describe a conflict with an engineer and how you resolved it." "How do you prioritize when everything is urgent?"

**Your 5 prepared STAR stories:**
1. "How I built the PM Co-pilot" - shows initiative, technical learning, product thinking
2. "How I applied AI to B2B shipping" - shows domain expertise meets AI
3. "A time I shipped under uncertainty" - from your current PM role, shows execution
4. "A time I influenced without authority" - stakeholder management, works for any PM story
5. "A time I had to make a hard tradeoff" - prioritization, saying no, data-driven decisions

**Company-specific notes:**
- **Google:** Product sense round is king. Practice "design an AI product" questions extensively. They value structured thinking and creativity. "Googleyness" = collaboration + intellectual humility.
- **Meta:** Metrics-heavy. They want you to reason about data, experimentation, and growth loops. Execution focus, ship fast.
- **Microsoft:** Technical depth matters (especially for Copilot/Azure AI roles). Enterprise customer empathy is a plus. Strategy round often involves enterprise vs. consumer tradeoffs.
- **Amazon:** Leadership Principles dominate every round. Frame every answer through 2-3 LPs. "Working Backwards" and "Customer Obsession" are table stakes. "Dive Deep" and "Bias for Action" are where AI PMs differentiate.
- **Apple:** Design-centric. Privacy as a feature, not a constraint. Less public about process but heavy on craftsmanship and user experience.

### Interview Prep Resources

- **Exponent** (tryexponent.com) - AI PM mock interviews, structured practice
- **Lewis Lin, "Decode and Conquer"** - PM interview framework, adapt to AI scenarios
- **Lenny Rachitsky, "How to get into AI PM"** - newsletter, landscape and advice
- **"Cracking the PM Interview" by Gayle McDowell** - foundational, then layer AI specifics on top
- **IGotAnOffer** (igotanoffer.com) - Google/Meta specific PM prep

### Interview Prep Schedule (within Weeks 6-7)

- **Days 1-3:** Read frameworks, internalize the round structure
- **Days 4-7:** Practice 2 product sense questions per day (write out answers, time yourself to 30 min)
- **Days 8-10:** Practice 2 technical/metrics questions per day
- **Days 11-12:** Practice STAR stories out loud (record yourself, listen back)
- **Days 13-14:** Do 2-3 mock interviews (with a friend, Exponent, or AI-assisted)

---

## Ongoing Habits (start Week 1)

- **Daily (15 min):** Read one of: Simon Willison's blog, Lenny's AI posts, or Hacker News AI threads.
- **Weekly (1 hr):** Try a new AI product. Write 2-3 bullet notes: what it does well, where it breaks, what the PM optimized for.
- **Weekly:** Use Claude/ChatGPT for at least one real PM task (PRD drafting, data analysis, competitive research).
- **Weekly:** Post at least one observation or learning on LinkedIn. Consistency > polish.
- **Bi-weekly:** Read one post from Anthropic, OpenAI, or Google DeepMind blogs.
- **Monthly:** Do a product teardown of one AI feature (Notion AI, Linear AI, Perplexity, etc.) as a PM, not a user.

---

## Book List (priority order)

| # | Book | Why | Time |
|---|------|-----|------|
| 1 | The Mom Test, Rob Fitzpatrick | Learn to talk to customers without bias | ~2hrs |
| 2 | Continuous Discovery Habits, Teresa Torres | Build the discovery muscle you're missing | ~6hrs |
| 3 | Inspired, Marty Cagan | Reframe PM work around outcomes, not output | ~8hrs |
| 4 | The AI Product Playbook, Marily Nika & Diego Granados | Ship AI features end-to-end | ~6hrs |
| 5 | Reimagined: Building Products with GenAI, Shi, Cai, Rong | Case studies and frameworks | ~8hrs |
| 6 | Obviously Awesome, April Dunford | Positioning and strategy | ~3hrs |
| 7 | Co-Intelligence, Ethan Mollick | Working with AI, organizational adoption | ~6hrs |
| 8 | AI Snake Oil, Narayanan & Kapoor | BS-detection framework | ~6hrs |

---

## Industry Snapshot (early 2026)

**Where AI PM hiring is strongest:**
- Developer tools and infrastructure
- Vertical SaaS (healthcare, legal, logistics, fintech)
- Enterprise AI platforms
- AI-native startups at Series A-B

**Your competitive advantage as a freight forwarding PM:**
- You understand complex, multi-stakeholder B2B workflows
- You've lived with messy real-world data (shipping data is notoriously unstructured)
- You can speak to ROI and business outcomes, not just "cool AI demos"
- Domain-specific AI PMs are in higher demand than generalist AI PMs
- Ops experience means you understand internal tooling, automation, and process efficiency

**What interviewers test for:**
- Can you define and run evals?
- Do you know when AI is and isn't the right solution?
- Can you scope an AI feature from "idea" to "shipped"?
- Can you work with ML engineers on tradeoffs (cost, latency, quality)?
- Have you shipped something?
- Can you think in outcomes, not just outputs?

---

## Key People to Follow

- **Lenny Rachitsky** - AI product sense, PM career advice
- **Shreyas Doshi** - Product strategy, prioritization, product sense
- **Teresa Torres** - Continuous discovery, opportunity solution trees
- **Marty Cagan** - Product leadership, outcomes over outputs
- **Simon Willison** - Best real-time coverage of what's new and what actually matters
- **Ethan Mollick** - AI adoption, organizational change, practical AI use
- **Chip Huyen** - Production ML systems, engineering-PM bridge
- **Hamel Husain** - Evals, practical LLM development
- **Eugene Yan** - Systems patterns for AI products
- **Maggie Appleton** - AI UX and interaction design
- **April Dunford** - Positioning and competitive strategy
- **Andrew Ng** - AI fundamentals, weekly AI news via The Batch newsletter
- **Ben Thompson** - AI strategy and business model analysis (Stratechery)
- **Marily Nika** - Shipping AI features end-to-end, AI Product Playbook author

## Newsletters and Blogs

**PM Fundamentals**
- Lenny's Newsletter (lennysnewsletter.com) - PM craft, career, strategy, increasingly AI-focused
- SVPG Blog (svpg.com/articles) - Marty Cagan's team on outcomes and empowered teams
- Product Talk (producttalk.org) - Teresa Torres on continuous discovery
- First Round Review (review.firstround.com) - Long-form operator stories from top startups
- Reforge Blog (reforge.com/blog) - Growth, strategy, retention frameworks
- Department of Product (departmentofproduct.com) - Curated PM articles and frameworks

**AI Product and Industry**
- Simon Willison's Weblog (simonwillison.net) - Daily practitioner-level LLM and tools coverage
- One Useful Thing (oneusefulthing.org) - Ethan Mollick's Substack on practical AI use
- The Batch (deeplearning.ai/the-batch) - Andrew Ng's weekly AI news digest
- Stratechery (stratechery.com) - Ben Thompson on AI strategy and platform dynamics
- a16z AI Blog (a16z.com/ai) - VC perspective on AI markets and architectures
- Anthropic Blog (anthropic.com/blog) - Agent design patterns, tool use, safety
- OpenAI Blog (openai.com/blog) - Frontier model releases and research
- Google DeepMind Blog (deepmind.google/blog) - Research and product-facing AI updates
- Hamel Husain's Blog (hamel.dev) - Evals and practical LLM development
- Eugene Yan's Blog (eugeneyan.com) - AI product design patterns

**B2B and Logistics**
- FreightWaves (freightwaves.com) - Freight industry news with growing AI coverage
- Supply Chain Dive (supplychaindive.com) - Concise industry updates
- The Logistics of Logistics podcast (thelogisticsoflogistics.com) - AI-focused episodes

## Communities

- **Lenny's Slack** - Paid (with newsletter sub). High-quality, active PMs at top companies
- **Mind the Product Slack** - Free. Large PM community, job postings
- **Hacker News** (news.ycombinator.com) - Filter for AI threads; comments often better than articles
- **r/ProductManagement** (Reddit) - General PM questions and calibration
- **r/artificial** and **r/MachineLearning** (Reddit) - AI industry news and discussion
- **X/Twitter** - Build a list from the people above. AI news breaks here first
- **LinkedIn PM groups** - Search "AI Product Management"; engage in comments before posting
- **AI tool Discords** (Anthropic, LangChain, etc.) - Technical depth and builder perspectives

## Websites and Publications

- Mind the Product (mindtheproduct.com) - Articles, conference talks, job board
- Product School Blog (productschool.com/blog) - Frameworks, templates, interview prep
- Pragmatic Institute (pragmaticinstitute.com) - B2B product management focus
- Exponent (tryexponent.com) - AI PM mock interviews and structured practice
- IGotAnOffer (igotanoffer.com) - Google/Meta specific PM interview prep

---

## Progress Tracker

| Week | AI Track | PM Track | Co-pilot | Public artifact | Status |
|------|----------|----------|----------|----------------|--------|
| 1 | LLM fundamentals | Discovery (Mom Test) | v0 setup | (private) | In progress |
| 2 | Product stack | Outcome metrics (CDH 1-6) | v1 evals | LinkedIn: co-pilot teardown | In progress |
| 3 | RAG & retrieval | Product strategy (CDH 7-14) | v2 domain layer | LinkedIn/Substack: shipping AI landscape | Not started |
| 4 | AI evals | Customer segmentation (Inspired) | Capstone 2 start | LinkedIn: eval framework post | Not started |
| 5 | Agentic AI + freight AI | Competitive analysis | Ship both projects | GitHub: both repos live | Not started |
| 6 | Prompt engineering + strategy | Outcome roadmapping | v3 final | LinkedIn/Substack: strategy memo | Not started |
| 7 | Shipping AI features | Go-to-market | Portfolio assembly | Portfolio site live + case study | Not started |
| 8 | Self-assessment | Synthesis | - | Outreach blitz + applications | Not started |
