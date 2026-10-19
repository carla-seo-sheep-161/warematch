#!/usr/bin/env python3
"""Build a drafting prompt for one NeuronWriter variant.
usage: build_prompt.py <run> <variant: top10|top30|top-intent> <config.json>
config.json holds the sheet row + paths (see configs/shopify-3pl.json). Output: runs/<run>/prompt_<variant>.md"""
import json, sys
run, variant, cfg_path = sys.argv[1:4]
cfg = json.load(open(cfg_path))
a = json.load(open(f"runs/{run}/analysis_{variant}.json"))
t = a["terms_txt"]
ideas = a.get("ideas", {})
def lines(x, n=None):
    x = x if isinstance(x, list) else str(x).splitlines()
    x = [i.get("q", i) if isinstance(i, dict) else i for i in x]
    return "\n".join(f"- {i}" for i in x[:n])
comp = a["competitors"][:10]
outline = "\n".join(f"{c['rank']}. {c['title']} ({c.get('word_count')} words, score {c.get('content_score')})" for c in comp)
tmpl = open("templates/prompt_template.md").read()
fill = {
 "PAGE_URL": cfg["page_url"], "H1_SHEET": cfg["h1"], "PRIMARY": cfg["primary"],
 "SECONDARY": cfg["secondary"], "LONGTAIL": cfg["longtail"],
 "WORD_TARGET": a["metrics"]["word_count"]["target"], "READABILITY": a["metrics"]["readability"]["target"],
 "NW_TITLE": t["title"], "NW_H1": t["h1"], "NW_H2": t["h2"],
 "NW_BASIC": t["content_basic_w_ranges"], "NW_ENTITIES": t["entities"],
 "PAA": lines(ideas.get("people_also_ask", []), 15), "QUESTIONS": lines(ideas.get("suggest_questions", []), 15),
 "SERP": outline, "SKELETON": open(cfg["skeleton"]).read(), "FACTS": open(cfg["facts"]).read(),
 "EXISTING_PROBLEMS": cfg["existing_problems"], "VARIANT": variant,
}
for k, v in fill.items(): tmpl = tmpl.replace("{{%s}}" % k, str(v))
open(f"runs/{run}/prompt_{variant}.md", "w").write(tmpl)
print(variant, len(tmpl.split()), "words in prompt")
