# Structured data: status and value (research run 2026-10-19)

Method: each page fetched with WebFetch on 2026-10-19. Sources are primary only (Google Search Central, Bing/Microsoft, schema.org, W3C). "Date shown" is what the page displayed. Confidence A = primary, B = primary but inferred/partially read. Quotes are short fragments as returned by the fetch tool. Items I could not verify are marked UNVERIFIED.

## 1. Google Search Central

| # | Claim | Quote | URL | Publisher / date shown | Conf | Implication |
|---|---|---|---|---|---|---|
| 1.1 | FAQ rich result is gone entirely (2026) | "This feature will no longer appear in Google Search starting May 7, 2026." | https://developers.google.com/search/updates (entry 8 May 2026) | Google Search Central changelog; 8 May 2026 | A | FAQPage markup yields no Google rich result. |
| 1.2 | FAQ docs removed | "The FAQ rich result feature is no longer shown in Google Search results." | https://developers.google.com/search/updates (entry 15 Jun 2026) | Google; 15 Jun 2026 | A | Do not justify FAQPage as a Google feature. |
| 1.3 | Earlier (2023) FAQ restriction | "only shown for well-known, authoritative government and health websites" | https://developers.google.com/search/docs/appearance/structured-data/faqpage (changelog entry 14 Sep 2023) | Google; 14 Sep 2023 | A | Already near-useless for a commercial site since 2023; now fully gone. Fetch of the 2023 blog post body failed (page truncated), so the 2023 blog wording is UNVERIFIED; the date is from the changelog. |
| 1.4 | HowTo removed | "as this rich result is no longer shown in search results" | https://developers.google.com/search/docs/appearance/structured-data/how-to (changelog 14 Sep 2023) | Google; 14 Sep 2023 | A | HowTo has no Google rich result since 2023. |
| 1.5 | Gallery no longer lists FAQ or HowTo | "Q&A Pages are web pages that contain data in a question and answer format." (only related entry) | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | Google; Last updated 2026-10-16 | A | Gallery lists 25 features incl. Breadcrumb, Local business, Organization, Review snippet, Software app, Speakable, Carousel. No CollectionPage, Service, Place, Person, ContactPage/AboutPage rich results. |
| 1.6 | More deprecations 2025-26 | "we will be phasing out support for a few structured data features in Search." | https://developers.google.com/search/updates (12 Jun 2025; docs removed 9 Sep 2025 for course info, estimated salary, learning video, special announcement, vehicle listing; practice problem 6 Jan 2026) | Google; 2025-2026 | A | Trend: Google is shrinking rich result types. Don't build on niche types. Partial read of changelog (last ~79k chars not read). |
| 1.7 | General policy: visible content | "Don't mark up content that is not visible to readers of the page." | https://developers.google.com/search/docs/appearance/structured-data/sd-policies | Google; Last updated 2026-07-10 | A | Every marked-up fact (FAQ, ratings, hours) must be on the page. |
| 1.8 | Policy: no fake/irrelevant | "Don't mark up irrelevant or misleading content, such as fake reviews" | same | same | A | No empty/placeholder ratings, prices or reviews. |
| 1.9 | No guarantee | "Google does not guarantee that your structured data will show up in search results" | same | same | A | Schema is eligibility, not a ranking or display guarantee. |
| 1.10 | Markup placement | "Put the structured data on the page that it describes." | same | same | A | Child-listing data belongs on the listing page, not only on the parent. |
| 1.11 | Required props missing = no rich result; bad ratings = manual action | "Items that are missing required properties are not eligible for rich results." | same | same | A | Empty fields make the item ineligible; fake ratings risk a manual action (the page also says manual action "doesn't affect how the page ranks" for structured-data actions, i.e. rich-result loss). |
| 1.12 | Link nodes with @id | use "@id" to link related items (paraphrase of page) | same | same | B | Supports @id cross-references inside a graph. |
| 1.13 | JSON-LD preferred | "Google recommends using JSON-LD for structured data" | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | Google; Last updated 2025-12-10 | A | Keep JSON-LD. |
| 1.14 | LocalBusiness | required: `address`, `name`; "most specific LocalBusiness sub-type possible" (paraphrase, page quote returned partly) | https://developers.google.com/search/docs/appearance/structured-data/local-business | Google; Last updated 2026-09-08 | A | Use specific subtype; the markup is for hours, departments etc. Google's feature is for the business's own page. |
| 1.15 | BreadcrumbList | final item may omit `item`; Google then uses "the URL of the containing page" | https://developers.google.com/search/docs/appearance/structured-data/breadcrumb | Google; Last updated 2026-09-08 | A | Item URLs must be the real page URLs; last crumb URL optional. |
| 1.16 | Organization | "Adding organization structured data to your home page can help Google better understand" | https://developers.google.com/search/docs/appearance/structured-data/organization | Google; Last updated 2026-09-08 | A | Put full Organization on home (or about) page; all properties optional. |
| 1.17 | Review snippet: self-serving | LocalBusiness/Organization controlling own reviews are "ineligible for star review feature" | https://developers.google.com/search/docs/appearance/structured-data/review-snippet | Google; Last updated 2026-09-08 | A | No aggregateRating on own Organization/LocalBusiness; listings (third-party warehouses) with no real user reviews: omit. |
| 1.18 | Ratings source | "Ratings must be sourced directly from users." | same | same | A | No editor-compiled or aggregated-from-elsewhere ratings. |
| 1.19 | SoftwareApplication | needs `offers.price` plus `aggregateRating` or `review` for rich result | https://developers.google.com/search/docs/appearance/structured-data/software-app | Google; Last updated 2026-09-08 | A | Without real ratings, SoftwareApplication gives no rich result (still fine as entity markup). |
| 1.20 | Speakable | "This feature is in beta and subject to change." Works for US English Google Home users | https://developers.google.com/search/docs/appearance/structured-data/speakable | Google; Last updated 2026-09-08 | A | Low value; not tied to AI Overviews. |

