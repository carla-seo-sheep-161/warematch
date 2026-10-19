# Geo open-data APIs for programmatic 3PL location pages: GeoNames and OSM Overpass

Tested 2026-10-19 from Carla's Mac with curl. Raw samples are in `samples/`. Anything marked **(unverified)** was not tested live. Distances and sums marked "computed" were calculated by me from the downloaded dump with a haversine script.

## Verdicts

| API | Verdict |
|---|---|
| GeoNames, free dump `cities15000.zip` | **Viable, use it.** It is keyless, fresh and CC-BY 4.0. |
| GeoNames web services | **Not testable keyless.** They need a free username. Use only if the dumps are not enough. |
| OSM Overpass | **Viable only as a batch, cached, heavily hedged data source. Do not call it live per page build.** Public servers were flaky (HTTP 500 and 502). Results differed between backends. Tagging is inconsistent. |

---

## 1. GeoNames

### a) Access, terms, limits
- **Web services (api.geonames.org)** need a registered username on every call.
  - Keyless call tested: `curl "http://api.geonames.org/searchJSON?q=columbus&maxRows=1"` returned HTTP 401 and `{"status":{"message":"Please add a username to each call ...","value":10}}`.
  - The shared `demo` account is unusable. It returned `{"status":{"message":"the daily limit of 20000 credits for demo has been exceeded. Please use an application specific account. Do not use the demo account for your application.","value":18}}`.
  - Signup steps (not performed): create an account at geonames.org/login, confirm the email, then go to the account page and tick "Enable free web services". Use the username as `&username=XXX`.
  - Free-tier limits **(unverified in this session)**: roughly 20,000 credits per day and 1,000 credits per hour, where one simple call is one credit and some calls cost more. The "20000 daily" figure for demo is confirmed by the error above. Premium plans exist for more.
- **Downloadable dumps (download.geonames.org/export/dump/)** need no login. The free dump works keyless.
  - `cities15000.zip` (3.36 MB, Last-Modified **2026-10-19 02:00 UTC**, so refreshed daily) holds 34,173 places with population of 15,000 or more. `cities5000.zip` and `cities1000.zip` also exist **(not downloaded)**.
  - `admin1CodesASCII.txt` maps state/province codes to names. Samples: `US.OH Ohio`, `CA.01 Alberta`.
- **License:** the readme says "Creative Commons Attribution 4.0 License". Attribution to GeoNames is required.

### b) Endpoints and queries
The web-service endpoints below are from my knowledge of the GeoNames API and are **not tested**.
- Search: `http://api.geonames.org/searchJSON?q=Columbus&country=US&adminCode1=OH&featureClass=P&maxRows=1&username=X`
- Nearby places: `.../findNearbyPlaceNameJSON?lat=39.96118&lng=-82.99879&radius=50&cities=cities15000&maxRows=30&username=X`
- Nearby cities by bounding box: `.../citiesJSON?north=..&south=..&east=..&west=..&username=X`
- Postal codes: `.../postalCodeSearchJSON?placename=Columbus&country=US&username=X`
- Hierarchy: `.../hierarchyJSON?geonameId=4509177&username=X`
- Timezone: `.../timezoneJSON?lat=..&lng=..&username=X`
- Single record with population: `.../getJSON?geonameId=4509177&username=X`

**Tested dump approach (no key).** The file is tab-separated. Columns: 0 geonameid, 1 name, 4 lat, 5 lon, 6 feature class, 7 feature code, 8 country, 10 admin1 code, 14 population, 17 timezone, 18 modification date.
```
curl -O https://download.geonames.org/export/dump/cities15000.zip
curl -O https://download.geonames.org/export/dump/admin1CodesASCII.txt
```

### c) Facts for pages
- **Country page:** list of cities of 15,000 or more and their populations (from the dump).
- **State page:** count of cities of 15,000 or more and their summed population.
- **City page:** population, timezone, lat/lon and nearby cities with straight-line distance (a service-area section). Postal codes need the web service or the `allCountries` / postal dump **(unverified)**.

Caveats:
- `cities15000` is a population-threshold file and includes **neighbourhoods and subdivisions flagged as populated places**.
  - Calgary's "nearby cities" came back as Centre City, Beltline, Edgemont and Panorama Hills. These sit inside Calgary.
  - **Filter by feature code** (for example keep PPLA/PPLA2/PPLA3/PPLC and exclude plain `PPL` inside the same municipality). This filter is **untested**. Never sum populations of overlapping places.
- Population values can be old or estimated. Straight-line distance is not driving distance.
- The `Columbus` name is ambiguous across states. Match on geonameId (4509177 for Columbus OH), never on name alone.

