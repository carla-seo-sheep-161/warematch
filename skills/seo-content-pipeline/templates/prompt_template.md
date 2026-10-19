# Task
Write the full body copy for a WareMatch industry/landing page ({{PAGE_URL}}). Output HTML-in-markdown exactly following the SKELETON below (keep its tags and section order; replace notes/placeholders with real copy; delete all "Notes:" lines). Audience: ecommerce operators/founders on Shopify evaluating a 3PL. Voice: plain, specific, helpful, no hype. WareMatch is a marketplace that matches brands to vetted 3PL warehouses via an RFQ.

# Hard rules
0. TEMPLATE LOCK. Use ONLY the H2s in the SKELETON, in order; never add, rename-away or reorder an H2. Fixed slot sizes (H3 counts, sentence counts) in the skeleton are binding. Extra material must fit inside an existing slot. No emoji or emoji entities anywhere (icons are `<i class="icon icon-NAME" aria-hidden="true"></i>` placeholders). Do not label H3s 'Issue 1/Issue 2': use descriptive titles. NO links in the TL;DR paragraph or the Key Takeaways list. No general market statistics: put concrete, decision-relevant details (cutoffs, minimums, timelines, fees) in the TL;DR and section intros instead.
1. NO REPETITION. Every section must introduce a distinct point. Do not repeat a statistic, claim, benefit or phrase in two sections. Do not repeat the exact keyword in consecutive headings. Mentioning WareMatch's RFQ/CTA at most twice in the whole page (once mid, once at the end).
2. HARD FACTS ONLY FROM THE FACTS BLOCK. Do not invent or round any number, company, price or date. If you need a number that is not in FACTS, write the point qualitatively. Put "(verify)" nowhere — simply omit unsupported numbers.
3. OUTSIDE SOURCES: link at least 2 EXTERNAL facts from FACTS using <a href="URL" rel="nofollow noopener" target="_blank">anchor</a>. Place each next to the claim it supports. Max one external link per claim; never link competitors' marketing pages.
4. INTERNAL LINKS: at most 5 in the whole page, each unique and present in site_inventory.json (`suggest_links.py` gives candidates; you choose semantically: reframe a sentence slightly so the mention is natural, e.g. 'wholesale orders' -> /fulfilment/b2b-wholesale). Use the skeleton's required link (apparel, anchor '3pl fulfillment') first. Descriptive anchors, plain <a href>, no nofollow, none in headings/TL;DR/takeaways.
5. Internal WareMatch claims (INTERNAL list) must be phrased as typical ranges ("typically", "often"), never as guarantees.
6. SEO: primary keyword in H1, first 100 words and one H2; weave the secondary keywords naturally (once each at most unless NEURON ranges below say more). Hit NEURON term ranges below where natural; do not stuff. Target ~{{WORD_TARGET}} words, readability ≈ {{READABILITY}} (Neuron scale; keep sentences short).
7. FAQ: up to 10 questions drawn from the long-tail queries / People Also Ask; answers 2-4 sentences, each answer must contain something the body did not already say.
8. Return ONLY the page HTML-in-markdown, then after a line "---" a table: | claim | number used | source URL | internal/external |, and a list of the title tag (<=60 chars) and meta description (<=155 chars).

# Keyword data (from sheet)
Page H1 in sheet: {{H1_SHEET}}
Primary: {{PRIMARY}}
Secondary: {{SECONDARY}}
Long-tail queries: {{LONGTAIL}}

# NeuronWriter data (variant: {{VARIANT}})
Title terms:
{{NW_TITLE}}
H1 terms:
{{NW_H1}}
H2 terms:
{{NW_H2}}
Body terms with usage ranges:
{{NW_BASIC}}
Entities:
{{NW_ENTITIES}}
People also ask:
{{PAA}}
Suggested questions:
{{QUESTIONS}}
Top SERP pages for context (do not copy; find angles they miss):
{{SERP}}

# Problems with current live page to fix
{{EXISTING_PROBLEMS}}

# FACTS (the only permitted numbers/sources)
{{FACTS}}

# SKELETON
{{SKELETON}}
