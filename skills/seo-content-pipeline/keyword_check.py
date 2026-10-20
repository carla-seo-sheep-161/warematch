#!/usr/bin/env python3
"""Sanity-check the sheet's primary keyword against what the page actually gets impressions for.
usage: keyword_check.py <gsc.json> "<sheet primary keyword>" ["<alt keyword>" ...]
gsc.json = [{"query": "...", "impressions": N}, ...] exported from Search Console / SEO Gets for the page URL (90 days).
Prints the share of impressions matching each keyword's terms and recommends which NeuronWriter brief to treat as primary.
Lesson (Florida page): sheet primary was 'warehouse Florida' but 3PL queries carried the impressions and the 'warehouse' SERP was landlord/real-estate intent."""
import json, re, sys
rows = json.load(open(sys.argv[1])); tot = sum(r["impressions"] for r in rows) or 1
def share(kw):
    t = [w for w in re.findall(r"[a-z0-9]+", kw.lower()) if w not in ("in", "the", "a")]
    m = sum(r["impressions"] for r in rows if all(w in r["query"].lower() for w in t)); return m, m / tot
best = None
for kw in sys.argv[2:]:
    m, s = share(kw); print(f"{kw!r}: {m} impressions ({s:.0%} of {tot})"); best = max(best or (s, kw), (s, kw))
print("recommend primary brief:", best[1], "| also check the SERP intent (listing/real-estate vs 3PL services) before choosing")