### d) Live results (dump, 2026-10-19)
Excerpt of the Columbus OH and Calgary rows (`samples/geonames_cities15000_rows.tsv`):
```
4509177 Columbus  39.96118 -82.99879 P PPLA  US  OH 049 ... 913175  ... America/New_York 2026-04-14
5913490 Calgary   51.05011 -114.08529 P PPL  CA  01 ... 1306784 ... America/Edmonton  2026-01-20
```
Computed within 100 km (`samples/geonames_cities15000_nearby_100km.txt`):
- Columbus: 25 other places of 15,000 or more. The nearest are Upper Arlington OH (7 km, pop 34,907), Whitehall (10 km, 18,694), Grove City (12 km, 39,388), Gahanna (12 km, 34,590), Hilliard (16 km, 33,649), Reynoldsburg (16 km, 37,158), Dublin (18 km, 45,098) and Westerville (19 km, 38,384).
- Calgary: 17 hits, but they are mostly neighbourhoods (see caveat). **Do not use this list as is.**
- State totals from the dump: Ohio has 127 places of 15,000 or more (summed pop 5,718,753). Alberta has 33 (summed pop 3,477,672). Both sums include overlapping places for Alberta, so they are indicative only.

**Freshness:** the file was regenerated on 2026-10-19, and the sampled rows were edited 2026-01 and 2026-04. Freshness is good.

### e) Usefulness: 3 out of 5
It is reliable and cheap, but the facts are fairly generic. They are best as a service-area and "metro size" section.

Example sentences (numbers from real data):
- "Columbus has a population of 913,175, and 25 other cities of 15,000 or more lie within 100 km, including Dublin (18 km) and Westerville (19 km). (Source: GeoNames, CC BY 4.0)"
- "Ohio has 127 cities with 15,000 or more residents, and a 3PL in Columbus can reach several within a day's drive. (Source: GeoNames)" Check the "day's drive" claim separately.
- "Calgary operates on the America/Edmonton timezone, the same as the rest of Alberta." This needs a check of the Alberta-wide claim.

### f) Pipeline
- **City slug to row:** keep a hand-made `slug -> geonameId` map, or look up by (country, admin1, name) in a local SQLite or CSV built from the dump. Fail the build on duplicate matches.
- **Caching:** download the dump weekly (it changes daily) and store it with its Last-Modified date. No web calls are needed for the core facts.
- **Citation template:** `Population and nearby-city data: GeoNames (geonames.org), CC BY 4.0, dump of {YYYY-MM-DD}.`
- **Failure handling:** if the dump is unreachable, use the cached copy. If the city is not found, omit the section. Do not guess.
- **Web services (only if a key is added later):** retry 429 or limit errors with backoff, and store results by geonameId.

---

## 2. OpenStreetMap Overpass API

### a) Access, terms, limits
- **No key is needed.** A descriptive `User-Agent` is expected. A request without one to overpass-api.de returned HTTP 406 "Not Acceptable".
- **Public instances.** The OSM wiki (Overpass API page, fetched 2026-10-19) lists:
  - `https://overpass-api.de/api/interpreter` (FOSSGIS)
  - `https://overpass.private.coffee/api/interpreter`, described as "Previously known as overpass.kumi.systems", with "no rate limit" but "notify us in advance if you intend to use our service in a large scale project"
  - `https://maps.mail.ru/osm/tools/overpass/api/interpreter`, with no limits stated
- **Usage policy for the main instance (from the wiki):**
  - Under 10,000 queries per day, under 1 GB per day and under 10 minutes of total processing is fine for one-off use.
  - Regular use should divide those numbers by 100, so under 100 queries and under 10 MB per day.
  - Send a unique `User-Agent` or `Referer`, run no parallel scripts and cache.
  - On HTTP 429 or 406, pause 30 seconds.
  - **"Commercial use should use self-hosted or paid Overpass servers."**
- **Status endpoint:** `/api/status`. At test time overpass-api.de's status returned "502 Gateway Timeout ... at capacity" on three separate attempts. The page also said the public endpoint is "intended for browser-based and human-operated tools" and asked automated users to run their own instance. private.coffee and mail.ru also failed on status (HTTP 500 and 504). The one that worked was `overpass.kumi.systems`, which still resolves.
- **Timeouts:** set `[timeout:N]` in the query. The server kills queries over its limit (the status output showed per-query time limits such as 10 to 280 seconds).
- **License: ODbL 1.0.** Source: OSM Foundation Attribution Guidelines, fetched.
  - Attribution is required when a "Produced Work" is used publicly. The licence needs attribution "reasonably calculated to make any Person ... aware that Content was obtained from [OpenStreetMap]".
  - Statistics and counts that you publish in text are a Produced Work. As I understand ODbL (not legal advice), share-alike applies to a derivative *database* you publish, not to a Produced Work. Do **not** republish the raw feature list as a dataset without checking ODbL.
  - Standard credit text: "© OpenStreetMap contributors" with a link to openstreetmap.org/copyright.
  - Have counsel confirm before launch.

