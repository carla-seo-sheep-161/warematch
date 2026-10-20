#!/usr/bin/env python3
"""Regression run: re-check every page config that has a 'final_draft'. Run after ANY change to optimize.py / check_page.py / audit.py.
usage: regress.py   -> prints a table: template/policy check, score gate, basic-term coverage, over-used terms. Exit 1 if any page FAILS."""
import glob, json, subprocess, sys
bad = 0
print(f"{'page':16s} {'template':9s} {'gate':6s} detail")
for p in sorted(glob.glob("configs/*.json")):
    name = p.split("/")[-1][:-5]
    if name.startswith("_"): continue
    c = json.load(open(p))
    if not c.get("final_draft"): continue
    mode = c.get("mode", "-"); args = ["python3", "-I", "check_page.py", c["final_draft"], mode] + ([c["locked_json"]] if c.get("locked_json") else [])
    t = subprocess.run(args, capture_output=True, text=True); tmpl = "PASS" if t.returncode == 0 else "FAIL"
    o = subprocess.run(["python3", "-I", "optimize.py", name, c.get("gate_brief", "top10"), c["final_draft"]], capture_output=True, text=True)
    out = (o.stdout + o.stderr).strip().splitlines(); gate = "PASS" if o.returncode == 0 else "FAIL"
    cov = next((l for l in out if l.startswith("term coverage")), ""); last = out[-1] if out else ""
    print(f"{name:16s} {tmpl:9s} {gate:6s} {last[:110]}\n{'':32s}{cov[:110]}")
    bad += (tmpl == "FAIL") + (gate == "FAIL")
sys.exit(1 if bad else 0)
