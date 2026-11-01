# Plugin vs generic Claude

This compares three ways of writing the same 10 PRDs: plain Claude, the style-only RAG co-pilot ([pm-copilot](https://github.com/Vishal-Rpr/pm-copilot)), and the freight plugin ([logistics-pm](https://github.com/Vishal-Rpr/logistics-pm)).

## Overview

Ten features, three conditions, 30 PRDs. Each PRD was ranked on a 5-dimension rubric.

I scored them, and so did an LLM judge. Both were blind to which condition produced the PRD.

## Model versions used

| Model version | Used for |
| --- | --- |
| Sonnet 5.5 - Medium | Generating all 30 PRDs |
| Opus 4.7 - Medium | LLM judge for all 30 |

## Eval rubric

Five rubrics, with anchor scores of 1, 3, and 5. 5 is best.

| Rubric | Goal |
| --- | --- |
| Domain accuracy | Capture domain use cases and nuances |
| Completeness | Cover the surface area of the feature |
| Actionability | Chart next steps an engineer can start from |
| Metric specificity | Coverage, baseline, target, and calculation of success metrics |
| Style consistency | Match the source PRD and the PM's writing style |

## Headline result

The plugin scored **21.0**. Plain Claude scored **16.0**. The gap is **5.0** points on a 25-point total.

- **Plain Claude:** my total 16.0, judge total 23.4
- **RAG co-pilot:** my total 15.6, judge total 18.5
- **Full plugin:** my total 21.0, judge total 24.3

### Where the gap came from

- **Style** made most of the gap. I scored every plain Claude PRD a 1 for style, and the plugin **4.8**.
- **Domain accuracy** was the other real lift, from **2.8** to **4.5**.
- **Actionability** did not move with the plugin. I scored the plugin **3.0** and plain Claude **4.3**. A long PRD is not a PRD engineering can start from. The judge does the opposite. It gives actionability more weight when the document is verbose.

The judge scored the plugin **24.3** and plain Claude **23.4**. It did not see the gap. It scores the content higher, and it does not have a sharp sense of domain accuracy. On the sales board, plain Claude put an Ops persona on a sales workflow. I scored domain accuracy **1**. The judge scored the same PRD a **4**.

RAG scored **15.6** for me and **18.5** for the judge. It brought in my voice. My style score went from **1.0** on plain Claude to **4.0** on RAG. Domain accuracy only moved from **2.8** to **3.2**.

### Where the LLM judge over-scored

- **Sales workload, plain Claude (Eval 5).** The PRD uses the wrong persona for the board and misses modes of shipping. I scored domain accuracy 1. The judge scored 4.
- **Rate-sheet ingestion, plain Claude (Eval 29).** A basic field for this feature is missing. I scored domain accuracy 3 and completeness 3. The judge scored both 5. Total 25 against my 14.
- **Credit limits, RAG (Eval 20).** The credit calculation leaves out a component. I scored domain accuracy 3. The judge scored 5.
- **HTS codes, plain Claude (Eval 21).** A catalog case is missing. I scored domain accuracy 3. The judge scored 5.
- **Actionability follows length.** On the plugin set my mean is 3.0 and the judge's is 4.9. The sharp case is HTS on the plugin (Eval 23). I scored actionability 1. The judge scored 5.
- **Demurrage, RAG (Eval 10)** is the one place the judge matched the rubric. Totals tied at 15. It withheld a 5 because a cost consequence was missing. I scored domain accuracy 3. The judge scored 4.

## What I changed because of it

The judge was required to quote the sentence it penalised. On the credit, HTS, and rate-sheet misses it wrote "none" and scored domain accuracy 5.

## Cost and latency

The table is an estimate, not an API invoice, and the runs were not timed. Output tokens for the three PRD rows are the exported document at about 4 characters per token. The judge row is the score line, not an exported PRD. Dollars are the public list price with no prompt caching. Seconds are output tokens at about 80 a second, plus about 3 seconds to start each turn.

| Scenario | Model used | Output tokens per PRD | Dollar cost per PRD | Seconds per PRD |
| --- | --- | --- | --- | --- |
| Plain Claude | Sonnet 5.5 - Medium | ~6,400 | ~$0.06 | ~85 |
| RAG Co-pilot | Sonnet 5.5 - Medium | ~1,800 | ~$0.02 | ~25 |
| Full Plugin | Sonnet 5.5 - Medium | ~4,100 | ~$0.10 | ~65 |
| LLM Judge | Opus 4.7 - Medium | ~200 | ~$0.03 | ~20 |

Notes on the cost:

- **RAG co-pilot.** One Sonnet 5.5 call. The system prompt is 1,514 characters, about 400 tokens. Retrieval adds 3 chunks of about 500 characters, about 400 tokens. About 800 tokens of instruction per PRD. The built-in eval costs about $0.11 for 10 PRDs. It is optional, and it is not included in the cost above.
- **Full plugin.** The eval skill is already inside the $0.10, about $0.08 across 10 PRDs. The scorecard is about $0.05 more and is not in the table. It is built into the plugin by default.

## Next steps

- Expand the golden data set, so domain checks are explicit rather than left to the judge's general sense of the domain.
- Get a second human rater.
- Re-run a sample when the model version changes.
