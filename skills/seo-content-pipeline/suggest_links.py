#!/usr/bin/env python3
"""Internal-link candidate finder. Scans a draft for natural mentions of other WareMatch pages' topics.
usage: suggest_links.py <draft.md> <self_url> [max=12]
Ranks inventory pages (site_inventory.json) by concept match to sentences in the body (skips TL;DR + Key Takeaways, existing links).
Output = candidates for the writer/agent to choose from; the final page may use at most 5 internal links."""
import json, re, sys
draft, self_url = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 12
html = open(draft).read().split("\n---")[0]
body = html.split("</ul>", 1)[1] if "Key Takeaways" in html else html      # skip TL;DR + takeaways
STOP = set("the 3pl and for a of to in with fulfillment fulfilment services service best to right your guide how what is find".split())
import math
from collections import Counter
inv = json.load(open("site_inventory.json")); seen = set(); out = []
TYPE_W = {"Fulfilment": 3, "Fufillment": 3, "Integration": 2, "Blog": 2, "Site": 1, "Encyclopedia": 1, "Location": 0}
def concepts_of(p): return {w for w in re.findall(r"[a-z0-9]+", (p["h1"] + " " + p["primary"].split("[")[0]).lower()) if w not in STOP and len(w) > 2}
pages = []
for p in inv:
    if p["url"] in seen or p["url"].rstrip("/") == self_url.rstrip("/") or TYPE_W.get(p["type"], 0) == 0: continue
    seen.add(p["url"])
    if "redirect" in (p["redirect"] or "").lower() and "final" not in (p["redirect"] or "").lower(): continue
    pages.append((p, concepts_of(p)))
df = Counter(c for _, cs in pages for c in cs); N = len(pages)
idf = lambda c: math.log(N / df[c])
sentences = [(re.sub(r"<[^>]+>", " ", x).lower(), x) for x in re.split(r"(?<=[.!?])\s+|\n", body) if "<a " not in x and not x.strip().startswith("<h")]
for p, cs in pages:
    if not cs: continue
    tot = sum(idf(c) for c in cs)
    for t, _ in sentences:
        hit = {c for c in cs if re.search(r"\b" + re.escape(c) + r"s?\b", t)}
        w = sum(idf(c) for c in hit)
        if w >= 0.55 * tot and w >= 3.0:          # most of the page's distinctive concept must appear
            out.append((w / tot + TYPE_W[p["type"]] / 10, p["url"], p["h1"], sorted(hit), re.sub(r"\s+", " ", t).strip()[:150])); 
out.sort(reverse=True); done = set()
for sc, u, h1, hit, s_ in out:
    if u in done: continue
    done.add(u); print(f"{sc:.2f} | {u} | {h1[:45]} | matched {hit}\n      in: {s_}")
    if len(done) >= mx: break
