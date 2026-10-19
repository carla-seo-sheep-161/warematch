#!/usr/bin/env python3
"""GEO / intent / utility audit (deterministic part). Local only: no network, no LLM, no embeddings.
usage: audit.py <draft.html|md> --queries queries.txt [--primary "3pl us"] [--type location|industry|blog] [--title T --desc D] [--brand WareMatch] [--entities analysis.json]
Prints a markdown report. Heuristics only: the LLM-judged rubric (rubric.md) must be applied on top."""
import argparse, collections, html as H, json, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("draft"); ap.add_argument("--queries", required=True); ap.add_argument("--primary", default="")
ap.add_argument("--type", default="blog"); ap.add_argument("--title", default=""); ap.add_argument("--desc", default="")
ap.add_argument("--brand", default="WareMatch"); ap.add_argument("--entities", default="")
a = ap.parse_args()
raw = open(a.draft).read().split("\n---")[0]
STOP = set("a an the of to in for and or is are be on at by with from how what do does can i my you your it its this that as vs which when why who should".split())
def toks(s): return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1]
def stem(w): return re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w
def plain(s): return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
# ---- sections
parts = re.split(r"(?=<h[1-3][ >])", raw)
secs = []; intro = plain(parts[0])
for p in parts:
    m = re.match(r"<h([1-3])[^>]*>(.*?)</h[1-3]>", p, re.S)
    if m: secs.append({"lvl": int(m.group(1)), "head": plain(m.group(2)), "html": p[m.end():], "text": plain(p[m.end():])})
h1 = next((s for s in secs if s["lvl"] == 1), None)
tldr = plain(h1["html"].split("<h2")[0]) if h1 else intro
words = lambda s: len(s.split())
out = []; P = out.append
P(f"# GEO / intent audit: {a.draft}\n")
# ---- 1 intent: query coverage
Q = [q.strip() for q in open(a.queries) if q.strip() and not q.startswith("#")]
cov = []
for q in Q:
    qt = {stem(t) for t in toks(q)}
    best = (0, None)
    for s in secs:
        st = {stem(t) for t in toks(s["head"] + " " + s["head"] + " " + s["text"])}
        sc = len(qt & st) / max(len(qt), 1)
        if sc > best[0]: best = (sc, s["head"])
    cov.append((best[0], q, best[1]))
covered = [c for c in cov if c[0] >= 0.7]
P("## 1. Intent / query coverage (lexical: a query counts as covered if >=70% of its terms sit in ONE section)")
P(f"- covered {len(covered)}/{len(Q)} queries")
for sc, q, h in sorted(cov):
    if sc < 0.7: P(f"  - NOT covered ({sc:.0%}): {q}  [closest: {h}]")
pt = {stem(t) for t in toks(a.primary)} if a.primary else set()
first100 = {stem(t) for t in toks(" ".join(tldr.split()[:100]))}
if pt: P(f"- primary query terms in first 100 words: {len(pt & first100)}/{len(pt)}")
# ---- 2 answer-first + passage self-containment
P("\n## 2. GEO extractability (answer-first, self-contained passages)")
bad_open = re.compile(r"^(this|that|it|these|those|they|there is no single|it depends|depends on)\b", re.I)
qform = re.compile(r"^(how|what|is|can|do|does|why|when|which|who|should|are)\b|\?$", re.I)
nq = sum(1 for s in secs if s["lvl"] >= 2 and qform.search(s["head"]))
P(f"- question-form headings: {nq}/{sum(1 for s in secs if s['lvl']>=2)}")
flags = []
for s in secs:
    if s["lvl"] < 3 or not s["text"]: continue
    first = re.split(r"(?<=[.!?])\s+", s["text"])[0]; n = words(s["text"])
    if bad_open.search(first): flags.append(f"opens with a pronoun/hedge ('{first[:50]}...') -> {s['head'][:50]}")
    if n < 20: flags.append(f"very short passage ({n} words): {s['head'][:50]}")
    if n > 140: flags.append(f"long passage ({n} words): {s['head'][:50]}")
    if qform.search(s["head"]) and words(first) > 45: flags.append(f"answer sentence too long ({words(first)} words): {s['head'][:50]}")
