#!/usr/bin/env python3
"""Technical on-page GEO/SEO check from the team's audit docs (metadata rules, schema architecture, JS-rendering findings).
usage: technical_check.py <url|file.html> [--type location|industry|integration|blog|listing|home] [--primary "3pl us"] [--must "phrase1|phrase2"] [--brand WareMatch] [--ua "UA string"]
Fetches the RAW HTML (no JavaScript executed) so it shows what a non-rendering crawler sees. Network only for URLs; no LLM calls. Prints a markdown report with PASS / WARN / FAIL and evidence."""
import argparse, gzip, html as H, json, re, sys, urllib.request, urllib.parse
ap = argparse.ArgumentParser(); ap.add_argument("target"); ap.add_argument("--type", default="blog"); ap.add_argument("--primary", default="")
ap.add_argument("--must", default=""); ap.add_argument("--brand", default="WareMatch"); ap.add_argument("--ua", default="Mozilla/5.0 (compatible; technical-check/1.0)")
a = ap.parse_args()
LAST_HDRS = {}
def get(url):
    global LAST_HDRS
    req = urllib.request.Request(url, headers={"User-Agent": a.ua, "Accept-Encoding": "gzip"})
    r = urllib.request.urlopen(req, timeout=40); b = r.read(); LAST_HDRS = {k.lower(): v for k, v in r.headers.items()}
    if r.headers.get("Content-Encoding") == "gzip": b = gzip.decompress(b)
    return r.status, b.decode("utf8", "ignore"), r.geturl()
if a.target.startswith("http"):
    status, raw, final = get(a.target); url = final; PAGE_HDRS = dict(LAST_HDRS)
else:
    raw = open(a.target).read(); status, url = 200, ""; PAGE_HDRS = {}
out = []; R = lambda lvl, msg: out.append(f"- {lvl:4s} {msg}")
out.append(f"# Technical check: {a.target}  (type={a.type}, HTTP {status}, {len(raw)//1024} KB raw HTML)\n")
def plain(s): return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
body = re.sub(r"<(script|style|svg|noscript)\b.*?</\1>", "", raw, flags=re.S | re.I)
text = plain(body); words = len(text.split())
# ---- 1 raw-HTML visibility (what a non-JS crawler sees)
out.append("## 1. Visible in the raw HTML (no JavaScript)")
R("PASS" if words >= 500 else "FAIL", f"{words} words of text in the initial HTML" + ("" if words >= 500 else " (looks like an empty app shell: content may be injected by JS)"))
nxt = raw.count("self.__next_f.push"); R("INFO", f"Next.js flight chunks: {nxt} (content can be in the payload yet still be invisible if not in the DOM text)")
h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", raw, re.S | re.I)
R("PASS" if len(h1s) == 1 else "FAIL", f"H1 count in raw HTML: {len(h1s)} {[plain(x)[:60] for x in h1s[:2]]}")
heads = [(int(l), plain(t)) for l, t in re.findall(r"<h([1-6])[^>]*>(.*?)</h[1-6]>", raw, re.S | re.I)]
skips = [(heads[i-1][1][:30], heads[i][1][:30]) for i in range(1, len(heads)) if heads[i][0] - heads[i-1][0] > 1]
R("PASS" if not skips else "WARN", f"heading levels skipped: {skips[:3] or 'none'}; empty headings: {sum(1 for _, t in heads if not t)}")
for m in [x.strip() for x in a.must.split("|") if x.strip()]:
    R("PASS" if m.lower() in text.lower() else "FAIL", f"must-have text present in raw HTML: '{m[:60]}'")
cards = len(re.findall(r"View Details|Get a Quote", raw)); 
if cards: R("INFO", f"listing-style buttons in raw HTML: {cards} (compare with what the page promises; items behind a 'view all' click are not seen by LLMs)")
# ---- 2 metadata (house rules)
out.append("\n## 2. Metadata (team rules: title <=65, description <=160, keyword in first 40, '| WareMatch', write '3PL', CTA, no '...')")
title = plain(re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I).group(1)) if re.search(r"<title", raw, re.I) else ""
dm = re.search(r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)', raw, re.I) or re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description', raw, re.I)
desc = H.unescape(dm.group(1)) if dm else ""
R("PASS" if title and len(title) <= 65 else "FAIL", f"title ({len(title)} chars): {title}")
R("PASS" if desc and len(desc) <= 160 else "FAIL", f"description ({len(desc)} chars): {desc[:120]}{'...' if len(desc)>120 else ''}")
if a.primary: R("PASS" if a.primary.split()[0].lower() in title[:40].lower() else "WARN", f"main keyword '{a.primary}' starts in first 40 chars of title")
R("PASS" if title.rstrip().endswith("| " + a.brand) else "WARN", f"title ends with '| {a.brand}'")
R("FAIL" if desc.rstrip().endswith(("...", "…")) else "PASS", "description not cut off with '...'")
R("WARN" if re.search(r"third[- ]party logistics", title + " " + desc, re.I) else "PASS", "uses '3PL' not 'third-party logistics' in title/description")
R("FAIL" if re.search(r"\{[A-Za-z]+\}|undefined|, ,|\b(\w+) \1\b", title + " " + desc, re.I) else "PASS", "no placeholders / doubled words in title/description")
canon = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', raw, re.I) or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical', raw, re.I)
if canon and url:
    cn = canon.group(1).rstrip("/"); un = url.split("#")[0].split("?")[0].rstrip("/")
    R("PASS" if cn == un else "WARN", f"canonical {canon.group(1)} vs page {url} ({'self-referential' if cn == un else 'DIFFERENT or has parameters'})")
