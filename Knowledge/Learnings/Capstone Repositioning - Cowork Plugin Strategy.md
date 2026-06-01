# Capstone Repositioning: From CLI Co-pilot to Cowork Plugin

**Date:** June 1, 2026

---

## Context shift

Anthropic launched Claude Cowork (Jan 2026) and knowledge-work-plugins (18.5k stars) with an official **product-management plugin**. The generic "PM co-pilot" space is now officially occupied. Our capstone needs to differentiate.

Claude Design (April 2026) also launched — a visual creation tool for prototypes, slides, one-pagers. Relevant for our prototype workflow but not a direct competitor to the co-pilot.

---

## What Anthropic's PM plugin does

- Write specs, plan roadmaps, synthesize user research
- Keep stakeholders updated, track competitive landscape
- Connectors: Slack, Linear, Asana, Monday, ClickUp, Jira, Notion, Figma, Amplitude, Pendo, Intercom, Fireflies
- Architecture: `skills/` (auto-fire), `commands/` (explicit slash commands), `.mcp.json` (connectors)
- All file-based: markdown and JSON, no code

---

## What it DOESN'T do (our gaps to fill)

1. **RAG-based style matching** — No personalized output. Uses generic frameworks/templates. Can't learn YOUR writing voice from reference docs.
2. **Domain specificity** — Generic PM workflows. No freight/logistics knowledge (RFQ analysis, BOL processing, rate comparison, credit risk, customs compliance).
3. **Eval frameworks** — No mechanism for measuring output quality. No "is this PRD good enough?" system.

---

## Repositioned capstone: Domain-specific Cowork plugin with evals

### What we're building

A Cowork plugin for logistics/supply-chain PMs that adds:
1. Freight-domain skills (RFQ analysis, rate benchmarking, credit risk assessment, BOL processing workflows)
2. RAG-based style matching from reference documents (our original differentiator)
3. An eval layer for measuring output quality (the gap nobody's filled)

### Architecture (follows Anthropic's plugin structure)

```
logistics-pm-plugin/
├── .claude-plugin/plugin.json   # Manifest: name, description, version
├── .mcp.json                    # Connectors: Linear, your rate APIs, QuickBooks
├── commands/
│   ├── write-spec.md            # /logistics-pm:write-spec
│   ├── rfq-analysis.md          # /logistics-pm:rfq-analysis
│   ├── rate-comparison.md       # /logistics-pm:rate-comparison
│   └── credit-assessment.md     # /logistics-pm:credit-assessment
├── skills/
│   ├── domain-knowledge.md      # Freight terminology, workflows, industry context
│   ├── style-matching.md        # RAG instructions for matching user's writing voice
│   ├── eval-framework.md        # Quality rubrics for generated artifacts
│   └── prd-generation.md        # PRD skill with domain-specific sections
└── reference-docs/              # Example PRDs, user stories for RAG style matching
```

### How this maps to what we already have

| What we built | What it becomes in the plugin |
|---|---|
| AGENTS.md instructions | `skills/domain-knowledge.md` + `skills/style-matching.md` |
| Reference PRDs in Knowledge/ | `reference-docs/` for RAG style matching |
| Linear MCP integration | `.mcp.json` connector config |
| Task creation format | `commands/write-spec.md` slash command |
| Sample user story template | `reference-docs/` example |

---

## Interview narrative

"Anthropic released a product-management plugin with their Cowork launch. I identified two gaps: it doesn't handle domain-specific PM work, and it has no quality measurement system. I built a plugin that adds freight/logistics domain skills and an eval framework for measuring output quality. The architecture follows their open-source plugin spec, so it's compatible with the ecosystem. Along the way, I made specific architectural decisions — RAG over fine-tuning for style matching, ChromaDB for local vector search, Sonnet 4.6 for cost-quality balance — and I can walk you through the tradeoffs."

---

## Key references

- Anthropic knowledge-work-plugins: https://github.com/anthropics/knowledge-work-plugins
- Product-management plugin: https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management
- Plugin management (scaffolding): https://github.com/anthropics/knowledge-work-plugins/tree/main/cowork-plugin-management
- Our landscape research: `Knowledge/Learnings/PM Copilot Landscape & Architecture.md`

---

## Next steps

1. Clone the knowledge-work-plugins repo and study the product-management plugin structure in detail
2. Scaffold our logistics-pm-plugin following their architecture
3. Write 2-3 domain skills (start with PRD generation + credit risk assessment)
4. Design the eval rubric (completeness, style consistency, domain accuracy, actionability)
5. Test against our existing reference PRDs
6. Publish to GitHub with a README that reads like a product brief
