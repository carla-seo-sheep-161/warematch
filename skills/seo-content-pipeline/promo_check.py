#!/usr/bin/env python3
"""Blog bias/promo lint: education first, WareMatch as ONE option, never the only option.
usage: promo_check.py <draft.md> [brand=WareMatch]; exit 1 on FAIL. Thresholds are starting points; tune after review."""
import re, sys
URG = "--urgent" in sys.argv; args = [a for a in sys.argv[1:] if not a.startswith("--")]
html = open(args[0]).read().split("\n---")[0]; brand = (args[1] if len(args) > 1 else "WareMatch").lower()
text = re.sub(r"<[^>]+>", " ", html).lower(); words = len(text.split())
secs = re.split(r"(?=<h2)", html); fails = []
mentions = [m.start() for m in re.finditer(brand, text)]
share = len(mentions) / max(words / 100, 1)                       # mentions per 100 words
first = (mentions[0] / len(text)) if mentions else 1
promo_h2 = [re.sub(r"<[^>]+>", "", s.split("</h2>")[0]).strip() for s in secs[1:] if brand in re.sub(r"<[^>]+>", " ", s).lower()]
text_nn = re.sub(r"not (?:the )?only", "not exclusive", text)
claims = re.findall(r"[^.]*\b" + brand + r"\b[^.]*\b(only|best|#1|number one|fastest|leading|no other|unmatched|guarantee[sd]?)\b[^.]*\.", text_nn)
alts = [a for a in ("broker", "landlord", "direct", "other marketplace", "marketplaces", "3pl", "short-term", "sublease", "coworking warehouse", "shared warehouse") if a in text]
patterns = {p: len(re.findall(p, text)) for p in ("instead of", "real options", "real listings", "real quotes", "one request")}
print(f"mentions={len(mentions)} per100w={share:.2f} first_mention_at={first:.0%} of text | H2s mentioning brand: {promo_h2}")
print(f"claim words near brand: {len(claims)} | alternatives named: {alts} | pattern repeats: {patterns}")
if URG:
    if first > 0.2: fails.append("urgent mode: brand must be recommended within the first 20% of the text")
    if len(promo_h2) > 2: fails.append("urgent mode: brand in more than 2 H2 sections")
    if "not the only" not in text and "not only" not in text: fails.append("urgent mode: must state WareMatch is not the only route")
else:
    if first < 0.6: fails.append("brand introduced before 60% of the body")
    if len(promo_h2) > 1: fails.append("brand appears in more than one H2 section")
if claims: fails.append("superlative/exclusive claim about brand: " + claims[0].strip()[:80])
if len(alts) < 3: fails.append("fewer than 3 alternatives named")
if any(v > 2 for v in patterns.values()): fails.append("repeated promo framing pattern >2x")
print("FAIL: " + "; ".join(fails) if fails else "PASS promo/bias checks"); sys.exit(1 if fails else 0)
