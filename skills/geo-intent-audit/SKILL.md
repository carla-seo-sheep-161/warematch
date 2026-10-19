---
name: geo-intent-audit
description: Audit a drafted or live page for deep GEO relevance, search-intent match and real usefulness to the reader, beyond the surface NeuronWriter/SEO score. Use after a draft passes the pipeline gates (or on a live page) when asked to evaluate utility, intent coverage, AI-answer (GEO) extractability, specificity/expertise, trust, or whether a page would actually be cited or useful. Companion to the seo-content-pipeline skill.
---

# GEO + intent + utility audit

Purpose: the pipeline's NeuronWriter gate measures term coverage. It does not tell you whether the page answers what searchers actually want, whether an AI engine could lift a clean answer from it, or whether it says anything an expert would call useful. This skill does, with evidence.

## Inputs
- the page (HTML-in-markdown draft, or a live URL fetched to text)
- `queries.txt`: one query per line = sheet long-tail queries + the primary/secondary keywords + NeuronWriter people-also-ask / topic_matrix questions + real GSC / SEO Gets queries for the page (include the conversational, LLM-style ones: they show how AI engines fan out)
- page type (location | industry | blog), primary keyword, the NW analysis JSON (SERP intent mix, competitor headings, entities), the facts file, the title/meta that will ship

## Process
1. **Gather queries** (never invent them). Note the SERP intent mix and content types from the NW `serp_summary`.
2. **Run the deterministic checks** (local, no network, no LLM, no embeddings):
   `python3 -I skills/geo-intent-audit/scripts/audit.py <draft> --queries queries.txt --primary "<kw>" --type <type> --title "<T>" --desc "<D>" --entities <analysis.json>`
   It reports query coverage, answer-first / passage self-containment, specificity per section (flags INTERCHANGEABLE sections), uncited figures, freshness, promo ratio, repetition, schema readiness, and the house metadata rules (title <=65, description <=160, keyword in first 40 chars, "| WareMatch", write "3PL", CTA).
3. **Apply the judged rubric** in `rubric.md` yourself, quoting the page for every score (intent fit, decision utility, information gain vs the SERP, location swap-test, trust, differentiation, house-rule compliance).
4. **Optional live check** (only for published pages): fetch the raw HTML and confirm the H1, TL;DR and key sections exist WITHOUT JavaScript (AI crawlers often do not run JS; the team's own audit found rendered-vs-initial HTML mismatches and listings hidden behind a click that LLMs never see).
5. **Report**: scorecard (0-5 per dimension with evidence), the 5 highest-value fixes ranked by reader impact, what data/expert input each fix needs, and open decisions for the owner. Be blunt: say when a section is interchangeable with any 3PL page.

## Rules
- Do not call external LLM or embedding APIs (e.g. the Gemini key) with page content unless the owner approves; the local lexical checks are v1.
- Never fabricate numbers, sources or queries. Mark anything unverified.
- Never rank or name competitors in suggested fixes; stay agnostic.
- Scores are judgements with evidence, not predictions of ranking or citation.
- Log the audit result (before/after) in the pipeline case log; feed fixes back as tasks, not silent rewrites.