## 2. Google on structured data and AI Overviews / AI Mode
- "There are no additional requirements to appear in AI Overviews or AI Mode" and "There's also no special schema.org structured data that you need to add." URL: https://developers.google.com/search/docs/appearance/ai-features. Publisher Google; Last updated 2025-12-10. Conf A.
- Same page lists "Making sure your structured data matches the visible text on the page" as general SEO best practice.
- Implication: schema is not required for AI features; its value is general understanding and rich results, not AI eligibility. (Page was read through a summarizing fetch; re-verify exact wording before publishing the quotes externally.)

## 3. Microsoft / Bing
| Claim | Quote | URL | Publisher / date | Conf | Implication |
|---|---|---|---|---|---|
| Bing says schema-marked content helps AI interpret/summarize | "Structured content, like schema-marked product pages, FAQs, and comparison tables," (sentence continues: easier for AI systems to interpret) | https://blogs.bing.com/webmaster/2025/11/How-AI-Search-Is-Changing%E2%80%AFthe%E2%80%AFWay%E2%80%AFConversions%E2%80%AFare-Measured/ | Bing Webmaster Blog, Fabrice Canel and Krishna Madhavan; 20 Nov 2025 | A | Only explicit Microsoft statement found; qualitative, no proof of citation uplift, does not name Copilot in that sentence. |
| Bing AI Performance post: structure helps citation | "Clear headings, tables, and FAQ sections help surface key information" | https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/ | Bing Webmaster Blog (Microsoft AI authors); 10-11 Feb 2026 | A | Page does not mention schema; it recommends visible on-page structure. Bing's FAQ advice is about visible FAQ sections, not FAQPage markup. |
| Bing uses structured data as a clue | (2018) Bing says structured data is one clue it uses to understand pages | https://blogs.bing.com/webmaster/august-2018/Introducing-JSON-LD-Support-in-Bing-Webmaster-Tools | Bing Webmaster Blog; 2018 (not re-fetched, from search snippet) | B | Old; UNVERIFIED wording. |
| Bing guidelines on markup and grounding | search summary claimed guidelines say structured data may help grounding, must match visible content | https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a | Bing | UNVERIFIED | Fetch returned an empty shell page; could not confirm. Do not cite. |
| Product schema + IndexNow for AI-powered discovery | post mentions schema.org/Product | https://blogs.bing.com/webmaster/2025/5/IndexNow-Enables-Faster-and-More-Reliable-Updates-for-Shopping-and-Ads/ | Bing; 20 May 2025 | B | Not relevant (no Product on listings). |
No conference-talk reports were used. Gap: no Microsoft page found that says schema directly improves Copilot citations.

