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

## Stages
1. **Row + audit**: match the sheet row by URL (rows drift); fetch the live page; pull GSC/SEO Gets queries for the page.
2. **Skeleton**: locked template (industry, location templates in `templates/`) or, for blogs, one inferred from SERP headings + long-tail queries and approved by a human.
3. **Facts**: every number current, cited, and read at the PRIMARY source into `facts/<slug>.md` (grade A/B/C, dates, re-verify-by). Never cite competitors. Agent-supplied claims are re-read by the lead before use.
4. **NeuronWriter**: `nw.py new-query` (one mode by default; modes differ little), `fetch_analyses.py`. Build the term skip-list for competitor boilerplate.
5. **Draft** with `build_prompt.py` + `templates/prompt_template.md` (fresh agent).
6. **Gate**: `optimize.py <run> <mode> <draft>` (score with the SHIPPING title/meta, term ranges, numbers vs facts), `check_page.py <draft> <industry|blog|location>` (template lock, no emoji, link rules), `promo_check.py` (blogs: education first, brand late and once, no superlatives), `verify_sources.py`, `suggest_links.py` (candidates; final choice is judgement; max 5).
7. **Human read-through** (required): agents add filler and unsupported lines to reach a score; cut them.
8. **Audit**: run the `geo-intent-audit` skill (intent coverage, extractability, specificity, locality swap-test).
9. **Import** to NeuronWriter, log before/after in `PIPELINE.md`, then publish and annotate (SEO Gets) only with owner approval.

## Rules that override the score
Template lock; house metadata rules (titles <=65 with the keyword in the first 40 and "| WareMatch", descriptions <=160 with a CTA, write "3PL"); education-first blogs with WareMatch as one option; no competitor names or rankings; no invented or uncited numbers; authored content must be in the initial HTML.
