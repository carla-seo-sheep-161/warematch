# U.S. government data APIs for WareMatch 3PL location pages

Tested live on 2026-10-19. Raw samples are in `/Users/carlaklaasen/Desktop/WareMatch/content-writing/pipeline/research/samples/`.
Files from this report: `bls_v1_*.json`, `qcew_2026q1_*.csv`, `bts_*.json`, `census_cbp2023_geography.txt`, `census_cbp2023_vars.txt`.
The other files in that folder come from other research tasks.

Verdicts
- **BLS: viable now, no key.** QCEW (keyless CSV), the v1 API for CES, LAUS and OEWS (keyless but 25 queries a day) and the v2 API (free key) all work.
- **BTS: viable, no key.** Socrata gives CFS 2022 warehousing flows, border truck crossings and port data.
- **Census: viable only with a free key.** Keyless data calls were rejected from this machine. Metadata is keyless.

---

## 1. U.S. Census Bureau API (api.census.gov)

### a) Access
- **Free, but a key is effectively required.**
  - Keyless data calls return HTTP 302 to `https://api.census.gov/data/missing_key.html`, with the response header `X-DataWebAPI-KeyError: 1`.
  - I tested CBP 2022, CBP 2023 and ACS5 2023. A bogus key redirects to `invalid_key.html`.
  - Census historically allowed about 500 keyless queries a day per IP. That did NOT work from this IP. Treat keyless as unavailable.
  - Cannot tell whether the block is global or specific to this IP. Unverified.
- **Metadata is keyless and returned HTTP 200.** This covers `/data.json`, `/data/2023/cbp/variables.json` and `geography.json`.
- **Signup:** go to https://api.census.gov/data/key_signup.html, enter an organization name and email, then click the activation link in the email. I did not sign up.
- **Rate limits:** with a key, the commonly cited limit is about 500 variables per call and no hard daily cap. Not verified, because the official limits page returned 404.
- **Terms:** Census data is U.S. government public domain. Census requires this disclaimer on API-powered products: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau." This is from memory, so verify before launch.

### b) Endpoints and variables
Latest vintages per the live discovery catalog (`data.json`):
- CBP: 2023 (modified 2025-03-06)
- ACS5: 2024 (modified 2025-09-02)
- Nonemployer statistics (`nonemp`): 2024 (modified 2026-03-13)
- Economic Census (`ecnbasic`): 2022
- Annual Business Survey (`abscs`, `abscb`): 2023

CBP variables are confirmed from `variables.json`: `ESTAB` (establishments), `EMP` (employees), `PAYANN` (annual payroll, $1,000), `PAYQTR1`, `NAICS2017`, `EMPSZES`, `LFO`.

CBP geographies are confirmed from `geography.json`: us, state, county (needs state), metro/micro statistical area, combined statistical area, congressional district, zip code. **There is no place (city) level.**

Example requests (add `&key=KEY`). These were NOT run successfully, so the sample values are unverified.
- State warehousing: `https://api.census.gov/data/2023/cbp?get=NAME,ESTAB,EMP,PAYANN&for=state:*&NAICS2017=493`
- Counties in Texas: `https://api.census.gov/data/2023/cbp?get=NAME,ESTAB,EMP,PAYANN&for=county:*&in=state:48&NAICS2017=493`
- Metro areas: `https://api.census.gov/data/2023/cbp?get=NAME,ESTAB,EMP&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*&NAICS2017=493`
- E-commerce NAICS 4541: use the same CBP call with `NAICS2017=4541`. Note that 454110 is NAICS 2012. CBP 2023 uses NAICS 2017, where 4541 is "Electronic shopping and mail-order houses" (verified in the BTS CFS data). Check the NAICS code list before relying on 454110.
- ACS5, state level: `https://api.census.gov/data/2024/acs/acs5?get=NAME,B01003_001E,B19013_001E,B11001_001E&for=state:*`
  - `B01003_001E` is total population.
  - `B19013_001E` is median household income.
  - `B11001_001E` is total households.
- ACS5, place (city) level: `...&for=place:*&in=state:48`
- Nonemployer: `https://api.census.gov/data/2024/nonemp?get=NAME,NESTAB,NRCPTOT&for=state:*&NAICS2017=493`

**Quarterly E-Commerce:** I found NO Census API dataset for it in the discovery catalog. It is published as downloadable files only. Mark that as unverified for the API.
- Not in the catalog: `timeseries/eits/ecomm`.
- Only `ecnecomm` (2022, manufacturing e-commerce) appeared.

