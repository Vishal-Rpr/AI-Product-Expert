# Ayuda pathway (active plan)

Source: `Knowledge/Learnings/VP Product Pathway.pdf` (Malay Krishna, September 2026).
Plan window: 28 Sep 2026 to 17 Jan 2027.

This file is the pickup note for the other machine. The PDF is the source. Do the current week only.

- Weekly tracker: https://docs.google.com/spreadsheets/d/1opv196vY2AIwAVHQBfwnDmWHaOeIyHafmkO-PFn-3yg/edit
- Job list: Job Radar spreadsheet, tab **Pathway targets** (https://docs.google.com/spreadsheets/d/1g5tZ2S6GmeYYgxjIXNzYoEyw84sMIbxM7GA6_NkXcjs/edit)

## Resume here (16 Oct 2026)

Week 3 (12 to 18 Oct) is the open week: finish generating the 30 PRDs. Week 4 scoring starts 19 Oct. Do not score until the four missing condition C docs are linked.

Sheet: Scenario Run Master on the weekly tracker. That tab holds the output links. Score later on Blind rank, not on this tab and not on Eval key, because those show the condition.

Progress on 16 Oct, before the last four runs:

- Conditions A and B are done. 10 docs each. All linked. Do not regenerate them.
- Condition C has 6 docs linked: Blind IDs 2, 3, 6, 7, 9, 12.
- Condition C still needs links for Blind IDs 14 (invoicing and disputes), 18 (sales workload), 23 (HTS codes), and 25 (carrier scorecard).
- Model for every run: Sonnet 5.5.

How to finish condition C, one new Claude Desktop chat per PRD:

1. Plugin is logistics-pm, already pushed (`Updated write spec command`). Reinstall from the Desktop zip only if this machine does not have that version. The two style PRDs are inside `skills/style-matching/SKILL.md`.
2. Send `/logistics-pm:write-spec` plus the feature text only. Do not wrap it in "Generate a PRD for".
3. On every follow-up, send only: `Nothing to add. Write the PRD.`
4. Paste the PRD into the doc. Leave the plugin scorecard out.
5. Name the doc `Eval {Blind ID} - {short title}`. Short titles: Shipment tracking, Sales workload, RFQ to priced quote, Demurrage and detention, Invoicing and disputes, Carrier scorecard, HTS codes, Credit limits, LCL consolidation, Rate-sheet ingestion.

Before scoring, two linked docs still reveal the generation setup:

- Eval 2, Demurrage and detention. A non-goal says the feature does not name users, sources, systems, workflows, or latency. The integration section says "The feature text does not name any source."
- Eval 6, Shipment tracking. The overview says scope "is not specified in the feature request."

No linked C doc names the plugin, the model, or a scorecard.

Locked domain anchors, written before generation. Do not paste these into either public repo.

- Demurrage: container still at the port past free time. Clock starts at offload. Ends at pickup from the port.
- Detention: empty container not returned to the yard.
- Sales priority: a rejected quote and an unanswered RFQ both outrank an accepted quote that expired and needs a requote.
- Stage flow: Shipper Bookings, then RFQ submitted, then Quote shared, then after acceptance send the booking email, then rejected quotes if any.
- LCL score of 5 includes weight and volume, stackable and dangerous goods, and the breakeven `Cost per CBM x Total CBM occupied >= Total $ cost of the full container`.
- Carrier congestion sits next to the score and must not lower it. Shipper delay is not carrier performance.
- One HTS code can be shared. The official definition must be shown.
- Credit score of 5 includes outstanding invoices, credit notes, and ageing.

Scoring rules for Week 4: domain accuracy 1 is a false operating rule an engineer would build, 3 is correct but missing a cost or compliance consequence, 5 is correct and names the second-order economics. Completeness is not "it copied my headings." Style is voice and format, not length. A metric needs a name, a formula, and a data source. Human scores and judge scores stay in separate column blocks. If C wins completeness because the template demands more sections, say that. If domain accuracy does not move, say that too. B and C now share the same two style PRDs. C still adds the freight skill, the template, the questions, and the checklist.

Code state, already on GitHub: `Pilot build v1` at `readme and freight knowledge removed from primary copilot`. `logistics-pm` at `Updated write spec command`. Pull both on the other machine. Do not put company facts back into either public repo.

The July 2026 note in `AI PM Learning Plan.md` is the older plan. Do not mark those milestone boxes done against this pathway.

## Part 3 eval exercise

Part 3 is the pilot-project review of the two repos. The eval is the section titled "The eval you should run." It is how the co-pilot and the logistics plugin stop being a hobby and become AI PM proof. Budget in the document: two weekends, about 10 hours.

The question it answers in interviews is "how would you evaluate this?" The answer has to be what you ran, what surprised you, and what you changed. Not a theory answer.

### Step 1. Golden set

Write 10 feature prompts that span the domain and the difficulty. Use these, from the document:

| # | Feature prompt | Why it is in the set |
|---|---|---|
| 1 | Credit limit enforcement for B2B shippers | Finance plus integration. You know the right answer cold. |
| 2 | Demurrage and detention alerting | Domain-heavy. Generic tools miss the economics. |
| 3 | RFQ auto-triage by lane and mode | Core forwarding workflow. |
| 4 | Customer-facing shipment tracking page | Closest to generic SaaS. This is the control case. |
| 5 | Vendor rate-sheet ingestion | Links to the Silq AI project. |
| 6 | ISF filing reminders for US imports | Compliance. High cost of error. |
| 7 | Consolidation planning for LCL | Hard domain logic. |
| 8 | Invoice dispute workflow | Finance ops. |
| 9 | Sales rep workload dashboard | Internal tool. |
| 10 | Carrier performance scorecard | Data product. |

### Step 2. Anchors before you look at any output

Use the existing five rubric dimensions. Before generating anything, write a concrete anchor for scores 1, 3, and 5 on each dimension.

Domain accuracy example from the document:

- 1 = contains a factual error that would mislead engineers
- 3 = correct, but misses a key cost or compliance consideration
- 5 = correct, and names the second-order economics (for example, who pays demurrage and when)

Do the same for the other four dimensions. The point is that "good" is defined before you see the outputs.

### Step 3. Three conditions, 30 outputs

Run every prompt under three conditions:

- **A. Generic.** Claude with no RAG and no domain skill. This is a plain Claude call, not the co-pilot.
- **B. RAG only.** The co-pilot with style references. In the CLI that is `python -m copilot generate "<prompt>"` from `Pilot build v1`, after `python -m copilot ingest`.
- **C. Full plugin.** Domain knowledge, plus style matching, plus the template. That is the logistics-pm plugin (`/logistics-pm:write-spec`), not another flag on the CLI.

10 prompts times 3 conditions = 30 outputs. Save each output with its prompt number. Do not label the condition in the file you will score.

`--no-rag` on the co-pilot is not condition A. That flag still uses the co-pilot prompt. Condition A is Claude with none of the repo attached.

### Step 4. Score twice

- You score all 30 blind. Shuffle the outputs so you do not know which condition you are reading.
- An LLM judge scores all 30 with the same rubric and the same 1/3/5 anchors.
- Compare. Where do you and the judge agree? Where does the judge get fooled?

The document's expected finding, which you must check against your own scores rather than assume: the judge rewards length and a confident tone, and under-penalises domain errors. If that is what you see, that finding is the interview story. If it is not, report what you actually saw.

### Step 5. One-page result

Report these five things. The numbers in the PDF are examples of the shape, not targets. Use your numbers.

- Headline result. Average score of the full plugin vs generic Claude, and which dimension made the gap.
- Judge vs human agreement. How often you were within 1 point, and where the judge over-scored domain errors.
- What you changed because of it. The document's example is adding an explicit domain-error check and making the judge cite the line it penalised.
- Cost and latency. Cost and seconds per PRD, and how much the eval adds. That is why eval stays opt-in.
- What you would do next. The document's example is a golden set of 30, a second human rater, and drift tracking when the model version changes.

A modest honest gap is a valid result. If the plugin only wins by 2 points, the story is where vertical context helped and where it did not.

### When the week plan says to do each step

- Week 2 (5 to 11 Oct): write the 10 prompts and the 1/3/5 anchors.
- Week 3 (12 to 18 Oct): generate the 30 outputs.
- Week 4 (19 to 25 Oct): blind-score all 30, run the LLM judge, compare. Send Malay the first two mock answers this week, not this write-up.
- Week 5: publish Project 1 with the results in the README.

### How to say it in under 45 seconds

From Part 3, fill in your own X after you have the scores:

"I kept seeing AI tools write PRDs that sounded generic and missed the things that actually matter in freight, like surcharge stacking or who pays demurrage. So I built a RAG-based co-pilot that learns a PM's style from their past PRDs and tickets. I shipped it as a CLI first, to prove the pipeline before building any interface. Then I repackaged it as a Claude plugin with freight domain knowledge and an eval rubric weighted on domain accuracy. When I ran a blind eval across 10 features, the plugin beat generic Claude by X points, mostly on domain accuracy. The interesting finding was that the LLM judge kept over-scoring confident but wrong outputs, so I changed the rubric to force it to cite errors."
