# warematch

Claude skills for WareMatch SEO/GEO work.

| Skill | What it does |
|---|---|
| [`skills/seo-content-pipeline`](skills/seo-content-pipeline/SKILL.md) | Keyword-map row to cited, template-locked, NeuronWriter-scored page content; facts files, gates, link picking, case log. |
| [`skills/geo-intent-audit`](skills/geo-intent-audit/SKILL.md) | GEO check for on-site content: intent fit, non-commodity usefulness, AI-search readiness (crawler access, raw HTML, snippet controls), metadata and schema hygiene, with an evidence-graded rubric and sourced references. |

Notes: no API keys are stored here (the pipeline reads them from a local `.env`); `runs/` and raw research samples are git-ignored. Facts files are dated and must be re-verified before reuse.
