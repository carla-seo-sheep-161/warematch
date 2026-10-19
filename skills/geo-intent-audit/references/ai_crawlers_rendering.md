# AI crawlers, rendering and snippet controls: primary-source notes

Researched 2026-10-19. Confidence: A = read at primary source via WebFetch; B = secondary.
Caveat: WebFetch returns text via a summarizing model, so quotes below are as returned and may be lightly paraphrased. Re-verify wording against the live page before quoting externally.

## 1. Google (Search Central)

| Claim | Quote | URL | Publisher / date | Conf | Checker implication |
|---|---|---|---|---|---|
| AI Overviews/AI Mode need no extra technical requirements beyond Search eligibility | "There are no additional technical requirements." | https://developers.google.com/search/docs/appearance/ai-features | Google; updated 2025-12-10 | A | Test only normal indexability: 200, not noindex, not blocked, snippet-eligible. |
| Page must be eligible for a snippet | "eligible to be shown in Google Search with a snippet" | same | same | A | Flag nosnippet / max-snippet:0 as blocking AI-feature eligibility. |
| No special markup | "no special schema.org structured data that you need to add" | same | same | A | Schema is not an AI-eligibility gate; do not report missing schema as a GEO blocker. |
| No AI text files (covers llms.txt by implication; llms.txt itself is not named on this page) | "You don't need to create new machine readable files, AI text files, or markup" | same | same | A | llms.txt = informational only. |
| Preview controls must be visible to Googlebot | "Make sure that the preview control is correct and visible to Googlebot." | same | same | A | Check controls in raw HTML/headers and that robots.txt does not hide the page. |
| Controls: nosnippet, data-nosnippet, max-snippet, noindex | (page lists these as the controls) | same | same | A | Inventory these per page. |
| nosnippet / max-snippet apply to AI Overviews and AI Mode | "used as a direct input for AI Overviews and AI Mode" | https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag | Google; updated 2026-03-24 | A | Treat nosnippet and any max-snippet cap as limiting AI citation text. data-nosnippet and noindex: AI features not mentioned on this page (unverified for AI). |
| Google renders JS | "runs JavaScript with an evergreen version of Chromium" | https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics | Google; updated 2026-03-04 | A | Googlebot-based features can see JS content, but rendering is queued; still prefer content in initial HTML. |
| Google-Extended does not affect Search | "does not impact a site's inclusion in Google Search" | https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers | Google; updated 2026-10-15 | A | Blocking Google-Extended is not a way to opt out of AI Overviews, and does not hurt Search. It governs Gemini training/grounding (Gemini Apps, Vertex AI). Opt-out of AI Overviews goes through snippet controls. |

Note: the AI-features page itself says Google-Extended limits "AI training and grounding in some of Google's other systems" (A). The overview-of-crawlers and special-case-crawlers pages did not mention Google-Extended when fetched.

## 2. OpenAI  (https://developers.openai.com/api/docs/bots; old URL platform.openai.com/docs/bots 301s here). Publisher OpenAI; no date shown on fetched text. Conf A.

| Bot | Quote | Implication |
|---|---|---|
| GPTBot (training) | "Disallowing GPTBot indicates a site's content should not be used" | Disallowing it affects training only; check but do not equate with search visibility. |
| OAI-SearchBot (ChatGPT search) | "Sites that are opted out of OAI-SearchBot will not be shown" | Must be allowed for ChatGPT search citations. Robots.txt changes take about 24h (page). |
| ChatGPT-User (user actions) | "robots.txt rules may not apply." | Page says it is user-initiated and not used for Search eligibility. Blocking it in robots.txt may not be honored; do not rely on it. |

No JavaScript statement found on this page (unknown).

## 3. Anthropic  https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler  (Anthropic Help Center; April 7, 2026; A)

- ClaudeBot: training collection. Claude-User: fetches when a user asks. Claude-SearchBot: indexes content to improve search result relevance.
- Quote: "honoring industry-standard robots.txt directives" (paraphrase-level, as returned). Also supports non-standard Crawl-delay. Page says blocking by IP may not work because bots then cannot read robots.txt.
- Page says blocking Claude-SearchBot may reduce visibility and accuracy in search results; blocking Claude-User may reduce visibility in user-directed search.
- Implication: check ClaudeBot, Claude-SearchBot and Claude-User separately; blocking ClaudeBot alone is training-only. No JavaScript statement found (unknown).

## 4. Perplexity  https://docs.perplexity.ai/guides/bots  (Perplexity docs; no date shown; A)

- PerplexityBot: surfaces/links sites in Perplexity results; "not used to crawl content for AI foundation models." Allow in robots.txt (and its published IP ranges) to appear.
- Perplexity-User: user-initiated; "generally ignores robots.txt rules."
- Implication: check PerplexityBot allowed in robots.txt and not WAF-blocked; robots.txt does not control Perplexity-User. No JavaScript statement found (unknown).

## 5. Microsoft Bing / Copilot