### b) Queries (all tested through kumi.systems)
Call pattern:
```
curl -s -A "WareMatchResearch/0.1 (contact: your-email)" --data-urlencode 'data=<QL>' https://overpass.kumi.systems/api/interpreter
```
(or GET `https://overpass-api.de/api/interpreter?data=<url-encoded QL>`)

1. **Warehouse and industrial counts within 25 km** (tested):
```
[out:json][timeout:60];
(way[building=warehouse](around:25000,LAT,LON););out count;
(way[landuse=industrial](around:25000,LAT,LON);relation[landuse=industrial](around:25000,LAT,LON);)out count;
```
2. **Airports with an IATA code within 150 km** (tested): `nwr[aeroway=aerodrome][iata](around:150000,LAT,LON);out tags center;`
3. **Rail yards and intermodal** (tested): `nwr[railway=yard](around:50000,LAT,LON);out tags center 25;`
4. **Logistics and port tagging** (tested): `nwr[industrial~"^(intermodal|logistics|warehouse|port)$"](around:50000,LAT,LON);out tags center 25;`
5. **Motorway junctions within 25 km** (tested): `node[highway=motorway_junction](around:25000,LAT,LON);out count;`
6. **Ports/harbours** (tested, returned nothing): `nwr[harbour](around:50000,LAT,LON);out tags center 10;`

**Bounding box versus area:** `around:` (radius) was used here, so no city polygon is needed. An area query needs the boundary relation's area id. Example: `area["name"="Columbus"]["admin_level"]...->.a;way[building=warehouse](area.a);out count;`. This form is **untested**. It is more precise (city limits) but depends on boundary tagging and is more expensive. A bounding box (`(south,west,north,east)`) is cheapest but crosses borders.

### c) Facts for pages
- **City page:** the count of `building=warehouse` ways and `landuse=industrial` features within a radius, plus named rail-yard / intermodal nodes with computed distance, and the nearest airport with an IATA code.
- **State and country pages:** an Overpass query is too heavy for a whole state or country. Use city-level results aggregated from your own list, or a Geofabrik extract **(unverified)**.
- **Cargo airports:** OSM has no reliable "cargo" flag. Use a curated list of cargo hubs (for example the IATA codes LCK or CMH, or YYC) and take the distance from OSM coordinates.

Caveats:
- **Completeness differs by region.** Calgary had 181 warehouse ways and 496 industrial features within 25 km, while Columbus had 536 and 475. That gap probably reflects mapping and tagging practice, not real warehouse counts. **A raw count is not comparable across cities.**
- `building=warehouse` covers anything from a self-storage unit to a distribution centre. `landuse=industrial` includes plants and yards that are not warehouses.
- **Silent empty results.** Calgary's `railway=yard` query returned 0 elements, yet Calgary has rail yards (not verified in OSM). Columbus's port query returned 0 and its junction query kept failing. A zero is not a fact.
- The `iata` key was also on hospital heliports (for example "Alberta Children's Hospital CAC6"). Filter by name or use a whitelist.
- Rail-yard items were *nodes* with names like "CSX Intermodal Terminal". They are labels rather than facilities with an area.

### d) Live results
Radius counts around the GeoNames coordinates (`samples/overpass_*_counts_25km.json`):

| | Columbus OH | Calgary AB |
|---|---|---|
| `building=warehouse` ways, 25 km | **536** | **181** |
| `landuse=industrial` (ways + relations), 25 km | **475** (458 ways + 17 relations) | **496** (493 ways + 3 relations) |
| Backend OSM snapshot | 2026-06-01T08:52:28Z | 2026-07-24T11:04:51Z |

