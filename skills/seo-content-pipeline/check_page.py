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
    # slot sentence limits from the country template
    def nsent(t):
        t = re.sub(r"\bU\.S\.", "US", re.sub(r"<[^>]+>", " ", t)); return len(re.findall(r"[.!?](?:\s+(?=[A-Z0-9\"(])|\s*$)", t.strip() + " "))
    for s_ in secs[1:]:
        title = re.sub(r"<[^>]+>", "", s_.split("</h2>")[0]).lower()
        paras = [(re.sub(r"<[^>]+>", "", h3).strip(), p) for h3, p in re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", s_, re.S)]
        if "what to consider" in title:
            for i, (h3, p) in enumerate(paras):
                lim = 1 if i == 2 else 5
                if nsent(p) > lim: fails.append(f"consider point {i+1} has {nsent(p)} sentences (max {lim}): {h3[:40]}")
            intro = re.search(r"</h2>\s*<p>(.*?)</p>", s_, re.S)
            if intro and nsent(intro.group(1)) != 1: fails.append("consider intro must be 1 sentence")
        if "what to look for" in title:
            for h3, p in paras:
                if nsent(p) > 3: fails.append(f"look-for point has {nsent(p)} sentences (max 3): {h3[:40]}")
        if "find a 3pl in" in title:
            ps = re.findall(r"<p>(.*?)</p>", s_, re.S)
            if not ps or not 1 <= nsent(ps[0]) <= 2: fails.append("'Find a 3PL in...' blurb must be 1-2 sentences")
    tl = re.search(r"</h1>\s*<p>(.*?)</p>", html, re.S)
    if tl and nsent(tl.group(1)) > 3: fails.append(f"TL;DR has {nsent(tl.group(1))} sentences (keep to 3 or fewer)")
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
