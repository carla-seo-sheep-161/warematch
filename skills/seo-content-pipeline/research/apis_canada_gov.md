# Canadian government data APIs for WareMatch 3PL location pages

Research and live tests run 2026-10-19. All numbers below come from real calls made that day. Raw responses are in `/Users/carlaklaasen/Desktop/WareMatch/content-writing/pipeline/research/samples/` (file names are given next to each test). Anything I did not verify is marked **UNVERIFIED**.

## Verdicts

| API | Free / keyless | Fresh | Geography | Page-level fit | Rating | Verdict |
|---|---|---|---|---|---|---|
| 1. StatCan Web Data Services (WDS) | Yes / no key | Yes: monthly series to Jul-Sep 2026 | Canada, province, some CMA and economic region | Country, province, city (CMA) | **5/5** | Build now |
| 2. StatCan Job Vacancy and Wage Survey (JVWS) | Yes / no key | Yes: 2026 Q2, released 2026-09-15 | Canada, province, economic region (83), NOC unit group | Country, province, city via the economic region | **4/5** | Build now, with suppression handling |
| 3. Transport Canada open data | Yes / no key | Mixed: some files are stale, some are live | Point and file data, not statistical | Context (airports, border wait times) | **2/5** direct, **4/5** via StatCan transport tables | Use StatCan's TC-sourced tables. Use TC files only as small static lookups. |

---

## 0. Common licence and access terms

