# References index and verdicts (compiled 2026-10-21). Grades: A primary official, B original-data study, C academic by analogy, D marketing/unverified.
Files: ai_crawlers_rendering.md (crawler access, rendering, snippet controls, llms.txt) · structured_data.md (schema status + team-doc verdict table) · content_evidence.md (26 official-guidance rows, 9 original-data rows, studies, evidence table).
Re-read at the source by the lead (2026-10-21): Google AI optimization guide and AI features page; Google Search updates changelog (FAQ/HowTo); schema.org type pages.

## Established
- Google: "optimizing for generative AI search is optimizing for the search experience, and thus still SEO"; non-commodity = "unique expert or experienced takes that go beyond common knowledge"; no chunking, llms.txt, special schema.org markup or AI-specific writing needed (guide updated 2026-07-10). AI features need only an indexed, snippet-eligible page; nosnippet/max-snippet limit AI Overviews input (AI features page 2025-12-10; robots meta docs).
- Google ended FAQ rich results (no longer shown from 2026-05-07; docs removed 2026-06-15; limited to gov/health since 2023-09) and removed HowTo (2023-09-14).
- schema.org/LogisticsBusiness does not exist (404). LocalBusiness, MovingCompany, SelfStorage, CollectionPage, ItemList exist.
- OpenAI, Anthropic, Perplexity run separate training / search / user-fetch bots; search bots honor robots.txt; user-initiated fetchers may not. Blocking training bots does not block search citations.
- Googlebot renders JavaScript (queued, evergreen Chromium).
## Unknown / weak
- Whether non-Google AI crawlers execute JavaScript: no official statement; one 2024 third-party log study says GPT/Claude/Perplexity bots do not. Treat "content in initial HTML" as a prudent default.
- llms.txt: no confirmed support from any major vendor (Google says unnecessary). Informational only.
- Schema as an AI citation lever: Ahrefs causal test (1,885 treated pages vs 4,000 controls, 2026-05) showed no measurable change (AI Mode +2.4%, ChatGPT +2.2%, both indistinguishable from zero; AI Overviews -4.6%). Microsoft says schema-marked pages, FAQs and tables help its AI interpret content (qualitative, 2025-11-20).
- Quotations/statistics/citations: GEO paper (KDD 2024) found ~30-40% gains on its metric; C-SEO Bench re-tests found most edits ineffective or harmful on citation rank. Benchmarks are generic QA/e-commerce, not 3PL/B2B.
- Freshness: assistants cite fresher pages (Ahrefs 2025), Google AI Overviews showed no preference; fake dates flip pairwise preferences in a lab study. Weakest claims to avoid repeating: schema or llms.txt as lifts, "chunk to N words", position-in-page percentages, "3-10x for original research".
## Team schema doc (Sept 2026) vs evidence
| Recommendation | Verdict |
|---|---|
| One unified @graph, no duplicate @id | Supported as tidy practice (JSON-LD 1.1 merges same-@id nodes within one document; cross-block merging unverified) |
| Organization / LocalBusiness (name+address) / BreadcrumbList with real URLs | Supported by Google docs |
| LocalBusiness + LogisticsBusiness | OUTDATED/INVALID: LogisticsBusiness does not exist; drop it |
| FAQPage, HowTo | Outdated as a rich-result tactic; harmless if the content is visible; low priority |
| CollectionPage, ItemList, Place/containedInPlace, Service/areaServed, WebPage, About/ContactPage | Valid, low value (no Google or Bing feature) |
| SoftwareApplication | No rich result without offers.price plus a real rating/review |
| aggregateRating / review | Only with real data (supported rule) |
| speakable | Beta, US English only: skip |
| Person nodes for the team | Unverified |
