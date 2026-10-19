#!/usr/bin/env python3
"""Template + policy checks. usage: check_page.py <draft.md> <skeleton_h2s.json|-> ; exits 1 on any FAIL.
Checks: only allowed H2s in order; H3 counts; no emoji/emoji entities; no links in TL;DR and Key Takeaways;
<=5 internal links, each in site_inventory.json and unique; >=2 external, all rel=nofollow; no em-dash overuse."""
import json, os, re, sys, html as H
html = open(sys.argv[1]).read().split("\n---")[0]
inv = {p["url"].rstrip("/") for p in json.load(open("site_inventory.json"))}
fails = []
h2 = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S | re.I)]
want = ["key takeaways", "why (and when)", "why shopify", "seamless", "specific things", "frequently asked"]
got = [next((w for w in want if w in h.lower()), "OTHER:" + h) for h in h2]
MODE = sys.argv[2] if len(sys.argv) > 2 else "-"
BLOG = MODE in ("blog", "location")
if MODE == "location":
    LOC = ["find 3pls", "why use warematch", "find a 3pl in", "how warematch works", "what to consider", "what to look for", "frequently asked"]
    got_l = [next((w for w in LOC if w in h.lower()), "OTHER:" + h) for h in h2]
    if got_l != LOC: fails.append(f"H2 sequence {got_l} != country template {LOC}")
    lock = json.load(open("runs/location-usa/locked_sections.json")) if os.path.exists("runs/location-usa/locked_sections.json") else {}
    plain = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", html)))
    for k, v in lock.items():
        for line in [x.strip() for x in v.splitlines() if x.strip()]:
            if re.sub(r"\s+", " ", line) not in plain: fails.append("locked copy changed: " + line[:50]); break
    secs = re.split(r"(?=<h2)", html)
    cnt = {n: len(re.findall("<h3", s_)) for s_ in secs[1:] for n in [next((w for w in LOC if w in re.sub(r"<[^>]+>", "", s_.split("</h2>")[0]).lower()), "?")]}
    for n, want_n in (("what to consider", 3), ("what to look for", 8), ("frequently asked", 6)):
        if cnt.get(n) != want_n: fails.append(f"{n}: {cnt.get(n)} H3s, template wants {want_n}")
if not BLOG and got != want: fails.append(f"H2 sequence {got} != template {want}")
if re.search("[\U0001F300-\U0001FAFF☀-➿]|&#(?:9\d{3}|1[2-3]\d{4});", html): fails.append("emoji found")
tldr = html.split("<h2", 1)[0]; kt = re.search(r"Key Takeaways.*?(?=<h2)", html, re.S | re.I)
for name, seg in (("TL;DR", tldr), ("Key Takeaways", kt.group(0) if kt else "")):
    if "<a " in seg: fails.append(f"link inside {name}")
links = re.findall(r'<a [^>]*href="([^"]+)"[^>]*>', html)
internal = [l for l in links if l.startswith("/") or "warematch.com" in l]; ext = re.findall(r'<a [^>]*href="https?://(?!www\.warematch)[^"]+"[^>]*>', html)
norm = [("https://www.warematch.com" + l if l.startswith("/") else l).rstrip("/") for l in internal]
if len(norm) > 5: fails.append(f"{len(norm)} internal links (max 5)")
if len(set(norm)) != len(norm): fails.append("duplicate internal link target")
for u in norm:
    if u not in inv: fails.append(f"internal link not in site inventory: {u}")
if len(ext) < 2: fails.append("fewer than 2 external links")
if any("nofollow" not in a for a in ext): fails.append("external link missing nofollow")
sections = re.split(r"(?=<h2)", html)
h3n = {re.sub(r"<[^>]+>", "", s.split("</h2>")[0]).strip()[:30]: len(re.findall("<h3", s)) for s in sections[1:]}
print("H3 per section:", h3n)
print("internal:", len(norm), "external:", len(ext), "words:", len(re.sub(r"<[^>]+>", " ", html).split()))
print("FAIL: " + "; ".join(fails) if fails else "PASS template/policy checks"); sys.exit(1 if fails else 0)