else: R("WARN" if not canon else "INFO", "canonical tag " + ("missing" if not canon else "present"))
rb = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']*)', raw, re.I); R("FAIL" if rb and re.search("noindex", rb.group(1), re.I) else "PASS", f"meta robots: {rb.group(1) if rb else 'none (indexable)'}")
xr = PAGE_HDRS.get("x-robots-tag", "")
sn = [d for d in ("nosnippet", "max-snippet", "noarchive") if d in ((rb.group(1) if rb else "") + " " + xr).lower()]
R("WARN" if "nosnippet" in sn or any(s.startswith("max-snippet") for s in sn) else "PASS", f"snippet controls limiting AI Overviews/AI Mode input (Google: nosnippet / max-snippet): {sn or 'none'}; data-nosnippet elements: {len(re.findall(r'data-nosnippet', raw))}; X-Robots-Tag: {xr or 'none'}")
for p in ("og:title", "og:description", "og:image"): R("PASS" if re.search(r'property=["\']' + p, raw, re.I) else "WARN", f"{p} present")
lm = re.search(r"<html[^>]*lang=.([A-Za-z-]+)", raw, re.I); R("INFO", "<html lang>: " + (lm.group(1) if lm else "missing"))
# ---- 3 structured data
out.append("\n## 3. Structured data (JSON-LD), per the team's schema architecture doc")
blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', raw, re.S | re.I)
R("PASS" if len(blocks) == 1 else "WARN", f"{len(blocks)} JSON-LD script block(s) (doc: one unified @graph per page)")
nodes = []; bad = 0
for b in blocks:
    try: j = json.loads(H.unescape(b.strip()))
    except Exception: bad += 1; continue
    stack = j.get("@graph", [j]) if isinstance(j, dict) else j
    nodes += [n for n in stack if isinstance(n, dict)]
if bad: R("FAIL", f"{bad} JSON-LD block(s) failed to parse")
types = []
for n in nodes:
    t = n.get("@type"); types += t if isinstance(t, list) else [t]
R("INFO", f"types found: {sorted(set(str(t) for t in types))}")
ids = [n.get("@id") for n in nodes if n.get("@id")]; dup = sorted({i for i in ids if ids.count(i) > 1})
R("FAIL" if dup else "PASS", f"duplicate @id (conflicting identity declarations): {dup or 'none'}")
EXP = {"location": ["CollectionPage", "BreadcrumbList", "FAQPage", "HowTo", "Service"], "industry": ["CollectionPage", "Service", "HowTo", "BreadcrumbList"],
       "integration": ["WebPage", "SoftwareApplication", "HowTo", "ItemList", "BreadcrumbList"], "blog": ["BreadcrumbList", "Article|BlogPosting|NewsArticle"],
       "listing": ["LocalBusiness", "BreadcrumbList"], "home": ["Organization", "WebSite", "WebPage"]}
for t in EXP.get(a.type, []):
    ok = any(x in types for x in t.split("|")); R("PASS" if ok else "WARN", f"expected {a.type}-page type present: {t}")
if "LogisticsBusiness" in types: R("FAIL", "type LogisticsBusiness does not exist on schema.org (404); use LocalBusiness (or a real subtype)")
if "FAQPage" in types or "HowTo" in types: R("INFO", "FAQPage/HowTo: Google no longer shows these rich results (HowTo removed 2023; FAQ ended May 2026). Harmless if the content is visible; low priority")
if a.type == "listing" and "Product" in types: R("FAIL", "Product type on a warehouse listing (doc: wrong type; remove)")
for n in nodes:
    if n.get("@type") == "BreadcrumbList" and url:
        items = n.get("itemListElement", []); last = items[-1].get("item") if items else ""
        lastu = last.get("@id", "") if isinstance(last, dict) else last
        R("PASS" if lastu and lastu.rstrip("/").split("?")[0] == url.rstrip("/").split("?")[0] else "FAIL", f"BreadcrumbList last item URL {lastu} matches this page (doc bug: items pointing to the homepage)")
    if "offers" in n and json.dumps(n["offers"]).lower().find("n/a") >= 0: R("FAIL", "offers.price 'N/A' (invalid)")
    if isinstance(n.get("aggregateRating"), dict) and str(n["aggregateRating"].get("ratingValue", "0")) in ("0", "", "None"): R("FAIL", "empty aggregateRating")
    if re.search(r"<[a-z]+[^>]*>", str(n.get("description", ""))): R("FAIL", f"HTML tags inside schema description ({n.get('@type')})")
