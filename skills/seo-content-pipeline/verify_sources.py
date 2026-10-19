#!/usr/bin/env python3
"""Vet external links in a draft: HTTP status, claimed figure present on the page, domain tier.
usage: verify_sources.py <draft.md>  (checks every <a href=http...> not on warematch.com; 'needle' = figures in the anchor's sentence)"""
import re, sys, urllib.request
TIER = {"gov": 1, ".edu": 1, "nrf.com": 1, "fred.stlouisfed.org": 1, "census.gov": 1, "shopify.com": 2, "flexport.com": 2}
html = open(sys.argv[1]).read().split("\n---")[0]
for m in re.finditer(r'<a [^>]*href="(https?://(?!www\.warematch)[^"]+)"[^>]*>(.*?)</a>', html, re.S):
    url, anchor = m.groups()
    sent = re.sub(r"<[^>]+>", " ", html[max(0, m.start()-300): m.end()+300])
    needles = re.findall(r"\d+(?:\.\d+)?%|\$[\d.]+ ?\w*|\b20\d\d\b", sent)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf8", "ignore"); status = 200
    except Exception as e:
        body, status = "", str(e)[:40]
    found = [n for n in needles if n in body]
    tier = next((v for k, v in TIER.items() if k in url), 3)
    nofollow = 'rel="nofollow' in m.group(0)
    print(f"{url}\n  status={status} tier={tier} nofollow={nofollow} anchor='{re.sub('<[^>]+>','',anchor)[:50]}'\n  figures near link: {needles}  found on page: {found}")