- **Key or account:** none for any call below. I created no accounts and entered no personal information.
- **Licences:**
  - StatCan data falls under the **Statistics Canada Open Licence** (https://www.statcan.gc.ca/en/terms-conditions/open-licence, fetched and read).
  - open.canada.ca datasets from Transport Canada and CBSA tagged `ca-ogl-lgo` fall under the **Open Government Licence - Canada** (https://open.canada.ca/en/open-government-licence-canada, fetched and read).
- **Commercial use:** allowed under both. StatCan's licence grants a "worldwide, royalty-free, non-exclusive licence to use, reproduce, publish, freely distribute, or sell the Information" and Value-added Products. OGL-Canada allows use "for any lawful purpose".
- **Statistics Canada attribution:**
  - If you reproduce raw data: `Source: Statistics Canada, <name of product>, <reference date>. Reproduced and distributed on an "as is" basis with the permission of Statistics Canada.`
  - If you derive or adapt it (shares, rankings, sums, sentences): `Adapted from Statistics Canada, <name of product>, <reference date>. This does not constitute an endorsement by Statistics Canada of this product.`
  - Do not use the StatCan or Government of Canada name, logo or wordmark. Do not suggest endorsement. Do not misrepresent the data.
- **OGL-Canada attribution:** `Contains information licensed under the Open Government Licence - Canada.` Link to the licence where possible. Use the provider's own attribution statement if one is specified.
- **Rate limits:** WDS publishes limits of 50 requests per second server-wide and 25 requests per second per IP (from the user guide, https://www.statcan.gc.ca/en/developers/wds/user-guide). The same guide says the API may return HTTP **409** while tables are being updated, around release times (08:30 ET). The guide also says WDS is not meant for bulk downloads, and points to full-table CSV downloads and the Delta File for that. Retry with backoff. I did not stress-test the limits.

---

## 1. Statistics Canada Web Data Services (WDS)

### a) Access
- Base URL: `https://www150.statcan.gc.ca/t1/wds/rest/`
- No key. Methods are GET or POST with JSON bodies.
- Methods tested live (all HTTP 200):
  - `getChangedCubeList/{date}` (`wds_changed_cubes.json`)
  - `getCubeMetadata` (POST `[{"productId":N}]`)
  - `getCodeSets` (`wds_codesets.json`)
  - `getSeriesInfoFromVector` (`wds_seriesinfo_vectors.json`, `wds_seriesinfo_vectors2.json`)
  - `getDataFromCubePidCoordAndLatestNPeriods` (POST `[{"productId":N,"coordinate":"a.b.c.0.0.0.0.0.0.0","latestN":k}]`)
- **Important behaviour:** a bulk POST (many items in one request) does **not return results in request order**. In my 70-item test the results came back sorted by coordinate string. Always key results by `productId` plus `coordinate` or `vectorId`. Never zip them with the request list. I made this mistake in my first pass and the mismatch was obvious. `wds_province_matrix_raw.json` is the raw reordered response.
- Pricing: free. Terms: Statistics Canada Open Licence, see section 0.

### b) Table IDs (PIDs) and example requests

Verified live through `getCubeMetadata`. The "Latest period" column is the cube's `cubeEndDate` (or the last data point I fetched).

| Use | PID | Table title | Freq | Latest period (tested 2026-10-19) | Geography |
|---|---|---|---|---|---|
| Warehousing employment | 14-10-0201-01 (`14100201`) | Employment by industry, monthly, unadjusted for seasonality (SEPH) | Monthly | 2026-07 (released 2026-09-24) | Canada and 13 provinces and territories |
| Job vacancy (JV) by industry sub-sector | 14-10-0442-01 | Job vacancies, payroll employees, job vacancy rate, and average offered hourly wage by industry sub-sector, quarterly, unadjusted | Quarterly | 2026 Q2 (released 2026-09-15) | Province (14) |
| JV by occupation (NOC 2021 broad and unit group) | 14-10-0443-01 | Job vacancies, proportion of job vacancies and average offered hourly wage by occupation and selected characteristics | Quarterly | 2026 Q2 | Province (14) |
| JV by unit group by region | 14-10-0444-01 | Job vacancies and average offered hourly wage by occupation (unit group), quarterly | Quarterly | 2026 Q2 | Canada, province, **83 economic regions** (Toronto, Calgary, Edmonton, Lower Mainland-Southwest, etc.) |
| JV by economic region | 14-10-0441-01 | Job vacancies, payroll employees, JV rate and average offered hourly wage by economic regions | Quarterly | 2026 Q2 | 83 economic regions |
| JV, provincial monthly | 14-10-0371-01 (unadjusted), 14-10-0432-01 (seasonally adjusted) | Job vacancies, payroll employees, JV rate by provinces and territories, monthly | Monthly | 2026-07 | Province |
| Warehouse construction investment | 34-10-0293-01 | Investment in Building Construction | Monthly | 2026-07 (released 2026-09-21) | Canada, province, **about 40 CMAs** |
| Building permits | 34-10-0292-01 | Building permits, by type of structure and type of work | Monthly | 2026-08 (released 2026-10-14) | Canada, province, CMA (66 geographies) |
| CMA labour force | 14-10-0458-01 | Labour force characteristics by CMA, 3-month moving average, unadjusted | Monthly | 2026-09 | 43 CMAs |
| CMA population | 17-10-0148-01 | Population estimates, July 1, by CMA and CA, 2021 boundaries | Annual | July 1, 2025 (stored as refPer `2025-01-01`) | 211 CMAs and CAs |
| Retail e-commerce | 20-10-0056-01 | Monthly retail trade sales by province and territory | Monthly | 2026-07 | Canada, province, some cities |
| GDP share by industry | 36-10-0400-01 | GDP at basic prices, by industry, provinces and territories, percentage share | Annual | 2025 | Province |
| GDP monthly national | 36-10-0434-01 | GDP at basic prices, by industry, monthly | Monthly | 2026-07 | Canada only |
| Truck border crossings | 24-10-0052-01 | Vehicles entering Canada by land, by vehicle type and licence plate | Monthly | 2026-07 | Port and area (248 geographies) |
| Air cargo | 23-10-0254-01 | Air cargo traffic at Canadian airports, annual | Annual | 2025 | About 535 airports |
| Rail carloads | 23-10-0216-01 | Railway carloadings statistics, by total tonnage transported, monthly | Monthly | 2026-07 | Canada, Eastern and Western divisions |
| Rail intermodal OD | 23-10-0063-01 | Origin and destination of intermodal tonnage | Annual | 2024 | Province and region |
| Trade by mode | 12-10-0177-01 | Merchandise trade by mode of transport, customs-based | Monthly | 2026-08 | Canada only |

**Tables that exist but are not useful**
- `14100325`, `14100326`, `14100328`: old JV tables, inactive since 2023 Q3.
- `20100072`: retail e-commerce, inactive since 2022.
- `34100285`: building permits, inactive.
- `24100002`: vehicles crossing the border, ended 2021.
- `36100402`: GDP by industry for provinces, inactive.

**Not found**
- I found **no** StatCan table for industrial vacancy, rents or warehouse square footage (UNVERIFIED that none exists).
- I found no active provincial or CMA table of GDP in dollars for warehousing. I found only the percentage share (36100400) at province level. Province-level dollar tables may exist under other PIDs. I did not search further.
- I did not test provincial e-commerce. The table lists provinces, but my coordinate for Ontario returned `FAILED` (`ecomm_retail_Ontario_20100056.json`). I assume it is not published in that combination. UNVERIFIED.

**Example requests** (coordinates are 10 dimension member IDs separated by dots, padded with zeros)

```bash
# Warehousing and storage employees, Ontario (SEPH, geo 7, All employees 1, NAICS 252 = 493), last 4 months
curl -s -H 'Content-Type: application/json' \
  -d '[{"productId":14100201,"coordinate":"7.1.252.0.0.0.0.0.0.0","latestN":4}]' \
  https://www150.statcan.gc.ca/t1/wds/rest/getDataFromCubePidCoordAndLatestNPeriods

# Material handlers (NOC 75101, member 720), Ontario, average offered hourly wage (stat 5); stat 1 = vacancies
-d '[{"productId":14100443,"coordinate":"7.720.1.5.0.0.0.0.0.0","latestN":4}]'

# Warehouses structure type in Toronto CMA, unadjusted current dollars (34100293: geo 45 = Toronto, struct 21 = Warehouses, work 1 = total, value 1)
-d '[{"productId":34100293,"coordinate":"45.21.1.1.0.0.0.0.0.0","latestN":12}]'

# Trucks entering Canada by land at Fort Erie (24100052 dims: geo 102, licence plate 1 = all, vehicle type 4 = trucks)
-d '[{"productId":24100052,"coordinate":"102.1.4.0.0.0.0.0.0.0","latestN":6}]'
```

**Member IDs used**
- 14100201 geography: 1 Canada, 2 NL, 3 PE, 4 NS, 5 NB, 6 QC, 7 ON, 8 MB, 9 SK, 10 AB, 11 BC, 12 YT, **14 NT, 15 NU** (ID 13 is skipped in this table).
- 14100443, 14100442 and 14100371 geography: 1 Canada, 2 to 12 the provinces in the same order, 12 YT, 13 NT, 14 NU.
- NOC members in 14100443: 720 = Material handlers [75101], 369 = Shippers and receivers [14400], 703 = Transport truck drivers [73300], 356 = Production and transportation logistics coordinators [13201], 371 = Production logistics workers [14402], 620 = Store shelf stockers, clerks and order fillers [65102], 530 = Border services officers [43203].
- NAICS in 14100442: 86 = Warehousing and storage [493], 9 = Transportation and warehousing [48-49], 79 = Truck transportation, 85 = Couriers and messengers.
- Metadata change risk: member IDs are positions within a table, not stable codes. **Resolve them at runtime** from `getCubeMetadata` by `classificationCode` or name, and cache the result.

### c) Geography and mapping to page levels

| Page level | What we can use |
|---|---|
| Country | Everything above. |
| Province | SEPH warehousing employees (14100201), JV by NOC and by industry (14100442/3), GDP share (36100400), JV rates, retail sales, building investment. |
| City | Only through **CMA** (population 17100148, labour force 14100458, warehouse construction investment 34100293, building permits 34100292), **economic region** (JV, 14100444 and 14100441), or **border or airport entity** (24100052, 23100254). |

The mapping is a lookup you must build and maintain: `city slug -> CMA geo ID` (per table, since member IDs differ by table), and `city slug -> economic region`. Examples from the metadata: Toronto CMA is 22 in 17100148, 19 in 14100458 and 45 in 34100293. The Toronto economic region (SGC 3530) is 50 in 14100444. Cities outside a CMA (small towns) get province data only. Use SGC and CMA codes from the metadata `classificationCode` to join across tables.

### d) Freshness and real sample values

All samples fetched 2026-10-19.

| Series | Latest period | Value | Quality code | Source file |
|---|---|---|---|---|
| Warehousing and storage, all employees, Ontario (14100201) | 2026-07 | 51,604 persons | 5 (good) | `seph_warehousing_ON_14100201.json` |
| Same, Canada | 2026-07 | 95,703 persons | 4 (very good) | `seph_warehousing_CA_14100201.json` |
| Material handlers, Ontario, job vacancies (14100443) | 2026 Q2 | 4,860 | 5 (good) | `jv_matHandlers_ON_vac_14100443.json` |
| Material handlers, Ontario, average offered hourly wage | 2026 Q2 | $20.25 | 3 (excellent) | `jv_matHandlers_ON_wage_14100443.json` |
| Material handlers, Toronto economic region (14100444) vacancies | 2026 Q2 | 3,345 | 6 (acceptable) | `jv_regional_matHandlers_Toronto_14100444.json` |
| Same, wage | 2026 Q2 | $20.10 | 3 | `jv_regional_wage_matHandlers_Toronto_14100444.json` |
| Warehousing and storage, JV wage, Ontario (14100442) | 2026 Q2 | $28.10 (up from $24.35 in Q1 and $22.75 in Q4 2025) | 5 | `jv_warehousing_ON_wage_14100442.json` |
| Warehousing and storage, JV, Ontario, vacancies | 2026 Q2 | 810 | 7 (use with caution) | `jv_warehousing_ON_vac_14100442.json` |
| Same, Q3 2025 to Q1 2026 | | null (status 8) | 8 (too unreliable to be published) | same file |
| Toronto CMA unemployment rate (14100458, 3-month moving average) | 2026-09 | 7.5% (Aug 7.4%, Jul 7.2%) | 0 | `lfs_cma_Toronto_unemp_14100458.json` |
| Toronto CMA employment | 2026-09 | 3,794.2 thousand persons | 0 | `lfs_cma_Toronto_employment_14100458.json` |
| Toronto CMA population (17100148) | July 1, 2025 | 7,108,874 (2024: 7,109,866) | 0 | `pop_cma_Toronto_17100148.json` |
| Warehouse construction investment, Toronto CMA (34100293) | 2026-07 | $197,949,780 (current dollars, unadjusted, monthly) | 0 | `bldg_warehouses_Toronto_34100293.json` |
| Same, sum of Aug 2025 to Jul 2026 | 12 months | $2,220,719,401 (my sum of the 12 monthly values) | 0 | same file |
| Same, Calgary CMA, 12-month sum | Aug 2025 to Jul 2026 | $903,960,743 (July alone: $82,067,040) | 0 | `bldg_warehouses_Calgary_34100293.json` |
| Same, Ontario, 12-month sum | Aug 2025 to Jul 2026 | $3,826,378,103 | 0 | `bldg_warehouses_Ontario_34100293.json` |
| Transportation and warehousing share of GDP, Ontario (36100400) | 2025 | 4.29% (2024 4.37%, 2023 4.37%) | 0 | `gdp_share_TW_Ontario_36100400.json` |
| Retail e-commerce sales, Canada (20100056, unadjusted) | 2026-07 | $5,084,789 thousand ($5.08 billion), 6.5% of total retail $77,817,236 thousand | 4 | `ecomm_retail_Canada_20100056.json`, `retail_total_Canada_20100056.json` |
| GDP transportation and warehousing, Canada, monthly (36100434) | 2026-07 | $107,403 million (chained 2017 dollars, seasonally adjusted at annual rates) | 0 | `gdp_monthly_TW_Canada_36100434.json` |

Response excerpt (real, trimmed) from `seph_warehousing_ON_14100201.json`:
```json
{"status":"SUCCESS","object":{"responseStatusCode":0,"productId":14100201,"coordinate":"7.1.252.0.0.0.0.0.0.0","vectorId":1557739,"vectorDataPoint":[{"refPer":"2026-04-01","value":49967.0,"decimals":0,"scalarFactorCode":0,"symbolCode":0,"statusCode":3,"releaseTime":"2026-07-30T08:30","frequencyCode":6}, ... ]}}
```

**Cross-check of the data:** province SEPH warehousing employment for July 2026 sums (NL 243, PE 206, NS 254, NB 1,244, QC 9,682, ON 51,604, MB 1,574, SK 586, AB 13,833, BC 16,466) to 95,692, against Canada 95,703. The territories returned null. The difference of 11 is rounding or suppression. This supports the mapping of member IDs. The full province matrix is in `wds_province_matrix_raw.json`.

**Freshness polling:** `getChangedCubeList/2026-10-15` returned the product IDs released that day, with release times. `getCubeMetadata` also returns `releaseTime` and `cubeEndDate` per table.

**Unit gotchas (confirmed via `getSeriesInfoFromVector`):**
- Retail e-commerce is in **thousands of dollars** (scalar code 3).
- Toronto CMA employment (14100458) is in **thousands of persons**, even though its scalar code is 0.
- GDP monthly is in **millions** of dollars.
- Warehouse construction investment (34100293) is in **dollars** (scalar code 0).
- Air cargo is in **tonnes**.
- Population and employees are in persons.
- For 14100443, 14100442 and 34100293, `getSeriesInfoFromVector` (`wds_seriesinfo_vectors.json`) gives the unit. Always read the unit from that endpoint and the scalar factor, not from the table title.

### e) Usefulness: 5 of 5

This is the only source here with province and CMA granularity, a monthly refresh and a stable API. The only gaps are no industrial vacancy or rent data, and CMA coverage limited to about 40 to 43 cities.

Example sentences, all with real numbers from the calls above:

1. "Ontario had 51,604 employees in warehousing and storage in July 2026, about 54% of the national total of 95,703 (Adapted from Statistics Canada, Table 14-10-0201-01, Employment by industry, monthly, unadjusted for seasonality, July 2026)."
2. "Employers in Ontario were advertising 4,860 vacancies for material handlers in the second quarter of 2026, at an average offered wage of $20.25 an hour (Adapted from Statistics Canada, Table 14-10-0443-01, Job vacancies and average offered hourly wage by occupation, Q2 2026)."
3. "In the Toronto economic region, material handler postings averaged $20.10 an hour in Q2 2026, with 3,345 vacancies (Adapted from Statistics Canada, Table 14-10-0444-01, Q2 2026)."
4. "Over the 12 months to July 2026, warehouse construction investment in the Toronto CMA totalled about $2.22 billion, including $198 million in July alone (Adapted from Statistics Canada, Table 34-10-0293-01, Investment in Building Construction, August 2025 to July 2026; sum calculated by WareMatch)."
5. "Calgary's warehouse construction investment reached $904 million over the 12 months to July 2026 (same table and citation)."
6. "Transportation and warehousing made up 4.29% of Ontario's GDP in 2025 (Adapted from Statistics Canada, Table 36-10-0400-01, 2025)."
7. "Online sales were 6.5% of Canadian retail in July 2026 ($5.08 billion of $77.8 billion, unadjusted) (Adapted from Statistics Canada, Table 20-10-0056-01, July 2026)." This is a national figure only, so use it on the country page.

### f) Pipeline incorporation

1. **Discovery at build time, not at page time.** Run `getCubeMetadata` once per PID. Write a `config/statcan_geo_map.json` that maps city slug to CMA member ID per PID (matching by SGC `classificationCode`), and province slug to member ID per PID. Rebuild it when `cubeEndDate` or `releaseTime` changes.
2. **One batch request per page set.** Build all coordinates, POST them to `getDataFromCubePidCoordAndLatestNPeriods`, and index responses by `(productId, coordinate)`. Use `latestN=4` for quarterly series and 12 to 13 for monthly series (for YoY and 12-month sums).
3. **Cache** responses per `(PID, coordinate)` with a TTL set to the table's frequency: 24 hours for monthly and quarterly tables, 30 days for annual tables. Check `getChangedCubeList/{today}` on a schedule and bust the cache only for PIDs that changed.
4. **Citation template** (adapted data):
   `Adapted from Statistics Canada, Table {pid_dashed}, {cubeTitleEn}, {reference period}. This does not constitute an endorsement by Statistics Canada of this product.`
   Build `{pid_dashed}` as `14-10-0443-01`. Render the reference period from `refPer` (quarters as "Q2 2026", annual population as "July 1, 2025").
5. **Failure handling:**
   - Treat `status != SUCCESS`, an empty `vectorDataPoint`, or `value == null` as "no stat" and skip the sentence. Do not insert zero.
   - Treat HTTP 409 as "retry later" (backoff, 3 tries).
   - On a hard failure, use the last cached value and show its reference period.
6. **Caveats:**
   - **Suppression.** `statusCode 8` means "too unreliable to be published" (null value). In my Ontario warehousing JV series, three of four quarters were null. In the province matrix, most province-by-industry JV cells for warehousing were suppressed. Use the broader NOC series (material handlers) for provinces, and warehousing JV only when the value exists.
   - **Quality flags.** `statusCode 7` means "use with caution" (e.g. Ontario warehousing vacancies 810). Write "about" or drop the figure at 7.
   - **Volatility.** Offered wages in narrow industries swing sharply (Ontario warehousing: $22.75, $24.35, $28.10 over three quarters). Do not write trend claims from one quarter.
   - **Overlap.** SEPH counts payroll employees (survey of employers). It is not the same as the LFS, and the two will not agree.
   - **Definitions.** 14100442 uses NAICS 493 ("Warehousing and storage"). 14100443 uses NOC 2021 unit groups, so "material handlers" is NOC 75101, not "warehouse workers".
   - **Reference period labels.** CMA population is a July 1 estimate stored under refPer `2025-01-01`. Do not print "January 2025".
   - **Lag.** SEPH is about 2 months. JV is about 5 months after quarter end. CMA investment is about 2 months. Population is about 15 months.
   - **CMA boundaries.** Six CMAs (Fredericton, Drummondville, Red Deer, Nanaimo, Kamloops, Chilliwack) were created in 2021. Their 2017 to 2020 values in 34100293 are "for reference only" (table footnote 4).
   - **Revisions.** Values for recent periods can be revised (status symbol 1 = preliminary, 3 = revised). Show the period with every number.
   - **Bilingual.** Names exist in both languages: `cubeTitleFr`, `memberNameFr`, plus `footnotesFr`. Data values are language-neutral. A French page can reuse the same numbers and cite `https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1410044301` (FR table link pattern taken from the open.canada.ca listings; UNVERIFIED for these PIDs).

---

## 2. Statistics Canada Job Vacancy and Wage Survey (JVWS)

JVWS is published through the same WDS API. Everything under section 1 (access, licence, rate limit, ordering gotcha) applies.

### a) Access
Same as WDS: free, no key, same host.

### b) Table IDs

| PID | Content | Geography | Period tested |
|---|---|---|---|
| 14-10-0443-01 | JV, share of JV and average offered hourly wage by NOC (824 members: broad groups and unit groups) and by job characteristics (education, experience, certification, type of position, duration, etc.) | Canada and 13 provinces and territories | 2026 Q2 |
| 14-10-0444-01 | JV and average offered hourly wage by unit group | Canada, provinces, 83 economic regions | 2026 Q2 |
| 14-10-0442-01 | JV, payroll employees, JV rate and wage by industry sub-sector (includes Warehousing and storage, Truck transportation, Couriers, Wholesale) | Province | 2026 Q2 |
| 14-10-0441-01 | Same metrics, all industries | 83 economic regions | 2026 Q2 |
| 14-10-0371-01 / 14-10-0432-01 | Monthly JV and JV rate (no wage) | Province | 2026-07 |

The older tables 14100325, 14100326 and 14100328 are inactive (last period 2023 Q3).

**Relevant NOC unit groups** (member ID in 14100443/14100444, SGC code):
- Material handlers: 720 / 75101
- Shippers and receivers: 369 / 14400
- Transport truck drivers: 703 / 73300
- Production and transportation logistics coordinators: 356 / 13201
- Supervisors, supply chain, tracking and scheduling: 335 / 12013
- Production logistics workers: 371 / 14402
- Store shelf stockers, clerks and order fillers: 620 / 65102

I confirmed these member names and IDs from the metadata. I did not look for a separate forklift-operator unit group (UNVERIFIED where forklift operators are classified).

**Example requests**
```bash
# Shippers and receivers, British Columbia, avg offered wage (14100443: geo 11, NOC 369, type-of-work all 1, stat 5)
-d '[{"productId":14100443,"coordinate":"11.369.1.5.0.0.0.0.0.0","latestN":4}]'
# Material handlers, Toronto economic region (14100444: geo 50, NOC 720, stat 1 = vacancies, 5 = wage)
-d '[{"productId":14100444,"coordinate":"50.720.5.0.0.0.0.0.0.0","latestN":4}]'
```
Note: 14100443 has four dimensions (geo, NOC, characteristic, statistic). 14100444 has three (geo, NOC, statistic). 14100442 has three (geo, NAICS, statistic: 1 vacancies, 3 payroll employees, 4 rate, 5 wage).

### c) Geography
Province and 83 **economic regions** (not CMAs). Economic region to city mapping is approximate: Toronto ER (SGC 3530), Calgary ER (4830), and so on. A city belongs to its economic region, and some regions are large rural areas. Calgary and Toronto map cleanly. Many cities share a region with other cities, such as Hamilton-Niagara Peninsula. Say "Toronto economic region" on the page, not "Toronto".

### d) Freshness and real sample values

| Series | Q3 2025 | Q4 2025 | Q1 2026 | **Q2 2026** (latest) |
|---|---|---|---|---|
| Material handlers, Ontario, vacancies | 2,875 | 2,695 | 4,200 | **4,860** (code 5) |
| Material handlers, Ontario, avg offered wage | $20.85 | $21.35 | $20.35 | **$20.25** (code 3) |
| Shippers and receivers, BC, avg offered wage | $22.00 | $20.40 | $24.95 | **$20.95** (code 3) |
| Material handlers, Toronto ER, vacancies | 1,670 | 2,040 | 3,325 | **3,345** (code 6) |
| Material handlers, Lower Mainland-Southwest ER, vacancies | 480 | 690 | 985 | **635** (code 6) |
| Warehousing and storage, Ontario, JV rate | 2.2% (code 7) | null (8) | null (8) | **1.4%** (code 7) |

Files: `jv_matHandlers_ON_*`, `jv_shippers_BC_wage_14100443.json`, `jv_regional_*`, `jv_warehousing_ON_*`.

The Q2 2026 release (reference period `2026-04-01`) came out on 2026-09-15, per the cube's `releaseTime`.

Province matrix for Q2 2026 (from `wds_province_matrix_raw.json`, joined by coordinate): material handler vacancies are published for Canada (9,175), NL (75), NS (235), NB (90), QC (1,540), ON (4,860), MB (280), SK (235), AB (735) and BC (1,115). They are null (suppressed or unavailable) for PE and the territories. Material handler wages are published for the same provinces plus Canada ($20.70), all in the $17.45 to $22.20 range. Warehousing-industry wages are published only for Canada ($27.15), QC ($24.95), ON ($28.10), MB ($19.10), AB ($24.00) and BC ($31.00); other provinces are suppressed.

### e) Usefulness: 4 of 5

It is the only free source of occupation-level labour demand and wages by province and metro-sized region. Limits: warehousing-industry cells are often suppressed, wages are job-posting offers (not paid wages), and the data is quarterly with a five-month lag.

Example sentences:
1. "Ontario employers had 4,860 open material handler positions in Q2 2026, up from 2,875 in Q3 2025, with an average offered wage of $20.25 an hour (Adapted from Statistics Canada, Table 14-10-0443-01, Q3 2025 to Q2 2026)."
2. "In the Toronto economic region, the average offered wage for material handlers was $20.10 an hour in Q2 2026, and shippers and receivers were offered $24.80 (code 3, high quality) (Adapted from Statistics Canada, Table 14-10-0444-01, Q2 2026)." The $24.80 figure is the Q2 2026 value in `jv_regional_wage_shippers_Toronto_14100444.json` (quality code 3), but the series swung from $22.40 to $21.10 earlier, so avoid trend claims.
3. "British Columbia employers were offering shippers and receivers an average of $20.95 an hour in Q2 2026 (Table 14-10-0443-01)."
4. "Across Canada the JV survey recorded 9,175 vacancies for material handlers in Q2 2026 (Table 14-10-0443-01)."
5. Stat block: Warehousing and storage average offered wage, Ontario: $28.10 (Q2 2026; quality 5). Add a "volatile" flag and omit trend text.

### f) Pipeline
- Same calls and cache as section 1. Pull `latestN=4` to show the last four quarters.
- **Suppression is the main issue.** Run a rule per metric: need `value != null` and `statusCode in (0..6)`. At `statusCode 7`, write "about" or drop. At 8, 1, 9 or 10, skip the sentence. Prefer the NOC tables (14100443/4) over industry tables (14100442) for provinces.
- **Fallback chain for a city page:** economic region (14100444) then province (14100443) then Canada. Say which level you are using ("In Ontario...").
- **Citation:** use the section 1 template with the 14-10-0443-01 or 14-10-0444-01 title. Add "average offered wage reflects posted job vacancies, not wages paid".
- **Caveats:** the survey is sample-based, so very small cells are suppressed. Quarter labels: refPer `2026-04-01` is Q2. The `refPer` is the first day of the quarter. Occupation classification switched to NOC 2021 (the older tables used NOC 2016, so do not compare across table versions). Bilingual: NOC and NAICS names are available in French through `memberNameFr`.

---

## 3. Transport Canada open data

### a) Access
- **There is no general Transport Canada statistics API.** The open.canada.ca catalogue is a CKAN API: `https://open.canada.ca/data/api/3/action/package_search?...`. It is free, with no key. It returned HTTP 200 (`tc_ckan_search_transport.json`). I saw no documented rate limit (UNVERIFIED). It is a metadata catalogue only. The data itself lives in files or map services listed on each dataset.
- `fq=organization:tc` returns **49 Transport Canada datasets** (`tc_ckan_org_tc_all.json`). I reviewed every title. Most are safety, vehicles, vessels, programs and internal audits. Only a few are relevant to location pages (see below).
- Licence: all the TC and CBSA datasets I opened are `ca-ogl-lgo` (Open Government Licence - Canada). Commercial use is allowed. Attribution: "Contains information licensed under the Open Government Licence - Canada."

### b) What actually exists

**Real-time or API-style**

| Data | Format | URL | Tested |
|---|---|---|---|
| Airports with air navigation services (93 airports) | CSV and ArcGIS REST MapServer | CSV: `https://ftp.cartes.canada.ca/pub/tc_tc/Airports_Aeroport/canadian_airports_w_air_navigation_services/Airports_Aeroports.csv`; REST: `https://maps-cartes.services.geo.ca/server_serveur/rest/services/TC/canadian_airports_w_air_navigation_services_en/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json` | Yes, both returned 200 (`tc_airports.csv`, `tc_airports_arcgis_query.json`) |
| Canada's National Highway System | ArcGIS REST, WMS, GDB | `https://maps-cartes.services.geo.ca/server_serveur/rest/services/TC/canada_national_highway_system_en/MapServer` | Not queried. Listed on the dataset. |
| Grade Crossings Inventory (rail) | CSV | on dataset `d0f54727-6c0b-4e5a-aa04-ea1463cf9f4c` | Not downloaded. Updated 2023. |
| Weekly rail system performance indicators | HTML and XLSX dictionary | `https://tdih-cdit.tc.canada.ca/en/rail-2023` | Not queried. Series stopped (StatCan copy ends 2023-04). |

**CBSA (not Transport Canada but needed for border context):** Current Border Wait Times, a CSV refreshed continually: `https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv` (and `bwt-fra.csv`). It returned 200 with 30 crossings (`cbsa_bwt_eng.csv`). Values at 2026-10-19 about 09:30 local, commercial flow Canada bound: Peace Bridge (Fort Erie, ON) "1 minute", Ambassador Bridge (Windsor, ON) "5 minutes", Blue Water Bridge "No Delay", Pacific Highway (Surrey, BC) "5 minutes", Coutts "No Delay", Emerson "No Delay". The format is a `;;`-delimited text file, not a standard CSV. Parse manually. There is also a historical land-mode wait-time dataset (CBSA, `000fe5aa...`, not downloaded) and traveller volumes by port of entry and month (CBSA dataset `1b1c2b92-b388-47d9-87d4-01aee8d3c3e4`, not downloaded). Wait times are real-time, so they are unsuitable for a static SEO page (they change hourly).

**What does NOT exist as a TC dataset** (I searched the catalogue: "marine port", "intermodal terminal", "container port", "trade corridor", "warehouse"):
- No Transport Canada dataset of ports, container terminals or intermodal terminals as a table or API. I found only old NRCan Atlas maps (2006, JPG and PDF) and a National Trade Corridors Fund audit report. No intermodal terminal dataset (search returned 0).
- No TC freight tonnage by port or by city table. (Port Authority statistics exist at individual port authority websites, outside this research. UNVERIFIED.)
- No Transport Canada warehouse or logistics real-estate data.

**TC-sourced statistics published through StatCan WDS** (these are the useful ones, and they are on the same keyless API):

| PID | Title | Latest | Notes |
|---|---|---|---|
| 23-10-0254-01 | Air cargo traffic at Canadian airports, annual | 2025 | Tonnes loaded and unloaded by airport, with domestic, transborder and international splits |
| 24-10-0052-01 | Vehicles entering Canada by land (trucks by crossing) | 2026-07 | Includes truck counts by crossing |
| 23-10-0216-01 | Railway carloadings, by tonnage, monthly | 2026-07 | Canada and two divisions only |
| 23-10-0063-01 | Intermodal tonnage by origin and destination | 2024 | Province-to-province |
| 23-10-0269 / 270 / 271 | Transport Canada indicators: activity, utilization, supply chain performance | 2024-09 | Stale (last 2024-09) |
| 12-10-0177-01 | Merchandise trade by mode of transport | 2026-08 | National only |

### c) Geography
- Airports: point data (lat/long, province, city name) for 93 airports with NAV CANADA services (BC 23, ON 18, QC 14, AB 14, MB 5, NL 4, SK 4, NB 3, NT 3, NU 2, YT 1, NS 1, PEI 1). The airports file is **not** a list of cargo airports, and **at least one data error exists**: `YYT` St. John's International is labelled city "Saint John" (the real city is St. John's) (YVR is listed under Richmond, which is where the airport sits, so city labels follow the airport's municipality, not the metro). Verify city names before publishing.
- Border and air cargo: crossing or airport entities, not cities. Map them by a manually maintained lookup (for example: Windsor page gets Ambassador Bridge and Gordie Howe; Fort Erie page gets Fort Erie crossing).
- Province page: use province field (airports) and provincial members in 24100052's "Ontario" geography (ID 90).

### d) Freshness and real sample values

| Series | Latest | Values | File |
|---|---|---|---|
| Air cargo, Toronto Pearson (23100254), total loaded and unloaded | 2025 | 482,483.9 tonnes (2024: 433,219.5; 2023: 411,554.4), +11.4% vs 2024 (my calculation) | `aircargo_Pearson_23100254.json` |
| Air cargo, Vancouver International | 2025 | 330,223.6 tonnes (2024: 308,093.9) | `aircargo_YVR_23100254.json` |
| Air cargo, Calgary International | 2025 | 138,531.3 tonnes (2024: 124,374.8) | `aircargo_YYC_23100254.json` |
| Trucks entering Canada, Fort Erie crossing (24100052) | 2026-07 | 43,583 (June 42,724; Feb 37,155) | `trucks_FortErie_24100052.json` |
| Trucks entering Canada, Pacific Highway | 2026-07 | 32,064 | `trucks_PacificHwy_24100052.json` |
| Trucks entering Canada, Coutts | 2026-07 | 13,016 | `trucks_Coutts_24100052.json` |
| Trucks entering Canada, Windsor - Gordie Howe International Bridge | 2026-07 | 4,114 (Feb to Jun are null with status 1, "not available for a specific reference period", because the bridge was new) | `trucks_GordieHowe_24100052.json` |
| Rail carloadings, Canada, total traffic, tonnes (23100216) | 2026-07 | 31,686,803 (June 30,991,339; May 33,407,677) | `rail_carloads_Canada_tonnes_23100216.json` |

Air cargo and truck counts are in tonnes and vehicles. The "Ambassador Bridge" is not a named member in 24100052 (my search for it found only "Windsor - other locations" and the Gordie Howe bridge). UNVERIFIED whether Ambassador Bridge traffic is under "Windsor - other locations".

### e) Usefulness: 2 of 5 for the TC files, 4 of 5 for the TC-sourced StatCan tables

- TC's own files: static point lists with data errors, no freight volumes, no ports. Only the airport list is marginally useful, and a hand-maintained airport file would be cleaner.
- The StatCan tables (air cargo by airport, trucks by crossing, rail tonnage, intermodal OD) are good, current and keyless. They make useful "logistics gateway" blocks for pages near an airport or a border.

Example sentences:
1. "Toronto Pearson handled 482,484 tonnes of air cargo in 2025, up 11.4% from 433,220 tonnes in 2024 (Adapted from Statistics Canada, Table 23-10-0254-01, Air cargo traffic at Canadian airports, annual, 2025)."
2. "About 43,600 trucks entered Canada at Fort Erie in July 2026 (Statistics Canada, Table 24-10-0052-01, Vehicles entering Canada by land, July 2026)."
3. "Vancouver International moved 330,224 tonnes of air cargo in 2025 (same table)."
4. "Canadian railways carried 31.7 million tonnes of freight in July 2026 (Statistics Canada, Table 23-10-0216-01, Railway carloadings statistics, July 2026)."
5. Border wait times (CBSA, Open Government Licence - Canada) can power a "live" widget but not static copy. At 2026-10-19 09:28 EDT the commercial delay at Ambassador Bridge, Windsor was "5 minutes". Do not hard-code this.

### f) Pipeline
- **StatCan tables:** same WDS pipeline as section 1, with a hand-built `city -> airport member ID` and `city -> crossing member ID` map. Air cargo is annual (cache 30 days). Truck counts are monthly.
- **Airport CSV:** download once, store in the repo, refresh quarterly. The file is **Latin-1 encoded** (the bytes appear as replacement characters in UTF-8). Open with `encoding='latin-1'`. Fix known name errors.
- **CBSA wait times:** do not use in static pages. If wanted for a live widget, fetch client-side or via a short-TTL (5 minutes) cache. Split on `;;`. Cite "Contains information licensed under the Open Government Licence - Canada."
- **Citation templates:**
  - StatCan: section 1 template.
  - OGL (TC and CBSA): `Contains information licensed under the Open Government Licence - Canada. Source: {publisher}, {dataset title}, retrieved {date}.`
- **Failure handling:** same as section 1. For null values (new crossings, status 1) omit the sentence.
- **Caveats:**
  - Truck counts are vehicles entering Canada (inbound only, not exports).
  - "Trucks" in 24100052 is a vehicle type, not a load or tonnage measure.
  - Air cargo is annual with a long lag (2025 published mid-2026).
  - The TC indicator tables 23100269 to 23100271 stop at 2024-09, so they are stale.
  - Bilingual: the airports file has `PROVINCE_FR` and `AIRPORT_T`/French columns. The CBSA wait file has an FR twin (`bwt-fra.csv`).

---

## Recommended build order

1. **WDS core:** 14100201, 14100443/4, 34100293, 17100148, 14100458, 36100400, 20100056 (national only). Build the runtime member-ID resolver and the `(PID, coordinate)` keyed cache.
2. **WDS logistics blocks:** 23100254 (air cargo) and 24100052 (trucks) with a hand-built crossing and airport lookup.
3. **Skip or defer:** Transport Canada's own files (low value), CBSA wait times (live only), and TC indicator tables 23100269 to 271 (stale).
4. **Open questions to check before launch:** which province-level data is published for the territories (SEPH returned nulls for YT, NT and NU in July 2026), and whether Ambassador Bridge traffic appears in 24100052 under another label.

## Files saved

All under `/Users/carlaklaasen/Desktop/WareMatch/content-writing/pipeline/research/samples/`:
`wds_*.json` (cube metadata, code sets, series info, province matrix), `seph_*`, `jv_*`, `jvmonthly_*`, `bldg_*`, `pop_*`, `lfs_*`, `gdp_*`, `ecomm_*`, `retail_total_*`, `aircargo_*`, `trucks_*`, `rail_*`, `tc_*`, `cbsa_*`.
