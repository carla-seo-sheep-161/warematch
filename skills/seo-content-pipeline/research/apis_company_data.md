# Company-data APIs for programmatic 3PL location pages: research

Retrieval date for every source below: 2026-10-19. Method: WebFetch/WebSearch of official docs, pricing and terms pages only. No accounts created, no keys entered, no API calls made. Page text was summarised by the fetch tool, so quotes are as returned by that tool; re-verify before any contract or spend. "UNVERIFIED" marks anything not confirmed on an official page.

Context: ~400 location pages (country, state/province, city) for WareMatch, a 3PL marketplace.

---

## Summary table

| API | Usefulness (1-5) | Can publish aggregates on a marketing page? | Verdict |
|---|---|---|---|
| Brandfetch | 2 | Logos: yes only for WareMatch's own customers/partners with permission, hotlinked via `<img>`; not for generic "companies in this city" | Narrow use only (WareMatch's own partner/customer logos) |
| OpenCorporates | 2-3 | Allowed, but ODbL share-alike and a "from OpenCorporates" hyperlink are required on the free tier; paid plans remove share-alike | Possible but weak: registry industry coding is a poor proxy for "3PLs" |
| BuiltWith | 3 | No: ToS prohibits publicly reproducing/distributing BuiltWith data | Not viable for published stats without a written licence |
| Store Leads | 4 on data quality, 2 on legality | No: ToS prohibits republishing data in any form without permission | Not viable without written permission; ask for it |
| TikTok Research / Commercial Content | 1 | No: commercial use barred; sharing derived data barred | Not viable |

---

## 1. Brandfetch

### a) Access
- Free tier exists: $0, "No cost, no card, no hassle." Free: 100 brand fetches one-time (Brand API and Brand Context API), 1M Logo API renders per month, 500K Brand Search calls per month, best-effort support. Source: https://brandfetch.com/developers/pricing
- Growth: $99/month on the pricing card, up to 2,500 brand fetches per month, overage $0.10 per fetch; yearly billing saves 23%. The same page's FAQ says "$129/month (or $1188/yearly)". The page contradicts itself, so the price is UNVERIFIED (confirm at checkout). Source: https://brandfetch.com/developers/pricing
- Custom: "Let's talk", more than 10,000 fetches per month, custom licensing terms. 40% off for qualified startups and nonprofits for 12 months. Same source.
- Key / client ID: Brand API uses `Authorization: Bearer <key>`. Logo API needs a free client ID on every request ("To use Logo API, you must include your client ID with every request"). Sources: https://docs.brandfetch.com/reference/brand-api and https://docs.brandfetch.com/docs/logo-api
- Rate limits (Logo API): 1,000 requests per 5 minutes per IP, 2,400 per 5 minutes per customer; 1M per month on free is a soft limit. Brand API numeric rate limits are not stated on the fetched page. Every 404 consumes a credit. Source: Logo API docs above.

### b) Endpoints and fields
- Brand API: `GET https://api.brandfetch.io/v2/brands/{identifier}` (domain, ticker, ISIN, crypto, email, URL), plus explicit `/v2/brands/domain/{domain}`. Optional `palette=true`, `cachedOnly=true`. Source: https://docs.brandfetch.com/reference/brand-api
- Fields: name, domain, description, longDescription, social links, logos (svg/png/webp, light/dark), colors, fonts, images, qualityScore, and `company` block: employees (size band), foundedYear, kind, financialIdentifiers, industries, location (city, state, region, country, country code, subregion).
- Logo API: CDN image URLs by domain. Brand Search API: name to domain lookup (listed on the pricing page; endpoint path not fetched).
- Useful 3PL-relevant fields: company.location (HQ city/state), foundedYear, employees band, industries. Brandfetch has no "list companies in a city" query, so you must already know the domains.

### c) Geography
HQ city/state/country per brand only. No aggregate geography.