## 4. schema.org definitions (development version V30.1 shown)
| Term | Result | Quote | URL | Conf |
|---|---|---|---|---|
| CollectionPage | exists; Thing > CreativeWork > WebPage > CollectionPage | "Web page type: Collection page." | https://schema.org/CollectionPage | A |
| ItemList | exists; use ListItem + `position` for order; `numberOfItems` is whole list even if paginated | "A list of items of any sort" | https://schema.org/ItemList | A |
| containedInPlace | domain Place, range Place; inverse containsPlace | "The basic containment relation between a place and one that contains it." | https://schema.org/containedInPlace | A |
| areaServed | usable on Service and Organization; range AdministrativeArea, GeoShape, Place, Text | "The geographic area where a service or offered item is provided." | https://schema.org/areaServed | A |
| Service | Thing > Intangible > Service; has areaServed, provider, serviceType | "A service provided by an organization" | https://schema.org/Service | A |
| LogisticsBusiness | DOES NOT EXIST: HTTP 404 | n/a | https://schema.org/LogisticsBusiness | A |
| Alternatives that exist | MovingCompany (LocalBusiness > HomeAndConstructionBusiness), SelfStorage (LocalBusiness) | "A self-storage facility." | https://schema.org/SelfStorage ; https://schema.org/MovingCompany | A |
| HowTo | exists, no deprecation flag | "Instructions that explain how to achieve a result by performing a sequence of steps." | https://schema.org/HowTo | A |
| speakable | exists, on Article and WebPage; no stability flag shown | "Indicates sections of a Web page that are particularly 'speakable'" | https://schema.org/speakable | A |
| ContactPage / AboutPage | both exist under WebPage | "Web page type: About page." | https://schema.org/AboutPage ; https://schema.org/ContactPage | A |
Note: the team's LocalBusiness subtype for warehouses is not verified; a generic `LocalBusiness` (or a custom approach: plain Organization/Place with `additionalType`) is the safe path. Whether a 3PL/warehouse fits schema.org type "WarehouseStore"-like types is UNVERIFIED (I did not look up other candidates).