### c) Granularity and mapping
- **Country:** use `for=us:*`.
- **State pages:** the state FIPS goes in `for=state:48`.
- **City pages:**
  - ACS has place-level data, matched with the Census place FIPS (needs a city-to-place crosswalk, e.g. from the Gazetteer files).
  - CBP has only county, metro or ZIP. Map each city to a county or metro (CBSA).
  - ZIP-level CBP exists, but 2023 ZBP is not in the catalog (ZBP stops at 2018 in the catalog output). CBP 2023 does list a `zip code` geography.
- CBP has disclosure suppression. County cells for 493 may carry employment flags or ranges (`EMP_N`, `EMPSZES`). Unverified here.

### d) Freshness (live)
Keyless data calls failed, so there are no sample values.
- The latest vintages above come from catalog metadata, not from data calls.
- Typical lag:
  - CBP lags about 18 months (2023 data released March 2025).
  - ACS5 lags about 1 year.

### e) Usefulness: 3/5, if a key is obtained
Candidate stat blocks, with numbers to be filled from real calls:
- "Census Bureau, County Business Patterns 2023: {ESTAB} warehousing and storage establishments employing {EMP} people in {state}."
- "ACS 2020-2024 5-year: median household income of ${B19013} and {B01003} residents in {city}."
- Both are generic demographics, and similar content is common. CBP is the more unique data. Counts of establishments and employees show the 3PL footprint.

### f) Pipeline
- **Call:** `get_cbp(state_fips, county_fips|cbsa)`.
- **Cache:** annual vintage, so cache per vintage. Raw JSON goes to disk by URL hash. Refresh once a year.
- **Citation template:** "U.S. Census Bureau, County Business Patterns {vintage}, NAICS 493 (Warehousing and Storage), {geo}."
- **Failure handling:** a 302 to `missing_key.html` or `invalid_key.html` means a key problem. Fail hard, and do not follow the redirect.
- **Caveats:**
  - Suppressed cells.
  - NAICS 2017 versus 2022 code changes.
  - CBP excludes self-employed people and most agricultural and government employment.
  - CBP counts establishments, not warehouse square footage.

---

## 2. U.S. Bureau of Labor Statistics

### a) Access
- **Three endpoints, no key for the first two.**

| Access | Limits | Verified |
|---|---|---|
| QCEW open-data CSV (`data.bls.gov/cew/data/api/...`) | No key. Limits not stated. | Yes, HTTP 200. |
| Public Data API v1 (`https://api.bls.gov/publicAPI/v1/timeseries/data/`) | No key. 25 queries a day, 25 series a query, 10 years a query. | Yes, POST calls worked. |
| Public Data API v2 | Free key. 500 queries a day, 50 series a query, 20 years a query. Catalog and calculations available. | Not called (no key). |

