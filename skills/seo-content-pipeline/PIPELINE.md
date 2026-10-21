# Content optimization pipeline (industry / landing pages)

Built on the Shopify 3PL page (2026-10-15). Everything is parameterized so a programmatic-SEO run is: new config.json + new facts file + new skeleton → same scripts.

## Inputs per page
| Input | Where | Notes |
|---|---|---|
| Keyword row | Google Sheet `site_keyword_map` (find the row by URL; row numbers drift, e.g. the Shopify URL is row 42, not 74) | cols: Page URL, H1, Primary KW [SV], Secondary KWs [SV], Long-tail queries |
| Skeleton | `templates/skeleton_*.md` | generic = `industry_page_temp.md`; page-specific = annotated skeleton showing content type per section |
| Facts file | `facts/<slug>.md` | **verified** numbers + source URLs, split EXTERNAL (linked, nofollow) / INTERNAL (WareMatch claims, hedge wording) |
| Config | `configs/<slug>.json` | URL, H1, primary/secondary/long-tail, skeleton path, facts path, known problems of current page |
| NeuronWriter key | `API_KEY_NEURONWRITER` in `~/Desktop/WareMatch/.env` (never echoed) | Gold plan+; each `/new-query` uses 1 analysis credit |

## Steps
1. **Audit current page** (WebFetch): note repeated phrases, CTAs, missing stats → goes into config `existing_problems`.
2. **Pull keyword row** from the sheet (match on URL).
3. **Fact research** (WebSearch + WebFetch on the primary source). Rules: only primary/authoritative sources (gov, trade bodies, platform's own docs); fetch the page and confirm the number before writing it to the facts file; record date. Need ≥2 EXTERNAL facts per page. Competitor marketing pages are never cited. If a primary URL 404s (Census PDF did), cite an official mirror (FRED).
4. **NeuronWriter queries** — `nw.py new-query` ×3 on the same keyword with `competitors_mode` = `top10`, `top30`, `top-intent` (project `d18ee15696efff53`, engine `google.com`). Then `fetch_analyses.py <run>` polls `/get-query` until ready (~60s) → `runs/<slug>/analysis_<mode>.json`.
   - Observed: SERP competitor table is the same 28 rows across modes; modes change the *term/entity/H2 recommendations* and readability target (top10/intent 40, top30 38). Word target was 2088 in all.
5. **Build prompts** — `build_prompt.py <run> <mode> <config>` fills `templates/prompt_template.md` ({{PLACEHOLDERS}}) → `prompt_<mode>.md`.
6. **Draft** — each prompt is run in a fresh agent (no shared context) → `draft_<mode>.md` (page, claims table, title, meta).
7. **Compare/QA** — `compare.py <run>`: NeuronWriter `/evaluate-content` score (no credit use), repeated-trigram count (repetition proxy), external links all `rel="nofollow"`, number count. Then human check of the claims table against the facts file.
8. **Score gate + optimize loop** — `optimize.py <run> <mode> [draft]` scores the draft against the SERP and writes `gaps_<mode>.md` (under/over-used terms vs Neuron ranges, missing H2 terms and entities, numbers not in the facts file). **Gate to pass: score >= max(top-10 SERP median + 2, 60); no term above its suggested max; zero numbers outside the facts file; >=2 external links all nofollow.** If REVISE, a fresh agent rewrites using the gaps brief (max 3 rounds) → `draft_<mode>_r<N>.md`. Realism rules: add terms only where they read naturally, never exceed the max, no competitor brand names as terms, no new facts (missing facts → add to facts file with a verified source first, or leave out), new sections allowed only if they add new information.
9. **Pick winner, publish** (human), then log result. Optionally `/import-content` the winner into the NeuronWriter query so the score/history lives there (not done automatically).

## Template lock (non-negotiable; pages are built from the template)
Only the skeleton's H2s, in order, with its H3/sentence slot sizes. Extra content goes *inside* slots (the free-form integration section, FAQ answers, longer sentences), never as new H2s. `check_page.py` enforces: H2 sequence, no emoji/emoji entities, no links in TL;DR/Key Takeaways, <=5 unique internal links all present in the site inventory, >=2 external links all `rel="nofollow noopener"`. It is part of the `optimize.py` gate. Icons are placeholders (`<i class="icon icon-NAME" aria-hidden="true">`); no emoji. H3s are descriptive, never "Issue 1". TL;DR/section intros carry concrete decision details, not general market stats.

## Internal linking (max 5 per page)
1. `fetch_inventory.py` pulls the full `site_keyword_map` tab (public CSV export by tab gid) -> `site_inventory.json` (677 URLs: industry, integration, blog, encyclopedia, location pages).
2. `suggest_links.py <draft> <self_url>` lists candidate pages whose distinctive concepts appear in body sentences (skips TL;DR/takeaways, existing links). It is a heuristic: it surfaced multi-channel, TikTok, reverse-logistics and connect/shopify but MISSED wholesale and apparel, so the final pick is a semantic judgement over the inventory H1s, not the script alone.
3. Choose <=5: required skeleton link first, then the best natural reframings (e.g. "wholesale orders" -> /fulfilment/b2b-wholesale), spread across sections, descriptive anchors, one per target. `check_page.py` validates.

## External source sourcing + vetting
Where they come from: WebSearch to find candidates, then WebFetch on the *primary* page. Admit a source only if (a) it is the originator of the figure (trade body, government data, the platform's or company's own page), not a blog repeating it; (b) the exact wording/figure was read on that page and logged in `facts/<slug>.md` with the date; (c) it supports the specific claim it sits next to. Never link a competitor's marketing page. `verify_sources.py <draft>` re-checks every external link: HTTP 200, tier (1 = gov/trade body/data series, 2 = platform/company primary, 3 = other: avoid), nofollow present, and that the figures near the link appear on the page. Known limits: it cannot confirm context (a figure can appear on a page for another reason), and JS-heavy pages (FRED) time out, so those are confirmed by hand fetch. Example catch (2026-10-15): a blog-derived claim that Shopify "sold" its Fulfillment Network was replaced after fetching Flexport's own announcement, which says Flexport acquired the assets of Shopify Logistics incl. Deliverr and that services run "in the merchant-facing Shopify Fulfillment Network app" (the network was NOT shut down).

## Guardrails baked into the prompt (the two big concerns)
- *Repetition*: one new point per section; no stat/claim reused; CTA ≤2 mentions; no keyword repeated in consecutive headings.
- *No hard facts*: the writer may only use numbers from the facts file; INTERNAL claims must be hedged; output includes a claim→source table for review.
- *Credibility*: ≥2 external links with `rel="nofollow noopener"`, each beside its claim.

## For programmatic SEO later
- Loop over sheet rows → generate `config` + skeleton choice; facts file is the only manual step (could be a per-industry facts library with a freshness date and re-check after ~6 months).
- Cache by `(keyword, mode)`; `/list-queries` (tags) avoids re-spending credits.
- Add: schema (FAQPage) generation from the FAQ block, link-checker for externals, and Neuron score threshold gate before human review.

## Files
`nw.py` API client · `fetch_analyses.py` · `build_prompt.py` · `compare.py` · `check_page.py` · `fetch_inventory.py` · `suggest_links.py` · `verify_sources.py` · `optimize.py` · `templates/` · `facts/` · `configs/` · `runs/<slug>/` (query_*.json, analysis_*.json, prompt_*.md, draft_*.md)

## Blog mode (no template)
- **Editorial rule: education first, WareMatch as one option, never the only option, non-biased.** The article must fully answer the reader's problem without WareMatch. WareMatch appears once, late (after ~60% of the body), in one clearly labeled section for readers who hit specific problems (no time, no known providers), framed as "one way", never "the only/best/fastest".
- Include a fair alternatives comparison (e.g. broker, direct to landlord/operator, other marketplaces, 3PL, short-term space) with "best when / watch for" for each, including cases where WareMatch is not the best fit.
- WareMatch's own numbers are hedged and attributed ("typically"), or left out of the educational sections. Comparative claims about other routes need a vetted source.
- Skeleton is inferred from SERP competitor headings (`analysis_*.json` -> competitors[].headers) + the sheet's long-tail queries, then approved by a human before drafting.
- Gate adds `promo_check.py` (brand share, first-mention position, one promo H2 max, no superlative/exclusive claims, >=3 named alternatives, repeated promo patterns <=2). Refresh pages also get a before/after diff and a GSC baseline (position, impressions).

## Fact freshness + source-quality policy (numbers rule, set 2026-10-19)
Every number in copy must be CURRENT, CITED and fetched from the publisher itself; none invented, rounded or estimated. Facts file records publisher, date, retrieval date, exact wording, quality grade (A primary data publisher / B practitioner, attribute by name / C hold-exclude) and a re-verify-by date (LMI monthly, broker reports quarterly, evergreen definitions yearly); re-run `verify_sources.py` and re-fetch within 7 days of publish. Never cite competitors (other marketplaces / flex-warehouse providers) or link to them. When sources disagree (vacancy differs by firm), cite one named publisher and never mix. If vendors disagree on a number (per-pallet prices), leave it out. Search-engine summaries are leads only: they got the LMI capacity driver wrong and mislabeled a vendor guide as independent.

---
# CASE LOG (before/after, NeuronWriter) — keep appending one block per page

## How scores are measured
- Content score = NeuronWriter `/evaluate-content` (saves nothing) or the score shown after `/import-content`. **Always send title + meta** (body-only runs 16-19 pts low vs the editor).
- "Before" = the LIVE page scored by URL (`evaluate-content` with `url`), which also picks up the page's own title/meta; page chrome (nav/footer) may be included, so treat as approximate. Raw output: `runs/live_baseline_scores.json`.
- Scores are term/structure coverage vs the SERP competitors, NOT rankings or traffic. Outcome is tracked separately with GSC (baseline below; re-measure 28/90 days after publish, noting confounders).
- NeuronWriter's AI Optimization score is NOT exposed by the API: record it manually from the editor.

## Case 1 — /fulfilment/shopify-brand-fulfillment (industry page, locked template) — keyword "shopify 3pl"
| Stage | top-10 query | top-30 query | match-intent query | Notes |
|---|---|---|---|---|
| Live page (before) | 55 | 49 | 57 | scored 2026-10-19 by URL |
| First AI drafts, body only | 46 | 41 | 49 | one draft per mode, prompt = template + NW terms + facts |
| After 3 optimization rounds, body only | 68 | 69 | 68 | but violated template (extra H2s, emoji, 7-8 internal links) and had filler: rejected |
| Final merged draft, template-locked, body only | 62 | 62 | 61 | after human cleanup of filler / slot violations |
| Final, imported with title + meta (after) | **81** | **78** | **81** | 5 internal / 3 external nofollow links; 2,141 words |
Competitors: top-10 median 59-62, all-28 median 54.5-57.5, best ~86 (a 5.6k-word listicle).
GSC baseline (90d to 2026-10-19): 4 impressions, 0 clicks, 1 query ("shopify order fulfillment partners", pos 73.8). Context: site-wide indexing fixes in Sep-Oct 2026.
Not yet published. AI Optimization score: not recorded.
Findings: mode choice (10/30/intent) moved scores by only 1-3 pts after revision; the revision loop and the template-lock/filler cleanup mattered far more. Template limits cap term coverage.

## Case 2 — /blog/how-to-find-warehouse-space-immediately (blog, no template) — keyword "how to find warehouse space"
| Stage | top-10 query | Notes |
|---|---|---|
| Live page (before) | 49 | ~1,000 words, no sourced facts, 3-question FAQ, no tables |
| Draft v1 (new, tables + cited facts), with title + meta | 65 | editor showed Title 84%, Headings 61%, Terms 50%, AI Optimization 58% |
| Final after targeted term pass, with title + meta | **76** | 2,940 words; gate 75; unusable competitor-boilerplate terms filtered; 1 usable term left |
Competitors: top-10 median 41, best 78 (a competitor city/listing page; the only guide-type pages score 26 and 41).
GSC baseline (90d to 2026-10-19): 284 impressions, 0 clicks, 65 queries; top: "what's the fastest way to source warehouse space?" 59 impr pos 7.3; "need warehousing fast" 27 pos 9.1; "how to find warehouse space" 21 pos 9.4.
Not yet published. AI Optimization score after the final pass: not recorded.
Findings: the top-10 term list was polluted by one competitor's city-page boilerplate (3 of 10 results): needed a skip-list; the "best competitor" was a different page type than ours.

---
# pSEO FOUNDATION — what exists vs what to build
## Already working (reusable per page)
- Inputs by URL: sheet row (`site_keyword_map` tab, public CSV export by gid), live-page audit, GSC/SEO Gets queries per page, site inventory (677 URLs) for internal links.
- Per-page unit = `configs/<slug>.json` + `facts/<slug>.md` + a skeleton (locked template for industry pages; SERP-derived for blogs).
- Scripts: `nw.py` (queries, import), `fetch_analyses.py`, `build_prompt.py`, `optimize.py` (score gate + gap brief), `check_page.py` (template/policy), `promo_check.py` (blog bias), `suggest_links.py`, `verify_sources.py`, `compare.py`.
- Policies: facts current + cited + primary-fetched; no competitor names; template lock; <=5 internal links; education-first blogs; skip-list for polluted terms.
## To build before scaling to many pages
1. **Orchestrator**: one command takes a URL -> reads sheet row, writes the config, creates the NW query (default 1 mode), builds the prompt, runs draft + gate loop, outputs draft + claims table + before/after record.
2. **Facts library**: per-industry/topic facts with grade + re-verify-by date; a shared WareMatch claims file with a `confirmed` flag; automated freshness check.
3. **Expert-input layer** (transcripts, ops/quote data, SME review) + a **specificity check** in the gate. Open gap: this is the biggest quality risk.
4. **Skeleton generator** for blogs (SERP headings + long-tail queries) with human approval; locked templates by page type for industry pages.
5. **AI/GEO measurement**: record NW AI Optimization manually per page; define a citation check (LLM-query sample) to compare before/after.
6. **Automated before/after logging** into this case log (live score by URL, final score, GSC baseline) and a publish step (SEO Gets annotation only at publish).
7. **Batching + review queue**: prioritize by SV/impressions, cap credits per run, require human sign-off on claims, internal-claim confirmation and tone.
8. **Refresh vs new** handling (preserve URL/H1/hook, diff against live, redirect safety).

---
# LOCATION PAGES (pSEO) — design v0 (2026-10-21). WareMatch listing data NOT available -> design without it.
Research detail + samples: `research/apis_us_gov.md`, `research/apis_canada_gov.md`, `research/apis_geo.md`, `research/apis_company_data.md`, `research/samples/`.

## Sheet row = unit of work (tab `site_keyword_map`; match by URL, rows drift)
Inputs: Page URL, Page Type (Location), H1, Primary/Secondary KW [SV], Cumulative SV, GSC impressions/position, Priority, Content Status, Redirect/Merge, Long-tail queries.
Pipeline OUTPUT columns to fill (only after owner approval to write to the sheet): Status, Projected Week of Completion, Neuronwriter Link, Score Before, Score After, Google Doc Link, SEO Gets + Search Atlas Date Last Updated, Date Live/Updated.
Test row: 164 = /location/usa ("3PL US" 5,400 SV; P4; In Progress).

## Country template (`../location_page_country_template`; city + state templates to come)
Locked (no edits): "Find 3PLs & Warehousing Across [Country]", "Why Use WareMatch?", "Find a 3PL in [Country] for Your Business" (1-2 sentences, heading before marketplace embed), "How WareMatch Works".
Written per page: H1; TL;DR (must answer the primary query immediately); "What to Consider Choosing a 3PL in [Country]" (1 intro sentence + 3 points, 1-5 sentences each, researched, location-specific); "What to Look for in a [Country] 3PL" (heading can change; 8 points, 1-3 sentences, must cover a DIFFERENT aspect than the previous section); FAQ (6).

## Data layer (cache per slug; every value stored with publisher, dataset/table, period, retrieval date, units, quality flag -> feeds `facts/<slug>.md` automatically)
| Source | Key | Verdict | Use |
|---|---|---|---|
| BLS QCEW (NAICS 493, county/state/US, quarterly CSV) | none | build now (verified) | warehouse jobs, establishments, avg weekly wage, employment concentration (LQ); county is finest level, cities map to county |
| BLS v1 API (OEWS wages, LAUS, CES) | none, 25 queries/day (v2 free key = 500/day) | build now, get v2 key for batches | hourly wages for material movers / forklift operators, unemployment |
| BTS data.bts.gov (Commodity Flow Survey 2022, Border Crossing Entry) | none | build now, caveats | state/metro freight, border-port truck crossings; CFS sampling error 13-37%, suppressed cells |
| U.S. Census (CBP, ACS) | free key REQUIRED (not yet obtained) | blocked | county business counts, place population/income |
| StatCan WDS + JVWS | none | build now | warehousing employment, vacancies, offered wages, construction investment, air cargo, border trucks; province/CMA/economic region only; resolve member IDs at runtime; read units per series |
| Transport Canada | none | skip own files; use StatCan tables | - |
| GeoNames dumps (cities15000 etc.) | none (CC BY 4.0, daily) | build now | city population, timezone, nearby places for service-area section (feature-code filter needed); web services need free username (not obtained) |
| OSM Overpass | none, unreliable; commercial use -> self-host/paid | monthly cached batch only | named facilities (intermodal terminals, airports, ports) with distances; counts only with hedging + timestamp; empty result != zero; ODbL credit |
| Brandfetch, OpenCorporates, BuiltWith, Store Leads, TikTok | paid/restricted | not now | ToS block publishing; revisit with written permission |
Rule: data goes in a page ONLY if it changes a reader's decision. Never pad with stats. Citation wording per source terms (StatCan: "Adapted from Statistics Canada, [table/period]..."; OGL-Canada line; ODbL "© OpenStreetMap contributors"; GeoNames CC BY).

## Slot -> content plan (without WareMatch data)
- TL;DR: direct answer to the primary query + 1-2 decision-relevant local facts.
- "Consider" 3 points: (1) labor: warehouse workforce size/wages vs national (BLS / StatCan); (2) freight + border + ports/airports (BTS / StatCan / OSM named facilities); (3) a cited regulatory/tax angle that is truly location-specific (e.g. how inventory in a state can create tax obligations; US vs Canada differences) - needs primary-source research per country/state.
- "Look for" 8 points: different lens (selection criteria: integrations, returns, certifications, peak capacity, carriers, contract terms...) localized where a real local fact exists; do not force local facts where none exists.
- FAQ 6: from the row's long-tail queries; cost question answered with cited wage/labor data and honest "varies" framing.
- Dropped for now: any provider/facility counts; live-page stats ("800+ facilities", etc.) are unsourced - never reuse.

## Risks to manage
1. City/state pages: county/metro/CMA mapping tables (hand-built) and fallback chain (city -> county/region -> state -> country).
2. Near-duplicate content across ~400 location pages (data-driven sentences can still read templated): vary structure by data availability; add embedding-based similarity check (Gemini key exists, untested).
3. Data caveats: suppression, sampling error, OSM completeness; record caveats with the number and hedge wording.
4. Freshness: stored timestamps + re-pull schedule (BLS/StatCan quarterly-monthly, GeoNames daily, OSM monthly).
5. 'What to look for' section risks generic copy again -> expert-input layer and specificity check (open gap).

## Case 3 — /location/usa (country location page, locked template; sheet row 164) — keyword "3pl us" (5,400 SV)
| Stage | match-intent query | top-10 query | Notes |
|---|---|---|---|
| Live page (before), scored by URL | 47 | 47 | includes ~110k chars of listing cards; not like-for-like with our import |
| Draft v1 (locked copy + new authored sections, title + meta) | 45 | 43 | 1,569 words |
| After 2 optimization rounds (agent) | 61 | 50 | 1,743 words; contained filler + own-wording claims |
| Final after manual cleanup, imported | **59** | **49** | 1,663 words; 5 internal / 9 nofollow external links; below the 60 gate on both |
Competitors: match-intent median 39.5 / best 78 (informational, 58.6% of SERP; listicles 27.6%); top-10 median 48.5 / best 71.
Queries: https://app.neuronwriter.com/analysis/view/d4d516a6b79c2b3f (intent), https://app.neuronwriter.com/analysis/view/e6482141305bdd6b (top 10). Draft: runs/location-usa/draft_final.md. GSC baseline (90d): 37 impressions, 0 clicks, no relevant queries. Not published; sheet columns not yet written; AI Optimization not recorded.
Findings: (1) the locked text + small slots cap the score (~49 unused terms; "supply chain", "ecommerce" etc. only at the low end); (2) the top-10 SERP is dominated by 'top 3PL companies' rankings the page must not produce; (3) the optimization agent re-introduced filler again, so a manual read-through/cleanup is a required stage (cost ~2 pts); (4) compliance facts were each re-read at government/court sources by the lead, and 3 agent claims (Wayfair quote, PHMSA pages, a cosmetics-holding exemption) were NOT used because they could not be verified; (5) check_page.py gained a 'location' mode: H2 order, locked copy verbatim vs live, H3 counts 3/8/6.

### Case 3 update (2026-10-21, after owner pushback 'you stopped too early')
Screenshot of NW editor at the 59 version: Title 77%, Headings 35%, Terms 61%, best competitor 74. Levers I had not pulled: HEADINGS (own H3s, FAQ questions, the changeable 'What to Look for' H2) and the title/meta tags. Changes: H3s/FAQ questions rewritten to carry usable heading terms (3PL provider, 3PL services, third-party logistics, supply chain, working with a 3PL, outsource, 3PL companies in the US) with ranking terms (best/top/largest) still excluded; title -> '3PL US: Find Third-Party Logistics and 3PL Companies in the US'; meta rewritten with 3pl companies / third-party logistics providers / warehouse; ~10 more usable terms added in plain sentences; over-use fixes. Result: match-intent 59 -> **69**, top-10 49 -> **56**. Lesson: before declaring a template ceiling, run the heading/title/meta pass; AI Optimization score must be read by a human from the editor (click Update).

---
# SITE RULES LEARNED FROM THE TEAM'S SEO AUDIT DOCS (2026-10-21) — pipeline must obey these
Sources: SEO audit checklist sheet (action tracker; columns Action / Section / Priority / Status / Details / Verification / Rollout), `WareMatch Schema Markup Architecture` doc, `meta_description_issues` doc.
## Metadata (the site generates these by formula; the pipeline must not fight them)
Titles <=65 chars, descriptions <=160 (aim ~155), never cut mid-word or end with '...'; main keyword in the FIRST 40 chars of the title; keyword once in title and once in description, never a keyword list; write '3PL' not 'third-party logistics provider'; '{City}, {ST}' in titles; titles end '| WareMatch' (drop the brand first when short, never the keyword); no two pages share a title/description; every description has >=1 page-specific fact; no empty/broken values or doubled words; consistent spelling 'fulfillment'; description must match the page; end with one CTA ('Get a quote', 'Compare rates'); sentences not pipe lists; automated pre-launch check (length, uniqueness, keyword in title, no placeholders). Formulas: country/state title '3PL Services & Warehouses in {State} | WareMatch', description 'Find 3PL warehouses across {State}, including {topCity1}, {topCity2} and {topCity3}. Compare pallet storage, fulfillment and distribution providers and get quotes.'; blogs: title = the target question (<60 chars), description = direct answer + hook (<155). Keyword study: head term '3PL'; '3pl {loc}' and '{loc} 3pl' dominate location searches.
**Impact on scoring:** NeuronWriter scores must be measured with the formula title/meta, not a keyword-stuffed one. USA page: 69/56 (stuffed title+meta, used 'third-party logistics', no brand) became **58/49** with the formula title/meta.
## Schema the content must visibly support (location pages): CollectionPage, ItemList of children (country->states, state->cities, city->top 10-20 listings), HowTo (3 steps, locked how-it-works), Service with areaServed, FAQPage (visible Q&A), BreadcrumbList by level; Place hierarchy. No pricing, no empty ratings/reviews in schema.
## GEO-relevant technical findings: JS-injected content / rendered-vs-initial HTML mismatches (~1,600 pages, fixed 10/08); listings behind a 'view all' click are invisible to LLMs ('see more' on-page requested); pages with query parameters; OG images flagged. Pipeline rule: authored content must be in the initial HTML; check raw HTML for live pages.
## Process/style conventions worth copying into our trackers: each item has an owner, priority, rollout phase, dated status, and a VERIFICATION column ('check effect on indexation'): every content change should record what we will verify and when (GSC position/impressions at 28/90 days, annotation in SEO Gets at publish).

# SKILL: geo-intent-audit (companion to this pipeline) — `../.claude/skills/geo-intent-audit/`
Purpose: judge GEO relevance, search-intent fit and real usefulness, not NeuronWriter coverage. Parts: SKILL.md (process + rules), rubric.md (8 judged dimensions with evidence), scripts/audit.py (local deterministic checks: query coverage, answer-first/self-contained passages, per-section specificity (flags INTERCHANGEABLE sections), uncited figures, freshness, promo, repetition, schema readiness, house metadata rules, entity coverage). No network/LLM calls inside the script. First run on /location/usa draft: 16/23 queries covered (7 uncovered are the deliberate exclusions: top-10 lists, FedEx/Amazon, 'what does 3PL stand for'), 6 sections flagged INTERCHANGEABLE (inventory visibility, platform integrations, carrier access, returns/support, cost FAQ, contract questions), 2 answers open with a hedge ('There is no single price', 'It depends'): matches the manual audit.
Known limits: lexical coverage only (embeddings would be better but need approval to send content to an API); template/locked copy inflates promo and uncited-figure counts; intent verdicts are the model's judgement.

### Case 3, audit-informed rewrite (2026-10-21): before vs after (formula title/meta; full comparison in runs/location-usa/before_after.md)
| | match intent | top 10 | interchangeable sections | hedged answer openers | decision aids (red flag/good answer/fit rule) | words |
|---|---|---|---|---|---|---|
| Before | 58 | 49 | 6 | 2 | 0 | 1,726 |
| After | 58 | 48 | 5 | 0 | 7 | 1,832 |
What changed: Consider #1 replaced (warehouse-labor stats -> customer geography with cited Census ACS 2024 population shares + a method: rank your own top-10 destination states, ask each 3PL for transit times to them); look-for items 4-8 rewritten as ask / good answer / red flag; cost FAQ answers first and gives a no-price way to compare quotes; in-house FAQ answers first; contract FAQ lists the specific asks; TL;DR leads with the answer. NeuronWriter score unchanged (terms lost with rewritten text were re-added only where natural). Honest read: usefulness improved but the 5 flagged sections still contain no named facts: they need operator knowledge (expert-input layer). Instrument note: the audit script gained a 'decision aids' metric AFTER seeing this rewrite because its concrete-token count did not credit red flags/good answers; old metrics unchanged.

### Owner rulings (2026-10-21): (1) TEMPLATE STRUCTURE IS ALWAYS FOLLOWED: locked sections verbatim, H2 order, H3 counts, and now slot sentence limits (consider intro 1 sentence; consider points 1-5, point 3 exactly 1; look-for points 1-3; 'Find a 3PL in...' 1-2; TL;DR <=3) are enforced by check_page.py 'location' mode (tested: a 2-sentence point 3 fails). (2) Page titles may be changed when a more appropriate one exists, within the meta rules. Country title changed from '3PL Services & Warehouses in the United States | WareMatch' to '3PL Companies & Warehouses in the United States | WareMatch' (59 chars; '3PL' first; brand suffix; 'us 3pl companies' is a sheet secondary keyword); description 'Find 3PL companies and warehouses across the United States, including California, Texas and Pennsylvania. Compare providers and get quotes.' (137 chars) (3) The 'what a 3PL is' FAQ was dropped (one sentence in the TL;DR is enough) and replaced with 'How do I choose the best 3PL provider in the US?'.

### Blog 'recommended first' structure (owner ruling 2026-10-21; used on /blog/how-to-find-warehouse-space-immediately)
Mindset: the reader is stressed and wants an immediate answer. Structure: H1 + hook + a direct recommendation of WareMatch with its real reasons + 'Get quotes' CTA (RFQ link, exempt from link caps) -> 'Do This Now' 3 steps (spec, submit one RFQ -> match score out of 100, send quote requests; responses around a day or two) -> an explicit 'not the only route' sentence -> the full guide (fastest way, market, spec table, timeline + routes table, lease vs shared table, negotiation table, broker, FAQ) -> bottom line with a closing CTA. Still no 'best/only/fastest' claims about WareMatch (owner chose 'recommended', not 'the best'), alternatives named by category. `promo_check.py --urgent` enforces: brand within the first 20% of text, <=2 H2 sections with the brand, must state it is not the only route, no superlatives. check_page.py blog mode allows only the RFQ CTA link above the first H2.
Owner ruling: do NOT cite companies that sell warehousing/3PL/space (Buske Logistics, Link Logistics removed; lease-time source replaced by JLL research via Bisnow trade press, dated 2024, year always stated). Result: 76 (old structure) -> 75 (new structure) on the same query with the formula-style title/meta '... | WareMatch'; two helper bugs found and fixed (checker dropped an 'ext' variable; optimizer made 'newnums' conditional).

### Owner feedback on the USA page (2026-10-21) — rules for ALL future pages
1. Easy NeuronWriter terms must be inserted: before declaring a score 'ceiling', run an explicit easy-terms sweep (terms that fit naturally into existing sentences: fulfillment centers, third-party logistics providers, contract logistics, supply chain management, end-to-end logistics, hidden fees...). Still exclude ranking/brand/global-network terms.
2. Readability of figures: round in prose ('nearly 3 million', 'about 1.1 million', 'roughly 1 million'), keep exact values in the facts file; never pile several 6-digit numbers into one sentence. optimize.py now accepts rounded figures within 3% of a fact (also as thousands/millions).
3. Look-for/consider points that cite one regulation must also carry general practical advice (e.g. dangerous goods: classify items, label/document, train staff, segregate storage, red flag 'we'll figure it out').
4. Do not assume e-commerce on general 3PL/location pages: cost, process and integration copy must serve all shippers (parcel, pallet, wholesale/retail replenishment, cold chain).
5. Internal links: authored copy links TOPICAL pages (industry + guide pages); location pages' state/city links already exist in the template, so never make authored linking location-based. Max 5, visibly placed in the relevant point.
6. Never import into a NeuronWriter brief the owner is editing; use read-only evaluate-content and import only after they say so.
7. Sheet: pipeline fills only EMPTY output cells (Neuronwriter Link / Score Before / Score After) and never overwrites the owner's entries (row 126 already had link, before=30, after=76 and a Google Doc). Before-score methods differ (owner 30 vs URL-scored 49 on the blog): align the method.

### geo-intent-audit v1.0 finalized (2026-10-21)
Skill now has 3 layers (technical_check.py raw-HTML/metadata/schema/crawler checks; audit.py content checks; judged rubric with evidence grades) plus references (AI crawlers/rendering, structured data, content evidence; INDEX.md verdicts). Research findings that change plans: Google's AI guide (2026-07-10) says GEO is 'still SEO', main lever = unique non-commodity content, no need for llms.txt/chunking/special schema; FAQ rich results ended 2026-05-07 and HowTo removed 2023; schema.org/LogisticsBusiness does not exist (team schema doc recommendation invalid); schema showed no measurable AI lift in an Ahrefs causal test; JS rendering by non-Google AI bots is unconfirmed (keep content in initial HTML). Live-site findings: AI bots not blocked, canonicals ok, FAQ schema matches visible text; blog meta description ends with '...' and lacks breadcrumb schema/'| WareMatch'; 2 JSON-LD blocks per page; og:image missing on home/integration/Texas pages; listing page has only ~386 raw-HTML words and 2 H1s.

### 'So what' rule (owner feedback 2026-10-21): every statistic must change a decision. A sentence that lists figures without saying what the reader should do differently is a stat dump: cut it or turn it into advice ('rank your top ten destination states and ask each 3PL for transit times'). Keep at most one or two headline figures per point, rounded. geo-intent-audit now flags sections with >=4 figures and <2 decision cues. Removed from the USA page: the BLS labor-by-state sentence (accurate but not decision-relevant).

## Case 4: /location/usa/florida (state location page, locked state template; sheet row 229): keyword brief '3pl florida' (primary; GSC shows 3PL queries, e.g. '3pl companies florida' 130 impressions) + 'warehouse florida' (sheet primary; SERP is landlord/real-estate intent, informational only)
State template (../location_page_state_template): locked 'Why Use WareMatch?', 'Find a 3PL in [State]...' (1-2 sentences), 'How WareMatch Works'; authored TL;DR (<=3 sentences), 'When to Choose a 3PL [State]' (two-column table 'You need a [State] 3PL if' | 'You may not need one yet if', bullets), two 'what to consider' sections of 3 points each (1-5 sentences; headings changeable, second must cover a different aspect), FAQ 6. check_page.py has a 'state' mode (H2 order, locked copy vs live, table columns, bullets, 3/3/6 H3 counts, sentence limits). The live page has extra site modules not in the template (cost table, region lists): not authored by us.
Data used: BLS QCEW by county (Polk 17.8k jobs, 5.6x concentration, I-4 corridor), TIGERweb interstates, NHC season dates, FEMA flood lookup, JAXPORT/Port Everglades/MIA figures, Florida DOR physical-presence wording and the Oct 1 2025 commercial-rent sales-tax repeal (TIP 25A01-04). Live-page unsourced thresholds removed ('$8 per package', 'fewer than 200 orders').
| Stage | '3pl florida' brief | 'warehouse florida' brief | notes |
|---|---|---|---|
| Live page (before), scored by URL | 58 | 63 | includes ~8k chars of provider cards and city lists: not like-for-like |
| Draft v1 (template-locked, new copy) | 50 | 51 | before term pass |
| Final, imported (title 3PL Companies & Warehouses in Florida | WareMatch) | **65** | **58** | formula title scored 62/58; GSC-led title +3 |
Competitors ('3pl florida'): median 52 all / 56 top-10, best 77 (a directory), SERP 89% transactional, 63% local, landing pages 37%.
Lessons: (1) check the sheet's primary keyword against GSC before choosing the NeuronWriter brief; (2) the audit caught duplicated facts across sections (counties repeated in an FAQ, storm planning in 4 places): swap or point back instead of repeating; (3) state-level uniqueness came from county-level BLS data and Florida-only rules (rent-tax repeal, hurricane/flood), which the country page cannot offer; (4) agent-sourced PDF facts were not usable when text extraction failed: say 'commercial rentals', not 'warehouses', unless read verbatim.

---
# FAILURE MODES -> CONTROLS (consolidated 2026-10-21; every row came from a real run)
| Failure observed | Control now in the pipeline | Where |
|---|---|---|
| Agents added H2s/emoji/filler to chase a score | Template lock modes (industry, blog, location, state) incl. sentence limits; mandatory human read-through | check_page.py, READTHROUGH.md |
| Scores inflated by keyword-stuffed title/meta | Score with the SHIPPING title/meta only | optimize.py (config title/description) |
| Easy NeuronWriter terms skipped (Florida: 8 basic + 57 extended missing; rule existed only in notes) | HARD GATE: basic-term coverage >=90% (default for every page), extended coverage reported/warned; mandatory easy-terms sweep before any 'ceiling' claim | optimize.py, configs/_defaults.json |
| Competitor/ranking/brand terms leaking into targets | Default skip list merged with page skip list (never replaced) | configs/_defaults.json |
| Sheet primary keyword mismatched real demand (warehouse Florida vs 3PL queries; landlord SERP) | Keyword/brief sanity step before drafting | keyword_check.py |
| Stat dumps; unhelpful figures (BLS labor sentence) | 'So what' check: >=4 figures with <2 decision cues; rounded-figure rule | audit.py 3b, optimize.py (3% rounding tolerance) |
| Facts repeated across sections (counties; storm plan) | Cross-section repetition check | audit.py 3c |
| Ecommerce assumed on general 3PL pages | Audience-assumption check | audit.py 3c |
| WareMatch connection generic / nonexistent on location pages | Connection check (>=3 sentences tying local decisions to filters / one request / compare matched providers); no invented network counts | audit.py |
| Lowercased heading from case-insensitive replace | Heading-capital check; exact-case replacement helper pattern | check_page.py |
| Tooling edits broke other scripts (clobbered variable, conditional variable) | Regression runner re-checks every page config after any tool change | regress.py |
| Brief naming mismatch (analysis_<mode> vs tags) | Brief aliases in page config ('briefs') | optimize.py |
| Agent-supplied facts unverified; unreadable PDFs; wrong-source claims | Lead re-reads each claim at the source; unreadable/agent-only claims excluded; facts file grades A/B/C | facts/*.md, SKILL.md |
| Imported over an owner's brief; overwrote sheet cells | Never import into briefs being edited (use read-only evaluate); fill only empty sheet cells | SKILL.md, READTHROUGH.md |
| No visibility of time/cost | Per-run time + token + dollar log (token counts entered by hand; context re-read overhead estimated) | runlog.py |
| Page-specific template shapes (country vs state; extra live modules) | Mode per template with locked-copy check against live page; extra site modules are not authored | check_page.py, templates/ |
## Stage order (v2)
1 row + live audit + GSC queries -> 2 keyword/brief sanity (keyword_check.py) -> 3 skeleton/template mode -> 4 facts (primary-source, lead re-reads) -> 5 NeuronWriter briefs -> 6 draft -> 7 easy-terms sweep (gate: basic >=90%) -> 8 gates (check_page, optimize, promo_check, verify_sources) -> 9 READTHROUGH.md -> 10 geo-intent-audit (3b so-what, 3c repetition/audience/connection) -> 11 regress.py -> 12 import (only if the owner is not editing) + fill empty sheet cells -> 13 log case + runlog.py summary.
## Cost reference (claude-sonnet-5-5, per 1M tokens, Claude API reference 2026-10): input $2.00, output $10.00, cache read $0.20, cache write $2.50. Florida page run: ~190k counted tokens (~95k main thread + ~94k research agent) = roughly $0.7-$1.0 for the counted tokens alone; the real bill is dominated by the whole conversation being re-read on every tool call, so a plausible total is several dollars; measure with runlog.py going forward.

## Case 5: Florida editor feedback (2026-10-21), root causes and controls
Feedback from the content lead on the Florida v9 draft, and what each one exposed:
| Feedback | Root cause in my process | Control added |
|---|---|---|
| Always name which ports (Everglades, Jacksonville, etc.) | Wrote "Miami and Port Everglades" as a gesture; no rule that location-intent pages must name the physical gateways | `intro_must` gate in optimize.py: intro must name configured ports/capabilities; READTHROUGH 14 |
| Hurricane framing: "not many people look at hurricanes when picking a 3PL" | Chose the topic because it is salient and sourceable (NHC/FEMA), not because a buyer searches or decides on it. I optimized for what I could cite, not for buyer decision drivers | READTHROUGH 15 (demand test: would a buyer name this as a selection criterion? check GSC/PAA/competitor headings first); `storm_max` cap; topic reframed to insurance/liability |
| Intro should say who can accommodate what, by part of the state (capability + location in one search, the AEO play) | Intro summarized the page, not the query. Never modeled the "capability x location" query shape | READTHROUGH 16; intro_must requires a capability word and place names |
| Blurb: detail the project requirements and where to store | Defaulted to "send one request" (generic marketplace language) | banned_authored_regex blocks "send/submit/one request" in authored copy; READTHROUGH 17 |
| Remove "yet" from the table; add Florida geography (tucked away, higher shipping, longer transit) | Kept generic any-state bullets ("volume small", "validating") that are not location-specific; the Whether column was not swap-tested | Swap test on every table bullet (READTHROUGH 18): replace Florida with Ohio; if it still reads fine, it is generic, so rewrite with a state fact |
| "I don't think there's property tax on shippers storing with a 3PL" | I stated a tax exposure from a DOR "business connection" page without verifying that it applied to inventory at a 3PL. Florida exempts inventory from ad valorem tax (s. 196.185, F.S.). Also, the rent-tax repeal was about leases, not 3PL storage fees | Tax/legal claims need a statute or agency page that states the exact applicability; a claim of an obligation on the reader requires the strongest evidence (READTHROUGH 19); removed |
| "Request" makes the 3PL a commodity | Marketplace jargon copied from the locked modules into authored copy | Template-level: raised to the site owners; authored copy now uses project scope / matches / choose |
Metacognitive pattern: (a) I treated "sourceable and verifiable" as the same as "useful", (b) I wrote from the page's data (what I had) and not from the buyer's query (what they ask), (c) I reused generic copy across sections and states without a swap test, and (d) I let a regulation page imply an obligation. Process fix: before drafting, write the query shape ("[capability] in [place]"), list 5 buyer decision drivers from SERP/PAA/GSC, then pick sections from that list; review pass is by an editor-style checklist, not only the score gates.