### d) ToS and licensing
- Logo API: "We require logo links to be directly embedded in your applications." "Programmatic access to logo images is not permitted and may result in rate limiting or blocking." Attribution: "we don't ask for any attribution." Source: https://docs.brandfetch.com/docs/logo-api
- Logo API: "You cannot replicate the core user experience of Brandfetch." Same source.
- Terms of Service: the licence "does not extend to the original logos, images, or other brand assets"; third-party IP "remains the property of their respective owners"; cache licence limited to "a maximum period of thirty (30) days from the date of retrieval"; use "for the benefit of any third-parties" is prohibited without written consent; training AI on the data is prohibited without a written agreement; "Brandfetch does not endorse or control Third Party IP." Source: https://brandfetch.com/terms (no date shown on page).
- Showing customer/partner logos: Brandfetch's terms grant no trademark rights. WareMatch needs its own permission from each logo owner (or a nominative-use basis). Showing a competitor 3PL's logo as a "3PL in Dallas" listing, without their consent, risks implied endorsement and trademark complaints. Not a Brandfetch ToS issue as such, but Brandfetch gives no cover. The page links a "Guide to Logo Fair Use" whose content I did not retrieve.
- Note: the pricing page says images "can be cached locally under the usage guidelines", while the Logo API docs say to contact them for caching and the terms cap cached content at 30 days. Conflicting; treat as 30-day cache, hotlink via `<img>` for the Logo API.

