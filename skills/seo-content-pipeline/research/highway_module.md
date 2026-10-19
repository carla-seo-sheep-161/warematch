# Highways data module (state / city pages) - live test

Run date: 2026-10-19. Code: `pipeline/highway_module.py` (`interstates_in_state(fips, mode)`, `interstates_near(lat, lon, km)`, `geonames_city(name, st)`). Cache: `pipeline/runs/highway_cache/` (42 JSON files after this run). All sources keyless; the Census API key is not used (TIGERweb needs none).

## 1. Method
- Roads: TIGERweb Transportation MapServer, layer 0 (Primary Roads Interstates 5M scale) and layer 3 (Secondary Roads Interstates and US Highways), filtered `RTTYP='I'`. Layer 2 (Primary Roads, all scales) also queried as a cross-check.
- State boundary: TIGERweb State_County layer 0 (States, full detail), requested in WGS84 with `maxAllowableOffset=0.001` deg (~100 m). Intersection is done server-side (`esriSpatialRelIntersects`, polygon POSTed). So exact polygon intersection WAS feasible. Sensitivity check: GA with offset 0.001 vs 0 (1.27 MB polygon) returned the identical 15 routes.
- Bounding box mode is also implemented, to measure false positives.
- City proximity: envelope query (half-side = km converted to degrees: dlat = km/110.574, dlon = km/(111.320*cos(lat))), then exact point-to-polyline distance computed locally (equirectangular plane around the city) and anything beyond `km` is dropped. An envelope is a square, so its corners reach ~1.41x km; this step removes those.
- City coordinates: GeoNames cities15000 (US rows, matched on ascii name + admin1, largest population). Point is GeoNames' city point (not a verified downtown centroid).
- Route names in the data are messy (`I- 75`, `I- -285`, `E I- 10`, `I- 85 Bus`, `I- 10 Hov`). The module normalises to `I-75` and sets Bus routes aside (they are not interstates proper). Zero unparsed names in GA/OH.

## 2. Interstates crossing each state (polygon intersection)
Feature counts are road-segment records, NOT mileage; do not publish them as a size measure.

Georgia (15 routes; raw features L0=211, L3=1):
I-75 (53), I-85 (38), I-20 (32), I-16 (22), I-95 (17), I-285 (12), I-185 (6), I-575 (6), I-675 (6), I-24 (6), I-985 (4), I-475 (4), I-59 (2), I-516 (2), I-520 (2).

Ohio (22 routes; raw features L0=241, L3=0):
I-71 (30), I-90 (28), I-75 (25), I-70 (24), I-77 (18), I-80 (37), I-76 (12), I-271 (12), I-275 (13), I-480 (8), I-675 (6), I-74 (4), I-280 (4), I-270 (2), I-277 (2), I-470 (2), I-471 (2), I-475 (4), I-490 (2), I-670 (2), I-680 (2), I-480N (2).

Bounding-box false positives (found by bbox but not by polygon):
- Georgia, 7 routes: I-10 (14 features), I-26 (25), I-77 (10), I-126 (2), I-295 (2), I-385 (4), I-585 (2). Also I-85 Bus (excluded as Bus). Bbox inflated counts on real routes too (I-85 38 -> 54, I-95 17 -> 24).
- Ohio, 4 routes: I-64 (6), I-79 (18), I-94 (8), I-96 (2). Also I-94 Bus. Inflated: I-75 25 -> 39, I-275 13 -> 23.
Conclusion: bbox is unusable for these two states without polygon filtering; polygon mode is cheap (one POST per layer).

## 3. Cities (GeoNames point; min distance to interstate centerline, km)
| City | within 15 km | additional within 30 km |
|---|---|---|
| Atlanta GA (33.749,-84.388) | I-85 0.2, I-75 0.2, I-20 0.5, I-285 9.8, I-675 10.3 | none (I-575 found in envelope, dropped as >30 km) |
| Savannah GA (32.084,-81.100) | I-16 1.4, I-516 2.7, I-95 12.9 | none |
| Augusta GA (33.471,-81.975) | I-520 4.1, I-20 7.5 | none |
| Columbus OH (39.961,-82.999) | I-70 0.9, I-71 0.9, I-670 1.4, I-270 8.2 | none |
| Cleveland OH (41.500,-81.695) | I-90 1.1, I-77 1.8, I-71 2.2, I-490 2.7, I-480 8.7 | I-480N 15.6, I-271 17.4, I-80 20.7 |
| Cincinnati OH (39.127,-84.514) | I-71 1.5, I-75 1.6, I-471 2.1, I-74 3.6, I-275 9.9 | none |

Envelope-only drops (proof the distance refinement matters): Cleveland 15 km envelope returned I-271 and I-480N, both actually >15 km; Atlanta 30 km envelope returned I-575.
Layers 0 vs 2 gave identical min distances for Atlanta, Cleveland, Cincinnati (layer 0 is not visibly generalised for interstates). The route sets also matched for GA (layer 2: 211 features, same 15 routes).

