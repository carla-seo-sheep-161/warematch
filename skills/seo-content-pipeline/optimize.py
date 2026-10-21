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
import os as _os
_cfg0 = {**json.load(open("configs/_defaults.json")), **json.load(open(f"configs/{run}.json"))}
_tag = (_cfg0.get("briefs") or {}).get(v, v)
a = json.load(open(f"runs/{run}/analysis_{_tag}.json")); q = json.load(open(f"runs/{run}/query_{_tag}.json"))["query"]
_d = json.load(open("configs/_defaults.json")); _p = json.load(open(f"configs/{run}.json"))
cfg = {**_d, **_p}; cfg["skip_terms_regex"] = "|".join(x for x in (_d.get("skip_terms_regex"), _p.get("skip_terms_regex")) if x)  # defaults + page-specific, never replace
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
        elif n > hi and not re.search(cfg.get("over_ignore_regex", "$^"), t["t"], re.I): over.append(f"- '{t['t']}': used {n}x, MAX {hi}x — reduce")
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
chk = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_page.py"), path, cfg.get("mode", "-")] + ([cfg["locked_json"]] if cfg.get("locked_json") else []), capture_output=True, text=True)
page_ok = chk.returncode == 0
_basic = [t for t in a["terms"]["content_basic"] if not SKIP.search(t["t"])]
_bmiss = [t["t"] for t in _basic if count(t["t"]) < t["sugg_usage"][0]]
_bcov = (len(_basic) - len(_bmiss)) / max(len(_basic), 1)
_ext = [t for t in a["terms"]["content_extended"] if not SKIP.search(t["t"])]
_ecov = sum(1 for t in _ext if count(t["t"]) >= t["sugg_usage"][0]) / max(len(_ext), 1)
print(f"term coverage: basic {_bcov:.0%} (missing {_bmiss}), extended {_ecov:.0%}" + ("  <-- WARN: run the easy-terms sweep" if _ecov < cfg.get("ext_cov_warn", 0.4) else ""))
# editor-feedback gates (Case 5): intro must name configured entities; commodity-framing phrases banned in authored copy; storm mentions capped
_intro = (re.search(r"<h1>.*?</h1>\s*<p>(.*?)</p>", html, re.S) or [None, ""])[1]
_intro_miss = [r for r in cfg.get("intro_must", []) if not re.search(r, _intro, re.I)]
_locked = set(l.strip() for l in open(cfg["locked_text_file"])) if cfg.get("locked_text_file") and os.path.exists(cfg["locked_text_file"]) else set()
_ban = re.compile(cfg.get("banned_authored_regex") or r"(?!x)x", re.I)
_banned = [m.group(0) for l in html.splitlines() if re.sub(r"<[^>]+>", "", l).strip() not in _locked for m in [_ban.search(re.sub(r"<[^>]+>", "", l))] if m]
_storm = len(re.findall(r"hurricane|storm", text))
_fb_ok = not _intro_miss and not _banned and _storm <= cfg.get("storm_max", 99)
print(f"feedback gates: intro missing {_intro_miss}; banned phrases {_banned}; storm mentions {_storm}/{cfg.get('storm_max', 'n/a')} -> {'ok' if _fb_ok else 'FAIL'}")
ok = _fb_ok and page_ok and score is not None and _bcov >= cfg.get("basic_cov_min", 0.9) and score >= target and not over and all('rel="nofollow' in x for x in ext) and len(ext) >= 2
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
