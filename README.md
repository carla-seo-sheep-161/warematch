# warematch

Claude skills for WareMatch SEO/GEO work.

| Skill | What it does |
|---|---|
| [`skills/seo-content-pipeline`](skills/seo-content-pipeline/SKILL.md) | Keyword-map row to cited, template-locked, NeuronWriter-scored page content; facts files, gates, link picking, case log. |
| [`skills/geo-intent-audit`](skills/geo-intent-audit/SKILL.md) | Judges GEO relevance, search-intent fit and real usefulness beyond the surface SEO score. |

Notes: no API keys are stored here (the pipeline reads them from a local `.env`); `runs/` and raw research samples are git-ignored. Facts files are dated and must be re-verified before reuse.
