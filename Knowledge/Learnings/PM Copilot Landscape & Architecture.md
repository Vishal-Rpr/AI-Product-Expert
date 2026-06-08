# PM Co-pilot Landscape & Architecture Research

**Date:** May 31, 2026

---

## Competitive Landscape: PM Co-pilots (May 2026)

### Open-Source Projects

| Project | Stars | What it does | Key Insight |
|---------|-------|-------------|-------------|
| **phuryn/pm-skills** | 6.7k | 65+ agentic skills, 36 chained workflows for Claude Code | Encodes Teresa Torres, Cagan, Olsen frameworks into structured prompts. A masterclass in prompt engineering for PM workflows. |
| **PM Agent OS** (deepeshgupta12) | 7 | 16 built-in agents, full PM lifecycle | Full-stack: FastAPI + PostgreSQL + pgvector. Overkill for a single PM but shows what enterprise looks like. |
| **The Last PM** (JDAmiri) | 3 | 62+ expert agents, "Chief of Staff" | Runs inside Cursor/Claude. Deterministic, anti-hallucination OS. McKinsey-style strategy framing. |
| **PM Copilot by Product Faculty** | 39 | 65 skills, 8 sub-agents, slash commands | Plugin for Claude Code. MCP connectors to Linear, Jira, Notion. Linked to their Maven AI PM certification. |

### Paid SaaS Tools

| Tool | What it does | Pricing | Gap |
|------|-------------|---------|-----|
| **ChatPRD** | Conversational PRD generation, integrations with Linear/Notion/Slack | $30+/month | No style matching. Generic templates. |
| **Keeborg** | 8-document spec package in 90 seconds (PRD, API spec, DB schema, CLAUDE.md) | Paid | Developer-focused, not PM workflow. |

### Key Takeaway

None of the existing tools do RAG-based style matching from your own reference documents. They all use generic frameworks or fixed templates. Our co-pilot's differentiator is learning YOUR writing voice.

---

## pm-skills Prompt Architecture (phuryn)

### Structure

Every skill is a self-contained folder:
```
skills/create-prd/
  SKILL.md              <- main instructions
  references/
    TEMPLATE.md         <- output structure
    EXAMPLE.md          <- concrete example of good output
```

### SKILL.md Format

Two parts:
1. **YAML frontmatter** - `name` and `description` (the trigger for when AI fires this skill)
2. **Markdown body** - purpose, context, step-by-step instructions, output format

### Design Patterns

| Pattern | What it does | Example |
|---------|-------------|---------|
| Role assignment | Tells the AI WHO it is | "You are an experienced product manager..." |
| `$ARGUMENTS` variable | Placeholder for user input | "...creating a PRD for $ARGUMENTS" |
| Structured output template | Defines exact sections | 8-section PRD with specific headings |
| Thinking instructions | Forces step-by-step reasoning | "Before writing, analyze: What problem..." |
| Accessibility constraint | Controls tone | "Write for a primary school graduate" |
| Save instruction | Tells AI what to do with output | "Save as PRD-[product-name].md" |

### Example: create-prd skill

8-section template: Summary, Contacts, Background, Objective (SMART OKRs), Market Segments, Value Propositions (Value Curve framework), Solution (UX/Features/Tech/Assumptions), Release Plan.

### Example: opportunity-solution-tree skill

Based on Teresa Torres' Continuous Discovery Habits. 4-level structure:
1. Desired Outcome (measurable metric)
2. Opportunities (customer needs, framed as "I struggle to...")
3. Solutions (3+ per opportunity, Product Trio ideation)
4. Experiments (assumption testing: Value, Usability, Viability, Feasibility)

Uses Opportunity Score: Importance x (1 - Satisfaction).

---

## Our Co-pilot vs. pm-skills Approach

| pm-skills pattern | Our equivalent | Difference |
|-------------------|----------------|------------|
| YAML frontmatter (name, description) | AGENTS.md identity and rules | Same concept, different format |
| Fixed template in SKILL.md | `prompts.py` system prompts | We use dynamic RAG retrieval instead of static templates |
| `$ARGUMENTS` placeholder | Click CLI `topic` argument | Same concept |
| `references/TEMPLATE.md` | RAG-retrieved chunks from user's docs | Ours is personalized, theirs is generic |
| Step-by-step thinking instructions | System prompt: "Match the structure, heading style, and tone..." | Similar |