for f in flags: P(f"  - {f}")
if not flags: P("  - none")
# ---- 3 specificity
P("\n## 3. Specificity (concrete tokens per 100 words vs generic-advice phrases) per section")
GEN = re.compile(r"\b(ask (about|which|how|whether|who|what|each)|make sure|check (that|whether|which)|it depends|no single|varies|consider|important|best practices?|look for|confirm (that|who|whether))\b", re.I)
CON = re.compile(r"\d[\d,.]*%?|\b(CFR|FDA|CBP|BLS|BTS|UN \d|C-TPAT|NAICS|I-\d+)\b|\b20\d\d\b|\b[A-Z][a-z]+ (?:[A-Z][a-z]+)\b")
inter = []
for s in secs:
    if s["lvl"] < 3 or words(s["text"]) < 15: continue
    c = len(CON.findall(s["text"])); g = len(GEN.findall(s["text"])); d = c / (words(s["text"]) / 100)
    tag = "INTERCHANGEABLE (generic advice, no concrete detail)" if c == 0 and g >= 1 else ("thin" if d < 2 else "concrete")
    P(f"- {tag:55s} concrete={c} generic={g} :: {s['head'][:60]}")
    if tag.startswith("INTER"): inter.append(s["head"])
# decision aids (added 2026-10-21 after the USA rewrite: red flags / good answers / fit rules are real utility the concrete-token count misses)
DEC = re.compile(r"\b(red flag|good answer|warning sign|be wary|fits better when|usually a better fit|a good .{0,40} is)\b", re.I)
da = [s_["head"] for s_ in secs if s_["lvl"] >= 3 and DEC.search(s_["text"])]
P(f"\n- decision aids (red flags / good-answer markers / fit rules): {len(da)} sections")
# ---- 4 citations / freshness
P("\n## 4. Citations and freshness")
ext = re.findall(r'<a [^>]*href="https?://(?!www\.warematch)[^"]+"[^>]*>', raw)
P(f"- external links: {len(ext)}; all nofollow: {all('nofollow' in x for x in ext)}")
unc = []
for s in secs:
    for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"<a [^>]*>.*?</a>", " LINK ", s["html"], flags=re.S)):
        t = plain(sent)
        if re.search(r"\d[\d,]{3,}|\d+%", t) and "LINK" not in sent and "according to" not in t.lower(): unc.append(t[:90])
P(f"- sentences with a figure but no link/'according to' in the same sentence: {len(unc)}")
for u in unc[:6]: P(f"  - {u}")
yrs = collections.Counter(re.findall(r"\b20\d\d\b", plain(raw))); P(f"- years mentioned: {dict(yrs)}  (freshness signal: >=1 recent year with source)")
# ---- 5 promo / repetition
P("\n## 5. Promo and repetition")
txt = plain(raw).lower(); bm = txt.count(a.brand.lower())
P(f"- {a.brand} mentions: {bm} ({bm/(words(txt)/100):.2f} per 100 words); in TL;DR: {tldr.lower().count(a.brand.lower())}")
w = re.findall(r"[a-z']+", txt); tri = collections.Counter(zip(w, w[1:], w[2:]))
rep = [" ".join(k) + f" ({c})" for k, c in tri.items() if c >= 4]
P(f"- repeated 3-word phrases (>=4x): {rep[:8] or 'none'}")
# ---- 6 structure / schema readiness / metadata rules
P("\n## 6. Structure and metadata rules (from the team's schema + meta docs)")
faq_n = sum(1 for s in secs if s["lvl"] == 3 and qform.search(s["head"]))
P(f"- Q&A headings usable for FAQPage: {faq_n} (FAQPage needs real visible Q&A: ok if >=3)")
if a.type == "location": P("- location schema expects CollectionPage + ItemList(children) + HowTo(3 steps) + Service(areaServed) + FAQPage + BreadcrumbList: content must visibly support each (listing module, how-it-works steps, FAQ)")
if a.title or a.desc:
    t, d = a.title, a.desc
    P(f"- title {len(t)} chars (<=65): {'ok' if len(t)<=65 else 'FAIL'}; main keyword in first 40 chars: {'ok' if a.primary and (a.primary.split()[0].lower() in t[:40].lower()) else 'check'}; brand suffix '| WareMatch': {'ok' if t.rstrip().endswith('| WareMatch') else 'missing'}")
    P(f"- description {len(d)} chars (<=160): {'ok' if len(d)<=160 else 'FAIL'}; ends with '...': {'FAIL' if d.rstrip().endswith(('...','…')) else 'ok'}; has CTA (get/compare/request quote): {'ok' if re.search(r'(get|compare|request|find)', d.lower()) else 'check'}")
    P(f"- uses 'third-party logistics' (team rule: write '3PL'): {'FAIL' if 'third-party logistics' in (t+d).lower() else 'ok'}")
# ---- 7 entities
if a.entities:
    ents = [e["t"] for e in json.load(open(a.entities))["terms"]["entities"][:25]]
    miss = [e for e in ents if e.lower() not in txt]
    P(f"\n## 7. Entity coverage (NeuronWriter top-25): present {len(ents)-len(miss)}/{len(ents)}; missing: {miss[:12]}")
P("\n## Verdicts the script cannot give (apply rubric.md with evidence): intent fit, decision utility, information gain vs SERP, location swap-test, trust, differentiation.")
print("\n".join(out))