## 5. JSON-LD @graph, @id, multiple script blocks (W3C)
- Node identity: "In JSON-LD, a node is identified using the `@id` keyword." (JSON-LD 1.1 section 3.3; https://www.w3.org/TR/json-ld11/; W3C Recommendation 16 Jul 2020). A.
- Merging within one document: the Flattening algorithm "collects all properties of a node in a single map" (JSON-LD 1.1 API section 7.1.1; https://www.w3.org/TR/json-ld11/api/ i.e. https://www.w3.org/TR/json-ld11-api/), and Merge Node Maps creates "merged node objects containing information defined for a given subject" (section 7.3). A. Implication: two node objects with the same `@id` in one @graph are treated as one node whose properties are unioned; this is merging, not an error. Duplicate @ids with conflicting values (two different `name`s) become multiple values, which consumers may handle badly. Duplicates are legal but a hygiene issue; the team's "no duplicate @id" rule is a good-practice rule, not a spec requirement.
- Multiple script blocks: the spec says JSON-LD is embedded by "placing it in a script element with the type attribute set to application/ld+json" (section 7). Each script element is its own document; I found no statement that processors merge across script elements. Cross-script merging is consumer-specific: UNVERIFIED (Google's policy page only says use `@id` to link items). Implication: one @graph per page is the safest single-document design.
- Not located: spec text about graphs in `@graph` of the default graph being merged with top-level nodes (partial read). 

## 6. Validators
- Google Rich Results Test, https://search.google.com/test/rich-results: "Test your publicly accessible page to see which rich results can be generated by the structured data it contains." A. Tells you eligibility for Google rich result features only. Cannot tell about types with no rich result (CollectionPage, Service, Place), ranking, or AI citation. The tool's docs state structured data may be removed from reporting as features are deprecated (e.g. practice problem/dataset removal from Search Console and RRT starting Jan 2026, changelog 5 Nov 2025).
- Schema Markup Validator, https://validator.schema.org/: fetched page is a bare form with URL/code input and a VALIDATE button; its own description of coverage is UNVERIFIED from the page. Commonly used for generic schema.org syntax and property-vocabulary checks, not Google eligibility (general knowledge, B; not confirmed on page).
- Neither tool detects: content mismatch with visible text, duplicate @id across separate script blocks, wrong item URLs that still resolve, or whether a rating is real. Needs custom crawl checks.

## Checks to implement
1. Remove FAQPage and HowTo as "rich result" goals. If kept, keep only where the Q&A is visible on page; label as no-Google-benefit, optional Bing/LLM hygiene.
2. For each page: exactly one `<script type="application/ld+json">` containing one `@graph`; assert unique `@id` (crawl parse; fail on duplicates or conflicting property values).
3. Every marked-up value must appear in visible HTML (names, address, hours, FAQ text); diff JSON-LD strings against rendered text.
4. Block empty/placeholder `price`, `aggregateRating`, `review`, `ratingValue`, and any Product type on listings; no self-serving aggregateRating on Organization/LocalBusiness.
5. BreadcrumbList: each `item` URL returns 200, is canonical, absolute, matches the visible breadcrumb order; final item may omit `item`.
6. Organization/WebSite on home (and optionally about); do not repeat full global nodes on every page other than by `@id` reference (stylistic; Google says only mark up the page it describes). Mark as judgment call, not a documented rule.
7. LocalBusiness: require `name` and `address` on listing pages; use an existing schema.org subtype only; do NOT use `LogisticsBusiness` (404 at schema.org). Validate any subtype against schema.org.
8. CollectionPage + ItemList: `ListItem.position` sequential, urls canonical; `numberOfItems` = full count. Treat as low-cost entity hygiene with no documented Google or Bing benefit.
9. Place hierarchy: `containedInPlace` range is Place only; check chain country -> state -> city is consistent with visible breadcrumbs and URL tree.
10. Service `areaServed`: use AdministrativeArea/Place/Text values; fine.
11. SoftwareApplication: only mark up if a real product page; no rating fields without real user ratings.
12. Run Rich Results Test only on Breadcrumb/Local business/Organization/Software app pages; run Schema Markup Validator on all templates.
13. Track Bing AI Performance in Bing Webmaster Tools (https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) rather than assuming schema drives citations.
14. Spend GEO effort on visible content structure (headings, tables, visible FAQ sections) which Bing does recommend.

## Team schema doc recommendation -> verdict
| Recommendation | Verdict | Source |
|---|---|---|
| One unified @graph per page, no duplicate @id | supported (good practice; duplicate @id is merged by the spec, not an error) | W3C JSON-LD 1.1 API 7.1.1, 7.3; Google sd-policies (@id linking) |
| Organization / WebSite / Service global nodes | supported (Organization documented by Google; WebSite and Service have no Google feature, entity hygiene only) | Google organization doc; schema.org Service |
| WebPage | low value (no Google rich result; harmless) | Google gallery (not listed) |
| BreadcrumbList with correct item URLs | supported | Google breadcrumb doc, updated 2026-09-08 |
| FAQPage | outdated for Google (rich result ended 7 May 2026; docs removed 15 Jun 2026); low value for Bing (Bing endorses visible FAQ sections, not FAQPage markup) | Google updates changelog; Bing Feb 2026 post |
| HowTo | outdated (Google removed Sep 2023) | Google how-to page changelog |
| CollectionPage + ItemList of child pages | low value (valid schema.org, no Google feature listed; Carousel feature needs specific content types, UNVERIFIED for this use) | schema.org; Google gallery |
| Place hierarchy (containedInPlace) | low value / valid vocabulary, no documented search benefit | schema.org containedInPlace |
| LocalBusiness for warehouse listings, no Product, no empty price/rating/review | supported | Google local-business, review-snippet, sd-policies |
| LogisticsBusiness | outdated/incorrect: type does not exist in schema.org (404) | https://schema.org/LogisticsBusiness |
| SoftwareApplication | low value unless real offers.price + real ratings; otherwise ineligible for rich result | Google software-app doc |
| ContactPage / AboutPage | low value (valid types, no Google feature) | schema.org |
| Person nodes | unverified (not researched; Google has profile page feature only for ProfilePage) | Google gallery lists Profile page |
| speakable (if in doc) | low value (beta, US English Google Home only) | Google speakable doc |
| Claim that schema is needed for AI Overviews/AI Mode | unsupported: Google says no special schema needed | Google ai-features doc |
| Claim that schema boosts Copilot answers | unverified/weak: only a qualitative Bing blog sentence, no data | Bing blog 20 Nov 2025 |