## 4. Vintage / freshness metadata (what the service itself says)
- Service `currentVersion` 11.5 (ArcGIS Server version, not data version); `documentInfo.Version` 3.5.0.
- Service `copyrightText`: "Source: U.S. Census Bureau". Service description: "Primary roads, secondary roads, local roads, and railroads".
- Layer 0 description: "Source: U.S. Census Bureau Primary roads - Interstates; January 1, 2026". Layer 3: "...Interstates and US Highways; January 1, 2026". State polygon layers: "January 1, 2026 vintage".
- So the stated vintage is January 1, 2026. The service does not name the underlying TIGER/Line release year or say how often it refreshes: UNVERIFIED. It is not a real-time source (new/renumbered interstate segments may lag; not tested).
- Layer 3 interstate content is tiny (605 records nationally, mostly S1200 "Bus" business routes; 1 record in GA that parses to I-75, 0 in OH). Practically, layer 0 carries all real interstates (5,645 records nationally, MTFCC S1100). Layer 3 can be kept for completeness but adds nothing for this use.

## 5. Ground-truth cross-check (my own knowledge, not independently re-verified online)
- Georgia: all expected routes present (I-16, I-20, I-75, I-85, I-95, I-185, I-285) plus the auxiliaries I know exist (I-24, I-59 in the NW corner, I-475 Macon, I-516 Savannah, I-520 Augusta, I-575, I-675, I-985). I-10 correctly absent (does not enter GA). No discrepancy found.
- Ohio: expected I-70/71/75/77/80/90/76/270/275/480 all present; plus I-74, I-271, I-277, I-280, I-470, I-471, I-475, I-490, I-670, I-675, I-680, I-480N, which I recognise as real Ohio routes. I-64, I-79, I-94, I-96 correctly absent.
- Caveats found: (a) `I-480N` is a lettered suffix route; the module keeps it separate from I-480, and a page should decide whether to show it. (b) I-471 is mostly in Kentucky but touches Ohio; I-275 loops OH/KY/IN. Counting them as "Ohio interstates" is correct by geometry. (c) Georgia I-85 and I-75 counts etc. are segment records, not miles. (d) I-285 and I-675 distances from the GeoNames point cannot be checked against an independent source here; I-516/I-520 proximity matches my expectation but is unverified.
- No missing-route discrepancy was found for the 6 cities versus my expectations, but spot-checking distances with a map is recommended before publishing numbers.

## 6. Example sentences for a state page (ready, with citation)
1. "Interstate 16, 20, 24, 59, 75, 85 and 95 all cross Georgia, along with auxiliary routes including I-185, I-285, I-475, I-516, I-520, I-575, I-675 and I-985."
   Citation: U.S. Census Bureau, TIGERweb Transportation (Primary Roads Interstates 5M scale), vintage January 1, 2026, intersected with the Census state boundary.
2. "Ohio is crossed by I-70, I-71, I-74, I-75, I-76, I-77, I-80 and I-90, plus urban routes such as I-270, I-275 and I-480." (same citation form)
3. "Within 15 km of downtown Atlanta (GeoNames city point), the centerlines of I-20, I-75, I-85, I-285 and I-675 pass; I-16 and I-516 are within 3 km of downtown Savannah." Citation: U.S. Census Bureau, TIGERweb Transportation, vintage January 1, 2026; city coordinates GeoNames cities15000 (CC BY 4.0, verify licence text before use).
Citation string template (also `CITATION` in the module): "U.S. Census Bureau, TIGERweb Transportation (Primary Roads Interstates 5M scale; Secondary Roads Interstates and US Highways), vintage January 1, 2026".

## 7. Overclaiming caveat
The data supports only: "interstate X crosses state Y" and "the centerline of interstate X passes within N km of the city's GeoNames point". Do not write "warehouses near the highway", "easy highway access", "N minutes from I-75" (no road-network or travel-time data), or imply any specific warehouse listing is near an interstate (the distance is to the city point, not a facility; interchanges/ramps are not modelled). The 15/30 km values are straight-line distances. Do not present segment counts as mileage or importance. Cite the vintage; do not say "current".

## 8. Viability
High for state-level and city-level "interstates that cross / pass near" facts: keyless, fast, exact polygon intersection works server-side, results match ground truth for GA and OH. Not suited for: travel time, interchange access, truck-route/freight designations, or facility-level claims. Open items: confirm the TIGER release year behind "January 1, 2026" (unverified); a rate-limit/uptime policy for TIGERweb is not documented (cache all results); GeoNames licence attribution; run the remaining 48 states and watch for non-standard names (e.g. Hawaii `I- H-1` is unparsed by the regex and listed under `unparsed_names`), and for paging (`exceededTransferLimit` raises an error; current limit is 100,000 records).