### e) Usefulness: 2/5
Logos and brand data are decoration, not unique stats. Example blocks (no numbers invented):
1. "Brands WareMatch has matched in [state]" logo strip (only with consent, for real WareMatch customers).
2. "Featured 3PL partners near [city]" cards: logo, HQ city, founded year, employee band from `company`.
3. Colour-themed partner card using brand colours from `colors` (low value).
4. "Founded year / size" facts in a 3PL directory entry (only for companies already in WareMatch's own data).

### f) Pipeline and risks
- Script: build-time `GET /v2/brands/domain/{domain}` for each partner domain, store JSON (refresh at least every 30 days per terms). Render logos via Logo API CDN URL in `<img>` (client-side hotlink), not by downloading.
- Cost: pages share partners, so cost scales with distinct partner domains, not pages. Fits free tier (100 one-time fetches) for a small partner list; Growth for 2,500 per month if larger. Cost per page: effectively $0 on free, otherwise plan fee divided across pages (UNVERIFIED price, see above).
- Risks: trademark/endorsement, 30-day cache limit, Logo URLs must be hotlinked (page weight/third-party dependency), pricing page inconsistent.

---

## 2. OpenCorporates

### a) Access
- API key required for all calls (`api_token` param). Source: https://api.opencorporates.com/documentation/API-Reference
- Docs state default allowance of 200 requests per month and 50 per day, "though limits depend on your plan"; rate-limited requests return HTTP 403. Same source.
- Paid API plans (self-serve), quoted from https://opencorporates.com/pricing/ :
  - Essentials "£ 2,250/year" or "£225 per month": 500 calls/month, 200/day.
  - Starter "£ 6,600/year" or "£660 per month": 2,500 calls/month, 500/day.
  - Basic "£ 12,000/year" or "£1,200 per month": 5,000 calls/month, 1,000/day.
  - All three include "internal and external use". Enterprise: price on request, bulk data via SFTP, choice of jurisdictions.
- Free access: the pricing page offers it for public-benefit work (investigative journalists, NGOs, universities, anti-crime/anti-corruption research) via a contact form, not self-serve. A commercial marketplace such as WareMatch would not qualify. Terms: "financial institutions, corporations, government departments and regulatory authorities are not Permitted Users" of free keys. Source: https://opencorporates.com/terms-of-use-2/

### b) Endpoints and fields
- `GET /companies/search` with `q`, `jurisdiction_code`, `country_code`, `company_type`, `current_status`, `industry_codes`, `registered_address`, `incorporation_date` ranges, `inactive`, `branch`, `nonprofit`, `per_page` (max 100), `page` (capped at 100). Also `GET /industry_codes`, `/jurisdictions`, officers, filings. Source: API-Reference URL above.
- Returns: name, company number, jurisdiction, dates, status, type, registered address; full records add industry codes, officers, filings.
- Whether the search response includes a total result count (which would allow counts per state with one call): UNVERIFIED from the pages fetched. Check the sandbox/docs before building.

### c) Geography
Jurisdiction level (e.g. US state-level registries such as `us_tx`; countries). Registered address filter gives city-level, subject to data quality (UNVERIFIED).

### d) ToS and licensing
- "The OpenCorporates database is licensed under the Open Database License." "Use of any data must be accompanied by a hyperlink reading 'from OpenCorporates'." Attribution link "must in all cases be no smaller than 70% of the largest font relating to the information or 7px." Share-alike: "the resultant information must be published under the Attribution Share-Alike ODbL." Paid keys are "for a fee ... for example for use in commercial or proprietary applications." Source: https://opencorporates.com/terms-of-use-2/ (page shows "© 2024"; no last-updated date).
- Pricing page says paid plans remove share-alike: confirmed by the API reference ("Paid accounts remove the share-alike conditions"). Attribution wording on paid plans: UNVERIFIED.
- Aggregated statistics: the terms "do not address aggregated statistics specifically." Ask OpenCorporates for written confirmation.
- Automated extraction (scraping) beyond search indexation is restricted; use the API.

### e) Usefulness: 2-3/5
Registry data is unique and verifiable, but registries have no "3PL" category. Industry code coverage varies by jurisdiction (UNVERIFIED), and many US state registries carry no SIC/NAICS. A name-keyword search ("logistics", "warehousing", "fulfillment") is noisy. Example stat blocks:
1. "Companies with logistics-related names registered in [state]" (keyword count plus coverage caveat).
2. "New logistics-named registrations in [state] in the last 12 months" (incorporation_date range).
3. "Active vs dissolved logistics-named entities in [state]" (current_status filter).
4. "Registered-entity share of branch vs headquartered companies" (branch flag; low value).
All counts must be labelled as name/code-based registry counts, not "number of 3PLs".

### f) Pipeline and risks
- Script: for each jurisdiction, call `companies/search?q=...&jurisdiction_code=...&per_page=30` and read the total-count field if present; cache JSON per jurisdiction.
- Cost: US states and countries only. State/country pages (about 50-100) might cost one to a few calls each. City pages need address filtering, so cost depends on pagination. ~400 calls would fit one month of Essentials (500/month; daily cap 200 means at least 2 days). That is £225 on the monthly plan, or about £0.56 per call for 400 calls (arithmetic from the quoted price, assuming one call per page).
- Risks: free tier unavailable to WareMatch; share-alike on free; keyword-based counts are misleading; jurisdiction coverage uneven; the 100-page pagination cap.

---

## 3. BuiltWith

### a) Access
- All endpoints need a `KEY`. "API access is restricted to licensed Customers." Source terms: https://builtwith.com/terms (last updated 6 March 2026).
- Plans (monthly, as listed): Basic $295 (2 technologies), Pro $495 (unlimited), Team $995; "Team Ultra" listed with no details. Source: https://builtwith.com/plans. Yearly prices not readable. The plans page does not state API access per plan or call limits; API credit pricing is UNVERIFIED (docs say accounts use API credits bought via Stripe or x402; per-call costs not stated). Source: https://api.builtwith.com/
- Free API: `free1/api.json`, rate limited to "1 request per second"; how to get a free key is not explained on the page. Source: https://api.builtwith.com/free-api
- Trends API is marked free on the API index. Source: https://api.builtwith.com/
- Pay-per-lookup in USDC (x402) without an account is offered. Price per lookup not stated.

### b) Endpoints and fields
- Lists: `https://api.builtwith.com/lists13/api.json?TECH=Shopify&COUNTRY=DE&META=yes`. Params include TECH, OTHERTECHS (max 16), META, COUNTRY (ISO codes), SINCE, ALL, numeric filters (SPEND, REVENUE, SKU, EMPLOYEES, traffic ranks). Returns paged domains (`NextOffset`), with META giving company name, address, country and state. No aggregate counts by country or state are described; counts would require paging every result. "Mega technologies (10,000,000+ results) are no longer supported." Source: https://api.builtwith.com/lists-api
- Trends v6: `trends/v6/api.json?TECH=...&DATE=...`; returns coverage counts (Top 10k/100k/1M sites, entire internet, live and historical Pro database). No country breakdown described. Source: https://api.builtwith.com/trends-api
- Ask API: natural-language queries such as "Magento websites in Spain", sample results by default, `COMMIT=true` for paged results. Source: https://api.builtwith.com/
- Other: Domain, Relationships, Product (sites selling specific ecommerce products), Company to URL, Datasets (bulk, 2000 to date).

### c) Geography
Country filter (ISO 3166 alpha-2) on Lists; state/city only via META address per domain. Quality of location data: UNVERIFIED.

### d) ToS and licensing (https://builtwith.com/terms, updated 6 March 2026)
- Prohibited: "reproduce or distribute BuiltWith data publicly."
- Prohibited: "resell, redistribute, sublicense, or commercially exploit BuiltWith data."
- Allowed: "store report or API data privately for internal use."
- Prohibited: "aggregate or combine multiple reports or API responses to reconstruct substantial portions" of the data; bulk extraction "unless explicitly licensed through BuiltWith datasets."
- The Lists page says you may use the API to enhance your product but may not resell data as-is.
- Whether a single derived statistic (a count) on a page counts as "public reproduction": the terms do not carve out aggregates. Get written permission before publishing any BuiltWith-derived number.

### e) Usefulness: 3/5 (if licensed)
Platform adoption is relevant to a 3PL marketplace (ecommerce merchants are the demand side). Example blocks (no numbers invented):
1. "Shopify vs WooCommerce vs BigCommerce share of tracked ecommerce sites in [country]" (Lists with COUNTRY, counted by paging).
2. "Ecommerce sites added in the last 30 days in [country]" (SINCE filter).
3. "Fulfillment/shipping apps in use by sites in [country]" (technology counts, Trends coverage).
4. "Shopify Plus stores in [country]" (TECH=Shopify-Plus).
Country level only; state/city is not reliable.

### f) Pipeline and risks
- Script: Lists with COUNTRY and a counting loop over `NextOffset`, store counts only. Cost per call and per page UNVERIFIED (credit price not found). Large countries such as the US would page through very large lists (cost unknown); Trends may avoid paging but has no country split.
- Risks: ToS (public distribution banned), unknown credit costs, no aggregate endpoint, country not state level. Verdict: use only for internal research, or negotiate a written publishing licence.

---

## 4. Store Leads

### a) Access
- Plans, third-party source only (official /pricing URL returned 404 when fetched; UNVERIFIED): Premium $75/month with no API or CSV export; Pro $250/month (API from this tier, two platforms); Elite $450/month (all platforms); Enterprise $950/month. Sources: https://coldiq.com/blog/storeleads-pricing and https://selofy.com/tools/store-leads (found via search). Official 2020 post confirms Premium/Pro cover "any 2 ecommerce platforms" and Elite covers all platforms but gives no prices: https://storeleads.app/blog/2020/01/15/pricing-update. Confirm current prices at https://storeleads.app (/#pricing).
- Key from the Account page "API" tab; account must have API access. Rate limits: Retrieve Domain 5 req/s (Pro, Elite) and 20 req/s (Enterprise); List Apps 2 and 6 req/s. List Domains with `cursor=all` limited to 1 request/minute. Source: https://storeleads.app/api

### b) Endpoints and fields
- Base `https://storeleads.app/json/api/v1/all/`; `GET /domain/{name}`; list domains with filters; export domains; historical domains; lists; technologies; themes; apps. Source: https://storeleads.app/api
- Domain fields: platform, country code, state/province, city, categories, rank, product count, estimated sales/visits, technologies, installed apps, theme, tags.
- Filters on List Domains: `f:cc` (country), `f:city` (needs `f:cc` and `f:administrative_area_level_1`), `f:cat` (category), `f:ds` (domain state: Active/Inactive/Password Protected). Platform filter on the domains endpoint was not visible in the portion read (UNVERIFIED; the apps endpoint has `f:p`).
- No dedicated aggregate/count endpoint seen in the portion read (about 200K of 407K characters read). Whether a total count is returned in list responses: UNVERIFIED.

### c) Geography
Country, state/province (administrative_area_level_1) and city per store. This is the best granularity of the five.

### d) ToS and licensing (https://storeleads.app/terms; no date on page; "may revise these terms at any time without notice")
- Prohibited: "republish the data in any form without our permission."
- Prohibited: "resell the data, or resell access to the data through your paid plan, without our permission."
- "You must not reference our company, or website, in any external communication without prior written consent." This means even attribution needs consent.
- Prohibited: "use the information for competitive purposes."
- Aggregates and derived data are not addressed explicitly; the "republish ... in any form" wording likely covers them. Get written permission for publishing counts and agreed citation text.
- Programmatic access must go through the official API.

### e) Usefulness: 4/5 for content, but blocked by ToS until permission is granted
Example blocks (no numbers invented):
1. "Active ecommerce stores in [state/province] by platform (Shopify, WooCommerce, BigCommerce, Magento...)".
2. "Top product categories sold by stores based in [city]".
3. "Share of stores with high estimated sales/visits bands in [state]" (demand-side proxy for fulfillment volume).
4. "Fastest-growing categories in [country]" (needs historical data, Enterprise per third-party source; UNVERIFIED).
Counts are estimates by Store Leads; label them so.

### f) Pipeline and risks
- Script: for each (cc, admin1, city, platform, category) combination call List Domains with small `page_size` and read the total (if provided). 400 pages x several platform/category queries gives on the order of 400 to a few thousand calls; at 2 req/s that takes minutes. Cost: flat plan fee (about $250-450 per month if third-party prices hold), so a one-month subscription would cover the full build. UNVERIFIED pricing.
- Citation wording suggestion (only after written consent): "Source: Store Leads, [month year]. Estimates."
- Risks: ToS (republishing banned), no-reference clause, estimates not census, city text quality, terms change without notice.

---

## 5. TikTok Research API and Commercial Content API

### a) Access
- Research API: free but gated by application. Eligible: academic institutions (US, EEA, UK, Canada, Switzerland), not-for-profit or independent research bodies in the EU (beta), Brazil youth-safety organisations. "Applicants must be independent of commercial interests. Research must be conducted on a not-for-profit or non-commercial basis in pursuit of a public-interest mission." Decisions typically within 4 weeks. Source: https://developers.tiktok.com/products/research-api/
- Research API terms: use "for any commercial or unauthorized purpose" is barred (Section III); quota "determined by TikTok at its sole discretion"; no numeric per-day limits stated. Source: https://www.tiktok.com/legal/page/global/terms-of-service-research-api/en
- Commercial Content API: described as for "the public and researchers"; apply with a TikTok for Developers account, response within 2 working days per the product page (a search snippet said 1-2 weeks; conflicting). Source: https://developers.tiktok.com/products/commercial-content-api. The product page does not state commercial-use restrictions; check the TikTok Developer Terms of Service (not fetched) or commercial-research-questions@tiktok.com.

### b) Endpoints and fields
- Research API `POST https://open.tiktokapis.com/v2/research/video/query/`, scope `research.data.basic`. Fields include id, video_description, create_time, region_code, share/view/like/comment counts, hashtag_names, username, video_label. Filters: region_code, hashtag_name, keyword, create_date; `end_date` no more than 30 days after `start_date`; `max_count` up to 100. Source: https://developers.tiktok.com/doc/research-api-specs-query-videos
- Public data also includes "EU-based TikTok Shops" (product page above; fields not documented in what I retrieved).
- Commercial Content API: paid ads publish date, last-seen date, targeting info, impressions, advertiser info; searchable by advertiser name or keyword; data kept while the ad runs and one year after. Source: product page above.

### c) Geography
Research `region_code` is the country where the creator registered the account. Commercial Content ad data "currently covers only EU countries". No state/city.

### d) ToS and licensing
- Research Terms Section IV: you must not "disclose, copy, reproduce, share, sell, or otherwise transfer to any third party" TikTok Research Data or derived data. Outputs may not be traceable to a specific user, and TikTok's name or logo cannot be used without written approval; pre-publication copy to TikTok at least 7 days before publication. Source: Research API terms URL above.
- A commercial SEO marketing page is outside the permitted use.

### e) TikTok Shop seller stats
No official public API for market-wide seller statistics was found. TikTok Shop Partner API access is per authorised seller (OAuth, app registration in Partner Center); market figures online come from third-party estimates that disagree with each other (search results, e.g. https://www.dashboardly.io/statistics/tiktok-shop-seller-statistics, https://www.echotik.live/blog/tiktok-shop-data-api-access-endpoints-metrics-and-analytics-2026/). I did not verify the Partner Center docs directly (UNVERIFIED).

### f) Usefulness: 1/5
No eligible route, no geography below country, and no 3PL relevance. Possible blocks, all unrealistic for WareMatch: hashtag volume by country (research only); EU ad counts for fulfillment advertisers (Commercial Content API, legality unclear). Verdict: skip. Pipeline cost and risk are moot because a commercial company is ineligible for the Research API.

---

## Recommendation
1. Skip TikTok. Do not use BuiltWith or Store Leads data publicly without written permission; email both asking for a licence to publish aggregate counts with attribution, and get the citation wording in writing. Store Leads gives the best state/city granularity for "ecommerce merchants near [city]" content.
2. OpenCorporates paid Essentials is the only option with clear published terms for external use, but the content value is thin and keyword counts must be caveated.
3. Brandfetch only for logos of companies that have agreed to appear on WareMatch.
4. Fallback with fewer legal risks: WareMatch's own marketplace data (listed warehouses per location) as the main unique stat source, supplemented by public-agency statistics (not researched here).

## Unverified items to check before building
- Brandfetch Growth price ($99 vs $129 per month) and Brand API rate limits.
- OpenCorporates search total-count field, industry-code coverage by jurisdiction, attribution wording on paid plans.
- BuiltWith API credit pricing and whether any plan includes API access; free key signup; location data quality.
- Store Leads official current pricing, plan needed for API, platform filter on domains, count availability, aggregate-publishing permission.
- TikTok Developer Terms for the Commercial Content API; TikTok Shop Partner Center docs.
