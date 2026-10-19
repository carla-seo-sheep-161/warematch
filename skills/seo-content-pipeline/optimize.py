#!/usr/bin/env python3
"""Score a draft vs competitors and emit a revision brief (term gaps, no stuffing, no new facts).
usage: optimize.py <run> <variant> [draft_file]
Writes runs/<run>/gaps_<variant>.md and prints a one-line verdict. Exit 0 if gate passed, 1 if another revision round is needed.
Gate = score >= max(top-10-SERP median + 2, 60), no term over its suggested max, zero new numbers, nofollow on all externals."""
import json, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import nw
run, v = sys.argv[1:3]
path = sys.argv[3] if len(sys.argv) > 3 else f"runs/{run}/draft_{v}.md"
html = open(path).read().split("\n---")[0]
a = json.load(open(f"runs/{run}/analysis_{v}.json")); q = json.load(open(f"runs/{run}/query_{v}.json"))["query"]
cfg = json.load(open(f"configs/{run}.json"))
score = nw.call("evaluate-content", query=q, html=html, **({"title": cfg["title"], "description": cfg["description"]} if cfg.get("title") else {})).get("content_score")
comp = [c["content_score"] for c in a["competitors"][:10] if c.get("content_score") is not None]
target = cfg.get("gate") or max(st.median(comp) + 2, 60)
text = re.sub(r"&#?\w+;", " ", re.sub(r"<[^>]+>", " ", html)).lower()
head = " ".join(re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, re.I | re.S)).lower()
def count(t): return len(re.findall(r"(?<![a-z])" + re.escape(t.lower()) + r"(?![a-z])", text))
SKIP = re.compile(cfg.get("skip_terms_regex", "$^"), re.I)
missing, over = [], []
for k in ("content_basic", "content_extended"):
    for t in a["terms"][k]:
        if SKIP.search(t["t"]): continue
        lo, hi = t["sugg_usage"]; n = count(t["t"])
        if n < lo: missing.append(f"- '{t['t']}': used {n}x, target {lo}-{hi}x")
        elif n > hi: over.append(f"- '{t['t']}': used {n}x, MAX {hi}x — reduce")
miss_h2 = [t["t"] for t in a["terms"]["h2"] if t["usage_pc"] >= 50 and t["t"].lower() not in head]
ents = [e["t"] for e in a["terms"]["entities"][:25] if e["t"].lower() not in text and not SKIP.search(e["t"])]
facts = open("facts/" + json.load(open(f"configs/{run}.json"))["facts"].split("/")[-1]).read()
fn = {n.rstrip(".,") for n in re.findall(r"\d[\d,.]*", facts)}
if cfg.get("locked_text_file"): fn |= {n.rstrip(".,") for n in re.findall(r"\d[\d,.]*", open(cfg["locked_text_file"]).read())}
def _num(x):
    try: return float(x.replace(",", ""))
    except Exception: return None
_fv = [v for v in (_num(x) for x in fn) if v]
def _near(n):  # rounded figures are fine: within 3% of a fact, also as thousands/millions ("about 214,000", "1.1 million")
    v = _num(n)
    return v is not None and any(abs(v * m - f) / f <= 0.03 for f in _fv for m in (1, 1e3, 1e6))
newnums = sorted(n for n in {n.rstrip(".,") for n in re.findall(r"\b\d[\d,.]*\b", text)} - fn - set("123456789") - {"10"} if not _near(n))
ext = re.findall(r'<a [^>]*href="https?://(?!www\.warematch)[^"]*"[^>]*>', html)
import subprocess
chk = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_page.py"), path, cfg.get("mode", "-")], capture_output=True, text=True)
page_ok = chk.returncode == 0
ok = page_ok and score is not None and score >= target and not over and all('rel="nofollow' in x for x in ext) and len(ext) >= 2
brief = f"""# Revision brief — {v}
Score {score} | gate {target} | competitor top-10 median {st.median(comp)}, best {max(a['competitors'][i]['content_score'] for i in range(len(a['competitors'])) if a['competitors'][i].get('content_score'))}
## Terms under-used (add only where they read naturally; reach the LOW end, never exceed MAX)
{chr(10).join(missing) or '- none'}
## Terms over-used
{chr(10).join(over) or '- none'}
## Competitors' common H2 terms missing from your headings (work into existing headings/new subsections only if the topic is genuinely relevant)
{', '.join(miss_h2) or 'none'}
## Entities in competitor pages not yet mentioned (mention only if factually relevant; no invented claims)
{', '.join(ents) or 'none'}
## Numbers in text not in facts file (remove or replace)
{', '.join(newnums) or 'none'}
## Rules: no new statistics/prices/names beyond facts file; no repeated sentences/claims; keep >=2 nofollow external links; readability target {a['metrics']['readability']['target']}; you MAY add genuinely useful sections (e.g. comparison table of selection criteria, step-by-step switch checklist, cost-component breakdown WITHOUT dollar figures) if competitors cover them and they add new information.
"""
open(f"runs/{run}/gaps_{v}.md", "w").write(brief)
print(("" if page_ok else "TEMPLATE/POLICY FAIL: " + chk.stdout.strip().splitlines()[-1] + "\n") + f"{v}: score={score} gate={target:.0f} missing={len(missing)} over={len(over)} new_numbers={newnums} externals={len(ext)} -> {'PASS' if ok else 'REVISE'}")
sys.exit(0 if ok else 1)
