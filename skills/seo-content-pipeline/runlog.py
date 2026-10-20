#!/usr/bin/env python3
"""Time + token + dollar log per page run.
usage: runlog.py start <run> <stage> | stop <run> <stage> | tokens <run> <label> <input_tok> <output_tok> [cache_read_tok] | summary <run>
Writes runs/<run>/runlog.jsonl. Token counts come from the session counter / subagent reports (scripts cannot see them): enter them by hand.
Prices (USD per 1M tokens, claude-sonnet-5-5, from the Claude API reference 2026-10): input 2.00, output 10.00, cache read 0.20, cache write 2.50.
Real bills also include the whole conversation being re-read on every tool call (cache reads); estimate that with: calls x average_context_tokens x 0.20 / 1e6."""
import json, os, sys, time
P = {"in": 2.00, "out": 10.00, "cache_read": 0.20}
cmd, run = sys.argv[1], sys.argv[2]; os.makedirs(f"runs/{run}", exist_ok=True); path = f"runs/{run}/runlog.jsonl"
def add(d): open(path, "a").write(json.dumps({**d, "t": time.time()}) + "\n")
if cmd in ("start", "stop"): add({"event": cmd, "stage": sys.argv[3]})
elif cmd == "tokens": add({"event": "tokens", "label": sys.argv[3], "in": int(sys.argv[4]), "out": int(sys.argv[5]), "cache_read": int(sys.argv[6]) if len(sys.argv) > 6 else 0})
elif cmd == "summary":
    ev = [json.loads(l) for l in open(path)]; starts = {}; secs = 0
    for e in ev:
        if e["event"] == "start": starts[e["stage"]] = e["t"]
        elif e["event"] == "stop" and e["stage"] in starts: secs += e["t"] - starts.pop(e["stage"])
    tk = [e for e in ev if e["event"] == "tokens"]; i = sum(e["in"] for e in tk); o = sum(e["out"] for e in tk); c = sum(e["cache_read"] for e in tk)
    cost = (i * P["in"] + o * P["out"] + c * P["cache_read"]) / 1e6
    print(f"time {secs/60:.1f} min | tokens in {i:,} out {o:,} cache-read {c:,} | est. ${cost:.2f} (excludes unmeasured context re-reads)")