faq = [n for n in nodes if n.get("@type") == "FAQPage"]
if faq:
    qs = [plain(str(q.get("name", ""))) for q in faq[0].get("mainEntity", []) if isinstance(q, dict)]
    norm = lambda x: re.sub(r"[^a-z0-9 ]", "", x.lower())
    vt = norm(text)
    missing = [q for q in qs if q and norm(q)[:60] not in vt]
    R("PASS" if not missing else "FAIL", f"FAQPage: {len(qs)} questions in schema; {len(qs)-len(missing)} appear in the visible raw-HTML text" + (f"; NOT visible: {[m[:50] for m in missing[:3]]}" if missing else "") + " (schema must match visible content)")
    ans_missing = 0
    for q in faq[0].get("mainEntity", []):
        ans = plain(str((q.get("acceptedAnswer") or {}).get("text", "")))[:50]
        if ans and norm(ans) not in vt: ans_missing += 1
    R("PASS" if not ans_missing else "WARN", f"FAQPage answers whose opening text is not found in the visible text: {ans_missing}")
dm_ = [n.get("dateModified") for n in nodes if n.get("dateModified")]
vis_date = re.search(r"(last updated|updated on|updated:)\s*[A-Za-z0-9 ,/.-]{6,25}", text, re.I)
if a.type in ("blog", "industry", "location"): R("INFO" if (dm_ or vis_date) else "WARN", f"freshness signals: dateModified in schema={bool(dm_)}, visible 'updated' date={bool(vis_date)} (evidence mixed: modest weight; never fake dates)")
# ---- 4 links and images
out.append("\n## 4. Links and images")
links = re.findall(r'<a [^>]*href=["\']([^"\']+)', body, re.I); internal = [l for l in links if l.startswith("/") or "warematch.com" in l]
R("INFO", f"{len(links)} links in raw HTML ({len(internal)} internal)")
imgs = re.findall(r"<img\b[^>]*>", body, re.I); noalt = [i for i in imgs if not re.search(r'alt=["\'][^"\']+', i, re.I)]
R("PASS" if not noalt else "WARN", f"{len(imgs)} images, {len(noalt)} without alt text")
# ---- 5 robots.txt AI bots + llms.txt
if url:
    out.append("\n## 5. Crawler access (robots.txt) and llms.txt")
    root = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    try:
        _, rt, _ = get(root + "/robots.txt"); groups = re.split(r"(?im)^\s*user-agent:\s*", rt)[1:]
        rules = {}
        for g in groups:
            ua = g.splitlines()[0].strip().lower(); rules[ua] = [l.split(":", 1)[1].strip() for l in g.splitlines()[1:] if l.lower().startswith("disallow:") and l.split(":", 1)[1].strip()]
        for bot in ("gptbot", "oai-searchbot", "chatgpt-user", "claudebot", "claude-searchbot", "claude-user", "anthropic-ai", "perplexitybot", "perplexity-user", "google-extended", "ccbot", "bingbot", "googlebot"):
            r = rules.get(bot, rules.get("*", [])); blocked = "/" in r
            R("FAIL" if blocked else "PASS", f"{bot}: {'BLOCKED (Disallow: /)' if blocked else 'not blocked'} {('(specific rules: ' + ', '.join(rules[bot][:4]) + ')') if bot in rules and rules[bot] else ''}")
        R("INFO", "note: ChatGPT-User and Perplexity-User are user-initiated fetchers that may not follow robots.txt (vendor docs); training bots (GPTBot, ClaudeBot) vs search bots (OAI-SearchBot, Claude-SearchBot, PerplexityBot) are separate: blocking training does not block search citations")
        R("INFO", f"paths disallowed for all bots: {rules.get('*', [])[:8]}")
    except Exception as e: R("WARN", f"robots.txt not readable: {str(e)[:60]}")
    try:
        s, t, _ = get(root + "/llms.txt"); R("INFO", f"llms.txt present ({len(t)} bytes). No official AI engine support confirmed; informational only")
    except Exception: R("INFO", "llms.txt not present (not required; no confirmed engine support)")
print("\n".join(out))