- **Rate limits from the BLS FAQ (fetched):** both versions allow 50 requests per 10 seconds. v2 keys must be renewed yearly.
- **Signup for v2:** https://data.bls.gov/registrationEngine/. Enter an email and organization, then use the key emailed to you. I did not sign up.
- **Terms:** BLS content is public domain. BLS asks for citation as the source (see https://www.bls.gov/opub/copyright-information.htm). I could not fetch that page, so it is unverified.
- **Bot blocking:** `bls.gov` pages return a tiny stub to plain curl. The data hosts (`api.bls.gov`, `data.bls.gov/cew`) work.

### b) Series IDs and endpoints (all verified by live calls unless noted)

**CES employment, warehousing and storage (NAICS 493)**
- `CES4349300001` is national employees in thousands, seasonally adjusted. Naming follows the BLS CES convention for industry 43493000. The series title could not be fetched, because the v1 catalog is disabled.
- `CES4349300003` is average hourly earnings (all employees), and `CES4349300008` is average hourly earnings of production and nonsupervisory employees.
- `SMU48000004349300001` is Texas, not seasonally adjusted.
- Format: `SMU` + state FIPS (2) + area (5, `00000` for statewide) + industry (8) + data type (2).
- Metro-level 493 series like `SMU48191004349300001` do not exist. Metro CES works only at supersector level, e.g. `SMU48191004300000001` (Dallas, transportation, warehousing and utilities, 268.8 thousand in 2026-08).

**LAUS unemployment (data type 03 is the unemployment rate, 06 is the labor force)**
- `LASST480000000000003` is Texas, `LAUCN481130000000003` is Dallas County, `LAUMT481910000000003` is the Dallas metro, `LNS14000000` is national.

**OEWS wages**
- Format: `OE` + `U` + areatype (`N` national, `S` state, `M` metro) + area (7 digits) + industry (6 digits, `000000` for all) + occupation (6 digits) + data type (2 digits).
- Data types used: `01` employment, `03` hourly mean wage, `04` annual mean wage.
- Occupation codes used:
  - `537062` laborers and freight, stock and material movers, hand.
  - `537051` industrial truck and tractor operators (forklift).
  - `537065` stockers and order fillers.
- State and metro area codes are the FIPS or CBSA code padded to 7 digits (Texas is `4800000`, Dallas-Fort Worth is `0019100`).

**QCEW (the best fit for location pages)**
- By area: `https://data.bls.gov/cew/data/api/{year}/{qtr}/area/{area_fips}.csv`
- By industry: `https://data.bls.gov/cew/data/api/{year}/{qtr}/industry/493.csv`
- Area titles: `https://data.bls.gov/cew/doc/titles/area/area_titles.csv`
- Useful columns: `qtrly_estabs`, `month3_emplvl`, `avg_wkly_wage`, `lq_month3_emplvl` (location quotient), `oty_month3_emplvl_pct_chg`, `disclosure_code`.
- Row filter: `own_code=5` (private) and `industry_code` in `493`, `4931`, `493110` (general warehousing), `493120` (refrigerated), `493130` (farm product).

### c) Granularity and mapping
- **QCEW:** US (`US000`), state (`48000`), county (`48113`), MSA (`C1910`).
  - County is the finest level for 493.
  - Verified: the `industry/493.csv` file contains only agglvl 15 (US), 55 (state) and 75 (county), so no metro-level 493.
  - The MSA area file has only totals, which I saw as a single row.
- **OEWS:** national, state, metro (CBSA) and non-metro areas. No county or city.
- **LAUS:** national, state, county and metro.
- **City pages** map a city to a county (QCEW and LAUS) and to a CBSA (OEWS), via a crosswalk.
- **State pages** use the state area code directly.

### d) Freshness and live samples (2026-10-19)
- **CES national, 2026-09 (preliminary):** `CES4349300001` = 1831.8 thousand.
  - Response excerpt: `('2026','M09','1831.8',[{'code':'P','text':'preliminary'}])`
- **CES Texas, 2026-08:** `SMU48000004349300001` = 180.8 thousand.
- **LAUS Texas, 2026-08:** `LASST480000000000003` = 4.4%. Dallas County = 4.5%.
- **OEWS, May 2025 estimates, label `A01`:**
  - National laborers and material movers: 2,950,280 employed, $20.32 mean hourly wage.
  - Texas laborers and material movers: 216,970 employed, $18.94 mean hourly wage.
  - California laborers and material movers: $21.92 mean hourly wage.
  - Dallas-Fort Worth metro: $19.63 mean hourly wage.
  - Texas forklift operators: $21.83 mean hourly wage.
- **QCEW 2026 Q1** is the latest quarter. 2026 Q2 returned HTTP 404.

| Area | Estabs | Q1 2026 employment | Avg weekly wage | Notes |
|---|---|---|---|---|
| US, NAICS 493 | 23,848 | 1,859,296 | $1,077 | -0.5% over the year |
| Texas | 2,213 | 181,273 | $1,078 | +6.8% over the year, LQ 1.07 |
| Dallas County | 314 | 45,851 | $1,043 | +8.7% over the year, LQ 2.11 |

- Disclosure codes: Dallas County 493120 (refrigerated warehousing) has `disclosure_code='N'` with 12 establishments and employment 0. That is suppression, not zero employment.
- Cook County, IL (17031) has `own_code=3` suppressed. Check that the private row exists.
- Files: `qcew_2026q1_area_48000.csv`, `qcew_2026q1_area_48113.csv`, `qcew_2026q1_industry_493.csv`.

### e) Usefulness: 5/5
Employment, wages and unemployment by county and metro are real location data that competitors rarely publish. Example stat blocks:
- "BLS QCEW, 2026 Q1: Dallas County, Texas had 314 private warehousing and storage establishments employing 45,851 workers, an average weekly wage of $1,043."
- "Warehouse employment in Dallas County is 2.11 times the national concentration (location quotient), per BLS QCEW 2026 Q1."
- "BLS OEWS, May 2025: laborers and material movers in Texas average $18.94 per hour, against $20.32 nationally."
- "BLS LAUS, August 2026 (preliminary): Texas unemployment rate was 4.4%."
- "BLS CES, September 2026 (preliminary): U.S. warehousing and storage employs about 1,831,800 people."

### f) Pipeline
- **QCEW:**
  - One download per quarter for the industry file (`industry/493.csv`, about 350 KB) covers every state and county.
  - Parse with Python `csv` and filter `own_code=='5'`.
  - Look up the area code from the slug via a state/county FIPS table.
  - Cache by `{year}_{qtr}`.
- **v1 API:** batch up to 25 series per query, and cache everything. At 25 queries a day, a state-level build fits in a day. A county or metro build should get the v2 key.
- **Citation templates:**
  - QCEW: "U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, {year} Q{q}, NAICS 493, {area}."
  - OEWS: "U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May {year}."
  - LAUS: "U.S. Bureau of Labor Statistics, Local Area Unemployment Statistics, {month year}, {area}."
- **Failures:**
  - Series that do not exist return a message in `message[]`.
  - Series with no data return an empty `data` array.
  - A 404 on the QCEW file means the quarter is not out yet, so fall back one quarter.
  - On a suppression code (`disclosure_code` non-empty), skip the stat.
- **Caveats:**
  - Marking CES and LAUS as "preliminary" when the footnote code is `P`.
  - OEWS is annual with a lag of about 1 year.
  - QCEW lags about 5 months, and NAICS 493 covers firms, not warehouse facilities.
  - Also keep NAICS 493 distinct from fulfillment: it excludes parts of retail and e-commerce operations.

---

## 3. U.S. Bureau of Transportation Statistics (data.bts.gov, Socrata)

### a) Access
- **Free, no key.** The SODA endpoint is `https://data.bts.gov/resource/{id}.json`. I made keyless calls and they succeeded.
- **Rate limits:** Socrata throttles anonymous use at the shared-IP level, and an app token raises the limit. The exact limit is unverified. Sign up for a token at https://data.bts.gov/profile/edit/developer_settings (needs a free Socrata account, which I did not create).
- **Terms:** the CFS dataset license is "Public Domain U.S. Government" (USGOV_WORKS), attribution "US Census Bureau". Border Crossing and Top 25 Container Ports are marked "Public Domain".
- **Catalog search:** `https://api.us.socrata.com/api/catalog/v1?domains=data.bts.gov&only=datasets&q=...`

### b) Datasets (verified IDs)
- **`j246-y2rf` CFS Area File 2012-2022.**
  - Commodity Flow Survey, produced with Census. Has NAICS 4931 (Warehousing and storage) and 4541 (Electronic shopping and mail-order houses) at national, state and CFS-area levels.
  - Filters used: `year`, `naics`, `comm='0000'`, `dmode`, `shipwt='1'`, `shipdist='1'`, `ddestgeo='0100000US'`.
  - `geotype` 01 is national, 02 is state, 16 is a CFS metro area.
- **`keg4-3bc2` Border Crossing Entry Data.** Port-level monthly crossings, with a `measure` column (Trucks, Trains and so on) and a `state` column using full names ("Texas").
- **`sn74-xpkp` Top 25 Container Ports by TEU.** Sample columns: `port`, `imports`, `exports`, `domestic`. No year column in the sample, so the year is unverified.
- **`5rpz-kgm9` Port Data.** Latest `reporting_year` is 2023.
- **`y5ut-ibwt` Supply Chain and Freight Indicators**, updated weekly (rail dwell time and similar).
- **County-to-county truck travel times**, 2018 to 2024, experimental (e.g. `uta5-4eu5` for 2024). Not called.
- **FAF5** is hosted by FHWA and ORNL, with downloadable zip files (e.g. `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_State.zip` returned HTTP 206 for a ranged request). It is not on Socrata.
- **NTAD** (airports and ports layers) on `geo.dot.gov` ArcGIS returned "Token Required" or "Service not found" for the URLs I tried, so it is unverified.
- **TransBorder freight:** the catalog shows only a story page (`kijm-95mr`), not a data table. Unverified as an API.
- **There is no BTS warehouse dataset.** A catalog search for "warehouse" returned nothing.

Example calls:
- `https://data.bts.gov/resource/j246-y2rf.json?$select=geo_ttl,naics_ttl,dmode_ttl,year,ton,val&$where=year='2022' AND naics='4931' AND st='48' AND geotype='02' AND comm='0000' AND dmode='00' AND shipwt='1' AND shipdist='1' AND ddestgeo='0100000US'`
- `https://data.bts.gov/resource/keg4-3bc2.json?$select=port_name,sum(value) as total&$where=state='Texas' AND date>='2025-01-01' AND date<'2026-01-01' AND measure='Trucks'&$group=port_name&$order=total DESC&$limit=5`

### c) Granularity and mapping
- **CFS:** national, state, CFS metro area (FAF-style areas, such as "Dallas-Fort Worth, TX-OK CFS Area (part); Texas", `geo_id` `E330000US4820600000`).
- **Border crossings and ports:** point locations with latitude and longitude, so they map to a city or state by name or by distance.
- **State pages:** use the `st` FIPS filter for CFS and the full state name for border data.
- **City pages:** map the city to the nearest CFS area or port. Many cities have no CFS area (it is "Remainder of Texas").

### d) Freshness and live samples
- **CFS:** latest year is 2022 (`max(year)` returned `2022`). Units are not in the column metadata. Assumed thousands of tons and millions of dollars, which is consistent with the published U.S. totals (`ton`=12,468,902 and `val`=14,517,812 for 2017).
  - US, 4931 warehousing and storage: 305,651 ton and 1,347,716 val, 2022.
  - Texas, 4931: 48,085 ton and 167,137 val. Texas, 4541 e-commerce shippers: 2,588 ton and 52,542 val.
  - Dallas-Fort Worth CFS area (Texas part), 4931: 8,353 ton and 23,172 val.
  - Texas 4931 by mode: for-hire truck 10,423 ton, company-owned truck 25,178 ton, customer pick-up 5,080 ton.
  - Values of 0 with a non-zero tonnage (Houston 4931 `val`=0, Austin 4541 `val`=0) are suppressed, not real zeros.
  - Excerpt: `{"geo_ttl":"Texas","naics":"4931","naics_ttl":"Warehousing and storage","dmode_ttl":"All modes","year":"2022","ton":"48085","ton_s":"13.1","val":"167137","val_s":"23.4"}`
  - `val_s` and `ton_s` are standard errors in percent (an assumption from the column names). These are high, 13 to 37%.
- **Border Crossing:** latest month is 2026-08. Texas trucks in 2025: Laredo 2,945,388, Hidalgo 719,184, Ysleta 641,729, Eagle Pass 368,985, Brownsville 306,858.
- **Top 25 Container Ports:** Port Authority of New York and New Jersey 5,352,134 imports, Port of Los Angeles 5,231,585 (year unverified).

### e) Usefulness: 4/5 (state and port-city pages), 2/5 for general city pages
Example stat blocks:
- "U.S. Census Bureau and BTS, Commodity Flow Survey 2022: Texas warehousing establishments shipped about 48 million tons valued at $167 billion."
- "Of those shipments, company-owned trucks carried about 25.2 million tons (CFS 2022, Texas, NAICS 4931)."
- "Laredo handled 2,945,388 truck crossings in 2025, the most of any Texas port (BTS Border Crossing Entry Data)."
- Treat the CFS figures with care: sampling error is large.

### f) Pipeline
- **Call:** Socrata SoQL with `$where` filters. Use `$limit` and `$offset` for pages. Add an app token header (`X-App-Token`) once you have one.
- **Cache:** CFS is a 5-year survey, so cache for a year. Border data is monthly, so refresh monthly.
- **Citation template:** "U.S. Bureau of Transportation Statistics and U.S. Census Bureau, Commodity Flow Survey {year}, CFS Area File, NAICS 4931, {geo}."
- **Failure handling:** an empty array `[]` means no match (wrong code or the wrong state name). Check `val`=0 with `ton`>0 for suppression.
- **Caveats:**
  - Large standard errors.
  - The 2022 survey year is old for text such as "latest".
  - Mixed units (thousands of tons, millions of dollars).
  - Code 493 is 4931 here, and the CFS NAICS codes are not the same detail level as QCEW.

---

## Summary of verdicts
1. **BLS:** viable, 5/5. QCEW keyless gives county and state warehousing employment, wages and LQ for 2026 Q1.
2. **BLS v1:** gives CES, LAUS and OEWS keyless, but limited to 25 queries a day. Get the free v2 key for a full build.
3. **BTS:** viable, 4/5 for state and port pages. CFS 2022 has NAICS 4931 at state and metro level. Sampling error and suppression apply.
4. **Census:** blocked without a key. Keyless data calls redirected to `missing_key.html`. Get a free key at https://api.census.gov/data/key_signup.html and re-test.
5. **Census:** CBP 2023 and ACS5 2024 are the latest vintages in the catalog (unverified by data calls).
6. **Census:** CBP has no city level, only county, metro and ZIP. ACS has place level.
7. **Census:** no Quarterly E-Commerce API dataset was found.
8. **BTS:** no warehouse dataset. Ports, borders and freight flows only. FAF5 is download-only.
9. **Not verified:** the Census key limits, the BLS copyright page, Socrata anonymous limits, and TransBorder as an API.