---

## Claude API Pricing (May 2026)

### Per 1M Tokens

| Model | Input | Output | Context | Best for |
|-------|-------|--------|---------|----------|
| Haiku 4.5 | $1.00 | $5.00 | 200K | Simple tasks, classification, extraction |
| **Sonnet 4.6** (our choice) | $3.00 | $15.00 | 1M | Best quality-to-cost ratio |
| Opus 4.7 | $5.00 | $25.00 | 1M | Complex reasoning, deep research |

### Cost Estimates for Our Co-pilot

Typical PRD generation: ~2K input tokens + ~2K output tokens

| Model | Cost per PRD | 50 PRDs/month | 200 PRDs/month |
|-------|-------------|---------------|----------------|
| Haiku 4.5 | $0.012 | $0.60 | $2.40 |
| Sonnet 4.6 | $0.036 | $1.80 | $7.20 |
| Opus 4.7 | $0.060 | $3.00 | $12.00 |

### Cost Levers

| Technique | Savings | How |
|-----------|---------|-----|
| Prompt caching | 90% on cached input | Reuse system prompt across calls |
| Batch API | 50% on everything | Async processing within 24hr window |
| Model routing | 3-5x | Haiku for simple tasks, Sonnet for PRDs, Opus only when needed |

### Key Insight for Interviews

Output tokens cost 5x input across all models. PRD length matters more than prompt length for cost. At personal use (5-20 PRDs/week), Sonnet costs under $2/month. The cost conversation only matters at production scale (thousands of users).

---

## Architecture Decisions (for interview storytelling)

| Decision | What we chose | Why | Alternative considered |
|----------|--------------|-----|----------------------|
| Style matching | RAG from reference docs (PRDs + tickets with doc_type filtering) | Personalized output without fine-tuning cost/complexity | Fine-tuning (too expensive, needs hundreds of examples) |
| Vector store | ChromaDB (local) | Zero infrastructure, pip install only, good for personal tool | Pinecone/Weaviate (cloud, overkill for single user) |
| Embedding model | all-MiniLM-L6-v2 (via ChromaDB default) | Free, local, fast, good enough for document similarity | OpenAI embeddings (better quality but adds API cost) |
| LLM | Claude Sonnet 4.6 | Best quality-to-cost for structured generation | Haiku (cheaper but lower quality), Opus (better but 67% more expensive) |
| Interface | CLI (Click) | Simplest path to working product | Web UI (more impressive demo but 10x build time) |
| Ticket creation | Linear GraphQL + Jira REST API v3 | Dual-target support covers most PM workflows | Single integration (limits audience) |
| Publishing | Confluence REST API v2 | Lightweight markdown-to-storage converter, no heavy SDK | Google Docs API (planned as upcoming, heavier auth flow) |
| Diagram export | Excalidraw JSON output | Open format, PMs can edit diagrams after generation | Mermaid (less interactive), image export (not editable) |
| Integration pattern | Lightweight REST clients (no SDKs) | Minimal dependencies, easy to audit, portable | Official SDKs (heavier, version lock-in) |

### Current capabilities (as of June 2026)

- **PRD generation**: RAG-powered, style-matched from reference_docs/ (filtered by doc_type=prd)
- **Ticket generation**: RAG-powered style matching from reference_tickets/ (doc_type=ticket), output to Linear or Jira
- **Diagram generation**: Excalidraw JSON export for architecture and flow diagrams
- **Publishing**: Confluence page creation with markdown-to-storage conversion
- **Eval framework**: Designed (5 dimensions, 1-25 scoring) but CLI command not yet built

### Upcoming

- Eval CLI command (copilot eval PRD.md + --eval flag on generate)
- Google Docs publishing target
- Interactive mode (chat-style PRD refinement)
- pytest test suite for RAG pipeline
