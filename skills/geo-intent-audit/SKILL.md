---
name: geo-intent-audit
description: GEO check for on-site content. Audits a drafted or live page for search-intent fit, real usefulness (non-commodity content), AI-answer readiness (crawler access, raw-HTML visibility, snippet controls, clean visible sourcing) and technical on-page health (metadata rules, structured data hygiene, headings). Use after a draft passes the content pipeline gates, or on any live WareMatch page, when asked to run a GEO check, evaluate utility or intent coverage, check whether AI search can read/cite a page, or audit metadata/schema against the team's SEO audit docs. Companion to the seo-content-pipeline skill.
---

# GEO check (geo-intent-audit) v1.0

## What the evidence says (read this first; see references/INDEX.md)
- Google's own guide (updated 2026-07-10): optimizing for generative AI search "is still SEO". Its main lever is **unique, non-commodity content**, meaning "unique expert or experienced takes that go beyond common knowledge". It says you do not need to chunk content, create llms.txt, add special schema, or write differently for AI.
- So this skill weights **usefulness and eligibility** (indexed, snippet-eligible, readable without JavaScript, bots not blocked) far above any "AI trick". Schema, llms.txt, word counts and "ideal passage length" are hygiene or unproven, never reported as lift.
- Research on specific tactics (quotations, statistics, citations, answer-first, self-contained passages) is mixed and comes from generic QA benchmarks, not 3PL/B2B pages. Treat those items as quality practice graded C, not guarantees.

## Three layers
1. **Technical on-page** (`scripts/technical_check.py <url> --type location|industry|integration|blog|listing|home --primary "<kw>" [--must "text|text"]`). Fetches RAW HTML (no JavaScript): visible text, H1/heading order, metadata vs the team's rules (title <=65, description <=160, keyword in first 40, "| WareMatch", write "3PL", no "...", canonical, robots, Open Graph), snippet controls (nosnippet / max-snippet / data-nosnippet / X-Robots-Tag), JSON-LD hygiene (script-block count, duplicate @id, expected types, breadcrumb URL = page URL, no empty ratings/"N/A" prices, no invalid types such as LogisticsBusiness, FAQ schema matches visible text), alt text, robots.txt rules for AI bots (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Google-Extended, Bingbot, Googlebot), llms.txt (informational), freshness signals.
2. **Content checks** (`scripts/audit.py <draft> --queries queries.txt --primary "<kw>" --type <t> --title T --desc D --entities <nw analysis.json>`). Local only: query coverage (fan-out style), answer-first and self-contained passages, per-section specificity (flags INTERCHANGEABLE sections), decision aids (red flags / good answers), uncited figures and figures without a period, promo ratio, repetition, keyword-stuffing density, hype words, quote attribution, schema readiness, entity coverage.
3. **Judged rubric** (`rubric.md`): the model scores intent fit, non-commodity information gain, decision utility, locality swap-test, trust and house rules, quoting the page for every score and stating the evidence grade.

## Process
1. Gather queries (sheet long-tail, keywords, GSC / SEO Gets incl. conversational LLM-style queries, NeuronWriter people-also-ask / topic matrix). Never invent queries.
2. Run technical_check on the live URL (or skip for unpublished drafts) and audit.py on the draft.
3. Apply rubric.md; compare with the SERP (NeuronWriter competitor headings, serp_summary) for information gain.
4. Report: scorecard (0-5 + evidence + grade), INTERCHANGEABLE sections, technical FAIL/WARN list with the doc/source behind each, top-5 fixes ranked by reader impact, data or expert input each fix needs, owner decisions. Be blunt.
5. Log before/after in the pipeline case log; send fixes back as tasks.

## Rules
- Evidence grades: A = primary official source; B = original-data study by the publisher; C = academic/benchmark by analogy; D = marketing/unverified (never cite as a requirement).
- No external LLM/embedding API calls with page content unless the owner approves.
- Never fabricate numbers, sources, queries or dates; never recommend fake "last updated" dates.
- Never name or rank competitors in fixes.
- Do not report schema, llms.txt, chunk length or word count as GEO lift. Do not penalize a page for lacking them.
- The checkers are heuristics. Raw-HTML tests show what a non-rendering crawler sees; Googlebot does render JavaScript, other AI crawlers are unconfirmed (third-party 2024 study says no), so "content in the initial HTML" is a prudent default, not a proven rule.

## Known limits
Lexical coverage only; locked template copy inflates promo/uncited counts; no AI-citation testing tool; cross-script-block JSON-LD merging behavior is unverified; no study covers 3PL/B2B/location pages.