Other results:
- **Airports within 60 km (Columbus):** John Glenn Columbus International (CMH) and Rickenbacker International (LCK) are both present. Calgary International (YYC) is present. Excerpt: `("relation","John Glenn Columbus International Airport","CMH")`. Distance to YYC from the sample query: about 10 km (computed from the center).
- **Columbus rail yards within 50 km:** 7 nodes, including `CSX Intermodal Terminal` (about 11 km), `NS Rickenbacker Intermodal Terminal` (about 19 km), `Watkins Yard` (about 7 km) and `CSX Parsons Yard` (about 6 km). Duplicates exist (CSX Parsons Yard appears twice).
- **Columbus logistics tagging within 50 km:** only 3 hits: "UPS Columbus Hub" (`industrial=warehouse`, about 12 km), "Abrasive Technology" and "Cargill" (`industrial=port`, about 41 km). This is far too sparse to claim anything.
- **Calgary logistics within 50 km:** 11 hits, 5 tagged `industrial=logistics` and 6 `industrial=warehouse`, with names such as "Glenmore Trail Corporate Centre".
- **Calgary motorway junctions within 25 km:** 493 nodes. This is a count of tagged nodes and exit ramps, not of distinct interchanges. **Do not publish it as "interchanges".**
- **Reliability:** about half the calls returned HTTP 500 and needed up to 6 retries. Failures happened for Columbus junctions, Columbus cargo airports, Calgary ports, and more on first tries. One query returned HTTP 200 with 0 elements and a different snapshot date.
- **Freshness is uneven.** The same server answered with snapshot timestamps of 2026-05-31, 2026-06-01, 2026-07-15, 2026-07-24 and 2026-07-28 for different queries, so replicas lag by up to about 2 months (the date was 2026-10-19). Record `osm3s.timestamp_osm_base` with every number.

### e) Usefulness: 3 out of 5 as raw data, 4 out of 5 for named facts
The specific named facilities (intermodal terminals, hubs, airports) are unique and useful. Counts are weak and risky.

Example sentences, using only numbers from real calls (use "mapped" wording):
- "OpenStreetMap contributors have mapped 536 warehouse buildings within 25 km of downtown Columbus. This is a floor, not a full count. (Data © OpenStreetMap contributors, ODbL; snapshot 2026-06-01.)"
- "NS Rickenbacker Intermodal Terminal is mapped about 19 km from downtown Columbus, and CSX Intermodal Terminal about 11 km. (© OpenStreetMap contributors)" Distances are straight-line.
- "Calgary International Airport (YYC) sits roughly 10 km from the city centre. (© OpenStreetMap contributors)"
- "Within 25 km of Calgary's centre, OSM has 496 areas tagged as industrial land. (© OpenStreetMap contributors, snapshot 2026-07-24)"

### f) Pipeline
1. **Batch, not build-time.** Run a monthly job per city from a list (slug -> lat/lon from GeoNames). Write JSON to a cache keyed by `slug + query_id`, with the `timestamp_osm_base`, the date and the instance. Page builds read only the cache.
2. **Be polite.** One query at a time with a 5 to 10 second gap. Send `User-Agent: WareMatch-content-pipeline/1.0 (contact email)`. Because this is commercial use, **self-host Overpass or use a paid instance** for any scale. Sleep 30 seconds on 406 or 429. Use fallbacks: overpass-api.de, then private.coffee, then mail.ru.
3. **Failure handling.** Retry 502/503/504/500 up to 6 times with exponential backoff. Treat HTTP 200 with a non-JSON body (an error page or a `remark` field containing "runtime error") as a failure. After the retries, mark the fact "unavailable" and omit its sentence. Never publish a 0 or a missing value as zero.
4. **Avoid overclaiming:**
   - Use wording like "mapped in OpenStreetMap", "at least" and "within 25 km of the city centre". Never write "there are N warehouses".
   - Do not compare counts across cities.
   - Publish a count only when it exceeds a minimum (for example, 20) and the instance snapshot is under 90 days old. Otherwise fall back to qualitative text.
   - Spot-check each city against a satellite view before launch.
   - Never claim "no cargo airport / no intermodal yard" from an empty result.
   - Use whitelists for hubs and airports.
5. **Citation template:** `Data © OpenStreetMap contributors (ODbL, openstreetmap.org/copyright), queried via the Overpass API, snapshot {timestamp_osm_base}. City data: GeoNames (CC BY 4.0).`
6. **Do not republish** the raw feature lists as a downloadable dataset (ODbL share-alike risk).

## Sample files (`samples/`)
`geonames_nokey.txt`, `geonames_demo.txt`, `geonames_cities15000_head.txt`, `geonames_cities15000_rows.tsv`, `geonames_cities15000_nearby_100km.txt`, `geonames_admin1_samples.txt`, `overpass_status.txt`, `overpass_{columbus,calgary}_counts_25km.json`, `..._railyards_50km.json`, `..._logistics_50km.json`, `..._junctions_25km.json` (Calgary only), `..._cargo_airport.json` (Calgary only), `..._ports_50km.json` (Columbus only; 0 elements).
