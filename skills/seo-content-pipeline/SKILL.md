---
name: seo-content-pipeline
description: Plan, draft, score and audit SEO + GEO content for WareMatch pages (industry, blog and location pages) with NeuronWriter, cited facts, template locks and house rules. Use when asked to optimize or create a page from a keyword-map row, build a NeuronWriter query, assemble a facts file, run the score/policy gates, choose internal links, or prepare a programmatic-SEO batch. Pair with the geo-intent-audit skill for usefulness and intent checks.
---

# SEO content pipeline (WareMatch)

The unit of work is one page = one keyword-map row + a config (`configs/<slug>.json`) + a facts file (`facts/<slug>.md`) + a skeleton/template. See `PIPELINE.md` for the full design, lessons and the before/after case log.

## Setup
- Run commands from this skill's directory (scripts use relative paths; a `runs/<slug>/` folder is created locally and is git-ignored).
- Secrets live OUTSIDE the repo. `nw.py` reads `API_KEY_NEURONWRITER` from the file named by `ENV_FILE` (default `~/Desktop/WareMatch/.env`). Never print or commit keys.
- `fetch_inventory.py <sheet_id> [gid]` downloads the link-readable keyword-map tab into `site_inventory.json` (internal-link candidates).

## Stages (v2: every step exists because of a real miss; see PIPELINE.md "Failure modes -> controls")
1. **Row + live audit + GSC queries** (match the sheet row by URL; rows drift).
2. **Keyword/brief sanity**: `keyword_check.py <gsc.json> "<sheet primary>" ["<alt>"]` and the SERP intent (landlord/listing vs 3PL services) before choosing the NeuronWriter brief.
3. **Skeleton / template mode**: `check_page.py` modes `industry`, `blog` (add `--urgent` promo mode for "recommended first"), `location` (country), `state`; locked copy is checked verbatim against the live page.
4. **Facts**: primary-source only, lead re-reads every claim; unreadable PDFs and agent-only claims are excluded; never cite companies that sell warehousing/3PL/space.
5. **NeuronWriter brief**: ONE `nw.py new-query` per page with `competitors_mode` = `top-intent` (see PIPELINE.md Case 7), then `fetch_analyses.py <run>`; map briefs in the page config (`"briefs"`); defaults in `configs/_defaults.json` merge with the page skip list.
6. **Draft** (`build_prompt.py` + template) with a fresh agent, or write directly.
7. **Easy-terms sweep (mandatory)**: `optimize.py` prints basic and extended term coverage; **basic must be >= 90%** before any "ceiling" claim.
8. **Gates**: `optimize.py <run> <brief> <draft>` (score with the SHIPPING title/meta; rounded figures within 3% are accepted), `check_page.py`, `promo_check.py` (blogs), `verify_sources.py`.
9. **Human read-through**: `READTHROUGH.md` (12 checks: so-what, repetition, audience assumptions, unsupported claims, headings, WareMatch connection, links, template, sources, keyword choice, etiquette).
10. **geo-intent-audit** skill (intent, usefulness, so-what, repetition, WareMatch connection).
11. **`regress.py`** after ANY tool change: re-checks every page config.
12. **Import + sheet**: import only if the owner is not editing that brief (use read-only `evaluate-content` otherwise); fill only EMPTY sheet output cells; never overwrite owner entries.
13. **Log** the case in PIPELINE.md; `runlog.py` for time/tokens/dollars (token counts entered by hand; price per 1M tokens for claude-sonnet-5-5: input $2.00, output $10.00, cache read $0.20).

## Rules that override the score
Template lock; house metadata rules (titles <=65 with the keyword in the first 40 and "| WareMatch", descriptions <=160 with a CTA, write "3PL"); education-first blogs with WareMatch as one option; no competitor names or rankings; no invented or uncited numbers; authored content must be in the initial HTML.
