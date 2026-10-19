#!/usr/bin/env python3
"""Download the public site_keyword_map sheet as CSV -> site_inventory.json (internal-link candidates).
usage: fetch_inventory.py [sheet_id]"""
import csv, io, json, os, sys, urllib.request
SID = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KEYWORD_MAP_SHEET_ID")
if not SID: sys.exit("usage: fetch_inventory.py <sheet_id> [gid]  (or set KEYWORD_MAP_SHEET_ID); the sheet must be link-readable")
GID = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("KEYWORD_MAP_GID", "0")  # gid of the site_keyword_map tab
url = f"https://docs.google.com/spreadsheets/d/{SID}/export?format=csv&gid={GID}"
rows = list(csv.DictReader(io.StringIO(urllib.request.urlopen(url, timeout=60).read().decode())))
inv = [{"url": r["Page URL"].strip(), "type": r["Page Type"], "h1": r["H1"], "primary": r["Primary Keyword [SV]"],
        "secondary": r["Secondary Keywords [SV]"], "status": r["Content Status / Notes"], "redirect": r["Redirect / Merge"]}
       for r in rows if r["Page URL"].startswith("https://www.warematch.com")]
json.dump(inv, open("site_inventory.json", "w"), indent=1)
print(len(inv), "pages")