- Bing Webmaster Blog, "Introducing AI Performance in Bing Webmaster Tools Public Preview", 2026-02-10, https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview (A). Quote: "Bing respects all content owner preferences expressed through robots.txt" (as returned). Shows citations in Copilot, Bing AI summaries and partners; sampled data. Implication: Bing/Copilot eligibility follows Bing indexing plus robots.txt; use Bing Webmaster Tools AI Performance for validation.
- Bing Webmaster Blog, 2023-09-22, https://blogs.Bing.com/webmaster/september-2023/Announcing-new-options-for-webmasters-to-control-usage-of-their-content-in-Bing-Chat (A). Quote: "Content tagged NOARCHIVE will not be included in Bing Chat answers." NOCACHE: only URL, title, snippet shown. Both tags: treated as NOCACHE. It covers Bing Chat (2023), not explicitly Copilot today. Implication: flag noarchive/nocache meta on pages meant to be cited.
- Bing Webmaster Guidelines https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a : WebFetch returned only a title (client-rendered), so NOT read (unknown). Search Engine Journal (secondary, B, 2026-02-27, https://www.searchenginejournal.com/bing-adds-geo-to-official-guidelines-expands-ai-abuse-definitions/568442) reports the guidelines now name GEO/grounding/citations and that JS rendering guidance was removed. Unverified at the primary source; read the page in a browser before relying on it.
- Bing JS rendering statement: no official statement obtained.

## 6. JavaScript execution by AI crawlers

- Official: Googlebot yes (section 1, A). No official statement found from OpenAI, Anthropic, Perplexity or Microsoft on JS execution (unknown).
- SECONDARY (B): Vercel + MERJ, "The rise of the AI crawler", published 2024-12-17, https://vercel.com/blog/the-rise-of-the-ai-crawler. Method: server logs from nextjs.org and Vercel network over several months, cross-checked on two job sites. Finding: GPTBot, ClaudeBot (fetches JS files but does not execute) and PerplexityBot do not render JS; AppleBot and Googlebot/Gemini do. Caveats: nearly two years old, logs-based, only those crawlers at that time, covers training/index crawlers, not necessarily user-triggered fetchers. Treat as a strong prior, not a guarantee.
- Implication: critical content (answer text, headings, specs, prices, links, canonical, robots meta) should be in the initial HTML response.

## 7. llms.txt

- Google: Search docs say no AI text files needed (A, above); llms.txt not named. No official Google page found supporting llms.txt. Mueller/Illyes remarks ("purely speculative", "won't crawl") seen only via secondary reports (Search Engine Journal / Search Engine Land via search results, not fetched): unverified. Chrome Lighthouse reportedly added an experimental llms.txt audit: unverified.
- OpenAI, Anthropic, Perplexity, Microsoft: NO CONFIRMED SUPPORT. No official docs mentioned llms.txt (the pages above do not; Bing article does not).
- Unverified claims seen: Ahrefs "97% of llms.txt files received zero requests (May 2026)"; "Anthropic publishes its own llms.txt" (vendor/blog sources, not evidence).

## Checks to implement

1. robots.txt per-bot (fact: separate bots per vendor, sections 2-5)
   - Parse robots.txt and report allow/block status for: Googlebot, Google-Extended, Bingbot, OAI-SearchBot, GPTBot, ChatGPT-User, Claude-SearchBot, ClaudeBot, Claude-User, PerplexityBot, Perplexity-User.
   - Classify: search-citation bots (Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot) blocked = HIGH visibility risk; training bots (GPTBot, ClaudeBot, Google-Extended) blocked = informational (Google-Extended does not affect Search; OpenAI/Anthropic say training); user fetchers (ChatGPT-User, Claude-User, Perplexity-User) = informational, robots.txt may not apply.
   - Also test the page URL itself is not disallowed for Googlebot (blocked pages are not rendered).
   - Check WAF/CDN: fetch with each UA string and compare status (Perplexity and Anthropic docs mention IP ranges/robots reading).
2. Rendering / initial HTML (facts: Googlebot renders in a queue; no official JS statement from others; Vercel study B)
   - Fetch raw HTML without JS; assert main answer text, H1/H2s, key facts, internal links, canonical, title are present; diff vs rendered DOM (Screaming Frog stored vs rendered HTML). Flag content only present after JS as MEDIUM-HIGH risk, labelled "unconfirmed, based on secondary study".
   - Assert HTTP 200 (non-200 may skip rendering).
3. Meta / snippet controls (facts: Google AI-features and robots-meta pages; Bing 2023 post)
   - Detect in HTML and X-Robots-Tag: noindex, nosnippet, max-snippet (flag 0 or very low), data-nosnippet around key answer blocks, noarchive, nocache. nosnippet/max-snippet = confirmed AI Overviews/AI Mode limit; noarchive/nocache = Bing/Copilot (2023 Bing Chat wording).
   - Confirm controls are visible in the HTML Googlebot receives.
4. Do NOT score: schema.org presence as an AI-eligibility gate (Google says not required; still fine for other reasons), special AI files.
5. llms.txt: informational only. Report presence/absence, never a pass/fail. Note "no confirmed support from Google, OpenAI, Anthropic, Perplexity, Microsoft".
6. Bing: recommend verifying in Bing Webmaster Tools (AI Performance report) and reading the Bing guidelines page in a browser (not read here).

## Unknown / not established
- Any official JS-execution statement from OpenAI, Anthropic, Perplexity, Microsoft.
- Current Bing Webmaster Guidelines text (page not readable via fetch).
- Dates for OpenAI and Perplexity bot pages.
- Whether data-nosnippet / noindex are documented as affecting AI features (page does not say).
