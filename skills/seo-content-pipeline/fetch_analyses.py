import json, sys, time
sys.path.insert(0, '.')
import nw
run = sys.argv[1]
modes = sys.argv[2].split(",") if len(sys.argv) > 2 else ["top-intent"]  # default: ONE query per page (top-intent); pass "top10,top-intent" to compare
for mode in modes:
    q = json.load(open(f"runs/{run}/query_{mode}.json"))["query"]
    for _ in range(40):
        d = nw.call("get-query", query=q)
        if d.get("status") == "ready": break
        time.sleep(5)
    json.dump(d, open(f"runs/{run}/analysis_{mode}.json", "w"), indent=2)
    print(mode, d.get("status"), d.get("metrics", {}).get("word_count"), len(d.get("competitors", [])))
