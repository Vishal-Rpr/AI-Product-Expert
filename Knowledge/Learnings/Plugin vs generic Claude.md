# Plugin vs generic Claude

This compares three ways of writing the same 10 PRDs: plain Claude, the style-only RAG co-pilot ([pm-copilot](https://github.com/Vishal-Rpr/pm-copilot)), and the freight plugin ([logistics-pm](https://github.com/Vishal-Rpr/logistics-pm)).

## Overview

This is an in depth eval across 10 features aimed at evaluating the outputs from 3 separate conditions. Ten features across three conditions - plain Claude, the RAG co-pilot, and the full Claude plugin (RAG + Freight PM Module) - for a total of 30 PRDs which were ranked across a 5 dimension rubric.

The evaluation was carried out by me (human eval) as well as an LLM judge - both blind, ranked without knowing which condition the generated outputs followed.

## Model versions used

| Model version | Used for |
| --- | --- |
| Sonnet 5.5 - Medium | Generating outputs across all 30 conditions |
| Opus 4.7 - Medium | LLM judge for all conditions |

## Eval rubric

Eval was carried out across 5 key rubrics, with anchor scores in the golden data set of 1, 3, and 5 (5 being the best).

| Rubric | Goal |
| --- | --- |
| Domain accuracy | Capture deep domain use cases and nuances in the features |
| Completeness | Coverage of surface area across the entire lay of the land for the feature |
| Actionability | Measure immediate actionability / next steps charted out for engineering |
| Metric specificity | Measure coverage, baseline, target and calculation of success metrics |
| Style consistency | Compare style with source PRD in the PM's style of writing |

Link to output results - [Eval Sheet - v0](https://docs.google.com/spreadsheets/d/1XYLfQGMjEeJlcQRpNmjSYnuVZRU4C0MAmxslqUU-lus/edit?gid=909320359#gid=909320359)

## Headline result

Overall - The plugin scored **21.0**. Plain Claude scored **16.0**. The gap is **5.0** points on a 25-point total.

- **Plain Claude:** my total 16.0, judge total 23.4
- **RAG co-pilot:** my total 15.6, judge total 18.5
- **Full plugin:** my total 21.0, judge total 24.3

### Where the gap came from

- **Style** made most of the gap. I scored every plain Claude PRD a 1 for style, and the plugin **4.8**.
- **Domain accuracy** was the other real lift, from **2.8** to **4.5**.
- **Actionability** did not move with the plugin. I scored the plugin **3.0** and plain Claude **4.3**. A long PRD is not a PRD engineering can start from. The judge does the opposite. It gives actionability more weight when the document is verbose.

The judge scored the plugin **24.3** and plain Claude **23.4**. It did not see the gap. It scores the content higher, and it does not have a sharp sense of domain accuracy. The sales board example - plain Claude put an Ops persona on a sales board. I scored domain accuracy **1**. The judge scored the same PRD as a **4**.

RAG scored **15.6** for me and **18.5** for the judge. It brought in my voice. My style score went from **1.0** on plain Claude to **4.0** on RAG. Domain accuracy only moved from **2.8** to **3.2**.

### Where the LLM judge over-scored

The LLM judge tends to overscore verbose PRDs and sections. A similar tendency shows up on deep domain use cases, where the judge does not identify gaps in the domain cases covered in the PRD and ends up overscoring those documents.

The LLM calibration on **metric specificity** is in agreement with the human judgement for this exercise. Both scores are very similar on this eval rubric. Examples below:

- **Sales workload, plain Claude (Eval 5).** The PRD uses an Ops persona on a sales board and misses modes of shipping. I scored domain accuracy 1. The judge scored domain accuracy 4.
- **Rate-sheet ingestion, plain Claude (Eval 29).** Container types for different ocean containers are basic for this feature, and they are missing. I scored domain accuracy 3 and completeness 3. The judge scored both 5. Total 25 against my 14.
- **Credit limits, RAG (Eval 20).** The credit calculation leaves out unadjusted advances. I scored domain accuracy 3. The judge scored 5.
- **HTS codes, plain Claude (Eval 21).** A product needs a variant that can share one HTS code. That is missing. I scored domain accuracy 3. The judge scored 5.
- **Actionability follows length.** On the plugin set my mean is 3.0 and the judge's is 4.9. The sharp case is HTS on the plugin (Eval 23). I scored actionability 1. The judge scored 5.
- **Demurrage, RAG (Eval 10)** is the one place the judge matched the rubric. Totals tied at 15. It defined detention as the container outside the terminal past free time, and it withheld a 5 because the per-diem and dispute-window cost was missing. I scored domain accuracy 3. The judge scored 4.

## What I changed because of it

The judge was required to quote the sentence it penalised. On the credit, HTS, and rate-sheet misses it wrote "none" and scored domain accuracy 5.

## Cost and latency

The table is an estimate. Output tokens for the three PRD rows are the exported document at about 4 characters per token. The judge row is the score line, not an exported PRD. Seconds are output tokens at about 80 a second, plus about 3 seconds to start each turn.

| Scenario | Model used | Output tokens per PRD | Dollar cost per PRD | Seconds per PRD |
| --- | --- | --- | --- | --- |
| Plain Claude | Sonnet 5.5 - Medium | ~6,400 | ~$0.06 | ~85 |
| RAG Co-pilot | Sonnet 5.5 - Medium | ~1,800 | ~$0.02 | ~25 |
| Full Plugin | Sonnet 5.5 - Medium | ~4,100 | ~$0.10 | ~65 |
| LLM Judge | Opus 4.7 - Medium | ~200 | ~$0.03 | ~20 |

Notes on the cost:

- **RAG co-pilot.**
  - One Sonnet 5.5 call. The system prompt is 1,514 characters, about 400 tokens.
  - Retrieval adds 3 chunks of about 500 characters, about 400 tokens.
  - About 800 tokens of instruction per PRD.
  - Eval costs about $0.11 per 10 PRDs and is **optional** (not included in the cost above).
- **Full plugin.**
  - The eval skill is already inside the $0.10, about $0.08 across 10 PRDs. The scorecard is about $0.05 more and is not in the table. It is built into the plugin by default.

## Next steps and plan

- **Improve the golden data set.** Expand the golden data set to 30, to go further into domain expertise that can be leveraged from the plugin over regular Claude outputs.
- **Introducing a second human rater.** Get another independent domain expert to rate the outputs.
- **Re-run a sample when the model version changes.** Track and score model drift whenever there is a version upgrade in the LLM.
