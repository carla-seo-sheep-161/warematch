#!/usr/bin/env python3
"""Score each draft with NeuronWriter /evaluate-content (saves nothing) and run repetition/link checks.
usage: compare.py <run>"""
import json, re, sys, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import nw
run = sys.argv[1]
for v in ("top10", "top30", "top-intent"):
    html = open(f"runs/{run}/draft_{v}.md").read().split("\n---")[0]
    q = json.load(open(f"runs/{run}/query_{v}.json"))["query"]
    score = nw.call("evaluate-content", query=q, html=html).get("content_score")
    text = re.sub(r"<[^>]+>", " ", html).lower()
    words = re.findall(r"[a-z']+", text)
    tri = collections.Counter(zip(words, words[1:], words[2:]))
    rep = sum(1 for c in tri.values() if c >= 4)
    ext = re.findall(r'<a [^>]*href="https?://(?!www\.warematch)[^"]*"[^>]*>', html)
    nofollow_ok = all('rel="nofollow' in a for a in ext)
    nums = re.findall(r"\d[\d,.]*%?", text)
    print(f"{v}: NW score={score} words={len(words)} trigrams_repeated>=4x={rep} external_links={len(ext)} all_nofollow={nofollow_ok} numbers={len(nums)}")
