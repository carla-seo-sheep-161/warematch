---
name: seo-dashboard
description: Build and refresh the WareMatch weekly SEO / digital marketing dashboard (static HTML plus CSV exports, archived per run). Use when asked to run the Wednesday refresh, build or change a dashboard page, add a data source, or check dashboard data quality.
---

# WareMatch SEO dashboard

A weekly, human-reviewed retrospective: pull data, save the originals untouched, compute numbers in code, render a dated static HTML page, and have the owner review it before it is shared. Claude writes narrative and audit text on top of computed tables. Claude does not compute the numbers.

## Principles

- Numbers come from scripts. Narrative strings must be generated from the same variables, or checked against them. A hard-coded figure that no longer matches the data must fail the render.
- Every pull goes through one `save()` function that writes `{pulled_at, data}` JSON under `data/raw/run_<id>/<source>/`. Never overwrite a raw file and never write one ad hoc.
- Every event is one line in `data/results/<id>/process_log.md`: `HH:MM | step | source | OK/WARN/FAIL | detail`. Write anomalies as they happen.
- A failed source is flagged, not fatal. Retry once before moving on, and report `n/N tables saved`.
- Compare same-length windows. W = reporting week (Mon to Sun), P = the prior 7 days. Report on Wednesday so Search Console (2 to 3 day lag) settles. Always show a data-through date per source.
- Baseline is the Jun to Aug 2026 average. Goals are year over year.
- The page is a DRAFT until the owner approves it.

## Layout

```
digital_marketing_dashboard/
  src/extract.py, weekly_run.py, weekly_run_extra.py   pulls (read-only)
  src/seogets_capture.py                               connector data, checked against SEOgets totals
  src/weekly_analysis.py                               raw -> results.json (no network)
  src/render_weekly.py                                 results.json -> dashboards/<run>/index.html + exports/*.csv
  src/monthly_compare.py                               month vs month vs baseline vs last year
  data/raw/run_<id>/<source>/                          untouched originals
  data/results/<id>/                                   results.json, process_log.md, observer_notes.md
  data/manual/                                         idea_log.csv, optimized_pages.csv, pagespeed_baseline.csv, ...
  dashboards/<id>/                                     index.html, assets/, exports/ (archived, never deleted)
```

## Sources and auth

| Source | Route | Notes |
|---|---|---|
| Search Console | API, service account via `gcloud` impersonation | Domain property. Use `dataState=all` and treat the last 1 to 2 days as provisional. |
| GA4 | Data API, same service account | Dimensionless reports have no `dimensionValues` key, so use a separate parser. Property timezone differs from GSC (Pacific). |
| SEOgets | claude.ai connector (inside a Claude session only) | Branded filter, content groups, AI referrals (LLMs preset), indexing overview, annotations. Check every table against SEOgets' own totals before saving. |
| Google Ads | GA4 link plus Search Atlas Otto PPC | No Quality Score, change history or Auction Insights until a Ads API developer token exists. Impression share shown as `9.99` / `90.01` means `<10%` / `>90%`. |
| Search Atlas LLM Visibility | API | Scan counts and platform sets differ by period, so periods are not always comparable. Branded prompts inflate visibility. |
| Klaviyo | API key in `.env` | Campaign values report, last 30 days. |
| PageSpeed Insights | API key in `.env` | Slow (about 8 minutes for 6 runs). Run last or in the background, take the median of 3, use a short timeout with retry, and label the source (it differs from the sheet score). |
| Google Sheets | connector | Technical Actions, PageSpeed, idea log. Status text is free-form, so normalise it. |

Secrets live in `.env` outside the repo. Never print or log key values. Never commit IDs, tokens or keys: put them in a local config file.

The `gcloud` login expires, so treat the Wednesday run as human-in-the-loop. Run a preflight token check first and write the result to the log.

## Weekly run (Wednesday)

1. Preflight: token per source, logged.
2. Pull: `weekly_run.py`, then `weekly_run_extra.py`, then the connector sources (SEOgets, Sheets).
3. Checks: reconcile across routes (SEOgets vs GA4 API sessions, GA4 ad cost vs Search Atlas cost), flag key-event jumps, GSC provisional days, anonymised-query share shifts, indexing changes.
4. Analysis: `weekly_analysis.py` writes `results.json`. Branded regex: `ware ?match|warematch|wearmatch|ware-match`. AI referrals are matched by source/medium regex plus the GA4 `AI Assistant` default channel.
5. Render: `render_weekly.py` writes the page and one CSV export per table, linked from each table.
6. Browser review: open the page in Chrome. Scripted checks miss layout bugs.
7. Hand over as a draft with the list of stale or failed sources.

Monthly: headless Screaming Frog crawl (see the `screamingfrog-headless-crawl` skill), diffed against the previous month.

## Page design

- Light theme, Times New Roman, WareMatch palette: Midnight `#001226`, Deep Navy `#01264D`, Primary Navy `#003F81`, Signal Blue `#155DFC`, Sky Blue `#2B7FFF`, Ink `#101828`, Slate `#4A5565`, Steel `#C5D0E0`, Ice `#E6EBF2`, Dock Amber `#F59E0B` (text-safe `#B45309`).
- Left sidebar, one global Compare switch (WoW / MoM / YoY / vs baseline). Overview/Detailed and Branded/Non-branded toggles only on pages that use them.
- Hover definitions on KPI labels and table headers. Hover differences on daily charts. KPI notes carry the prior value and context.
- Add `[hidden]{display:none!important}`, because author CSS `display:flex` overrides the attribute.
- The renderer prints `BLANK COLUMN WARNING` when 40% or more of a column is empty. Split or remove such columns.
- Never link an export that does not exist.
- Do not present key-event growth as lead growth. Explain which event fired, and that new events make comparisons not useful.

## Known pitfalls

- Hand-copying connector output into JSON is error-prone. Automate it or check against totals.
- GA4 `Direct` includes logged-in software users. Use the SEOgets `Exclude Logins` filter before quoting direct or key-event numbers.
- GA4 search queries exist only for clicks that produced sessions, so wasted-spend terms are invisible without Ads search-term data.
- Paid vs organic query overlap is nearly empty because GSC anonymises long queries. Compare at theme or landing-page level.
- Quality Score, rank buckets, indexation state, AI visibility and review counts are point-in-time. The weekly archive is their only history.
- Keywords in the top 3/10/20+ from GSC are average-position buckets, not rank tracking. Label them that way.

## Roadmap

Phase 1 exec summary, SEO overview, channels, changelog, archive. Phase 2 SEM, synergy, technical. Phase 3 GEO and reviews. Phase 4 Klaviyo, LinkedIn, social, podcasts, competitors. Synergy and GEO pages are under review and need redesign.
